from django.conf import settings
from .models import SiteSettings

def site_settings(request):
    """Add site settings to template context."""
    try:
        site_settings = SiteSettings.get_settings()
        return {
            'site_name': site_settings.site_name,
            'site_description': site_settings.site_description,
            'contact_email': site_settings.contact_email,
            'phone': site_settings.phone,
            'address': site_settings.address,
            'facebook_url': site_settings.facebook_url,
            'twitter_url': site_settings.twitter_url,
            'instagram_url': site_settings.instagram_url,
            'pinterest_url': site_settings.pinterest_url,
            'youtube_url': site_settings.youtube_url,
            'maintenance_mode': site_settings.maintenance_mode,
            'maintenance_message': site_settings.maintenance_message,
            'google_analytics_id': site_settings.google_analytics_id,
            'meta_keywords': site_settings.meta_keywords,
            'meta_description': site_settings.meta_description,
        }
    except:
        # Return default values if settings don't exist
        return {
            'site_name': settings.SITE_NAME,
            'site_description': settings.SITE_DESCRIPTION,
            'contact_email': settings.DEFAULT_FROM_EMAIL,
            'phone': '',
            'address': '',
            'facebook_url': '',
            'twitter_url': '',
            'instagram_url': '',
            'pinterest_url': '',
            'youtube_url': '',
            'maintenance_mode': False,
            'maintenance_message': '',
            'google_analytics_id': '',
            'meta_keywords': '',
            'meta_description': '',
        }
