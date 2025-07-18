from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Newsletter, ContactMessage, SiteSettings

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Admin interface for SiteSettings model."""
    
    fieldsets = (
        (None, {
            'fields': ('site_name', 'site_description', 'contact_email', 'phone', 'address')
        }),
        (_('Social Media'), {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url', 'pinterest_url', 'youtube_url')
        }),
        (_('SEO'), {
            'fields': ('meta_keywords', 'meta_description')
        }),
        (_('Analytics'), {
            'fields': ('google_analytics_id',)
        }),
        (_('Maintenance'), {
            'fields': ('maintenance_mode', 'maintenance_message')
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one instance of SiteSettings
        return not SiteSettings.objects.exists()

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    """Admin interface for Newsletter model."""
    
    list_display = ('email', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('email',)
    date_hierarchy = 'created_at'

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """Admin interface for ContactMessage model."""
    
    list_display = ('name', 'email', 'subject', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'email', 'subject', 'message')
        }),
        (_('Status'), {
            'fields': ('status', 'notes')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
