from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import CartItem
from products.tasks import update_product_cache

@receiver(post_save, sender=CartItem)
def handle_cart_item_save(sender, instance, created, **kwargs):
    """Update product cache when cart item is created or updated"""
    if instance.product_id:
        update_product_cache.delay(instance.product_id)

@receiver(post_delete, sender=CartItem)
def handle_cart_item_delete(sender, instance, **kwargs):
    """Update product cache when cart item is deleted"""
    if instance.product_id:
        update_product_cache.delay(instance.product_id)
