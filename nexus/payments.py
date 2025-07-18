import stripe
from django.conf import settings
from django.core.exceptions import ValidationError
from typing import Dict, Any, Optional, List
import logging
from decimal import Decimal
from .monitoring import Monitoring

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentService:
    """Service class for handling payment operations."""

    @staticmethod
    def create_payment_intent(
        amount: Decimal,
        currency: str = 'usd',
        customer_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Create a payment intent with Stripe.
        
        Args:
            amount: Amount to charge (in dollars)
            currency: Currency code
            customer_id: Stripe customer ID
            metadata: Additional metadata
        """
        try:
            intent_data = {
                'amount': int(amount * 100),  # Convert to cents
                'currency': currency,
                'automatic_payment_methods': {'enabled': True},
            }

            if customer_id:
                intent_data['customer'] = customer_id

            if metadata:
                intent_data['metadata'] = metadata

            intent = stripe.PaymentIntent.create(**intent_data)

            logger.info(
                'payment_intent_created',
                amount=amount,
                currency=currency,
                intent_id=intent.id
            )

            return {
                'client_secret': intent.client_secret,
                'intent_id': intent.id,
                'amount': amount,
                'currency': currency,
            }

        except stripe.error.StripeError as e:
            logger.error(
                'payment_intent_failed',
                error=str(e),
                amount=amount,
                currency=currency
            )
            raise ValidationError(f"Payment processing failed: {str(e)}")

    @staticmethod
    def create_customer(
        email: str,
        name: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Create a Stripe customer."""
        try:
            customer_data = {
                'email': email,
            }

            if name:
                customer_data['name'] = name

            if metadata:
                customer_data['metadata'] = metadata

            customer = stripe.Customer.create(**customer_data)

            logger.info(
                'customer_created',
                customer_id=customer.id,
                email=email
            )

            return {
                'customer_id': customer.id,
                'email': customer.email,
                'name': customer.name,
            }

        except stripe.error.StripeError as e:
            logger.error(
                'customer_creation_failed',
                error=str(e),
                email=email
            )
            raise ValidationError(f"Customer creation failed: {str(e)}")

    @staticmethod
    def process_webhook(payload: bytes, signature: str) -> Dict:
        """Process Stripe webhook events."""
        try:
            event = stripe.Webhook.construct_event(
                payload,
                signature,
                settings.STRIPE_WEBHOOK_SECRET
            )

            logger.info(
                'webhook_received',
                event_type=event.type,
                event_id=event.id
            )

            # Handle different event types
            if event.type == 'payment_intent.succeeded':
                return PaymentService._handle_payment_succeeded(event.data.object)
            elif event.type == 'payment_intent.payment_failed':
                return PaymentService._handle_payment_failed(event.data.object)
            elif event.type == 'charge.refunded':
                return PaymentService._handle_refund(event.data.object)
            
            return {'status': 'ignored', 'event_type': event.type}

        except stripe.error.SignatureVerificationError as e:
            logger.error(
                'webhook_signature_verification_failed',
                error=str(e)
            )
            raise ValidationError("Invalid webhook signature")

        except Exception as e:
            logger.error(
                'webhook_processing_failed',
                error=str(e)
            )
            raise

    @staticmethod
    def create_refund(
        payment_intent_id: str,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None
    ) -> Dict:
        """Create a refund for a payment."""
        try:
            refund_data = {
                'payment_intent': payment_intent_id,
            }

            if amount:
                refund_data['amount'] = int(amount * 100)

            if reason:
                refund_data['reason'] = reason

            refund = stripe.Refund.create(**refund_data)

            logger.info(
                'refund_created',
                refund_id=refund.id,
                payment_intent=payment_intent_id,
                amount=amount
            )

            return {
                'refund_id': refund.id,
                'amount': Decimal(refund.amount) / 100,
                'status': refund.status,
            }

        except stripe.error.StripeError as e:
            logger.error(
                'refund_failed',
                error=str(e),
                payment_intent=payment_intent_id
            )
            raise ValidationError(f"Refund processing failed: {str(e)}")

    @staticmethod
    def get_payment_methods(customer_id: str) -> List[Dict]:
        """Get saved payment methods for a customer."""
        try:
            payment_methods = stripe.PaymentMethod.list(
                customer=customer_id,
                type='card'
            )

            return [{
                'id': pm.id,
                'type': pm.type,
                'card': {
                    'brand': pm.card.brand,
                    'last4': pm.card.last4,
                    'exp_month': pm.card.exp_month,
                    'exp_year': pm.card.exp_year,
                }
            } for pm in payment_methods.data]

        except stripe.error.StripeError as e:
            logger.error(
                'payment_methods_retrieval_failed',
                error=str(e),
                customer_id=customer_id
            )
            raise ValidationError(f"Failed to retrieve payment methods: {str(e)}")

    @staticmethod
    def _handle_payment_succeeded(payment_intent: Dict) -> Dict:
        """Handle successful payment webhook."""
        try:
            # Update order status
            from orders.models import Order
            order = Order.objects.get(
                payment_intent_id=payment_intent.id
            )
            order.mark_paid()

            # Send confirmation email
            from nexus.notifications import send_payment_confirmation
            send_payment_confirmation(order)

            return {
                'status': 'success',
                'order_id': order.id,
                'amount': Decimal(payment_intent.amount) / 100,
            }

        except Exception as e:
            logger.error(
                'payment_success_handling_failed',
                error=str(e),
                payment_intent_id=payment_intent.id
            )
            raise

    @staticmethod
    def _handle_payment_failed(payment_intent: Dict) -> Dict:
        """Handle failed payment webhook."""
        try:
            # Update order status
            from orders.models import Order
            order = Order.objects.get(
                payment_intent_id=payment_intent.id
            )
            order.mark_payment_failed()

            # Send notification
            from nexus.notifications import send_payment_failed_notification
            send_payment_failed_notification(order)

            return {
                'status': 'failed',
                'order_id': order.id,
                'error': payment_intent.last_payment_error,
            }

        except Exception as e:
            logger.error(
                'payment_failure_handling_failed',
                error=str(e),
                payment_intent_id=payment_intent.id
            )
            raise

    @staticmethod
    def _handle_refund(charge: Dict) -> Dict:
        """Handle refund webhook."""
        try:
            # Update order status
            from orders.models import Order
            order = Order.objects.get(
                payment_intent_id=charge.payment_intent
            )
            order.mark_refunded()

            # Send notification
            from nexus.notifications import send_refund_confirmation
            send_refund_confirmation(order)

            return {
                'status': 'refunded',
                'order_id': order.id,
                'amount': Decimal(charge.amount_refunded) / 100,
            }

        except Exception as e:
            logger.error(
                'refund_handling_failed',
                error=str(e),
                charge_id=charge.id
            )
            raise

    @staticmethod
    @Monitoring.monitor_performance
    def calculate_payment_summary(
        items: List[Dict],
        shipping_method: str,
        coupon_code: Optional[str] = None
    ) -> Dict:
        """Calculate payment summary including tax and shipping."""
        try:
            subtotal = sum(
                Decimal(str(item['price'])) * item['quantity']
                for item in items
            )

            # Calculate shipping cost
            shipping_cost = PaymentService._calculate_shipping_cost(
                shipping_method,
                subtotal
            )

            # Apply coupon if provided
            discount = Decimal('0')
            if coupon_code:
                discount = PaymentService._apply_coupon(
                    coupon_code,
                    subtotal
                )

            # Calculate tax
            tax = PaymentService._calculate_tax(subtotal - discount)

            # Calculate total
            total = subtotal + shipping_cost + tax - discount

            return {
                'subtotal': subtotal,
                'shipping_cost': shipping_cost,
                'discount': discount,
                'tax': tax,
                'total': total,
            }

        except Exception as e:
            logger.error(
                'payment_summary_calculation_failed',
                error=str(e)
            )
            raise ValidationError("Failed to calculate payment summary")

    @staticmethod
    def _calculate_shipping_cost(method: str, subtotal: Decimal) -> Decimal:
        """Calculate shipping cost based on method and order subtotal."""
        # Free shipping threshold
        if subtotal >= settings.FREE_SHIPPING_THRESHOLD:
            return Decimal('0')

        shipping_rates = {
            'standard': Decimal('5.99'),
            'express': Decimal('12.99'),
            'overnight': Decimal('24.99'),
        }

        return shipping_rates.get(method, Decimal('0'))

    @staticmethod
    def _calculate_tax(amount: Decimal) -> Decimal:
        """Calculate tax for the order amount."""
        # Simplified tax calculation - replace with proper tax service
        tax_rate = Decimal('0.08')  # 8% tax rate
        return (amount * tax_rate).quantize(Decimal('0.01'))

    @staticmethod
    def _apply_coupon(code: str, amount: Decimal) -> Decimal:
        """Apply coupon discount to the amount."""
        try:
            from coupons.models import Coupon
            coupon = Coupon.objects.get(
                code=code,
                is_active=True
            )
            return coupon.calculate_discount(amount)

        except Exception as e:
            logger.error(
                'coupon_application_failed',
                error=str(e),
                code=code
            )
            return Decimal('0')
