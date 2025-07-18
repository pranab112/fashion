from typing import Dict, List, Optional, Any, Union
from django.db.models import Model, QuerySet
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
import logging
from .exceptions import (
    PaymentError,
    InventoryError,
    OrderError,
    ValidationError as NexusValidationError
)
from .monitoring import Monitoring
from .cache import CacheService
from .analytics import AnalyticsService
from .notifications import NotificationManager

logger = logging.getLogger(__name__)

class OrderService:
    """Service for handling order operations."""

    @staticmethod
    @Monitoring.monitor_performance
    def create_order(
        user_id: int,
        items: List[Dict],
        shipping_address: Dict,
        billing_address: Dict,
        payment_method: str,
        **kwargs
    ) -> 'Order':
        """
        Create a new order.
        
        Args:
            user_id: User ID
            items: List of items with product_id and quantity
            shipping_address: Shipping address details
            billing_address: Billing address details
            payment_method: Payment method identifier
        """
        try:
            # Validate order data
            OrderService._validate_order_data(
                items,
                shipping_address,
                billing_address
            )

            # Check inventory
            OrderService._check_inventory(items)

            # Calculate totals
            totals = OrderService._calculate_totals(items)

            # Create order
            from orders.models import Order
            order = Order.objects.create(
                user_id=user_id,
                total_amount=totals['total'],
                shipping_address=shipping_address,
                billing_address=billing_address,
                payment_method=payment_method,
                **kwargs
            )

            # Add items
            OrderService._add_order_items(order, items)

            # Update inventory
            OrderService._update_inventory(items)

            # Send notifications
            NotificationManager.send_order_confirmation(order)

            # Track analytics
            AnalyticsService.track_order_created(order)

            return order

        except Exception as e:
            logger.error(f"Order creation failed: {str(e)}")
            raise OrderError(str(e))

    @staticmethod
    def _validate_order_data(
        items: List[Dict],
        shipping_address: Dict,
        billing_address: Dict
    ) -> None:
        """Validate order data."""
        if not items:
            raise ValidationError("Order must contain at least one item")

        from .validators import OrderValidators
        OrderValidators.validate_shipping_address(shipping_address)
        OrderValidators.validate_shipping_address(billing_address)

    @staticmethod
    def _check_inventory(items: List[Dict]) -> None:
        """Check if items are in stock."""
        from products.models import Product
        for item in items:
            product = Product.objects.get(id=item['product_id'])
            if product.stock_quantity < item['quantity']:
                raise InventoryError(
                    f"Insufficient stock for product {product.name}"
                )

    @staticmethod
    def _calculate_totals(items: List[Dict]) -> Dict[str, Decimal]:
        """Calculate order totals."""
        from products.models import Product
        subtotal = Decimal('0')
        
        for item in items:
            product = Product.objects.get(id=item['product_id'])
            subtotal += product.price * item['quantity']

        # Calculate tax and shipping
        tax = subtotal * Decimal('0.08')  # 8% tax
        shipping = Decimal('10.00')  # Flat rate shipping

        return {
            'subtotal': subtotal,
            'tax': tax,
            'shipping': shipping,
            'total': subtotal + tax + shipping
        }

    @staticmethod
    def _add_order_items(order: 'Order', items: List[Dict]) -> None:
        """Add items to order."""
        from orders.models import OrderItem
        from products.models import Product

        order_items = []
        for item in items:
            product = Product.objects.get(id=item['product_id'])
            order_items.append(
                OrderItem(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    price=product.price,
                    total_price=product.price * item['quantity']
                )
            )
        OrderItem.objects.bulk_create(order_items)

    @staticmethod
    def _update_inventory(items: List[Dict]) -> None:
        """Update product inventory."""
        from products.models import Product
        for item in items:
            Product.objects.filter(id=item['product_id']).update(
                stock_quantity=F('stock_quantity') - item['quantity']
            )

class CartService:
    """Service for handling shopping cart operations."""

    @staticmethod
    def add_to_cart(
        cart: 'Cart',
        product_id: int,
        quantity: int = 1
    ) -> 'CartItem':
        """Add item to cart."""
        try:
            from products.models import Product
            product = Product.objects.get(id=product_id)

            # Check inventory
            if product.stock_quantity < quantity:
                raise InventoryError(
                    f"Only {product.stock_quantity} units available"
                )

            # Add or update cart item
            cart_item, created = cart.items.get_or_create(
                product=product,
                defaults={'quantity': quantity}
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            # Update cart totals
            cart.update_totals()

            # Track analytics
            AnalyticsService.track_add_to_cart(cart, product, quantity)

            return cart_item

        except Exception as e:
            logger.error(f"Add to cart failed: {str(e)}")
            raise

    @staticmethod
    def remove_from_cart(
        cart: 'Cart',
        item_id: int
    ) -> None:
        """Remove item from cart."""
        try:
            item = cart.items.get(id=item_id)
            item.delete()
            cart.update_totals()

        except Exception as e:
            logger.error(f"Remove from cart failed: {str(e)}")
            raise

    @staticmethod
    def update_quantity(
        cart: 'Cart',
        item_id: int,
        quantity: int
    ) -> 'CartItem':
        """Update item quantity."""
        try:
            item = cart.items.get(id=item_id)
            
            # Check inventory
            if item.product.stock_quantity < quantity:
                raise InventoryError(
                    f"Only {item.product.stock_quantity} units available"
                )

            item.quantity = quantity
            item.save()
            cart.update_totals()

            return item

        except Exception as e:
            logger.error(f"Update quantity failed: {str(e)}")
            raise

class PaymentService:
    """Service for handling payment operations."""

    @staticmethod
    def process_payment(
        order: 'Order',
        payment_method: str,
        payment_data: Dict
    ) -> Dict:
        """Process payment for order."""
        try:
            # Validate payment data
            PaymentService._validate_payment_data(payment_data)

            # Get payment processor
            processor = PaymentService._get_payment_processor(payment_method)

            # Process payment
            result = processor.process_payment(
                amount=order.total_amount,
                currency=settings.DEFAULT_CURRENCY,
                payment_data=payment_data
            )

            # Update order status
            if result['status'] == 'success':
                order.status = 'paid'
                order.payment_id = result['transaction_id']
                order.save()

                # Send notifications
                NotificationManager.send_payment_confirmation(order)

            return result

        except Exception as e:
            logger.error(f"Payment processing failed: {str(e)}")
            raise PaymentError(str(e))

    @staticmethod
    def _validate_payment_data(payment_data: Dict) -> None:
        """Validate payment data."""
        required_fields = ['card_number', 'expiry_month', 'expiry_year', 'cvv']
        
        for field in required_fields:
            if field not in payment_data:
                raise ValidationError(f"Missing required field: {field}")

    @staticmethod
    def _get_payment_processor(payment_method: str) -> Any:
        """Get payment processor instance."""
        processors = {
            'stripe': StripePaymentProcessor(),
            'paypal': PayPalPaymentProcessor(),
        }
        
        if payment_method not in processors:
            raise ValidationError(f"Invalid payment method: {payment_method}")
        
        return processors[payment_method]

class InventoryService:
    """Service for handling inventory operations."""

    @staticmethod
    def update_stock(
        product_id: int,
        quantity: int,
        operation: str = 'add'
    ) -> 'Product':
        """Update product stock."""
        try:
            from products.models import Product
            product = Product.objects.get(id=product_id)

            if operation == 'add':
                product.stock_quantity += quantity
            elif operation == 'subtract':
                if product.stock_quantity < quantity:
                    raise InventoryError("Insufficient stock")
                product.stock_quantity -= quantity
            else:
                raise ValidationError(f"Invalid operation: {operation}")

            product.save()

            # Check low stock
            if product.stock_quantity <= product.low_stock_threshold:
                NotificationManager.notify_low_stock(product)

            return product

        except Exception as e:
            logger.error(f"Stock update failed: {str(e)}")
            raise

class ProductService:
    """Service for handling product operations."""

    @staticmethod
    def create_product(data: Dict) -> 'Product':
        """Create new product."""
        try:
            # Validate product data
            ProductService._validate_product_data(data)

            # Create product
            from products.models import Product
            product = Product.objects.create(**data)

            # Process images
            if 'images' in data:
                ProductService._process_product_images(product, data['images'])

            # Create variants
            if 'variants' in data:
                ProductService._create_product_variants(product, data['variants'])

            # Index for search
            from .search import ProductDocument
            ProductDocument().update(product)

            return product

        except Exception as e:
            logger.error(f"Product creation failed: {str(e)}")
            raise

    @staticmethod
    def _validate_product_data(data: Dict) -> None:
        """Validate product data."""
        required_fields = ['name', 'price', 'category']
        
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")

    @staticmethod
    def _process_product_images(
        product: 'Product',
        images: List
    ) -> None:
        """Process and save product images."""
        from .storage import StorageService
        for image in images:
            StorageService.save_image(
                image=image,
                path=f"products/{product.id}/"
            )

    @staticmethod
    def _create_product_variants(
        product: 'Product',
        variants: List[Dict]
    ) -> None:
        """Create product variants."""
        from products.models import ProductVariant
        variant_objects = []
        
        for variant in variants:
            variant['product'] = product
            variant_objects.append(ProductVariant(**variant))
        
        ProductVariant.objects.bulk_create(variant_objects)
