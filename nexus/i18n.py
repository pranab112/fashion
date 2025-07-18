from django.utils.translation import gettext_lazy as _
from django.utils import translation
from django.conf import settings
from typing import Dict, Any, List, Optional
import logging
from .cache import CacheService
from .monitoring import Monitoring
import pytz
from babel.numbers import format_currency, format_decimal
from babel.dates import format_datetime
from datetime import datetime

logger = logging.getLogger(__name__)

class LocalizationService:
    """Service class for handling internationalization and localization."""

    # Supported languages
    LANGUAGES = {
        'en': {
            'name': _('English'),
            'flag': '🇺🇸',
            'currency': 'USD',
            'decimal_separator': '.',
            'thousands_separator': ',',
            'date_format': '%m/%d/%Y',
            'time_format': '%I:%M %p',
        },
        'es': {
            'name': _('Spanish'),
            'flag': '🇪🇸',
            'currency': 'EUR',
            'decimal_separator': ',',
            'thousands_separator': '.',
            'date_format': '%d/%m/%Y',
            'time_format': '%H:%M',
        },
        'fr': {
            'name': _('French'),
            'flag': '🇫🇷',
            'currency': 'EUR',
            'decimal_separator': ',',
            'thousands_separator': ' ',
            'date_format': '%d/%m/%Y',
            'time_format': '%H:%M',
        },
        # Add more languages as needed
    }

    # Currency formatting
    CURRENCIES = {
        'USD': {'symbol': '$', 'position': 'before'},
        'EUR': {'symbol': '€', 'position': 'after'},
        'GBP': {'symbol': '£', 'position': 'before'},
        # Add more currencies as needed
    }

    @classmethod
    def get_supported_languages(cls) -> List[Dict[str, str]]:
        """Get list of supported languages."""
        return [
            {
                'code': code,
                'name': str(data['name']),
                'flag': data['flag']
            }
            for code, data in cls.LANGUAGES.items()
        ]

    @classmethod
    def get_language_data(cls, language_code: str) -> Dict[str, Any]:
        """Get language configuration data."""
        return cls.LANGUAGES.get(language_code, cls.LANGUAGES['en'])

    @classmethod
    @CacheService.cache_decorator('i18n')
    def get_translations(cls, language_code: str) -> Dict[str, str]:
        """Get translations for a specific language."""
        from django.utils.translation import get_language, activate

        current_lang = get_language()
        activate(language_code)

        translations = {
            # Common translations
            'welcome': _('Welcome to NEXUS Fashion'),
            'cart': _('Shopping Cart'),
            'wishlist': _('Wishlist'),
            'account': _('My Account'),
            'orders': _('My Orders'),
            'settings': _('Settings'),
            'logout': _('Logout'),
            
            # Product-related
            'add_to_cart': _('Add to Cart'),
            'add_to_wishlist': _('Add to Wishlist'),
            'out_of_stock': _('Out of Stock'),
            'in_stock': _('In Stock'),
            'size': _('Size'),
            'color': _('Color'),
            'quantity': _('Quantity'),
            
            # Order-related
            'order_status': _('Order Status'),
            'order_date': _('Order Date'),
            'order_total': _('Order Total'),
            'shipping_address': _('Shipping Address'),
            'billing_address': _('Billing Address'),
            
            # Checkout-related
            'checkout': _('Checkout'),
            'payment': _('Payment'),
            'shipping': _('Shipping'),
            'review': _('Review Order'),
            'confirm': _('Confirm Order'),
            
            # Form labels
            'email': _('Email Address'),
            'password': _('Password'),
            'confirm_password': _('Confirm Password'),
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
            'phone': _('Phone Number'),
            'address': _('Address'),
            'city': _('City'),
            'country': _('Country'),
            'postal_code': _('Postal Code'),
            
            # Messages
            'added_to_cart': _('Item added to cart'),
            'removed_from_cart': _('Item removed from cart'),
            'order_success': _('Order placed successfully'),
            'payment_error': _('Payment processing error'),
            
            # Error messages
            'required_field': _('This field is required'),
            'invalid_email': _('Please enter a valid email address'),
            'invalid_password': _('Password must be at least 8 characters long'),
            'passwords_not_match': _('Passwords do not match'),
        }

        activate(current_lang)
        return translations

    @classmethod
    def format_currency(
        cls,
        amount: float,
        currency: str = 'USD',
        locale: str = 'en_US'
    ) -> str:
        """Format currency amount."""
        try:
            return format_currency(amount, currency, locale=locale)
        except Exception as e:
            logger.error(f"Currency formatting error: {str(e)}")
            return f"{cls.CURRENCIES[currency]['symbol']}{amount}"

    @classmethod
    def format_number(
        cls,
        number: float,
        decimal_places: int = 2,
        locale: str = 'en_US'
    ) -> str:
        """Format number according to locale."""
        try:
            return format_decimal(
                number,
                format=f"#,##0.{'0' * decimal_places}",
                locale=locale
            )
        except Exception as e:
            logger.error(f"Number formatting error: {str(e)}")
            return str(number)

    @classmethod
    def format_date(
        cls,
        date: datetime,
        format: str = 'medium',
        locale: str = 'en_US'
    ) -> str:
        """Format date according to locale."""
        try:
            return format_datetime(date, format=format, locale=locale)
        except Exception as e:
            logger.error(f"Date formatting error: {str(e)}")
            return date.strftime(cls.LANGUAGES['en']['date_format'])

    @classmethod
    def get_timezone_choices(cls) -> List[tuple]:
        """Get list of available timezones."""
        return [(tz, tz) for tz in pytz.common_timezones]

    @classmethod
    def convert_timezone(
        cls,
        datetime_obj: datetime,
        to_timezone: str
    ) -> datetime:
        """Convert datetime to specified timezone."""
        try:
            target_tz = pytz.timezone(to_timezone)
            return datetime_obj.astimezone(target_tz)
        except Exception as e:
            logger.error(f"Timezone conversion error: {str(e)}")
            return datetime_obj

class TranslationMiddleware:
    """Middleware for handling language selection."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get language preference
        language = self._get_language_preference(request)
        
        # Activate language
        translation.activate(language)
        request.LANGUAGE_CODE = language

        response = self.get_response(request)

        # Add language cookie if it doesn't exist
        if not request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME):
            response.set_cookie(
                settings.LANGUAGE_COOKIE_NAME,
                language,
                max_age=settings.LANGUAGE_COOKIE_AGE,
                path=settings.LANGUAGE_COOKIE_PATH,
                domain=settings.LANGUAGE_COOKIE_DOMAIN,
                secure=settings.LANGUAGE_COOKIE_SECURE,
                httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
                samesite=settings.LANGUAGE_COOKIE_SAMESITE,
            )

        return response

    def _get_language_preference(self, request) -> str:
        """Get user's language preference."""
        # Check session
        if hasattr(request, 'session'):
            language = request.session.get(settings.LANGUAGE_SESSION_KEY)
            if language in LocalizationService.LANGUAGES:
                return language

        # Check cookie
        language = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
        if language in LocalizationService.LANGUAGES:
            return language

        # Check Accept-Language header
        accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
        for language in accept_language.split(','):
            lang_code = language.split(';')[0].strip().split('-')[0]
            if lang_code in LocalizationService.LANGUAGES:
                return lang_code

        # Default to English
        return 'en'

class LocaleMiddleware:
    """Middleware for handling locale-specific settings."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Set timezone if user is authenticated
        if request.user.is_authenticated and hasattr(request.user, 'timezone'):
            timezone.activate(pytz.timezone(request.user.timezone))
        else:
            timezone.deactivate()

        response = self.get_response(request)
        return response
