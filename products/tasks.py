from celery import shared_task
from django.core.cache import cache
from django.db.models import F
from django.utils import timezone

from .constants import (
    CACHE_KEY_PRODUCT,
    CACHE_KEY_PRODUCT_LIST,
    CACHE_KEY_FEATURED_PRODUCTS,
    CACHE_KEY_NEW_ARRIVALS,
    CACHE_KEY_TRENDING_PRODUCTS,
    CACHE_KEY_SEARCH_RESULTS,
    CACHE_TIMEOUT_PRODUCT,
    CACHE_TIMEOUT_PRODUCT_LIST,
    CACHE_TIMEOUT_FEATURED,
    CACHE_TIMEOUT_NEW_ARRIVALS,
    CACHE_TIMEOUT_TRENDING,
    CACHE_TIMEOUT_SEARCH_RESULTS,
)


@shared_task
def update_search_index(product_id, delete=False):
    """Update or delete product from search index"""
    from .models import Product
    from .services import SearchService

    try:
        if delete:
            SearchService.remove_from_index(product_id)
        else:
            product = Product.objects.get(id=product_id)
            SearchService.update_index(product)
        return True
    except Product.DoesNotExist:
        return False


@shared_task
def generate_product_thumbnails(image_id):
    """Generate thumbnails for a product image"""
    from .models import ProductImage
    from .services import ImageService

    try:
        image = ProductImage.objects.get(id=image_id)
        ImageService.generate_thumbnails(image)
        return True
    except ProductImage.DoesNotExist:
        return False


@shared_task
def notify_low_stock(product_id):
    """Send notification for low stock"""
    from .models import Product
    from .services import NotificationService

    try:
        product = Product.objects.get(id=product_id)
        NotificationService.send_low_stock_notification(product)
        return True
    except Product.DoesNotExist:
        return False


@shared_task
def update_product_analytics(product_id):
    """Update analytics for a product"""
    from .models import Product
    from .services import AnalyticsService

    try:
        product = Product.objects.get(id=product_id)
        AnalyticsService.update_product_metrics(product)
        return True
    except Product.DoesNotExist:
        return False


@shared_task
def update_product_cache(product_id):
    """Update the cache for a single product"""
    from .models import Product
    from .services import ProductService

    try:
        product = Product.objects.get(id=product_id)
        cache_key = CACHE_KEY_PRODUCT.format(id=product_id)
        cache.set(cache_key, ProductService.serialize_product(product), CACHE_TIMEOUT_PRODUCT)
        return True
    except Product.DoesNotExist:
        return False


@shared_task
def update_product_list_cache(params=None):
    """Update the cache for product listings with given parameters"""
    from .services import ProductService

    cache_key = CACHE_KEY_PRODUCT_LIST.format(params=params or 'all')
    products = ProductService.get_product_list(params)
    cache.set(cache_key, products, CACHE_TIMEOUT_PRODUCT_LIST)
    return True


@shared_task
def update_featured_products_cache():
    """Update the cache for featured products"""
    from .services import ProductService

    products = ProductService.get_featured_products()
    cache.set(CACHE_KEY_FEATURED_PRODUCTS, products, CACHE_TIMEOUT_FEATURED)
    return True


@shared_task
def update_new_arrivals_cache():
    """Update the cache for new arrivals"""
    from .services import ProductService

    products = ProductService.get_new_arrivals()
    cache.set(CACHE_KEY_NEW_ARRIVALS, products, CACHE_TIMEOUT_NEW_ARRIVALS)
    return True


@shared_task
def update_trending_products_cache():
    """Update the cache for trending products"""
    from .services import ProductService

    products = ProductService.get_trending_products()
    cache.set(CACHE_KEY_TRENDING_PRODUCTS, products, CACHE_TIMEOUT_TRENDING)
    return True


@shared_task
def update_search_results_cache(query, filters=None):
    """Update the cache for search results"""
    from .services import ProductService

    cache_key = CACHE_KEY_SEARCH_RESULTS.format(query=query)
    results = ProductService.search_products(query, filters)
    cache.set(cache_key, results, CACHE_TIMEOUT_SEARCH_RESULTS)
    return True


@shared_task
def process_product_view(view_id):
    """Process a product view asynchronously"""
    from .models import Product, ProductView

    try:
        view = ProductView.objects.get(id=view_id)
        # Update product view count
        Product.objects.filter(id=view.product_id).update(
            view_count=F('view_count') + 1,
            last_viewed_at=timezone.now()
        )
        return True
    except ProductView.DoesNotExist:
        return False


@shared_task
def cleanup_expired_product_views():
    """Clean up expired product views (older than 30 days)"""
    from .models import ProductView

    expiry_date = timezone.now() - timezone.timedelta(days=30)
    ProductView.objects.filter(viewed_at__lt=expiry_date).delete()
    return True


@shared_task
def update_product_ratings():
    """Update product ratings based on reviews"""
    from .models import Product
    from .services import ProductService

    for product in Product.objects.all():
        ProductService.update_product_rating(product)
    return True


@shared_task
def check_low_stock_products():
    """Check for products with low stock and notify"""
    from .services import ProductService

    ProductService.check_low_stock_products()
    return True


@shared_task
def generate_product_recommendations():
    """Generate product recommendations"""
    from .services import ProductService

    ProductService.generate_recommendations()
    return True
