from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from django.contrib.auth import get_user_model
from .models import ContactMessage, SiteSettings

User = get_user_model()

@receiver(post_save, sender=ContactMessage)
def handle_new_contact_message(sender, instance, created, **kwargs):
    """Handle new contact message creation."""
    if created:
        # Send notification email
        instance.send_notification()

@receiver(post_save, sender=SiteSettings)
def clear_site_settings_cache(sender, instance, **kwargs):
    """Clear site settings cache when settings are updated."""
    cache.delete('site_settings')

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a profile for new users."""
    if created and hasattr(instance, 'profile'):
        instance.profile.save()
