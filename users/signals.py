"""
Signal handlers for the users app.
"""

import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Profile, UserActivity

logger = logging.getLogger(__name__)

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a user profile when a new user is created"""
    if created:
        try:
            Profile.objects.create(user=instance)
            
            # Log user creation
            UserActivity.objects.create(
                user=instance,
                activity_type='account_created',
                timestamp=timezone.now()
            )
        except Exception as e:
            logger.error(f"Error creating user profile: {str(e)}")

@receiver(pre_save, sender=User)
def handle_user_status_change(sender, instance, **kwargs):
    """Handle user status changes"""
    try:
        if instance.pk:  # Only for existing users
            old_instance = User.objects.get(pk=instance.pk)
            
            # Check if is_active status changed
            if old_instance.is_active != instance.is_active:
                activity_type = 'account_activated' if instance.is_active else 'account_deactivated'
                UserActivity.objects.create(
                    user=instance,
                    activity_type=activity_type,
                    timestamp=timezone.now()
                )
                
            # Check if email changed
            if old_instance.email != instance.email:
                UserActivity.objects.create(
                    user=instance,
                    activity_type='email_changed',
                    timestamp=timezone.now(),
                    details={'old_email': old_instance.email, 'new_email': instance.email}
                )
    except Exception as e:
        logger.error(f"Error handling user status change: {str(e)}")

@receiver(post_save, sender=Profile)
def handle_profile_update(sender, instance, created, **kwargs):
    """Handle profile updates"""
    if not created:  # Only for updates, not creation
        try:
            UserActivity.objects.create(
                user=instance.user,
                activity_type='profile_updated',
                timestamp=timezone.now()
            )
        except Exception as e:
            logger.error(f"Error handling profile update: {str(e)}")
