"""
Celery tasks for the core app.
"""

import logging
from typing import Optional, List
from datetime import datetime, timedelta

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Q
from PIL import Image
from io import BytesIO

from .models import (
    SiteConfiguration,
    Banner,
    Newsletter,
    ContactMessage,
    Testimonial,
    SocialProof
)
from .utils import send_templated_email, clean_html

logger = logging.getLogger(__name__)

# Email Tasks
@shared_task(
    name='core.tasks.send_welcome_email',
    bind=True,
    max_retries=3,
    default_retry_delay=300  # 5 minutes
)
def send_welcome_email(self, subscriber_id: int) -> bool:
    """
    Send welcome email to new newsletter subscribers.
    
    Args:
        subscriber_id: ID of the newsletter subscriber
    
    Returns:
        bool: True if email was sent successfully
    """
    try:
        subscriber = Newsletter.objects.get(id=subscriber_id)
        context = {
            'email': subscriber.email,
            'unsubscribe_url': f"{settings.SITE_URL}/newsletter/unsubscribe/{subscriber.confirmation_token}/"
        }
        return send_templated_email(
            subject="Welcome to NEXUS Newsletter!",
            template_name="newsletter/welcome_email",
            context=context,
            recipient_list=[subscriber.email]
        )
    except Exception as exc:
        logger.error(f"Failed to send welcome email: {str(exc)}")
        self.retry(exc=exc)

@shared_task(
    name='core.tasks.send_contact_notification_to_staff',
    bind=True,
    max_retries=3
)
def send_contact_notification_to_staff(self, message_id: int) -> bool:
    """
    Notify staff about new contact messages.
    
    Args:
        message_id: ID of the contact message
    
    Returns:
        bool: True if notification was sent successfully
    """
    try:
        message = ContactMessage.objects.get(id=message_id)
        context = {
            'message': message,
            'admin_url': f"{settings.SITE_URL}/admin/core/contactmessage/{message.id}/"
        }
        return send_templated_email(
            subject=f"New Contact Message: {message.subject}",
            template_name="contact/staff_notification",
            context=context,
            recipient_list=[settings.CONTACT_EMAIL]
        )
    except Exception as exc:
        logger.error(f"Failed to send staff notification: {str(exc)}")
        self.retry(exc=exc)

# Image Processing Tasks
@shared_task(name='core.tasks.process_banner_image')
def process_banner_image(banner_id: int) -> bool:
    """
    Process and optimize banner images.
    
    Args:
        banner_id: ID of the banner
    
    Returns:
        bool: True if processing was successful
    """
    try:
        banner = Banner.objects.get(id=banner_id)
        if not banner.image:
            return False

        # Open image
        img = Image.open(banner.image.path)

        # Process for different sizes
        sizes = [(1920, 600), (1280, 400), (768, 240)]
        for width, height in sizes:
            # Resize image maintaining aspect ratio
            img_copy = img.copy()
            img_copy.thumbnail((width, height), Image.LANCZOS)

            # Save optimized version
            output = BytesIO()
            img_copy.save(output, format='WEBP', quality=85, optimize=True)
            
            # Save to storage
            filename = f"banners/{banner.id}_{width}x{height}.webp"
            banner.image.storage.save(filename, output)

        return True
    except Exception as e:
        logger.error(f"Failed to process banner image: {str(e)}")
        return False

@shared_task(name='core.tasks.process_testimonial_image')
def process_testimonial_image(testimonial_id: int) -> bool:
    """
    Process and optimize testimonial images.
    
    Args:
        testimonial_id: ID of the testimonial
    
    Returns:
        bool: True if processing was successful
    """
    try:
        testimonial = Testimonial.objects.get(id=testimonial_id)
        if not testimonial.image:
            return False

        # Open image
        img = Image.open(testimonial.image.path)

        # Create thumbnail
        size = (150, 150)
        img.thumbnail(size, Image.LANCZOS)

        # Save optimized version
        output = BytesIO()
        img.save(output, format='WEBP', quality=85, optimize=True)
        
        # Save to storage
        filename = f"testimonials/{testimonial.id}_thumb.webp"
        testimonial.image.storage.save(filename, output)

        return True
    except Exception as e:
        logger.error(f"Failed to process testimonial image: {str(e)}")
        return False

# Maintenance Tasks
@shared_task(name='core.tasks.clean_expired_sessions')
def clean_expired_sessions() -> int:
    """
    Clean expired sessions from the database.
    
    Returns:
        int: Number of sessions cleaned
    """
    from django.contrib.sessions.models import Session
    expired = Session.objects.filter(expire_date__lt=timezone.now())
    count = expired.count()
    expired.delete()
    return count

@shared_task(name='core.tasks.update_social_proof_queue')
def update_social_proof_queue() -> bool:
    """
    Update the queue of social proof notifications.
    
    Returns:
        bool: True if update was successful
    """
    try:
        proofs = SocialProof.objects.filter(is_active=True)
        cache.set('social_proof_queue', list(proofs.values()), timeout=3600)
        return True
    except Exception as e:
        logger.error(f"Failed to update social proof queue: {str(e)}")
        return False

@shared_task(name='core.tasks.clean_inactive_newsletters')
def clean_inactive_newsletters() -> int:
    """
    Remove unconfirmed newsletter subscriptions.
    
    Returns:
        int: Number of subscriptions removed
    """
    cutoff = timezone.now() - timedelta(days=30)
    inactive = Newsletter.objects.filter(
        is_active=False,
        created_at__lt=cutoff
    )
    count = inactive.count()
    inactive.delete()
    return count

# Cache Management Tasks
@shared_task(name='core.tasks.refresh_site_cache')
def refresh_site_cache() -> bool:
    """
    Refresh various site-wide caches.
    
    Returns:
        bool: True if refresh was successful
    """
    try:
        # Clear existing caches
        cache.delete_pattern('site_settings*')
        cache.delete_pattern('active_banners*')
        cache.delete_pattern('featured_products*')
        
        # Rebuild caches
        config = SiteConfiguration.objects.first()
        if config:
            cache.set('site_settings', {
                'site_name': config.site_name,
                'maintenance_mode': config.maintenance_mode,
                'contact_email': config.contact_email
            }, timeout=3600)
        
        return True
    except Exception as e:
        logger.error(f"Failed to refresh site cache: {str(e)}")
        return False

# Analytics Tasks
@shared_task(name='core.tasks.aggregate_daily_stats')
def aggregate_daily_stats(date: Optional[str] = None) -> bool:
    """
    Aggregate daily statistics for analytics.
    
    Args:
        date: Date to aggregate stats for (YYYY-MM-DD)
    
    Returns:
        bool: True if aggregation was successful
    """
    try:
        if date:
            target_date = datetime.strptime(date, '%Y-%m-%d').date()
        else:
            target_date = timezone.now().date() - timedelta(days=1)

        # Aggregate various statistics
        # This is a placeholder - implement actual aggregation logic
        stats = {
            'date': target_date.isoformat(),
            'visitors': 0,
            'page_views': 0,
            'orders': 0,
            'revenue': 0.0
        }

        # Store aggregated stats
        cache.set(f'daily_stats_{target_date.isoformat()}', stats, timeout=None)
        return True
    except Exception as e:
        logger.error(f"Failed to aggregate daily stats: {str(e)}")
        return False
