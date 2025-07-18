"""
Context processors for the products app.
"""

from typing import Any, Dict
from django.http import HttpRequest
from django.db.models import Count
from django.core.cache import cache

from .models import Category, Brand, Product
from .services import ProductService
from .constants import CACHE_TIMEOUT_CATEGORY, CACHE_TIMEOUT_BRAND

def categories(request: HttpRequest) -> Dict[str, Any]:
    """
    Add categories to template context.
    
    Args:
        request: HTTP request
        
    Returns:
        Dict[str, Any]: Context variables
    """
    # Try to get from cache
    categories = cache.get('categories_context')
    
    if categories is None:
        # Get root categories with product counts
        categories = Category.objects.filter(
            parent=None,
            is_active=True
        ).annotate(
            product_count=Count('products')
        ).prefetch_related(
            'children'
        ).order_by('order')
        
        # Cache the queryset
        cache.set('categories_context', categories, CACHE_TIMEOUT_CATEGORY)
    
    return {
        'categories': categories
    }

def brands(request: HttpRequest) -> Dict[str, Any]:
    """
    Add brands to template context.
    
    Args:
        request: HTTP request
        
    Returns:
        Dict[str, Any]: Context variables
    """
    # Try to get from cache
    brands = cache.get('brands_context')
    
    if brands is None:
        # Get active brands with product counts
        brands = Brand.objects.filter(
            is_active=True
        ).annotate(
            product_count=Count('products')
        ).order_by('name')
        
        # Cache the queryset
        cache.set('brands_context', brands, CACHE_TIMEOUT_BRAND)
    
    return {
        'brands': brands
    }

def featured_products(request: HttpRequest) -> Dict[str, Any]:
    """
    Add featured products to template context.
    
    Args:
        request: HTTP request
        
    Returns:
        Dict[str, Any]: Context variables
    """
    # Try to get from cache
    products = cache.get('featured_products_context')
    
    if products is None:
        # Get featured products
        products = Product.objects.filter(
            is_featured=True,
            status='active'
        ).select_related(
            'category',
            'brand'
        ).prefetch_related(
            'images'
        )[:8]
        
        # Cache the queryset
        cache.set('featured_products_context', products, 3600)
    
    return {
        'featured_products': products
    }

def new_arrivals(request: HttpRequest) -> Dict[str, Any]:
    """
    Add new arrival products to template context.
    
    Args:
        request: HTTP request
        
    Returns:
        Dict[str, Any]: Context variables
    """
    # Try to get from cache
    products = cache.get('new_arrivals_context')
    
    if products is None:
        # Get new arrival products
        products = Product.objects.filter(
            is_new_arrival=True,
            status='active'
        ).select_related(
            'category',
            'brand'
        ).prefetch_related(
            'images'
        ).order_by('-created_at')[:8]
        
        # Cache the queryset
        cache.set('new_arrivals_context', products, 3600)
    
    return {
        'new_arrivals': products
    }

def trending_products(request: HttpRequest) -> Dict[str, Any]:
    """
    Add trending products to template context.
    
    Args:
        request: HTTP request
        
    Returns:
        Dict[str, Any]: Context variables
    """
    # Try to get from cache
    products = cache.get('trending_products_context')
    
    if products is None:
        # Get trending products
        products = ProductService.get_trending_products()[:8]
        
        # Cache the queryset
        cache.set('trending_products_context', products, 1800)  # 30 minutes
    
    return {
        'trending_products': products
    }

def wishlist(request: HttpRequest) -> Dict[str, Any]:
    """
    Add wishlist to template context.
    
    Args:
        request: HTTP request
        
    Returns:
        Dict[str, Any]: Context variables
    """
    wishlist_count = 0
    wishlist_products = []
    
    if request.user.is_authenticated:
        # Get user's wishlist
        wishlist_products = request.user.wishlist.all()
        wishlist_count = wishlist_products.count()
    
    return {
        'wishlist_count': wishlist_count,
        'wishlist_products': wishlist_products
    }

def cart(request: HttpRequest) -> Dict[str, Any]:
    """
    Add cart to template context.
    
    Args:
        request: HTTP request
        
    Returns:
        Dict[str, Any]: Context variables
    """
    cart_count = 0
    cart_total = 0
    cart_items = []
    
    if request.user.is_authenticated:
        # Get user's cart
        cart = request.user.cart
        if cart:
            cart_items = cart.items.all()
            cart_count = cart_items.count()
            cart_total = cart.total
    
    return {
        'cart_count': cart_count,
        'cart_total': cart_total,
        'cart_items': cart_items
    }

def search_suggestions(request: HttpRequest) -> Dict[str, Any]:
    """
    Add search suggestions to template context.
    
    Args:
        request: HTTP request
        
    Returns:
        Dict[str, Any]: Context variables
    """
    # Get popular searches
    popular_searches = ProductService.get_popular_searches()
    
    return {
        'popular_searches': popular_searches
    }

def filter_options(request: HttpRequest) -> Dict[str, Any]:
    """
    Add filter options to template context.
    
    Args:
        request: HTTP request
        
    Returns:
        Dict[str, Any]: Context variables
    """
    # Try to get from cache
    options = cache.get('filter_options_context')
    
    if options is None:
        # Get unique sizes and colors
        sizes = set()
        colors = set()
        
        for product in Product.objects.filter(status='active'):
            sizes.update(product.available_sizes)
            colors.update(product.available_colors)
        
        options = {
            'sizes': sorted(sizes),
            'colors': sorted(colors)
        }
        
        # Cache the options
        cache.set('filter_options_context', options, 3600)
    
    return options
