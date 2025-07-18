"""
Notification handlers for the products app.
"""

import logging
from typing import Any, Dict, List, Optional
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Product, Wishlist
from .constants import NOTIFICATION_TYPES

logger = logging.getLogger(__name__)
User = get_user_model()

class ProductNotifications:
    """Handle product-related notifications."""

    @staticmethod
    def notify_low_stock(product: Product, threshold: int = 5) -> None:
        """
        Send low stock notification.
        
        Args:
            product: Product instance
            threshold: Stock threshold
        """
        try:
            if product.stock <= threshold:
                # Prepare notification data
                context = {
                    'product': product,
                    'current_stock': product.stock,
                    'threshold': threshold,
                    'admin_url': f"/admin/products/product/{product.id}/change/"
                }
                
                # Send email notification
                subject = _('Low Stock Alert: %(product)s') % {'product': product.name}
                message = render_to_string(
                    'products/emails/low_stock_alert.txt',
                    context
                )
                html_message = render_to_string(
                    'products/emails/low_stock_alert.html',
                    context
                )
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.ADMIN_EMAIL],
                    html_message=html_message
                )
                
                # Send to notification service if configured
                if hasattr(settings, 'NOTIFICATIONS_BACKEND'):
                    from core.notifications import send_notification
                    send_notification(
                        'low_stock_alert',
                        context,
                        ['admin']
                    )
                
        except Exception as e:
            logger.error(f"Error sending low stock notification: {str(e)}")

    @staticmethod
    def notify_back_in_stock(product: Product) -> None:
        """
        Notify users when product is back in stock.
        
        Args:
            product: Product instance
        """
        try:
            # Get users who have this product in their wishlist
            wishlists = Wishlist.objects.filter(products=product)
            
            for wishlist in wishlists:
                user = wishlist.user
                
                # Prepare notification data
                context = {
                    'user': user,
                    'product': product,
                    'product_url': product.get_absolute_url()
                }
                
                # Send email notification
                subject = _('Back in Stock: %(product)s') % {'product': product.name}
                message = render_to_string(
                    'products/emails/back_in_stock.txt',
                    context
                )
                html_message = render_to_string(
                    'products/emails/back_in_stock.html',
                    context
                )
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    html_message=html_message
                )
                
                # Send to notification service if configured
                if hasattr(settings, 'NOTIFICATIONS_BACKEND'):
                    from core.notifications import send_notification
                    send_notification(
                        'back_in_stock',
                        context,
                        [user.id]
                    )
                
        except Exception as e:
            logger.error(f"Error sending back in stock notification: {str(e)}")

    @staticmethod
    def notify_price_drop(product: Product, old_price: float) -> None:
        """
        Notify users of price drop.
        
        Args:
            product: Product instance
            old_price: Previous price
        """
        try:
            # Get users who have this product in their wishlist
            wishlists = Wishlist.objects.filter(products=product)
            
            for wishlist in wishlists:
                user = wishlist.user
                
                # Calculate price difference
                price_diff = old_price - float(product.price)
                discount_percent = (price_diff / old_price) * 100
                
                # Prepare notification data
                context = {
                    'user': user,
                    'product': product,
                    'old_price': old_price,
                    'new_price': product.price,
                    'price_diff': price_diff,
                    'discount_percent': round(discount_percent, 2),
                    'product_url': product.get_absolute_url()
                }
                
                # Send email notification
                subject = _('Price Drop Alert: %(product)s') % {'product': product.name}
                message = render_to_string(
                    'products/emails/price_drop.txt',
                    context
                )
                html_message = render_to_string(
                    'products/emails/price_drop.html',
                    context
                )
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    html_message=html_message
                )
                
                # Send to notification service if configured
                if hasattr(settings, 'NOTIFICATIONS_BACKEND'):
                    from core.notifications import send_notification
                    send_notification(
                        'price_drop',
                        context,
                        [user.id]
                    )
                
        except Exception as e:
            logger.error(f"Error sending price drop notification: {str(e)}")

    @staticmethod
    def notify_new_review(review: Any) -> None:
        """
        Notify admin of new product review.
        
        Args:
            review: Review instance
        """
        try:
            # Prepare notification data
            context = {
                'review': review,
                'product': review.product,
                'user': review.user,
                'admin_url': f"/admin/products/review/{review.id}/change/"
            }
            
            # Send email notification
            subject = _('New Review: %(product)s') % {'product': review.product.name}
            message = render_to_string(
                'products/emails/new_review.txt',
                context
            )
            html_message = render_to_string(
                'products/emails/new_review.html',
                context
            )
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL],
                html_message=html_message
            )
            
            # Send to notification service if configured
            if hasattr(settings, 'NOTIFICATIONS_BACKEND'):
                from core.notifications import send_notification
                send_notification(
                    'new_review',
                    context,
                    ['admin']
                )
                
        except Exception as e:
            logger.error(f"Error sending new review notification: {str(e)}")

    @staticmethod
    def notify_product_update(
        product: Product,
        changes: Dict[str, Any]
    ) -> None:
        """
        Notify admin of significant product updates.
        
        Args:
            product: Product instance
            changes: Dictionary of changes
        """
        try:
            # Prepare notification data
            context = {
                'product': product,
                'changes': changes,
                'admin_url': f"/admin/products/product/{product.id}/change/",
                'timestamp': timezone.now()
            }
            
            # Send email notification
            subject = _('Product Updated: %(product)s') % {'product': product.name}
            message = render_to_string(
                'products/emails/product_update.txt',
                context
            )
            html_message = render_to_string(
                'products/emails/product_update.html',
                context
            )
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL],
                html_message=html_message
            )
            
            # Send to notification service if configured
            if hasattr(settings, 'NOTIFICATIONS_BACKEND'):
                from core.notifications import send_notification
                send_notification(
                    'product_update',
                    context,
                    ['admin']
                )
                
        except Exception as e:
            logger.error(f"Error sending product update notification: {str(e)}")

def setup_notification_templates():
    """Set up email templates for notifications."""
    try:
        from django.template.loader import get_template
        
        # Verify all notification templates exist
        templates = [
            'products/emails/low_stock_alert.html',
            'products/emails/low_stock_alert.txt',
            'products/emails/back_in_stock.html',
            'products/emails/back_in_stock.txt',
            'products/emails/price_drop.html',
            'products/emails/price_drop.txt',
            'products/emails/new_review.html',
            'products/emails/new_review.txt',
            'products/emails/product_update.html',
            'products/emails/product_update.txt'
        ]
        
        for template_name in templates:
            get_template(template_name)
            
        logger.info("Product notification templates verified successfully")
        
    except Exception as e:
        logger.error(f"Error verifying notification templates: {str(e)}")
        raise
