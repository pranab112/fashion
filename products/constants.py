from django.utils.translation import gettext_lazy as _

STATUS_CHOICES = [
    ('draft', _('Draft')),
    ('active', _('Active')),
    ('inactive', _('Inactive')),
    ('out_of_stock', _('Out of Stock')),
]

THUMBNAIL_SIZES = [
    (150, 150),
    (300, 300),
    (600, 600),
]

CURRENCY_SYMBOLS = {
    'USD': '$',
    'EUR': '€',
    'GBP': '£',
}

DEFAULT_CURRENCY = 'USD'
CURRENCY_DECIMAL_PLACES = 2

CACHE_KEY_PRODUCT = "product:{slug}"
CACHE_KEY_PRODUCT_LIST = "product_list:{category_slug}:{brand_slug}:{min_price}:{max_price}:{sort_by}:{page}"
CACHE_KEY_CATEGORY_LIST = "category_list"
CACHE_KEY_BRAND_LIST = "brand_list"
CACHE_KEY_CATEGORY = "category:{slug}"
CACHE_KEY_BRAND = "brand:{slug}"
CACHE_KEY_FEATURED_PRODUCTS = "featured_products"
CACHE_KEY_NEW_ARRIVALS = "new_arrivals"
CACHE_KEY_ON_SALE_PRODUCTS = "on_sale_products"
CACHE_KEY_TRENDING_PRODUCTS = "trending_products"
CACHE_KEY_CATEGORY_TREE = "category_tree"
CACHE_KEY_SEARCH_SUGGESTIONS = "search_suggestions:{query}"
CACHE_KEY_SEARCH_RESULTS = "search_results:{query}:{category_slug}:{brand_slug}:{min_price}:{max_price}:{sort_by}:{page}"

CACHE_TIMEOUT_PRODUCT = 60 * 60  # 1 hour
CACHE_TIMEOUT_PRODUCT_LIST = 60 * 10  # 10 minutes
CACHE_TIMEOUT_CATEGORY_LIST = 60 * 60 * 24  # 24 hours
CACHE_TIMEOUT_BRAND_LIST = 60 * 60 * 24  # 24 hours
CACHE_TIMEOUT_CATEGORY_TREE = 60 * 60 * 24  # 24 hours
CACHE_TIMEOUT_SEARCH_SUGGESTIONS = 60 * 5  # 5 minutes
CACHE_TIMEOUT_CATEGORY = 60 * 60 * 24  # 24 hours
CACHE_TIMEOUT_BRAND = 60 * 60 * 24  # 24 hours
CACHE_TIMEOUT_FEATURED = 60 * 60  # 1 hour
CACHE_TIMEOUT_NEW_ARRIVALS = 60 * 60  # 1 hour
CACHE_TIMEOUT_ON_SALE = 60 * 60  # 1 hour
CACHE_TIMEOUT_TRENDING = 60 * 60  # 1 hour
CACHE_TIMEOUT_SEARCH = 60 * 5  # 5 minutes
CACHE_TIMEOUT_SEARCH_RESULTS = 60 * 5  # 5 minutes

ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif']
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB
MIN_REVIEW_LENGTH = 10
MAX_REVIEW_LENGTH = 500
MIN_REVIEW_TITLE_LENGTH = 5
MAX_REVIEW_TITLE_LENGTH = 100

COLORS = {
    'red': _('Red'),
    'blue': _('Blue'),
    'green': _('Green'),
    'black': _('Black'),
    'white': _('White'),
}

GENDER_CHOICES = [
    ('M', _('Men')),
    ('W', _('Women')),
    ('K', _('Kids')),
    ('U', _('Unisex')),
]

PRICE_RANGES = [
    (0, 25, 'Under $25'),
    (25, 50, '$25 - $50'),
    (50, 100, '$50 - $100'),
    (100, 200, '$100 - $200'),
    (200, 500, '$200 - $500'),
    (500, 0, 'Over $500'),
]

DISCOUNT_RANGES = [
    (0, 10, '0-10%'),
    (10, 20, '10-20%'),
    (20, 30, '20-30%'),
    (30, 50, '30-50%'),
    (50, 70, '50-70%'),
    (70, 100, '70-100%'),
]

SIZES_CLOTHING = [
    ('XS', _('Extra Small')),
    ('S', _('Small')),
    ('M', _('Medium')),
    ('L', _('Large')),
    ('XL', _('Extra Large')),
]

PRODUCTS_PER_PAGE = 12
API_PAGE_SIZE = 10
API_MAX_PAGE_SIZE = 100