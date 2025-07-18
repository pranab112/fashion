from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    HomepageSection,
    HeroBanner,
    HomepageSettings
)

@admin.register(HomepageSection)
class HomepageSectionAdmin(admin.ModelAdmin):
    """Admin interface for Homepage Sections."""
    
    list_display = ('title', 'section_type', 'is_active', 'order', 'updated_at')
    list_filter = ('section_type', 'is_active')
    search_fields = ('title',)
    list_editable = ('is_active', 'order')
    ordering = ('order', 'section_type')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'section_type', 'is_active', 'order')
        }),
    )

@admin.register(HeroBanner)
class HeroBannerAdmin(admin.ModelAdmin):
    """Admin interface for Hero Banners."""
    
    list_display = ('title', 'is_active', 'order', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'subtitle')
    list_editable = ('is_active', 'order')
    ordering = ('order', '-created_at')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'subtitle', 'image')
        }),
        (_('Link Settings'), {
            'fields': ('link_url', 'link_text'),
            'classes': ('collapse',)
        }),
        (_('Display Settings'), {
            'fields': ('is_active', 'order')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()

@admin.register(HomepageSettings)
class HomepageSettingsAdmin(admin.ModelAdmin):
    """Admin interface for Homepage Settings."""
    
    def has_add_permission(self, request):
        # Only allow one instance
        return not HomepageSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion
        return False
    
    fieldsets = (
        (_('Site Information'), {
            'fields': ('site_name', 'site_description')
        }),
        (_('Hero Banner Settings'), {
            'fields': ('hero_auto_play', 'hero_slide_duration')
        }),
        (_('Section Display Settings'), {
            'fields': ('products_per_section', 'brands_per_section', 'categories_per_section')
        }),
    )
    
    def changelist_view(self, request, extra_context=None):
        # Redirect to change view if settings exist
        if HomepageSettings.objects.exists():
            settings = HomepageSettings.objects.first()
            return self.change_view(request, str(settings.pk), extra_context)
        return super().changelist_view(request, extra_context)
