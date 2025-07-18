"""
Custom middleware for the products app.
"""

import time
from typing import Any, Callable
from django.http import HttpRequest, HttpResponse
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.utils.translation import gettext_lazy as _

from .models import ProductView
from .utils import get_client_ip
from .monitoring import ProductMetrics

class ProductViewMiddleware:
    """Middleware to track product views."""

    def __init__(self, get_response: Callable) -> None:
        """
        Initialize middleware.
        
        Args:
            get_response: Get response callable
        """
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Process request and track product views.
        
        Args:
            request: HTTP request
            
        Returns:
            HttpResponse: HTTP response
        """
        response = self.get_response(request)
        
        # Only track GET requests to product detail pages
        if (
            request.method == 'GET' and
            hasattr(request, 'resolver_match') and
            request.resolver_match and
            request.resolver_match.url_name == 'product_detail'
        ):
            try:
                product = request.resolver_match.func.view_class.get_object(
                    request.resolver_match.func.view_class(),
                    pk=request.resolver_match.kwargs.get('pk')
                )
                
                # Create product view
                ProductView.objects.create(
                    product=product,
                    user=request.user if request.user.is_authenticated else None,
                    session_key=request.session.session_key,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
                    referrer=request.META.get('HTTP_REFERER', '')[:255]
                )
                
            except Exception as e:
                # Log error but don't affect response
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Error tracking product view: {str(e)}')
        
        return response

class ProductCacheMiddleware:
    """Middleware to handle product caching."""

    def __init__(self, get_response: Callable) -> None:
        """
        Initialize middleware.
        
        Args:
            get_response: Get response callable
        """
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Process request and handle caching.
        
        Args:
            request: HTTP request
            
        Returns:
            HttpResponse: HTTP response
        """
        # Don't cache for authenticated users
        if request.user.is_authenticated:
            return self.get_response(request)
        
        # Only cache GET requests
        if request.method != 'GET':
            return self.get_response(request)
        
        # Generate cache key
        cache_key = f'product_page_{request.path}_{request.GET.urlencode()}'
        
        # Try to get from cache
        response = cache.get(cache_key)
        
        if response is None:
            response = self.get_response(request)
            
            # Cache successful responses
            if response.status_code == 200:
                cache.set(cache_key, response, timeout=3600)  # 1 hour
        
        return response

class ProductMetricsMiddleware:
    """Middleware to collect product metrics."""

    def __init__(self, get_response: Callable) -> None:
        """
        Initialize middleware.
        
        Args:
            get_response: Get response callable
        """
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Process request and collect metrics.
        
        Args:
            request: HTTP request
            
        Returns:
            HttpResponse: HTTP response
        """
        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time
        
        # Track metrics for product-related views
        if (
            hasattr(request, 'resolver_match') and
            request.resolver_match and
            request.resolver_match.app_name == 'products'
        ):
            ProductMetrics.track_request(
                path=request.path,
                method=request.method,
                status_code=response.status_code,
                duration=duration
            )
        
        return response

class ProductSecurityMiddleware:
    """Middleware to handle product security."""

    def __init__(self, get_response: Callable) -> None:
        """
        Initialize middleware.
        
        Args:
            get_response: Get response callable
        """
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Process request and handle security.
        
        Args:
            request: HTTP request
            
        Returns:
            HttpResponse: HTTP response
        """
        response = self.get_response(request)
        
        # Add security headers for product-related views
        if (
            hasattr(request, 'resolver_match') and
            request.resolver_match and
            request.resolver_match.app_name == 'products'
        ):
            # Prevent clickjacking
            response['X-Frame-Options'] = 'DENY'
            
            # Enable XSS protection
            response['X-XSS-Protection'] = '1; mode=block'
            
            # Prevent MIME type sniffing
            response['X-Content-Type-Options'] = 'nosniff'
            
            # Content Security Policy
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "img-src 'self' data: https:; "
                "style-src 'self' 'unsafe-inline'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval';"
            )
        
        return response

class ProductRateLimitMiddleware:
    """Middleware to handle rate limiting for product-related actions."""

    def __init__(self, get_response: Callable) -> None:
        """
        Initialize middleware.
        
        Args:
            get_response: Get response callable
        """
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Process request and handle rate limiting.
        
        Args:
            request: HTTP request
            
        Returns:
            HttpResponse: HTTP response
        """
        if (
            hasattr(request, 'resolver_match') and
            request.resolver_match and
            request.resolver_match.app_name == 'products'
        ):
            # Rate limit based on IP address
            ip = get_client_ip(request)
            cache_key = f'product_ratelimit_{ip}'
            
            # Get current request count
            requests = cache.get(cache_key, 0)
            
            # Check rate limit
            if requests >= getattr(settings, 'PRODUCT_RATE_LIMIT', 100):
                from django.http import HttpResponseTooManyRequests
                return HttpResponseTooManyRequests(
                    _('Too many requests. Please try again later.')
                )
            
            # Increment request count
            cache.set(
                cache_key,
                requests + 1,
                timeout=getattr(settings, 'PRODUCT_RATE_LIMIT_TIMEOUT', 3600)
            )
        
        return self.get_response(request)

class ProductMaintenanceMiddleware(MiddlewareMixin):
    """Middleware to handle product maintenance mode."""

    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """
        Process request and handle maintenance mode.
        
        Args:
            request: HTTP request
            
        Returns:
            Optional[HttpResponse]: HTTP response if in maintenance mode
        """
        from django.shortcuts import render
        
        # Check if product system is in maintenance mode
        if getattr(settings, 'PRODUCT_MAINTENANCE_MODE', False):
            # Allow staff users to bypass maintenance mode
            if request.user.is_staff:
                return None
            
            # Check if request is for product-related views
            if (
                hasattr(request, 'resolver_match') and
                request.resolver_match and
                request.resolver_match.app_name == 'products'
            ):
                return render(
                    request,
                    'products/maintenance.html',
                    status=503
                )
        
        return None
