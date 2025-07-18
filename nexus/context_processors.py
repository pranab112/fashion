from typing import Dict, Any
from django.http import HttpRequest
from django.conf import settings
from django.urls import reverse
from .analytics import AnalyticsService
from .cache import CacheService
from .constants import ProductConstants, CurrencyConstants

def global_settings(request: HttpRequest) -> Dict[str, Any]:
    """Add global settings to template context."""
    return {
        'SITE_NAME': settings.SITE_NAME,
        'SITE_URL': settings.SITE_URL,
        'CONTACT_EMAIL': settings.CONTACT_EMAIL,
        'CONTACT_PHONE': settings.CONTACT_PHONE,
        'SOCIAL_LINKS': {
            'facebook': settings.FACEBOOK_URL,
            'twitter': settings.TWITTER_URL,
            'instagram': settings.INSTAGRAM_URL,
            'linkedin': settings.LINKEDIN_URL
        },
        'COPYRIGHT_YEAR': settings.COPYRIGHT_YEAR,
        'GOOGLE_ANALYTICS_ID': settings.GOOGLE_ANALYTICS_ID,
        'MAINTENANCE_MODE': getattr(settings, 'MAINTENANCE_MODE', False)
    }

def user_context(request: HttpRequest) -> Dict[str, Any]:
    """Add user-related context."""
    context = {
        'is_authenticated': request.user.is_authenticated,
        'notifications_count': 0,
        'cart_count': 0,
        'wishlist_count': 0
    }

    if request.user.is_authenticated:
        # Get notifications count
        context['notifications_count'] = get_notifications_count(request.user)
        
        # Get cart count
        context['cart_count'] = get_cart_count(request.user)
        
        # Get wishlist count
        context['wishlist_count'] = get_wishlist_count(request.user)

    return context

def navigation_context(request: HttpRequest) -> Dict[str, Any]:
    """Add navigation-related context."""
    cache_key = 'navigation_menu'
    menu = CacheService.get_cache(cache_key)

    if menu is None:
        menu = {
            'categories': get_categories_menu(),
            'pages': get_pages_menu()
        }
        CacheService.set_cache(cache_key, menu, timeout=3600)  # Cache for 1 hour

    return {'navigation': menu}

def currency_context(request: HttpRequest) -> Dict[str, Any]:
    """Add currency-related context."""
    return {
        'DEFAULT_CURRENCY': settings.DEFAULT_CURRENCY,
        'CURRENCY_SYMBOL': CurrencyConstants.SYMBOLS.get(
            settings.DEFAULT_CURRENCY,
            '$'
        ),
        'SUPPORTED_CURRENCIES': CurrencyConstants.CURRENCIES
    }

def analytics_context(request: HttpRequest) -> Dict[str, Any]:
    """Add analytics-related context."""
    if not request.user.is_authenticated:
        return {}

    # Get personalized recommendations
    recommendations = AnalyticsService.get_user_recommendations(
        user_id=request.user.id,
        limit=5
    )

    # Get recently viewed products
    recently_viewed = AnalyticsService.get_recently_viewed_products(
        user_id=request.user.id,
        limit=5
    )

    return {
        'recommended_products': recommendations,
        'recently_viewed_products': recently_viewed
    }

def search_context(request: HttpRequest) -> Dict[str, Any]:
    """Add search-related context."""
    return {
        'popular_searches': get_popular_searches(),
        'search_filters': {
            'price_range': get_price_range(),
            'categories': get_category_filters(),
            'brands': get_brand_filters(),
            'sizes': ProductConstants.SIZE_CHART,
            'colors': ProductConstants.COLORS
        }
    }

def footer_context(request: HttpRequest) -> Dict[str, Any]:
    """Add footer-related context."""
    return {
        'footer_categories': get_footer_categories(),
        'footer_pages': get_footer_pages(),
        'footer_links': get_footer_links(),
        'payment_methods': get_payment_methods()
    }

# Helper functions
def get_notifications_count(user) -> int:
    """Get user's unread notifications count."""
    cache_key = f'notifications_count:{user.id}'
    count = CacheService.get_cache(cache_key)

    if count is None:
        count = user.notifications.filter(is_read=False).count()
        CacheService.set_cache(cache_key, count, timeout=300)  # Cache for 5 minutes

    return count

def get_cart_count(user) -> int:
    """Get user's cart items count."""
    cache_key = f'cart_count:{user.id}'
    count = CacheService.get_cache(cache_key)

    if count is None:
        count = user.cart.items.count() if hasattr(user, 'cart') else 0
        CacheService.set_cache(cache_key, count, timeout=300)

    return count

def get_wishlist_count(user) -> int:
    """Get user's wishlist items count."""
    cache_key = f'wishlist_count:{user.id}'
    count = CacheService.get_cache(cache_key)

    if count is None:
        count = user.wishlist.products.count() if hasattr(user, 'wishlist') else 0
        CacheService.set_cache(cache_key, count, timeout=300)

    return count

def get_categories_menu() -> list:
    """Get categories for navigation menu."""
    from products.models import Category
    return Category.objects.filter(
        is_active=True,
        parent__isnull=True
    ).prefetch_related('children').all()

def get_pages_menu() -> list:
    """Get static pages for navigation menu."""
    return [
        {'title': 'About Us', 'url': reverse('core:about')},
        {'title': 'Contact', 'url': reverse('core:contact')},
        {'title': 'FAQ', 'url': reverse('core:faq')},
        {'title': 'Terms & Conditions', 'url': reverse('core:terms')},
        {'title': 'Privacy Policy', 'url': reverse('core:privacy')}
    ]

def get_popular_searches() -> list:
    """Get popular search terms."""
    cache_key = 'popular_searches'
    searches = CacheService.get_cache(cache_key)

    if searches is None:
        searches = AnalyticsService.get_popular_searches(limit=5)
        CacheService.set_cache(cache_key, searches, timeout=3600)

    return searches

def get_price_range() -> Dict[str, float]:
    """Get product price range."""
    from products.models import Product
    from django.db.models import Min, Max

    cache_key = 'price_range'
    price_range = CacheService.get_cache(cache_key)

    if price_range is None:
        aggregates = Product.objects.aggregate(
            min_price=Min('price'),
            max_price=Max('price')
        )
        price_range = {
            'min': float(aggregates['min_price'] or 0),
            'max': float(aggregates['max_price'] or 0)
        }
        CacheService.set_cache(cache_key, price_range, timeout=3600)

    return price_range

def get_category_filters() -> list:
    """Get category filters with product counts."""
    from products.models import Category
    from django.db.models import Count

    cache_key = 'category_filters'
    categories = CacheService.get_cache(cache_key)

    if categories is None:
        categories = Category.objects.annotate(
            product_count=Count('products')
        ).filter(is_active=True).values(
            'id', 'name', 'product_count'
        )
        CacheService.set_cache(cache_key, list(categories), timeout=3600)

    return categories

def get_brand_filters() -> list:
    """Get brand filters with product counts."""
    from products.models import Brand
    from django.db.models import Count

    cache_key = 'brand_filters'
    brands = CacheService.get_cache(cache_key)

    if brands is None:
        brands = Brand.objects.annotate(
            product_count=Count('products')
        ).filter(is_active=True).values(
            'id', 'name', 'product_count'
        )
        CacheService.set_cache(cache_key, list(brands), timeout=3600)

    return brands

def get_footer_categories() -> list:
    """Get categories for footer."""
    from products.models import Category
    return Category.objects.filter(
        is_active=True,
        parent__isnull=True
    )[:6]

def get_footer_pages() -> list:
    """Get pages for footer."""
    return [
        {'title': 'About Us', 'url': reverse('core:about')},
        {'title': 'Contact', 'url': reverse('core:contact')},
        {'title': 'FAQ', 'url': reverse('core:faq')},
        {'title': 'Shipping', 'url': reverse('core:shipping')},
        {'title': 'Returns', 'url': reverse('core:returns')},
        {'title': 'Track Order', 'url': reverse('orders:track')}
    ]

def get_footer_links() -> Dict[str, list]:
    """Get links for footer sections."""
    return {
        'customer_service': [
            {'title': 'Help Center', 'url': reverse('core:help')},
            {'title': 'Contact Us', 'url': reverse('core:contact')},
            {'title': 'Size Guide', 'url': reverse('core:size-guide')},
            {'title': 'Gift Cards', 'url': reverse('core:gift-cards')}
        ],
        'company': [
            {'title': 'About Us', 'url': reverse('core:about')},
            {'title': 'Careers', 'url': reverse('core:careers')},
            {'title': 'Press', 'url': reverse('core:press')},
            {'title': 'Blog', 'url': reverse('blog:index')}
        ],
        'legal': [
            {'title': 'Terms & Conditions', 'url': reverse('core:terms')},
            {'title': 'Privacy Policy', 'url': reverse('core:privacy')},
            {'title': 'Cookie Policy', 'url': reverse('core:cookies')},
            {'title': 'Accessibility', 'url': reverse('core:accessibility')}
        ]
    }

def get_payment_methods() -> list:
    """Get supported payment methods."""
    return [
        {'name': 'Visa', 'icon': 'visa.png'},
        {'name': 'Mastercard', 'icon': 'mastercard.png'},
        {'name': 'American Express', 'icon': 'amex.png'},
        {'name': 'PayPal', 'icon': 'paypal.png'}
    ]
