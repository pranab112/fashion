from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Union
from django.http import HttpRequest, HttpResponse
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings
import time
import logging
from .exceptions import (
    AuthenticationError,
    AuthorizationError,
    RateLimitError,
    MaintenanceModeError
)
from .monitoring import Monitoring
from .cache import CacheService
from .security import SecurityService
from .constants import SecurityConstants

logger = logging.getLogger(__name__)

def require_authentication(redirect_url: str = None):
    """Decorator to require authentication for a view."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if redirect_url:
                    return redirect(f"{redirect_url}?next={request.path}")
                raise AuthenticationError()
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def require_permissions(permissions: Union[str, List[str]], require_all: bool = True):
    """
    Decorator to require specific permissions.
    
    Args:
        permissions: Single permission or list of permissions
        require_all: If True, all permissions are required; if False, any permission is sufficient
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise AuthenticationError()

            if isinstance(permissions, str):
                perm_list = [permissions]
            else:
                perm_list = permissions

            if require_all:
                has_perms = all(
                    request.user.has_perm(perm)
                    for perm in perm_list
                )
            else:
                has_perms = any(
                    request.user.has_perm(perm)
                    for perm in perm_list
                )

            if not has_perms:
                raise AuthorizationError()

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def require_roles(roles: Union[str, List[str]], require_all: bool = True):
    """
    Decorator to require specific roles.
    
    Args:
        roles: Single role or list of roles
        require_all: If True, all roles are required; if False, any role is sufficient
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise AuthenticationError()

            if isinstance(roles, str):
                role_list = [roles]
            else:
                role_list = roles

            user_roles = set(
                group.name
                for group in request.user.groups.all()
            )

            if require_all:
                has_roles = all(
                    role in user_roles
                    for role in role_list
                )
            else:
                has_roles = any(
                    role in user_roles
                    for role in role_list
                )

            if not has_roles:
                raise AuthorizationError()

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def rate_limit(
    requests: int,
    interval: int,
    by: str = 'ip',
    scope: str = None
):
    """
    Decorator to apply rate limiting.
    
    Args:
        requests: Number of allowed requests
        interval: Time interval in seconds
        by: Rate limit by 'ip' or 'user'
        scope: Optional scope for the rate limit
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Get identifier based on rate limit type
            if by == 'user' and request.user.is_authenticated:
                identifier = str(request.user.id)
            else:
                identifier = request.META.get('REMOTE_ADDR')

            # Add scope if provided
            if scope:
                identifier = f"{scope}:{identifier}"

            # Check rate limit
            cache_key = f"rate_limit:{identifier}"
            request_count = CacheService.get_cache(cache_key) or 0

            if request_count >= requests:
                raise RateLimitError(
                    limit=requests,
                    reset_time=interval
                )

            # Increment counter
            CacheService.set_cache(
                cache_key,
                request_count + 1,
                timeout=interval
            )

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def maintenance_mode_check(bypass_roles: List[str] = None):
    """
    Decorator to check if system is in maintenance mode.
    
    Args:
        bypass_roles: List of roles that can bypass maintenance mode
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if getattr(settings, 'MAINTENANCE_MODE', False):
                if bypass_roles and request.user.is_authenticated:
                    user_roles = set(
                        group.name
                        for group in request.user.groups.all()
                    )
                    if any(role in user_roles for role in bypass_roles):
                        return view_func(request, *args, **kwargs)

                raise MaintenanceModeError()
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def monitor_performance(name: str = None):
    """
    Decorator to monitor view performance.
    
    Args:
        name: Optional name for the monitoring metric
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            start_time = time.time()
            
            try:
                response = view_func(request, *args, **kwargs)
                duration = time.time() - start_time
                
                # Log performance metrics
                Monitoring.log_performance_metric(
                    name or view_func.__name__,
                    duration,
                    {
                        'path': request.path,
                        'method': request.method,
                        'user_id': getattr(request.user, 'id', None),
                        'status_code': getattr(response, 'status_code', None)
                    }
                )
                
                return response
            except Exception as e:
                duration = time.time() - start_time
                
                # Log error metrics
                Monitoring.log_error_metric(
                    name or view_func.__name__,
                    e,
                    duration,
                    {
                        'path': request.path,
                        'method': request.method,
                        'user_id': getattr(request.user, 'id', None)
                    }
                )
                
                raise
        return wrapper
    return decorator

def cache_response(
    timeout: int = 300,
    key_prefix: str = None,
    cache_errors: bool = False
):
    """
    Decorator to cache view response.
    
    Args:
        timeout: Cache timeout in seconds
        key_prefix: Optional prefix for cache key
        cache_errors: Whether to cache error responses
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.method != 'GET':
                return view_func(request, *args, **kwargs)

            # Generate cache key
            cache_key = CacheService.generate_cache_key(
                prefix=key_prefix or view_func.__name__,
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
            response = view_func(request, *args, **kwargs)

            # Cache response if successful or if cache_errors is True
            if cache_errors or response.status_code < 400:
                CacheService.set_cache(cache_key, response, timeout)

            return response
        return wrapper
    return decorator

def validate_request_data(*required_fields: str):
    """
    Decorator to validate request data.
    
    Args:
        required_fields: List of required field names
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            data = request.POST if request.method == 'POST' else request.GET
            
            missing_fields = [
                field for field in required_fields
                if field not in data or not data[field]
            ]
            
            if missing_fields:
                from .exceptions import ValidationError
                raise ValidationError(
                    message="Missing required fields",
                    errors={'missing_fields': missing_fields}
                )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def require_https(redirect: bool = False):
    """
    Decorator to require HTTPS.
    
    Args:
        redirect: Whether to redirect to HTTPS or raise an error
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.is_secure():
                if redirect:
                    return redirect(
                        f"https://{request.get_host()}{request.path}"
                    )
                raise SecurityError("HTTPS required")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def track_activity(activity_type: str):
    """
    Decorator to track user activity.
    
    Args:
        activity_type: Type of activity to track
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)
            
            if request.user.is_authenticated:
                from .analytics import AnalyticsService
                AnalyticsService.track_user_activity(
                    user_id=request.user.id,
                    activity_type=activity_type,
                    metadata={
                        'path': request.path,
                        'method': request.method,
                        'status_code': getattr(response, 'status_code', None)
                    }
                )
            
            return response
        return wrapper
    return decorator
