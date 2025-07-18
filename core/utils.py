"""
Utility functions for the core app.
"""

import logging
import hashlib
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta

from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.sites.shortcuts import get_current_site
from django.utils.text import slugify

logger = logging.getLogger(__name__)

def send_templated_email(
    subject: str,
    template_name: str,
    context: Dict[str, Any],
    recipient_list: List[str],
    from_email: Optional[str] = None,
    bcc: Optional[List[str]] = None,
    attachments: Optional[List[tuple]] = None
) -> bool:
    """
    Send an email using an HTML template.
    
    Args:
        subject: Email subject
        template_name: Name of the HTML template
        context: Context data for the template
        recipient_list: List of recipient email addresses
        from_email: Sender's email address (optional)
        bcc: List of BCC recipients (optional)
        attachments: List of (filename, content, mimetype) tuples (optional)
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Render HTML content
        html_content = render_to_string(f'emails/{template_name}.html', context)
        text_content = strip_tags(html_content)
        
        # Create email message
        from_email = from_email or settings.DEFAULT_FROM_EMAIL
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            from_email,
            recipient_list,
            bcc=bcc
        )
        msg.attach_alternative(html_content, "text/html")
        
        # Add attachments if any
        if attachments:
            for filename, content, mimetype in attachments:
                msg.attach(filename, content, mimetype)
        
        # Send email
        msg.send()
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False

def generate_unique_slug(
    instance: Any,
    value: str,
    slug_field: str = 'slug',
    max_length: int = 50
) -> str:
    """
    Generate a unique slug for a model instance.
    
    Args:
        instance: Model instance
        value: Value to create slug from
        slug_field: Name of the slug field
        max_length: Maximum length of the slug
    
    Returns:
        str: Unique slug
    """
    slug = slugify(value)
    if len(slug) > max_length:
        slug = slug[:max_length]
    
    model = instance.__class__
    qs = model.objects.filter(**{slug_field: slug}).exclude(pk=instance.pk)
    
    if qs.exists():
        # If slug exists, append number
        slug = f"{slug[:max_length-5]}-{qs.count() + 1}"
    
    return slug

def cache_with_key(
    key: str,
    timeout: int = 3600,
    version: Optional[int] = None
):
    """
    Decorator to cache function results with a specific key.
    
    Args:
        key: Cache key
        timeout: Cache timeout in seconds
        version: Cache version
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache_key = f"{key}:{hashlib.md5(str(args).encode()).hexdigest()}"
            result = cache.get(cache_key, version=version)
            
            if result is None:
                result = func(*args, **kwargs)
                cache.set(cache_key, result, timeout, version=version)
            
            return result
        return wrapper
    return decorator

def track_user_activity(user_id: int, activity_type: str, metadata: Dict = None):
    """
    Track user activity for analytics.
    
    Args:
        user_id: User ID
        activity_type: Type of activity
        metadata: Additional metadata
    """
    from .models import UserActivity
    try:
        UserActivity.objects.create(
            user_id=user_id,
            activity_type=activity_type,
            metadata=metadata or {},
            timestamp=timezone.now()
        )
    except Exception as e:
        logger.error(f"Failed to track user activity: {str(e)}")

def format_currency(
    amount: Union[int, float],
    currency: str = 'USD',
    locale: str = 'en_US'
) -> str:
    """
    Format currency amount.
    
    Args:
        amount: Amount to format
        currency: Currency code
        locale: Locale code
    
    Returns:
        str: Formatted currency string
    """
    import locale as loc
    from babel.numbers import format_currency as babel_format_currency
    
    try:
        loc.setlocale(loc.LC_ALL, locale)
        return babel_format_currency(amount, currency, locale=locale)
    except Exception as e:
        logger.error(f"Currency formatting error: {str(e)}")
        return f"{currency} {amount:.2f}"

def get_client_ip(request) -> Optional[str]:
    """
    Get client IP address from request.
    
    Args:
        request: HTTP request object
    
    Returns:
        str: IP address or None
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')

def log_spam_attempt(instance: Any):
    """
    Log spam attempts for monitoring.
    
    Args:
        instance: Contact message instance
    """
    logger.warning(
        f"Spam attempt detected from {instance.ip_address}",
        extra={
            'ip_address': instance.ip_address,
            'user_agent': instance.user_agent,
            'content': instance.message[:100]
        }
    )

def track_registration(user):
    """
    Track user registration for analytics.
    
    Args:
        user: User instance
    """
    if hasattr(settings, 'ANALYTICS_BACKEND'):
        from .analytics import track_event
        track_event('user_registration', {
            'user_id': user.id,
            'timestamp': timezone.now().isoformat()
        })

def track_contact_form(instance):
    """
    Track contact form submission for analytics.
    
    Args:
        instance: Contact message instance
    """
    if hasattr(settings, 'ANALYTICS_BACKEND'):
        from .analytics import track_event
        track_event('contact_form_submission', {
            'subject': instance.subject,
            'timestamp': timezone.now().isoformat()
        })

def clean_html(html_content: str) -> str:
    """
    Clean HTML content using bleach.
    
    Args:
        html_content: HTML content to clean
    
    Returns:
        str: Cleaned HTML content
    """
    import bleach
    allowed_tags = [
        'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'a', 'img'
    ]
    allowed_attrs = {
        'a': ['href', 'title'],
        'img': ['src', 'alt', 'title']
    }
    return bleach.clean(
        html_content,
        tags=allowed_tags,
        attributes=allowed_attrs,
        strip=True
    )

def generate_sitemap(request) -> Dict:
    """
    Generate sitemap data.
    
    Args:
        request: HTTP request object
    
    Returns:
        dict: Sitemap data
    """
    from django.urls import reverse
    from products.models import Product, Category
    
    site = get_current_site(request)
    protocol = 'https' if request.is_secure() else 'http'
    base_url = f"{protocol}://{site.domain}"
    
    return {
        'site_url': base_url,
        'products': Product.objects.filter(is_active=True),
        'categories': Category.objects.filter(is_active=True),
        'last_modified': timezone.now()
    }
