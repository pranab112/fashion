from django.utils.translation import gettext_lazy as _
from typing import Dict, List, Tuple

class ProductConstants:
    """Constants related to products."""

    # Product status choices
    STATUS_ACTIVE = 'active'
    STATUS_INACTIVE = 'inactive'
    STATUS_DRAFT = 'draft'
    STATUS_ARCHIVED = 'archived'

    STATUS_CHOICES = [
        (STATUS_ACTIVE, _('Active')),
        (STATUS_INACTIVE, _('Inactive')),
        (STATUS_DRAFT, _('Draft')),
        (STATUS_ARCHIVED, _('Archived'))
    ]

    # Size chart
    SIZE_XS = 'XS'
    SIZE_S = 'S'
    SIZE_M = 'M'
    SIZE_L = 'L'
    SIZE_XL = 'XL'
    SIZE_XXL = 'XXL'

    SIZE_CHOICES = [
        (SIZE_XS, _('Extra Small')),
        (SIZE_S, _('Small')),
        (SIZE_M, _('Medium')),
        (SIZE_L, _('Large')),
        (SIZE_XL, _('Extra Large')),
        (SIZE_XXL, _('Double Extra Large'))
    ]

    # Color choices
    COLORS = [
        ('black', _('Black')),
        ('white', _('White')),
        ('red', _('Red')),
        ('blue', _('Blue')),
        ('green', _('Green')),
        ('yellow', _('Yellow')),
        ('purple', _('Purple')),
        ('pink', _('Pink')),
        ('gray', _('Gray')),
        ('brown', _('Brown'))
    ]

    # Default values
    DEFAULT_LOW_STOCK_THRESHOLD = 10
    DEFAULT_TAX_RATE = 0.08  # 8%
    DEFAULT_SHIPPING_COST = 10.00

class OrderConstants:
    """Constants related to orders."""

    # Order status choices
    STATUS_PENDING = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_SHIPPED = 'shipped'
    STATUS_DELIVERED = 'delivered'
    STATUS_CANCELLED = 'cancelled'
    STATUS_REFUNDED = 'refunded'

    STATUS_CHOICES = [
        (STATUS_PENDING, _('Pending')),
        (STATUS_PROCESSING, _('Processing')),
        (STATUS_SHIPPED, _('Shipped')),
        (STATUS_DELIVERED, _('Delivered')),
        (STATUS_CANCELLED, _('Cancelled')),
        (STATUS_REFUNDED, _('Refunded'))
    ]

    # Payment status choices
    PAYMENT_PENDING = 'pending'
    PAYMENT_PAID = 'paid'
    PAYMENT_FAILED = 'failed'
    PAYMENT_REFUNDED = 'refunded'

    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_PENDING, _('Pending')),
        (PAYMENT_PAID, _('Paid')),
        (PAYMENT_FAILED, _('Failed')),
        (PAYMENT_REFUNDED, _('Refunded'))
    ]

    # Shipping methods
    SHIPPING_STANDARD = 'standard'
    SHIPPING_EXPRESS = 'express'
    SHIPPING_OVERNIGHT = 'overnight'

    SHIPPING_CHOICES = [
        (SHIPPING_STANDARD, _('Standard Shipping')),
        (SHIPPING_EXPRESS, _('Express Shipping')),
        (SHIPPING_OVERNIGHT, _('Overnight Shipping'))
    ]

class CartConstants:
    """Constants related to shopping cart."""

    # Cart status choices
    STATUS_ACTIVE = 'active'
    STATUS_ABANDONED = 'abandoned'
    STATUS_CONVERTED = 'converted'

    STATUS_CHOICES = [
        (STATUS_ACTIVE, _('Active')),
        (STATUS_ABANDONED, _('Abandoned')),
        (STATUS_CONVERTED, _('Converted'))
    ]

    # Cart limits
    MAX_ITEMS = 20
    MAX_QUANTITY_PER_ITEM = 10

class UserConstants:
    """Constants related to users."""

    # User roles
    ROLE_CUSTOMER = 'customer'
    ROLE_STAFF = 'staff'
    ROLE_ADMIN = 'admin'

    ROLE_CHOICES = [
        (ROLE_CUSTOMER, _('Customer')),
        (ROLE_STAFF, _('Staff')),
        (ROLE_ADMIN, _('Admin'))
    ]

    # Address types
    ADDRESS_SHIPPING = 'shipping'
    ADDRESS_BILLING = 'billing'

    ADDRESS_CHOICES = [
        (ADDRESS_SHIPPING, _('Shipping')),
        (ADDRESS_BILLING, _('Billing'))
    ]

class PaymentConstants:
    """Constants related to payments."""

    # Payment methods
    METHOD_CARD = 'card'
    METHOD_PAYPAL = 'paypal'
    METHOD_BANK_TRANSFER = 'bank_transfer'

    METHOD_CHOICES = [
        (METHOD_CARD, _('Credit/Debit Card')),
        (METHOD_PAYPAL, _('PayPal')),
        (METHOD_BANK_TRANSFER, _('Bank Transfer'))
    ]

    # Payment providers
    PROVIDER_STRIPE = 'stripe'
    PROVIDER_PAYPAL = 'paypal'
    PROVIDER_BANK = 'bank'

    PROVIDER_CHOICES = [
        (PROVIDER_STRIPE, _('Stripe')),
        (PROVIDER_PAYPAL, _('PayPal')),
        (PROVIDER_BANK, _('Bank'))
    ]

class ReviewConstants:
    """Constants related to reviews."""

    # Review status choices
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = [
        (STATUS_PENDING, _('Pending')),
        (STATUS_APPROVED, _('Approved')),
        (STATUS_REJECTED, _('Rejected'))
    ]

    # Rating choices
    RATING_CHOICES = [
        (1, _('1 Star')),
        (2, _('2 Stars')),
        (3, _('3 Stars')),
        (4, _('4 Stars')),
        (5, _('5 Stars'))
    ]

class CurrencyConstants:
    """Constants related to currencies."""

    # Currency codes
    USD = 'USD'
    EUR = 'EUR'
    GBP = 'GBP'
    JPY = 'JPY'
    CNY = 'CNY'
    INR = 'INR'

    CURRENCIES = [
        (USD, _('US Dollar')),
        (EUR, _('Euro')),
        (GBP, _('British Pound')),
        (JPY, _('Japanese Yen')),
        (CNY, _('Chinese Yuan')),
        (INR, _('Indian Rupee'))
    ]

    # Currency symbols
    SYMBOLS = {
        USD: '$',
        EUR: '€',
        GBP: '£',
        JPY: '¥',
        CNY: '¥',
        INR: '₹'
    }

class PaginationConstants:
    """Constants related to pagination."""

    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    PAGE_SIZE_OPTIONS = [10, 20, 50, 100]

class CacheConstants:
    """Constants related to caching."""

    # Cache timeouts (in seconds)
    TIMEOUT_FIVE_MINUTES = 300
    TIMEOUT_ONE_HOUR = 3600
    TIMEOUT_ONE_DAY = 86400
    TIMEOUT_ONE_WEEK = 604800

    # Cache keys
    KEY_PRODUCT_DETAIL = 'product:{}'
    KEY_CATEGORY_TREE = 'category_tree'
    KEY_EXCHANGE_RATES = 'exchange_rates'
    KEY_NAVIGATION_MENU = 'navigation_menu'

class ValidationConstants:
    """Constants related to validation."""

    # Password validation
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 128

    # Product validation
    MIN_PRICE = 0.01
    MAX_PRICE = 999999.99
    MAX_SKU_LENGTH = 50

    # Review validation
    MIN_REVIEW_LENGTH = 10
    MAX_REVIEW_LENGTH = 1000

class FileConstants:
    """Constants related to file handling."""

    # Image sizes
    THUMBNAIL_SIZE = (100, 100)
    MEDIUM_SIZE = (400, 400)
    LARGE_SIZE = (800, 800)

    # File size limits (in bytes)
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    # Allowed file types
    ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif']
    ALLOWED_DOCUMENT_TYPES = ['application/pdf', 'application/msword']
