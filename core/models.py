from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import EmailValidator

class HomepageSection(models.Model):
    """Model to manage different sections on the homepage."""
    
    SECTION_TYPES = [
        ('hero_banner', _('Hero Banner')),
        ('deal_of_day', _('Deal of the Day')),
        ('exclusive_brands', _('Exclusive Brands')),
        ('top_picks', _('Top Picks')),
        ('shop_by_category', _('Shop by Category')),
        ('brand_deals', _('Brand Deals')),
        ('trending_now', _('Trending Now')),
        ('indian_wear', _('Indian Wear')),
        ('sports_wear', _('Sports Wear')),
        ('footwear', _('Footwear')),
        ('new_brands', _('New Brands')),
    ]
    
    title = models.CharField(_('Title'), max_length=200)
    section_type = models.CharField(
        _('Section Type'),
        max_length=50,
        choices=SECTION_TYPES,
        unique=True
    )
    is_active = models.BooleanField(_('Active'), default=True)
    order = models.PositiveIntegerField(_('Display Order'), default=0)
    created_at = models.DateTimeField(_('Created at'), default=timezone.now)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Homepage Section')
        verbose_name_plural = _('Homepage Sections')
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_section_type_display()})"

class HeroBanner(models.Model):
    """Model for hero banner slides."""
    
    title = models.CharField(_('Title'), max_length=200)
    subtitle = models.CharField(_('Subtitle'), max_length=300, blank=True)
    image = models.ImageField(_('Image'), upload_to='hero_banners/')
    link_url = models.URLField(_('Link URL'), blank=True)
    link_text = models.CharField(_('Link Text'), max_length=100, blank=True)
    is_active = models.BooleanField(_('Active'), default=True)
    order = models.PositiveIntegerField(_('Display Order'), default=0)
    created_at = models.DateTimeField(_('Created at'), default=timezone.now)
    
    class Meta:
        verbose_name = _('Hero Banner')
        verbose_name_plural = _('Hero Banners')
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return self.title

class HomepageSettings(models.Model):
    """Global settings for homepage."""
    
    site_name = models.CharField(_('Site Name'), max_length=100, default='Fashion Store')
    site_description = models.TextField(_('Site Description'), blank=True)
    hero_auto_play = models.BooleanField(_('Hero Auto Play'), default=True)
    hero_slide_duration = models.PositiveIntegerField(
        _('Hero Slide Duration (seconds)'),
        default=4
    )
    products_per_section = models.PositiveIntegerField(
        _('Products per Section'),
        default=8,
        help_text=_('Number of products to show in each section')
    )
    brands_per_section = models.PositiveIntegerField(
        _('Brands per Section'),
        default=6,
        help_text=_('Number of brands to show in each section')
    )
    categories_per_section = models.PositiveIntegerField(
        _('Categories per Section'),
        default=8,
        help_text=_('Number of categories to show in Shop by Category')
    )
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Homepage Settings')
        verbose_name_plural = _('Homepage Settings')
    
    def __str__(self):
        return f"Homepage Settings - {self.site_name}"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and HomepageSettings.objects.exists():
            raise ValueError('Only one HomepageSettings instance is allowed')
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create homepage settings."""
        settings, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'site_name': 'Fashion Store',
                'site_description': 'Your one-stop destination for fashion',
            }
        )
        return settings

class Newsletter(models.Model):
    """Model for newsletter subscriptions."""
    
    email = models.EmailField(_('Email'), unique=True, validators=[EmailValidator()])
    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(_('Created at'), default=timezone.now)
    
    class Meta:
        verbose_name = _('Newsletter Subscription')
        verbose_name_plural = _('Newsletter Subscriptions')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email

class ContactMessage(models.Model):
    """Model for contact form messages."""
    
    STATUS_CHOICES = [
        ('new', _('New')),
        ('in_progress', _('In Progress')),
        ('resolved', _('Resolved')),
        ('closed', _('Closed')),
    ]
    
    name = models.CharField(_('Name'), max_length=100)
    email = models.EmailField(_('Email'), validators=[EmailValidator()])
    subject = models.CharField(_('Subject'), max_length=200)
    message = models.TextField(_('Message'))
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='new'
    )
    notes = models.TextField(_('Admin Notes'), blank=True)
    created_at = models.DateTimeField(_('Created at'), default=timezone.now)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Contact Message')
        verbose_name_plural = _('Contact Messages')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"

class SiteSettings(models.Model):
    """Global site settings."""
    
    site_name = models.CharField(_('Site Name'), max_length=100, default='Fashion Store')
    site_description = models.TextField(_('Site Description'), blank=True)
    contact_email = models.EmailField(_('Contact Email'), blank=True)
    phone = models.CharField(_('Phone'), max_length=20, blank=True)
    address = models.TextField(_('Address'), blank=True)
    
    # Social Media URLs
    facebook_url = models.URLField(_('Facebook URL'), blank=True)
    twitter_url = models.URLField(_('Twitter URL'), blank=True)
    instagram_url = models.URLField(_('Instagram URL'), blank=True)
    pinterest_url = models.URLField(_('Pinterest URL'), blank=True)
    youtube_url = models.URLField(_('YouTube URL'), blank=True)
    
    # SEO Settings
    meta_keywords = models.TextField(_('Meta Keywords'), blank=True)
    meta_description = models.TextField(_('Meta Description'), blank=True)
    
    # Analytics
    google_analytics_id = models.CharField(_('Google Analytics ID'), max_length=50, blank=True)
    
    # Maintenance Mode
    maintenance_mode = models.BooleanField(_('Maintenance Mode'), default=False)
    maintenance_message = models.TextField(_('Maintenance Message'), blank=True)
    
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Site Settings')
        verbose_name_plural = _('Site Settings')
    
    def __str__(self):
        return f"Site Settings - {self.site_name}"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and SiteSettings.objects.exists():
            raise ValueError('Only one SiteSettings instance is allowed')
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create site settings."""
        settings, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'site_name': 'Fashion Store',
                'site_description': 'Your one-stop destination for fashion',
            }
        )
        return settings
