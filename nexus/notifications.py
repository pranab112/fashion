from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from typing import Dict, List, Optional, Union
import logging
from .monitoring import Monitoring
from .cache import CacheService
from celery import shared_task

logger = logging.getLogger(__name__)

class EmailService:
    """Service class for handling email notifications."""

    TEMPLATES = {
        'welcome': {
            'subject': 'Welcome to NEXUS Fashion Store',
            'template': 'emails/welcome.html',
        },
        'order_confirmation': {
            'subject': 'Order Confirmation - #{order_id}',
            'template': 'emails/order_confirmation.html',
        },
        'order_shipped': {
            'subject': 'Your Order #{order_id} Has Been Shipped',
            'template': 'emails/order_shipped.html',
        },
        'order_delivered': {
            'subject': 'Your Order #{order_id} Has Been Delivered',
            'template': 'emails/order_delivered.html',
        },
        'payment_confirmation': {
            'subject': 'Payment Confirmation - #{order_id}',
            'template': 'emails/payment_confirmation.html',
        },
        'payment_failed': {
            'subject': 'Payment Failed - Order #{order_id}',
            'template': 'emails/payment_failed.html',
        },
        'password_reset': {
            'subject': 'Reset Your Password',
            'template': 'emails/password_reset.html',
        },
        'account_verification': {
            'subject': 'Verify Your Email Address',
            'template': 'emails/account_verification.html',
        },
        'abandoned_cart': {
            'subject': 'Complete Your Purchase',
            'template': 'emails/abandoned_cart.html',
        },
        'price_drop': {
            'subject': 'Price Drop Alert!',
            'template': 'emails/price_drop.html',
        },
        'back_in_stock': {
            'subject': 'Back in Stock Notification',
            'template': 'emails/back_in_stock.html',
        },
        'review_request': {
            'subject': 'How Was Your Purchase?',
            'template': 'emails/review_request.html',
        },
    }

    @classmethod
    @Monitoring.monitor_performance
    def send_email(
        cls,
        template_name: str,
        to_email: Union[str, List[str]],
        context: Dict,
        from_email: Optional[str] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[Dict]] = None,
        priority: str = 'medium'
    ) -> bool:
        """
        Send an email using a template.
        
        Args:
            template_name: Name of the template to use
            to_email: Recipient email(s)
            context: Template context data
            from_email: Sender email (optional)
            bcc: BCC recipients (optional)
            attachments: List of attachment dictionaries (optional)
            priority: Email priority (high, medium, low)
        """
        try:
            template_config = cls.TEMPLATES.get(template_name)
            if not template_config:
                raise ValueError(f"Template {template_name} not found")

            # Get template subject and format with context
            subject = template_config['subject'].format(**context)

            # Render HTML content
            html_content = render_to_string(
                template_config['template'],
                context
            )

            # Create plain text version
            text_content = strip_tags(html_content)

            # Create email message
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email or settings.DEFAULT_FROM_EMAIL,
                to=[to_email] if isinstance(to_email, str) else to_email,
                bcc=bcc,
            )

            # Attach HTML version
            email.attach_alternative(html_content, "text/html")

            # Add attachments if any
            if attachments:
                for attachment in attachments:
                    email.attach(
                        filename=attachment['filename'],
                        content=attachment['content'],
                        mimetype=attachment['mimetype']
                    )

            # Set priority header
            priority_headers = {
                'high': 1,
                'medium': 3,
                'low': 5
            }
            email.extra_headers['X-Priority'] = priority_headers.get(priority, 3)

            # Send email
            email.send(fail_silently=False)

            # Log success
            logger.info(
                'email_sent',
                template=template_name,
                to=to_email,
                subject=subject
            )

            return True

        except Exception as e:
            logger.error(
                'email_send_failed',
                error=str(e),
                template=template_name,
                to=to_email
            )
            return False

    @classmethod
    @shared_task(
        name='send_welcome_email',
        max_retries=3,
        default_retry_delay=300
    )
    def send_welcome_email(cls, user_email: str, user_name: str):
        """Send welcome email to new users."""
        context = {
            'user_name': user_name,
            'login_url': f"{settings.SITE_URL}/login",
            'help_url': f"{settings.SITE_URL}/help",
        }
        return cls.send_email('welcome', user_email, context)

    @classmethod
    @shared_task(
        name='send_order_confirmation',
        max_retries=3,
        default_retry_delay=300
    )
    def send_order_confirmation(cls, order):
        """Send order confirmation email."""
        context = {
            'order_id': order.id,
            'order_date': order.created_at,
            'order_items': order.items.all(),
            'order_total': order.total_amount,
            'shipping_address': order.shipping_address,
            'tracking_url': f"{settings.SITE_URL}/orders/{order.id}/track",
        }
        return cls.send_email(
            'order_confirmation',
            order.user.email,
            context,
            priority='high'
        )

    @classmethod
    @shared_task(name='send_abandoned_cart_reminder')
    def send_abandoned_cart_reminder(cls, user_email: str, cart_data: Dict):
        """Send reminder for abandoned cart."""
        context = {
            'cart_items': cart_data['items'],
            'cart_total': cart_data['total'],
            'checkout_url': f"{settings.SITE_URL}/cart",
        }
        return cls.send_email('abandoned_cart', user_email, context)

    @classmethod
    @shared_task(name='send_price_drop_alert')
    def send_price_drop_alert(
        cls,
        user_email: str,
        product_id: int,
        old_price: float,
        new_price: float
    ):
        """Send price drop notification."""
        from products.models import Product
        product = Product.objects.get(id=product_id)
        
        context = {
            'product': product,
            'old_price': old_price,
            'new_price': new_price,
            'product_url': f"{settings.SITE_URL}/products/{product.slug}",
        }
        return cls.send_email('price_drop', user_email, context)

    @classmethod
    @shared_task(name='send_back_in_stock_notification')
    def send_back_in_stock_notification(
        cls,
        user_email: str,
        product_id: int
    ):
        """Send back in stock notification."""
        from products.models import Product
        product = Product.objects.get(id=product_id)
        
        context = {
            'product': product,
            'product_url': f"{settings.SITE_URL}/products/{product.slug}",
        }
        return cls.send_email('back_in_stock', user_email, context)

    @classmethod
    @shared_task(
        name='send_review_request',
        max_retries=2,
        default_retry_delay=86400  # 1 day
    )
    def send_review_request(cls, order):
        """Send review request email."""
        context = {
            'order_id': order.id,
            'order_date': order.created_at,
            'order_items': order.items.all(),
            'review_url': f"{settings.SITE_URL}/orders/{order.id}/review",
        }
        return cls.send_email('review_request', order.user.email, context)

    @classmethod
    def send_password_reset(cls, user_email: str, reset_url: str):
        """Send password reset email."""
        context = {
            'reset_url': reset_url,
            'valid_hours': settings.PASSWORD_RESET_TIMEOUT // 3600,
        }
        return cls.send_email(
            'password_reset',
            user_email,
            context,
            priority='high'
        )

    @classmethod
    def send_account_verification(cls, user_email: str, verify_url: str):
        """Send account verification email."""
        context = {
            'verify_url': verify_url,
            'valid_hours': settings.ACCOUNT_VERIFICATION_TIMEOUT // 3600,
        }
        return cls.send_email(
            'account_verification',
            user_email,
            context,
            priority='high'
        )

class NotificationManager:
    """Manager class for handling all types of notifications."""

    @staticmethod
    @Monitoring.monitor_performance
    def notify_order_status_change(order, status: str):
        """Handle order status change notifications."""
        if status == 'shipped':
            EmailService.send_order_shipped.delay(order)
        elif status == 'delivered':
            EmailService.send_order_delivered.delay(order)
            # Schedule review request for 7 days later
            EmailService.send_review_request.apply_async(
                args=[order],
                countdown=604800  # 7 days
            )

    @staticmethod
    def schedule_abandoned_cart_reminder(cart):
        """Schedule abandoned cart reminder."""
        # Cache cart data
        cart_data = {
            'items': list(cart.items.all().values()),
            'total': float(cart.total),
        }
        cache_key = f"abandoned_cart:{cart.id}"
        CacheService.set_cache(cache_key, cart_data, timeout=86400)  # 24 hours

        # Schedule reminder
        EmailService.send_abandoned_cart_reminder.apply_async(
            args=[cart.user.email, cart_data],
            countdown=7200  # 2 hours
        )

    @staticmethod
    def notify_low_stock(product):
        """Notify admin about low stock."""
        context = {
            'product': product,
            'current_stock': product.stock_quantity,
            'threshold': settings.LOW_STOCK_THRESHOLD,
        }
        EmailService.send_email(
            'low_stock_alert',
            settings.ADMIN_EMAIL,
            context
        )

    @staticmethod
    def notify_price_change(product, old_price: float, new_price: float):
        """Notify users about price changes."""
        from products.models import PriceAlert
        alerts = PriceAlert.objects.filter(
            product=product,
            target_price__gte=new_price,
            is_active=True
        )

        for alert in alerts:
            EmailService.send_price_drop_alert.delay(
                alert.user.email,
                product.id,
                old_price,
                new_price
            )
            alert.deactivate()

    @staticmethod
    def notify_back_in_stock(product):
        """Notify users when product is back in stock."""
        from products.models import StockAlert
        alerts = StockAlert.objects.filter(
            product=product,
            is_active=True
        )

        for alert in alerts:
            EmailService.send_back_in_stock_notification.delay(
                alert.user.email,
                product.id
            )
            alert.deactivate()
