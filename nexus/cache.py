from django.core.cache import cache
from django.conf import settings
from functools import wraps
import hashlib
import json
import logging
from typing import Any, Callable, Dict, Optional, Union
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CacheService:
    """Service class for handling caching operations."""

    # Cache timeouts (in seconds)
    TIMEOUTS = {
        'product': 3600,  # 1 hour
        'category': 3600,
        'brand': 3600,
        'user': 1800,     # 30 minutes
        'cart': 1800,
        'wishlist': 1800,
        'search': 300,    # 5 minutes
        'homepage': 600,  # 10 minutes
        'catalog': 600,
    }

    # Cache prefixes
    PREFIXES = {
        'product': 'prod:',
        'category': 'cat:',
        'brand': 'brand:',
        'user': 'user:',
        'cart': 'cart:',
        'wishlist': 'wish:',
        'search': 'search:',
        'session': 'sess:',
        'rate_limit': 'rate:',
    }

    @classmethod
    def get_cache_key(cls, prefix: str, identifier: Union[str, int]) -> str:
        """Generate a cache key with prefix."""
        return f"{cls.PREFIXES.get(prefix, '')}{identifier}"

    @classmethod
    def get_timeout(cls, cache_type: str) -> int:
        """Get cache timeout for specific type."""
        return cls.TIMEOUTS.get(cache_type, 300)  # Default 5 minutes

    @classmethod
    def cache_key_exists(cls, key: str) -> bool:
        """Check if a cache key exists."""
        return cache.has_key(key)  # noqa

    @classmethod
    def set_cache(cls, key: str, data: Any, timeout: Optional[int] = None) -> None:
        """Set cache with optional timeout."""
        try:
            cache.set(key, data, timeout)
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {str(e)}")

    @classmethod
    def get_cache(cls, key: str) -> Any:
        """Get cached data."""
        try:
            return cache.get(key)
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {str(e)}")
            return None

    @classmethod
    def delete_cache(cls, key: str) -> None:
        """Delete cached data."""
        try:
            cache.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {str(e)}")

    @classmethod
    def clear_cache_pattern(cls, pattern: str) -> None:
        """Clear all cache keys matching pattern."""
        try:
            if hasattr(cache, 'delete_pattern'):
                cache.delete_pattern(pattern)
        except Exception as e:
            logger.error(f"Cache pattern delete error for pattern {pattern}: {str(e)}")

    @classmethod
    def cache_decorator(cls, cache_type: str, key_func: Optional[Callable] = None):
        """
        Decorator for caching function results.
        
        Args:
            cache_type: Type of cache (product, category, etc.)
            key_func: Optional function to generate cache key
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    # Default key generation
                    key_parts = [func.__name__]
                    key_parts.extend(str(arg) for arg in args)
                    key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
                    cache_key = cls.get_cache_key(
                        cache_type,
                        hashlib.md5(":".join(key_parts).encode()).hexdigest()
                    )

                # Try to get from cache
                cached_result = cls.get_cache(cache_key)
                if cached_result is not None:
                    return cached_result

                # If not in cache, execute function
                result = func(*args, **kwargs)
                
                # Cache the result
                cls.set_cache(
                    cache_key,
                    result,
                    cls.get_timeout(cache_type)
                )
                
                return result
            return wrapper
        return decorator

class RateLimiter:
    """Rate limiting implementation using Redis."""

    @classmethod
    def get_rate_limit_key(cls, identifier: str, action: str) -> str:
        """Generate rate limit key."""
        return CacheService.get_cache_key('rate_limit', f"{action}:{identifier}")

    @classmethod
    def check_rate_limit(
        cls,
        identifier: str,
        action: str,
        max_requests: int,
        time_window: int
    ) -> bool:
        """
        Check if request is within rate limit.
        
        Args:
            identifier: User identifier (IP, user_id, etc.)
            action: Action being rate limited
            max_requests: Maximum requests allowed
            time_window: Time window in seconds
        """
        key = cls.get_rate_limit_key(identifier, action)
        
        try:
            current = cache.get(key, 0)
            if current >= max_requests:
                return False
            
            # Increment counter
            if current == 0:
                # First request, set with expiry
                cache.set(key, 1, time_window)
            else:
                # Increment existing counter
                cache.incr(key)
            
            return True
        except Exception as e:
            logger.error(f"Rate limit error for {key}: {str(e)}")
            return True  # Allow on error

class SessionManager:
    """Session management using Redis."""

    @classmethod
    def get_session_key(cls, session_id: str) -> str:
        """Generate session key."""
        return CacheService.get_cache_key('session', session_id)

    @classmethod
    def get_session(cls, session_id: str) -> Dict:
        """Get session data."""
        key = cls.get_session_key(session_id)
        data = CacheService.get_cache(key)
        return json.loads(data) if data else {}

    @classmethod
    def set_session(cls, session_id: str, data: Dict, timeout: int = 3600) -> None:
        """Set session data."""
        key = cls.get_session_key(session_id)
        CacheService.set_cache(key, json.dumps(data), timeout)

    @classmethod
    def delete_session(cls, session_id: str) -> None:
        """Delete session data."""
        key = cls.get_session_key(session_id)
        CacheService.delete_cache(key)

    @classmethod
    def extend_session(cls, session_id: str, timeout: int = 3600) -> None:
        """Extend session timeout."""
        key = cls.get_session_key(session_id)
        data = CacheService.get_cache(key)
        if data:
            CacheService.set_cache(key, data, timeout)

class CacheWarmer:
    """Utility for warming up cache."""

    @classmethod
    def warm_product_cache(cls, product_ids: list) -> None:
        """Pre-cache product data."""
        from products.models import Product
        for product_id in product_ids:
            key = CacheService.get_cache_key('product', product_id)
            if not CacheService.cache_key_exists(key):
                try:
                    product = Product.objects.get(id=product_id)
                    CacheService.set_cache(
                        key,
                        product,
                        CacheService.get_timeout('product')
                    )
                except Exception as e:
                    logger.error(f"Cache warming error for product {product_id}: {str(e)}")

    @classmethod
    def warm_category_cache(cls) -> None:
        """Pre-cache category data."""
        from products.models import Category
        categories = Category.objects.all()
        for category in categories:
            key = CacheService.get_cache_key('category', category.id)
            CacheService.set_cache(
                key,
                category,
                CacheService.get_timeout('category')
            )

class CacheMonitor:
    """Cache monitoring and statistics."""

    @classmethod
    def get_cache_stats(cls) -> Dict:
        """Get cache statistics."""
        try:
            stats = {
                'hits': cache.get('cache_stats_hits', 0),
                'misses': cache.get('cache_stats_misses', 0),
                'size': len(cache._cache.keys()),  # For Redis
                'last_cleared': cache.get('cache_last_cleared'),
            }
            return stats
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {}

    @classmethod
    def record_cache_hit(cls) -> None:
        """Record cache hit."""
        cache.incr('cache_stats_hits')

    @classmethod
    def record_cache_miss(cls) -> None:
        """Record cache miss."""
        cache.incr('cache_stats_misses')

    @classmethod
    def clear_stats(cls) -> None:
        """Clear cache statistics."""
        cache.delete('cache_stats_hits')
        cache.delete('cache_stats_misses')
        cache.set('cache_last_cleared', datetime.now().isoformat())

# Initialize cache settings
if settings.DEBUG:
    logger.setLevel(logging.DEBUG)
