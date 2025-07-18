from django.db.models.signals import (
    pre_save,
    post_save,
    pre_delete,
    post_delete,
    m2m_changed
)
from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed
)
from django.core.signals import request_started, request_finished
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone
import logging
from .monitoring import Monitoring
from .analytics import AnalyticsService
from .notifications import NotificationManager
from .cache import CacheService

logger = logging.getLogger(__name__)
User = get_user_model()

# User-related signals
@receiver(user_logged_in)
def handle_user_login(sender, request, user, **kwargs):
    """Handle user login event."""
    try:
        # Update last login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        # Track login analytics
        AnalyticsService.track_event(
            'user_login',
            user.id,
            {
                'ip_address': request.META.get('REMOTE_ADDR'),
                'user_agent': request.META.get('HTTP_USER_AGENT')
            }
        )

        # Clear user-specific cache
        CacheService.clear_cache_pattern(f"user:{user.id}:*")

        logger.info(f"User logged in: {user.email}")

    except Exception as e:
        logger.error(f"Error handling user login: {str(e)}")
        Monitoring.log_error('user_login_error', e)

@receiver(user_logged_out)
def handle_user_logout(sender, request, user, **kwargs):
    """Handle user logout event."""
    try:
        if user:
            # Track logout analytics
            AnalyticsService.track_event(
                'user_logout',
                user.id,
                {
                    'ip_address': request.META.get('REMOTE_ADDR'),
                    'session_duration': (
                        timezone.now() - user.last_login
                        if user.last_login else None
                    )
                }
            )

            logger.info(f"User logged out: {user.email}")

    except Exception as e:
        logger.error(f"Error handling user logout: {str(e)}")
        Monitoring.log_error('user_logout_error', e)

@receiver(user_login_failed)
def handle_login_failed(sender, credentials, request, **kwargs):
    """Handle failed login attempts."""
    try:
        # Track failed login attempt
        AnalyticsService.track_event(
            'login_failed',
            None,
            {
                'ip_address': request.META.get('REMOTE_ADDR'),
                'username': credentials.get('username', 'unknown')
            }
        )

        logger.warning(
            f"Failed login attempt for user: {credentials.get('username', 'unknown')}"
        )

    except Exception as e:
        logger.error(f"Error handling login failure: {str(e)}")
        Monitoring.log_error('login_failure_error', e)

# Product-related signals
@receiver(post_save, sender='products.Product')
def handle_product_save(sender, instance, created, **kwargs):
    """Handle product save event."""
    try:
        # Clear product cache
        CacheService.clear_cache_pattern(f"product:{instance.id}:*")

        # Update search index
        from .search import ProductDocument
        ProductDocument().update(instance)

        # Check inventory levels
        if instance.stock_quantity <= instance.low_stock_threshold:
            NotificationManager.notify_low_stock(instance)

        # Track event
        AnalyticsService.track_event(
            'product_updated' if not created else 'product_created',
            None,
            {
                'product_id': instance.id,
                'name': instance.name,
                'category': instance.category.name if instance.category else None
            }
        )

        logger.info(
            f"{'Created' if created else 'Updated'} product: {instance.name}"
        )

    except Exception as e:
        logger.error(f"Error handling product save: {str(e)}")
        Monitoring.log_error('product_save_error', e)

# Order-related signals
@receiver(post_save, sender='orders.Order')
def handle_order_save(sender, instance, created, **kwargs):
    """Handle order save event."""
    try:
        if created:
            # Send order confirmation
            NotificationManager.send_order_confirmation(instance)

            # Update inventory
            for item in instance.items.all():
                product = item.product
                product.stock_quantity -= item.quantity
                product.save()

            # Track analytics
            AnalyticsService.track_event(
                'order_created',
                instance.user.id if instance.user else None,
                {
                    'order_id': instance.id,
                    'total_amount': float(instance.total_amount),
                    'items_count': instance.items.count()
                }
            )
        else:
            # Handle status changes
            if instance.status_changed:
                NotificationManager.notify_order_status_change(
                    instance,
                    instance.status
                )

        logger.info(
            f"{'Created' if created else 'Updated'} order: {instance.id}"
        )

    except Exception as e:
        logger.error(f"Error handling order save: {str(e)}")
        Monitoring.log_error('order_save_error', e)

# Cart-related signals
@receiver(m2m_changed, sender='cart.Cart.items.through')
def handle_cart_update(sender, instance, action, **kwargs):
    """Handle cart update event."""
    try:
        if action in ["post_add", "post_remove", "post_clear"]:
            # Clear cart cache
            CacheService.clear_cache_pattern(f"cart:{instance.id}:*")

            # Track event
            AnalyticsService.track_event(
                'cart_updated',
                instance.user.id if instance.user else None,
                {
                    'cart_id': instance.id,
                    'action': action,
                    'items_count': instance.items.count(),
                    'total_amount': float(instance.total_amount)
                }
            )

            # Check for abandoned cart
            if action == "post_add" and instance.user:
                from django.utils import timezone
                if (timezone.now() - instance.updated_at).hours >= 1:
                    NotificationManager.schedule_abandoned_cart_reminder(instance)

        logger.info(f"Updated cart: {instance.id}")

    except Exception as e:
        logger.error(f"Error handling cart update: {str(e)}")
        Monitoring.log_error('cart_update_error', e)

# Review-related signals
@receiver(post_save, sender='products.Review')
def handle_review_save(sender, instance, created, **kwargs):
    """Handle review save event."""
    try:
        if created:
            # Update product rating
            product = instance.product
            product.update_average_rating()

            # Clear product cache
            CacheService.clear_cache_pattern(f"product:{product.id}:*")

            # Track event
            AnalyticsService.track_event(
                'review_created',
                instance.user.id,
                {
                    'product_id': product.id,
                    'rating': instance.rating,
                    'review_id': instance.id
                }
            )

            # Notify product owner
            NotificationManager.notify_new_review(instance)

        logger.info(
            f"{'Created' if created else 'Updated'} review: {instance.id}"
        )

    except Exception as e:
        logger.error(f"Error handling review save: {str(e)}")
        Monitoring.log_error('review_save_error', e)

# Request signals
@receiver(request_started)
def handle_request_started(sender, environ, **kwargs):
    """Handle request start event."""
    try:
        # Track request metrics
        Monitoring.track_request_start(environ)

    except Exception as e:
        logger.error(f"Error handling request start: {str(e)}")
        Monitoring.log_error('request_start_error', e)

@receiver(request_finished)
def handle_request_finished(sender, **kwargs):
    """Handle request finish event."""
    try:
        # Track request metrics
        Monitoring.track_request_end()

    except Exception as e:
        logger.error(f"Error handling request finish: {str(e)}")
        Monitoring.log_error('request_finish_error', e)

# Cache invalidation signals
@receiver(post_save)
def handle_cache_invalidation(sender, instance, **kwargs):
    """Handle cache invalidation for model changes."""
    try:
        # Get model name
        model_name = sender._meta.model_name

        # Clear model-specific cache
        CacheService.clear_cache_pattern(f"{model_name}:*")

        # Clear related caches based on model
        if hasattr(instance, 'get_related_cache_keys'):
            related_keys = instance.get_related_cache_keys()
            for key in related_keys:
                CacheService.clear_cache_pattern(key)

    except Exception as e:
        logger.error(f"Error handling cache invalidation: {str(e)}")
        Monitoring.log_error('cache_invalidation_error', e)

# Search index signals
@receiver(post_save)
def handle_search_index_update(sender, instance, **kwargs):
    """Handle search index updates."""
    try:
        # Check if model is indexed
        if hasattr(instance, 'update_search_index'):
            instance.update_search_index()

    except Exception as e:
        logger.error(f"Error handling search index update: {str(e)}")
        Monitoring.log_error('search_index_update_error', e)
