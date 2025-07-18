from django.shortcuts import render
from django.urls import resolve
from django.conf import settings
from .models import SiteSettings

class MaintenanceModeMiddleware:
    """Middleware to handle site maintenance mode."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        try:
            # Check if maintenance mode is enabled
            site_settings = SiteSettings.get_settings()
            if site_settings.maintenance_mode:
                # Allow admin URLs
                if not request.path.startswith('/admin/'):
                    context = {
                        'maintenance_message': site_settings.maintenance_message
                    }
                    return render(request, 'core/maintenance.html', context, status=503)
        except:
            pass
        
        return self.get_response(request)

class TimezoneMiddleware:
    """Middleware to handle user timezone preferences."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated and hasattr(request.user, 'timezone'):
            # Set user's timezone if they have one set
            try:
                import pytz
                timezone.activate(pytz.timezone(request.user.timezone))
            except:
                timezone.deactivate()
        return self.get_response(request)

class BreadcrumbMiddleware:
    """Middleware to generate breadcrumbs."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Initialize breadcrumbs with home
        request.breadcrumbs = [('Home', '/')]
        
        # Get current URL name
        current = resolve(request.path_info)
        
        if current.url_name:
            # Add current page to breadcrumbs
            if current.url_name != 'home':
                request.breadcrumbs.append((
                    current.url_name.replace('_', ' ').title(),
                    request.path_info
                ))
        
        return self.get_response(request)

class MobileDetectionMiddleware:
    """Middleware to detect mobile devices."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if user agent indicates a mobile device
        is_mobile = False
        if request.META.get('HTTP_USER_AGENT'):
            user_agent = request.META['HTTP_USER_AGENT']
            # Very basic mobile detection - you might want to use a proper library
            mobile_strings = ['Mobile', 'Android', 'iPhone', 'iPad', 'Windows Phone']
            is_mobile = any(s in user_agent for s in mobile_strings)
        
        # Add mobile flag to request
        request.is_mobile = is_mobile
        
        return self.get_response(request)

class OnlineUsersMiddleware:
    """Middleware to track online users."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated:
            # Update user's last activity
            from django.utils import timezone
            request.user.last_activity = timezone.now()
            request.user.save(update_fields=['last_activity'])
        
        return self.get_response(request)
