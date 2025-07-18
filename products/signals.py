"""
Signal handlers for the products app.
"""

import logging
from typing import Any, Dict, Optional
from django.db.models.signals import (
    pre_save,
    post_save,
    pre_delete,
    post_delete,
    m2m_changed
)
from django.dispatch import receiver
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings

from .models import (
    Product,
    Category,
    Brand,
    ProductImage,
    Review,
    ProductView
)
from .services import ProductService
from .cache import (
    invalidate_product_caches,
    invalidate_category_caches,
    invalidate_brand_caches
)
from .tasks import (
    update_search_index,
    generate_product_thumbnails,
    notify_low_stock,
    update_product_analytics
)

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=Product)
def handle_product_pre_save(
    sender: Any,
    instance: Product,
    **kwargs: Any
) -> None:
    """
    Handle product pre-save signal.
    
    Args:
        sender: Signal sender
        instance: Product instance
        **kwargs: Signal keyword arguments
    """
    try:
        # Check if this is a new product
        if instance.pk is None:
            # Generate SKU if not provided
            if not instance.sku:
                instance.sku = ProductService.generate_sku()
            
            # Set initial timestamps
            now = timezone.now()
            instance.created_at = now
            instance.updated_at = now
        else:
            # Update timestamp
            instance.updated_at = timezone.now()
            
            # Get original instance
            try:
                original = Product.objects.get(pk=instance.pk)
                
                # Check for price changes
                if original.price != instance.price:
                    # Track price history
                    ProductService.track_price_change(
                        instance,
                        original.price,
                        instance.price
                    )
                
                # Check for stock changes
                if original.stock != instance.stock:
                    # Track stock history
                    ProductService.track_stock_change(
                        instance,
                        original.stock,
                        instance.stock
                    )
                    
                    # Check low stock threshold
                    if (
                        instance.stock <= instance.low_stock_threshold and
                        original.stock > instance.low_stock_threshold
                    ):
                        notify_low_stock.delay(instance.pk)
                
            except Product.DoesNotExist:
                pass
            
    except Exception as e:
        logger.error(f"Error in product pre-save signal: {str(e)}")

@receiver(post_save, sender=Product)
def handle_product_post_save(
    sender: Any,
    instance: Product,
    created: bool,
    **kwargs: Any
) -> None:
    """
    Handle product post-save signal.
    
    Args:
        sender: Signal sender
        instance: Product instance
        created: Whether this is a new instance
        **kwargs: Signal keyword arguments
    """
    try:
        # Invalidate caches
        invalidate_product_caches(instance.pk)
        
        # Update search index
        update_search_index.delay(instance.pk)
        
        # Update analytics
        update_product_analytics.delay(instance.pk)
        
        if created:
            # Send notifications for new product
            if instance.is_new_arrival:
                from .notifications import notify_new_arrival
                notify_new_arrival.delay(instance.pk)
        
    except Exception as e:
        logger.error(f"Error in product post-save signal: {str(e)}")

@receiver(pre_delete, sender=Product)
def handle_product_pre_delete(
    sender: Any,
    instance: Product,
    **kwargs: Any
) -> None:
    """
    Handle product pre-delete signal.
    
    Args:
        sender: Signal sender
        instance: Product instance
        **kwargs: Signal keyword arguments
    """
    try:
        # Clean up associated files
        for image in instance.images.all():
            image.image.delete(save=False)
            for thumbnail in image.thumbnails.all():
                thumbnail.image.delete(save=False)
        
    except Exception as e:
        logger.error(f"Error in product pre-delete signal: {str(e)}")

@receiver(post_delete, sender=Product)
def handle_product_post_delete(
    sender: Any,
    instance: Product,
    **kwargs: Any
) -> None:
    """
    Handle product post-delete signal.
    
    Args:
        sender: Signal sender
        instance: Product instance
        **kwargs: Signal keyword arguments
    """
    try:
        # Invalidate caches
        invalidate_product_caches(instance.pk)
        
        # Remove from search index
        update_search_index.delay(instance.pk, delete=True)
        
    except Exception as e:
        logger.error(f"Error in product post-delete signal: {str(e)}")

@receiver(post_save, sender=ProductImage)
def handle_product_image_post_save(
    sender: Any,
    instance: ProductImage,
    created: bool,
    **kwargs: Any
) -> None:
    """
    Handle product image post-save signal.
    
    Args:
        sender: Signal sender
        instance: ProductImage instance
        created: Whether this is a new instance
        **kwargs: Signal keyword arguments
    """
    try:
        if created:
            # Generate thumbnails
            generate_product_thumbnails.delay(instance.pk)
        
        # Invalidate caches
        invalidate_product_caches(instance.product.pk)
        
    except Exception as e:
        logger.error(f"Error in product image post-save signal: {str(e)}")

@receiver(post_save, sender=Review)
def handle_review_post_save(
    sender: Any,
    instance: Review,
    created: bool,
    **kwargs: Any
) -> None:
    """
    Handle review post-save signal.
    
    Args:
        sender: Signal sender
        instance: Review instance
        created: Whether this is a new instance
        **kwargs: Signal keyword arguments
    """
    try:
        # Update product rating
        instance.product.update_rating()
        
        # Invalidate caches
        invalidate_product_caches(instance.product.pk)
        
        if created and instance.is_verified:
            # Send notification
            from .notifications import notify_new_review
            notify_new_review.delay(instance.pk)
        
    except Exception as e:
        logger.error(f"Error in review post-save signal: {str(e)}")

@receiver(post_save, sender=Category)
def handle_category_post_save(
    sender: Any,
    instance: Category,
    **kwargs: Any
) -> None:
    """
    Handle category post-save signal.
    
    Args:
        sender: Signal sender
        instance: Category instance
        **kwargs: Signal keyword arguments
    """
    try:
        # Invalidate caches
        invalidate_category_caches(instance.pk)
        
    except Exception as e:
        logger.error(f"Error in category post-save signal: {str(e)}")

@receiver(post_save, sender=Brand)
def handle_brand_post_save(
    sender: Any,
    instance: Brand,
    **kwargs: Any
) -> None:
    """
    Handle brand post-save signal.
    
    Args:
        sender: Signal sender
        instance: Brand instance
        **kwargs: Signal keyword arguments
    """
    try:
        # Invalidate caches
        invalidate_brand_caches(instance.pk)
        
    except Exception as e:
        logger.error(f"Error in brand post-save signal: {str(e)}")

@receiver(post_save, sender=ProductView)
def handle_product_view_post_save(
    sender: Any,
    instance: ProductView,
    created: bool,
    **kwargs: Any
) -> None:
    """
    Handle product view post-save signal.
    
    Args:
        sender: Signal sender
        instance: ProductView instance
        created: Whether this is a new instance
        **kwargs: Signal keyword arguments
    """
    try:
        if created:
            # Update analytics
            update_product_analytics.delay(instance.product.pk)
        
    except Exception as e:
        logger.error(f"Error in product view post-save signal: {str(e)}")

@receiver(m2m_changed, sender=Product.tags.through)
def handle_product_tags_changed(
    sender: Any,
    instance: Product,
    action: str,
    **kwargs: Any
) -> None:
    """
    Handle product tags m2m changed signal.
    
    Args:
        sender: Signal sender
        instance: Product instance
        action: Action performed
        **kwargs: Signal keyword arguments
    """
    try:
        if action in ["post_add", "post_remove", "post_clear"]:
            # Invalidate caches
            invalidate_product_caches(instance.pk)
            
            # Update search index
            update_search_index.delay(instance.pk)
        
    except Exception as e:
        logger.error(f"Error in product tags changed signal: {str(e)}")
