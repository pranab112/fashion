"""
Caching functionality for the products app.
"""

import logging
from typing import Any, Dict, List, Optional, Union
from django.core.cache import cache
from django.conf import settings
from django.db.models import QuerySet
from django.http import HttpResponse

from .constants import (
    CACHE_KEY_PRODUCT,
    CACHE_KEY_CATEGORY,
    CACHE_KEY_BRAND,
    CACHE_KEY_FEATURED_PRODUCTS,
    CACHE_KEY_NEW_ARRIVALS,
    CACHE_KEY_TRENDING_PRODUCTS,
    CACHE_KEY_CATEGORY_TREE,
    CACHE_KEY_BRAND_LIST,
    CACHE_KEY_SEARCH_SUGGESTIONS,
    CACHE_TIMEOUT_PRODUCT,
    CACHE_TIMEOUT_CATEGORY,
    CACHE_TIMEOUT_BRAND,
    CACHE_TIMEOUT_FEATURED,
    CACHE_TIMEOUT_NEW_ARRIVALS,
    CACHE_TIMEOUT_TRENDING,
    CACHE_TIMEOUT_SEARCH
)

logger = logging.getLogger(__name__)

class ProductCache:
    """Cache manager for products."""

    @staticmethod
    def get_product(product_id: int) -> Optional[Dict[str, Any]]:
        """
        Get product from cache.
        
        Args:
            product_id: Product ID
            
        Returns:
            Optional[Dict[str, Any]]: Cached product data
        """
        cache_key = CACHE_KEY_PRODUCT.format(product_id)
        return cache.get(cache_key)

    @staticmethod
    def set_product(product_id: int, data: Dict[str, Any]) -> None:
        """
        Set product in cache.
        
        Args:
            product_id: Product ID
            data: Product data
        """
        cache_key = CACHE_KEY_PRODUCT.format(product_id)
        cache.set(cache_key, data, CACHE_TIMEOUT_PRODUCT)

    @staticmethod
    def delete_product(product_id: int) -> None:
        """
        Delete product from cache.
        
        Args:
            product_id: Product ID
        """
        cache_key = CACHE_KEY_PRODUCT.format(product_id)
        cache.delete(cache_key)

    @staticmethod
    def get_category_tree() -> Optional[List[Dict[str, Any]]]:
        """
        Get category tree from cache.
        
        Returns:
            Optional[List[Dict[str, Any]]]: Cached category tree
        """
        return cache.get(CACHE_KEY_CATEGORY_TREE)

    @staticmethod
    def set_category_tree(data: List[Dict[str, Any]]) -> None:
        """
        Set category tree in cache.
        
        Args:
            data: Category tree data
        """
        cache.set(CACHE_KEY_CATEGORY_TREE, data, CACHE_TIMEOUT_CATEGORY)

    @staticmethod
    def get_brand_list() -> Optional[List[Dict[str, Any]]]:
        """
        Get brand list from cache.
        
        Returns:
            Optional[List[Dict[str, Any]]]: Cached brand list
        """
        return cache.get(CACHE_KEY_BRAND_LIST)

    @staticmethod
    def set_brand_list(data: List[Dict[str, Any]]) -> None:
        """
        Set brand list in cache.
        
        Args:
            data: Brand list data
        """
        cache.set(CACHE_KEY_BRAND_LIST, data, CACHE_TIMEOUT_BRAND)

    @staticmethod
    def get_featured_products() -> Optional[List[Dict[str, Any]]]:
        """
        Get featured products from cache.
        
        Returns:
            Optional[List[Dict[str, Any]]]: Cached featured products
        """
        return cache.get(CACHE_KEY_FEATURED_PRODUCTS)

    @staticmethod
    def set_featured_products(data: List[Dict[str, Any]]) -> None:
        """
        Set featured products in cache.
        
        Args:
            data: Featured products data
        """
        cache.set(CACHE_KEY_FEATURED_PRODUCTS, data, CACHE_TIMEOUT_FEATURED)

    @staticmethod
    def get_new_arrivals() -> Optional[List[Dict[str, Any]]]:
        """
        Get new arrivals from cache.
        
        Returns:
            Optional[List[Dict[str, Any]]]: Cached new arrivals
        """
        return cache.get(CACHE_KEY_NEW_ARRIVALS)

    @staticmethod
    def set_new_arrivals(data: List[Dict[str, Any]]) -> None:
        """
        Set new arrivals in cache.
        
        Args:
            data: New arrivals data
        """
        cache.set(CACHE_KEY_NEW_ARRIVALS, data, CACHE_TIMEOUT_NEW_ARRIVALS)

    @staticmethod
    def get_trending_products() -> Optional[List[Dict[str, Any]]]:
        """
        Get trending products from cache.
        
        Returns:
            Optional[List[Dict[str, Any]]]: Cached trending products
        """
        return cache.get(CACHE_KEY_TRENDING_PRODUCTS)

    @staticmethod
    def set_trending_products(data: List[Dict[str, Any]]) -> None:
        """
        Set trending products in cache.
        
        Args:
            data: Trending products data
        """
        cache.set(CACHE_KEY_TRENDING_PRODUCTS, data, CACHE_TIMEOUT_TRENDING)

    @staticmethod
    def get_search_suggestions(query: str) -> Optional[List[str]]:
        """
        Get search suggestions from cache.
        
        Args:
            query: Search query
            
        Returns:
            Optional[List[str]]: Cached search suggestions
        """
        cache_key = f"{CACHE_KEY_SEARCH_SUGGESTIONS}_{query}"
        return cache.get(cache_key)

    @staticmethod
    def set_search_suggestions(query: str, suggestions: List[str]) -> None:
        """
        Set search suggestions in cache.
        
        Args:
            query: Search query
            suggestions: Search suggestions
        """
        cache_key = f"{CACHE_KEY_SEARCH_SUGGESTIONS}_{query}"
        cache.set(cache_key, suggestions, CACHE_TIMEOUT_SEARCH)

    @staticmethod
    def get(key: str) -> Any:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Any: Cached value
        """
        return cache.get(key)

    @staticmethod
    def set(key: str, value: Any, timeout: Optional[int] = None) -> None:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            timeout: Cache timeout in seconds
        """
        cache.set(key, value, timeout)

    @staticmethod
    def delete(key: str) -> None:
        """
        Delete value from cache.
        
        Args:
            key: Cache key
        """
        cache.delete(key)

    @staticmethod
    def clear() -> None:
        """Clear all cache."""
        cache.clear()

class QuerySetCache:
    """Cache manager for querysets."""

    @staticmethod
    def get_queryset(cache_key: str) -> Optional[QuerySet]:
        """
        Get queryset from cache.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Optional[QuerySet]: Cached queryset
        """
        return cache.get(cache_key)

    @staticmethod
    def set_queryset(
        cache_key: str,
        queryset: QuerySet,
        timeout: Optional[int] = None
    ) -> None:
        """
        Set queryset in cache.
        
        Args:
            cache_key: Cache key
            queryset: Queryset to cache
            timeout: Cache timeout in seconds
        """
        cache.set(cache_key, queryset, timeout)

class PageCache:
    """Cache manager for rendered pages."""

    @staticmethod
    def get_page(cache_key: str) -> Optional[HttpResponse]:
        """
        Get page from cache.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Optional[HttpResponse]: Cached page
        """
        return cache.get(cache_key)

    @staticmethod
    def set_page(
        cache_key: str,
        response: HttpResponse,
        timeout: Optional[int] = None
    ) -> None:
        """
        Set page in cache.
        
        Args:
            cache_key: Cache key
            response: Response to cache
            timeout: Cache timeout in seconds
        """
        cache.set(cache_key, response, timeout)

def cache_key_for_request(request: Any) -> str:
    """
    Generate cache key for request.
    
    Args:
        request: HTTP request
        
    Returns:
        str: Cache key
    """
    # Generate key based on path and query parameters
    key = f"page_{request.path}_{request.GET.urlencode()}"
    
    # Add user-specific data if needed
    if request.user.is_authenticated:
        key = f"{key}_user_{request.user.id}"
    
    return key

def invalidate_product_caches(product_id: int) -> None:
    """
    Invalidate all caches related to a product.
    
    Args:
        product_id: Product ID
    """
    # Delete specific product cache
    ProductCache.delete_product(product_id)
    
    # Delete list caches that might contain the product
    cache.delete(CACHE_KEY_FEATURED_PRODUCTS)
    cache.delete(CACHE_KEY_NEW_ARRIVALS)
    cache.delete(CACHE_KEY_TRENDING_PRODUCTS)
    
    # Delete category caches
    cache.delete(CACHE_KEY_CATEGORY_TREE)

def invalidate_category_caches(category_id: int) -> None:
    """
    Invalidate all caches related to a category.
    
    Args:
        category_id: Category ID
    """
    cache_key = CACHE_KEY_CATEGORY.format(category_id)
    cache.delete(cache_key)
    cache.delete(CACHE_KEY_CATEGORY_TREE)

def invalidate_brand_caches(brand_id: int) -> None:
    """
    Invalidate all caches related to a brand.
    
    Args:
        brand_id: Brand ID
    """
    cache_key = CACHE_KEY_BRAND.format(brand_id)
    cache.delete(cache_key)
    cache.delete(CACHE_KEY_BRAND_LIST)
