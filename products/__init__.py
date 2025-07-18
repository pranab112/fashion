"""
Products app for NEXUS e-commerce platform.

This app handles all product-related functionality including:
- Product catalog management
- Categories and brands
- Product search and filtering
- Reviews and ratings
- Product images and variants
- Stock management
"""

default_app_config = 'products.apps.ProductsConfig'

# Version of the products app
VERSION = (1, 0, 0)

def get_version():
    """Return the version as a string."""
    return '.'.join(str(v) for v in VERSION)

# Constants
GENDER_CHOICES = [
    ('M', 'Men'),
    ('W', 'Women'),
    ('U', 'Unisex'),
    ('K', 'Kids'),
]

STOCK_THRESHOLD = 5  # Low stock warning threshold

# Feature flags
ENABLE_REVIEWS = True
ENABLE_QUICK_VIEW = True
ENABLE_COMPARE = True
ENABLE_WISHLIST = True
SHOW_STOCK_BADGE = True
SHOW_SALE_BADGE = True

# Cache timeouts (in seconds)
CACHE_TIMEOUT = {
    'product_detail': 3600,  # 1 hour
    'category_tree': 3600,   # 1 hour
    'brand_list': 3600,      # 1 hour
    'product_list': 300,     # 5 minutes
    'search_results': 300,   # 5 minutes
}

# Image sizes
IMAGE_SIZES = {
    'thumbnail': (200, 200),
    'medium': (400, 400),
    'large': (800, 800),
}

# Search configuration
SEARCH_FIELDS = [
    'name',
    'description',
    'category__name',
    'brand__name',
    'sku',
]

SEARCH_BOOST = {
    'name': 4,
    'sku': 3,
    'category__name': 2,
    'brand__name': 2,
    'description': 1,
}

# Review settings
REVIEW_SETTINGS = {
    'require_login': True,
    'allow_anonymous': False,
    'moderation_required': True,
    'min_rating': 1,
    'max_rating': 5,
}

# Product list settings
PRODUCTS_PER_PAGE = 24
SORT_OPTIONS = [
    ('price_asc', 'Price: Low to High'),
    ('price_desc', 'Price: High to Low'),
    ('newest', 'Newest First'),
    ('rating', 'Average Rating'),
    ('popularity', 'Popularity'),
]

# Currency settings
CURRENCY_SYMBOL = '$'
CURRENCY_POSITION = 'before'  # 'before' or 'after'

# Social sharing platforms
SOCIAL_SHARING_PLATFORMS = [
    'facebook',
    'twitter',
    'pinterest',
    'email',
]
