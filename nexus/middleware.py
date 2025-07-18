from typing import Callable
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
import time
import logging
from .monitoring import Monitoring
from .cache import CacheService
from .security import SecurityService
from .exceptions import (
    MaintenanceModeError,
    RateLimitError,
    AuthenticationError
)

logger = logging.getLogger(__name__)

class RequestTimingMiddleware:
    """Middleware to track request timing."""

    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Start timer
        start_time = time.time()
        
        # Process request
        response = self.get_response(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Add timing header
        response['X-Request-Time'] = str(duration)
        
        # Log timing metrics
        Monitoring.log_request_timing(
            path=request.path,
            method=request.method,
            duration=duration,
            status_code=response.status_code
        )
        
        return response

class SecurityMiddleware:
    """Middleware for security headers and checks."""

    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Process request
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response['Content-Security-Policy'] = self._get_csp_policy()
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Feature-Policy'] = self._get_feature_policy()
        
        return response

    def _get_csp_policy(self) -> str:
        """Get Content Security Policy."""
        return '; '.join([
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
            "img-src 'self' data: https:",
            "font-src 'self' https://fonts.gstatic.com",
            "connect-src 'self' https://api.stripe.com",
            "frame-src 'self' https://js.stripe.com",
            "object-src 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "frame-ancestors 'none'",
            "block-all-mixed-content",
            "upgrade-insecure-requests"
        ])

    def _get_feature_policy(self) -> str:
        """Get Feature Policy."""
        return '; '.join([
            "geolocation 'none'",
            "midi 'none'",
            "notifications 'none'",
            "push 'none'",
            "sync-xhr 'none'",
            "microphone 'none'",
            "camera 'none'",
            "magnetometer 'none'",
            "gyroscope 'none'",
            "speaker 'none'",
            "vibrate 'none'",
            "fullscreen 'self'",
            "payment 'self'"
        ])

class MaintenanceModeMiddleware:
    """Middleware for maintenance mode."""

    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if getattr(settings, 'MAINTENANCE_MODE', False):
            # Check for bypass IPs
            client_ip = request.META.get('REMOTE_ADDR')
            bypass_ips = getattr(settings, 'MAINTENANCE_BYPASS_IPS', [])
            
            if client_ip not in bypass_ips:
                # Check for bypass URLs
                path = request.path_info.lstrip('/')
                bypass_urls = getattr(settings, 'MAINTENANCE_BYPASS_URLS', [])
                
                if not any(url.match(path) for url in bypass_urls):
                    raise MaintenanceModeError(
                        estimated_duration=getattr(
                            settings,
                            'MAINTENANCE_DURATION',
                            None
                        )
                    )
        
        return self.get_response(request)

class RateLimitMiddleware:
    """Middleware for rate limiting."""

    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if request.path.startswith('/api/'):
            # Get identifier based on authentication
            if request.user.is_authenticated:
                identifier = f"user:{request.user.id}"
                limit = getattr(
                    settings,
                    'API_RATE_LIMIT_AUTHENTICATED',
                    '1000/hour'
                )
            else:
                identifier = f"ip:{request.META.get('REMOTE_ADDR')}"
                limit = getattr(
                    settings,
                    'API_RATE_LIMIT_ANONYMOUS',
                    '100/hour'
                )

            # Check rate limit
            if not CacheService.check_rate_limit(identifier, limit):
                raise RateLimitError()

        return self.get_response(request)

class SessionMiddleware:
    """Middleware for session management."""

    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Process request
        response = self.get_response(request)
        
        if request.user.is_authenticated:
            # Extend session if needed
            self._extend_session_if_needed(request)
            
            # Update last activity
            self._update_last_activity(request)
        
        return response

    def _extend_session_if_needed(self, request: HttpRequest) -> None:
        """Extend session if it's about to expire."""
        if 'last_activity' in request.session:
            last_activity = request.session['last_activity']
            session_age = time.time() - last_activity
            
            # If session is more than 80% through its lifetime
            if session_age > (settings.SESSION_COOKIE_AGE * 0.8):
                request.session.set_expiry(settings.SESSION_COOKIE_AGE)

    def _update_last_activity(self, request: HttpRequest) -> None:
        """Update user's last activity timestamp."""
        request.session['last_activity'] = time.time()

class LocaleMiddleware:
    """Middleware for locale and timezone handling."""

    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Set language preference
        self._set_language(request)
        
        # Set timezone if user is authenticated
        if request.user.is_authenticated:
            self._set_timezone(request)
        
        return self.get_response(request)

    def _set_language(self, request: HttpRequest) -> None:
        """Set language based on user preference or header."""
        from django.utils import translation
        
        if request.user.is_authenticated and hasattr(request.user, 'language'):
            language = request.user.language
        else:
            language = request.META.get('HTTP_ACCEPT_LANGUAGE', '').split(',')[0]
        
        translation.activate(language)

    def _set_timezone(self, request: HttpRequest) -> None:
        """Set timezone based on user preference."""
        from django.utils import timezone
        import pytz
        
        if hasattr(request.user, 'timezone'):
            try:
                timezone.activate(pytz.timezone(request.user.timezone))
            except pytz.exceptions.UnknownTimeZoneError:
                timezone.deactivate()

class MetricsMiddleware:
    """Middleware for collecting metrics."""

    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Start metrics collection
        start_time = time.time()
        
        # Process request
        response = self.get_response(request)
        
        # Calculate metrics
        duration = time.time() - start_time
        
        # Record metrics
        Monitoring.record_request_metrics(
            path=request.path,
            method=request.method,
            status_code=response.status_code,
            duration=duration,
            user_id=getattr(request.user, 'id', None),
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        
        return response

class CacheMiddleware:
    """Middleware for request/response caching."""

    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Only cache GET requests
        if request.method != 'GET':
            return self.get_response(request)

        # Generate cache key
        cache_key = CacheService.generate_cache_key(
            prefix='page',
            params={
                'path': request.path,
                'query': request.GET.dict(),
                'user_id': getattr(request.user, 'id', None)
            }
        )

        # Try to get from cache
        cached_response = CacheService.get_cache(cache_key)
        if cached_response is not None:
            return cached_response

        # Get fresh response
        response = self.get_response(request)

        # Cache successful responses
        if response.status_code == 200:
            CacheService.set_cache(
                cache_key,
                response,
                timeout=settings.PAGE_CACHE_TIMEOUT
            )

        return response
