"""
Custom decorators for the core app.
"""

import time
import logging
from functools import wraps
from typing import Callable, Any

from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.conf import settings
from django.core.cache import cache
from django.contrib import messages
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)

def maintenance_mode_exempt(view_func: Callable) -> Callable:
    """
    Decorator to exempt views from maintenance mode.
    
    Args:
        view_func: View function to decorate
    
    Returns:
        Callable: Decorated view function
    """
    def wrapped_view(*args, **kwargs):
        view_func.maintenance_mode_exempt = True
        return view_func(*args, **kwargs)
    return wraps(view_func)(wrapped_view)

def staff_required(view_func: Callable) -> Callable:
    """
    Decorator to require staff status for a view.
    
    Args:
        view_func: View function to decorate
    
    Returns:
        Callable: Decorated view function
    """
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, _("Staff access required."))
            return HttpResponseRedirect(reverse('core:home'))
        return view_func(request, *args, **kwargs)
    return wraps(view_func)(wrapped_view)

def cache_page_by_user(timeout: int = 3600) -> Callable:
    """
    Cache page based on user status (anonymous/authenticated).
    
    Args:
        timeout: Cache timeout in seconds
    
    Returns:
        Callable: Decorator function
    """
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            # Generate cache key based on path and user status
            cache_key = f"page_cache:{request.path}:{'auth' if request.user.is_authenticated else 'anon'}"
            response = cache.get(cache_key)
            
            if response is None:
                response = view_func(request, *args, **kwargs)
                cache.set(cache_key, response, timeout)
            
            return response
        return wraps(view_func)(wrapped_view)
    return decorator

def track_page_view(view_func: Callable) -> Callable:
    """
    Track page views for analytics.
    
    Args:
        view_func: View function to decorate
    
    Returns:
        Callable: Decorated view function
    """
    def wrapped_view(request, *args, **kwargs):
        # Track the page view
        try:
            from .utils import track_user_activity
            track_user_activity(
                user_id=request.user.id if request.user.is_authenticated else None,
                activity_type='page_view',
                metadata={
                    'path': request.path,
                    'referrer': request.META.get('HTTP_REFERER', ''),
                    'user_agent': request.META.get('HTTP_USER_AGENT', '')
                }
            )
        except Exception as e:
            logger.error(f"Failed to track page view: {str(e)}")
        
        return view_func(request, *args, **kwargs)
    return wraps(view_func)(wrapped_view)

def require_ajax(view_func: Callable) -> Callable:
    """
    Require AJAX for a view.
    
    Args:
        view_func: View function to decorate
    
    Returns:
        Callable: Decorated view function
    """
    def wrapped_view(request, *args, **kwargs):
        if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'AJAX request required'}, status=400)
        return view_func(request, *args, **kwargs)
    return wraps(view_func)(wrapped_view)

def ratelimit(key: str = 'ip', rate: str = '100/h') -> Callable:
    """
    Rate limit views.
    
    Args:
        key: Key to rate limit by ('ip' or 'user')
        rate: Rate limit string (e.g., '100/h', '1000/d')
    
    Returns:
        Callable: Decorator function
    """
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            # Get client identifier
            if key == 'ip':
                client_id = request.META.get('REMOTE_ADDR')
            else:  # key == 'user'
                client_id = request.user.id if request.user.is_authenticated else None

            if client_id:
                cache_key = f"ratelimit:{key}:{client_id}"
                count = cache.get(cache_key, 0)
                
                # Parse rate limit
                limit, period = rate.split('/')
                limit = int(limit)
                
                # Convert period to seconds
                if period == 'h':
                    period_seconds = 3600
                elif period == 'd':
                    period_seconds = 86400
                else:
                    period_seconds = 60  # default to minutes
                
                if count >= limit:
                    return JsonResponse({'error': 'Rate limit exceeded'}, status=429)
                
                # Increment counter
                cache.set(cache_key, count + 1, period_seconds)
            
            return view_func(request, *args, **kwargs)
        return wraps(view_func)(wrapped_view)
    return decorator

def log_execution_time(view_func: Callable) -> Callable:
    """
    Log execution time of views.
    
    Args:
        view_func: View function to decorate
    
    Returns:
        Callable: Decorated view function
    """
    def wrapped_view(request, *args, **kwargs):
        start_time = time.time()
        response = view_func(request, *args, **kwargs)
        duration = time.time() - start_time
        
        logger.info(
            f"View {view_func.__name__} took {duration:.2f}s",
            extra={
                'duration': duration,
                'view_name': view_func.__name__,
                'path': request.path
            }
        )
        
        return response
    return wraps(view_func)(wrapped_view)

def check_permissions(*permissions: str) -> Callable:
    """
    Check multiple permissions for a view.
    
    Args:
        *permissions: Permission codenames to check
    
    Returns:
        Callable: Decorator function
    """
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, _("Please log in to access this page."))
                return HttpResponseRedirect(settings.LOGIN_URL)
            
            if not request.user.has_perms(permissions):
                messages.error(request, _("You don't have permission to access this page."))
                return HttpResponseRedirect(reverse('core:home'))
            
            return view_func(request, *args, **kwargs)
        return wraps(view_func)(wrapped_view)
    return decorator

def feature_flag(flag_name: str, redirect_url: str = None) -> Callable:
    """
    Check feature flag before executing view.
    
    Args:
        flag_name: Name of the feature flag
        redirect_url: URL to redirect to if feature is disabled
    
    Returns:
        Callable: Decorator function
    """
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            if not getattr(settings, f'FEATURE_{flag_name.upper()}', False):
                if redirect_url:
                    return HttpResponseRedirect(redirect_url)
                return render(request, 'core/feature_disabled.html', {
                    'feature_name': flag_name
                })
            return view_func(request, *args, **kwargs)
        return wraps(view_func)(wrapped_view)
    return decorator
