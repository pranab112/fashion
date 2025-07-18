"""
Custom model managers for the core app.
"""

from typing import Any, Dict, List, Optional, Union
from django.db import models
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from django.core.cache import cache

class BannerManager(models.Manager):
    """Custom manager for Banner model."""

    def active(self) -> models.QuerySet:
        """Get all active banners."""
        now = timezone.now()
        return self.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).order_by('order')

    def by_position(self, position: str) -> models.QuerySet:
        """Get active banners for a specific position."""
        return self.active().filter(position=position)

    def cached_active(self) -> List[Any]:
        """Get cached active banners."""
        cache_key = 'active_banners'
        banners = cache.get(cache_key)
        
        if banners is None:
            banners = list(self.active())
            cache.set(cache_key, banners, timeout=3600)  # Cache for 1 hour
        
        return banners

class NewsletterManager(models.Manager):
    """Custom manager for Newsletter model."""

    def active_subscribers(self) -> models.QuerySet:
        """Get all active newsletter subscribers."""
        return self.filter(is_active=True, confirmed_at__isnull=False)

    def unconfirmed(self) -> models.QuerySet:
        """Get unconfirmed subscriptions."""
        return self.filter(is_active=True, confirmed_at__isnull=True)

    def subscriber_count(self) -> int:
        """Get total number of active subscribers."""
        cache_key = 'newsletter_subscriber_count'
        count = cache.get(cache_key)
        
        if count is None:
            count = self.active_subscribers().count()
            cache.set(cache_key, count, timeout=3600)
        
        return count

class ContactMessageManager(models.Manager):
    """Custom manager for ContactMessage model."""

    def unresolved(self) -> models.QuerySet:
        """Get all unresolved messages."""
        return self.filter(status__in=['new', 'in_progress'])

    def spam(self) -> models.QuerySet:
        """Get messages marked as spam."""
        return self.filter(status='spam')

    def by_status(self, status: str) -> models.QuerySet:
        """Get messages by status."""
        return self.filter(status=status)

    def recent(self, days: int = 7) -> models.QuerySet:
        """Get recent messages."""
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return self.filter(created_at__gte=cutoff)

class FAQManager(models.Manager):
    """Custom manager for FAQ model."""

    def active(self) -> models.QuerySet:
        """Get all active FAQs."""
        return self.filter(is_active=True).order_by('category', 'order')

    def by_category(self, category: str) -> models.QuerySet:
        """Get active FAQs for a specific category."""
        return self.active().filter(category=category)

    def cached_by_category(self) -> Dict[str, List[Any]]:
        """Get cached FAQs grouped by category."""
        cache_key = 'faqs_by_category'
        faqs = cache.get(cache_key)
        
        if faqs is None:
            faqs = {}
            for faq in self.active():
                if faq.category not in faqs:
                    faqs[faq.category] = []
                faqs[faq.category].append(faq)
            cache.set(cache_key, faqs, timeout=3600)
        
        return faqs

class TestimonialManager(models.Manager):
    """Custom manager for Testimonial model."""

    def active(self) -> models.QuerySet:
        """Get all active testimonials."""
        return self.filter(is_active=True).order_by('order')

    def featured(self) -> models.QuerySet:
        """Get featured testimonials."""
        return self.active().filter(rating__gte=4)[:6]

    def by_rating(self, min_rating: int = 1) -> models.QuerySet:
        """Get testimonials with minimum rating."""
        return self.active().filter(rating__gte=min_rating)

    def cached_featured(self) -> List[Any]:
        """Get cached featured testimonials."""
        cache_key = 'featured_testimonials'
        testimonials = cache.get(cache_key)
        
        if testimonials is None:
            testimonials = list(self.featured())
            cache.set(cache_key, testimonials, timeout=3600)
        
        return testimonials

class SocialProofManager(models.Manager):
    """Custom manager for SocialProof model."""

    def active(self) -> models.QuerySet:
        """Get all active social proofs."""
        return self.filter(is_active=True)

    def by_action_type(self, action_type: str) -> models.QuerySet:
        """Get social proofs by action type."""
        return self.active().filter(action_type=action_type)

    def recent(self, minutes: int = 30) -> models.QuerySet:
        """Get recent social proofs."""
        return self.active().filter(time_ago__lte=minutes)

    def get_queue(self) -> List[Any]:
        """Get social proof notification queue."""
        cache_key = 'social_proof_queue'
        queue = cache.get(cache_key)
        
        if queue is None:
            queue = list(self.active().values())
            cache.set(cache_key, queue, timeout=3600)
        
        return queue

class SiteConfigurationManager(models.Manager):
    """Custom manager for SiteConfiguration model."""

    def get_current(self) -> Optional[Any]:
        """Get current site configuration."""
        cache_key = 'current_site_config'
        config = cache.get(cache_key)
        
        if config is None:
            try:
                config = self.first()
                cache.set(cache_key, config, timeout=3600)
            except self.model.DoesNotExist:
                return None
        
        return config

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a specific setting value."""
        config = self.get_current()
        return getattr(config, key, default) if config else default

    def is_maintenance_mode(self) -> bool:
        """Check if site is in maintenance mode."""
        return self.get_setting('maintenance_mode', False)
