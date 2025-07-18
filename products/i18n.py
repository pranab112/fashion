"""
Internationalization functionality for the products app.
"""

import logging
from typing import Any, Dict, List, Optional
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.cache import cache
from modeltranslation.translator import translator, TranslationOptions

from .models import Product, Category, Brand
from .constants import CURRENCY_SYMBOLS

logger = logging.getLogger(__name__)

# Model Translation Options
class ProductTranslationOptions(TranslationOptions):
    """Translation options for Product model."""
    
    fields = (
        'name',
        'description',
        'key_features',
        'meta_title',
        'meta_description'
    )

class CategoryTranslationOptions(TranslationOptions):
    """Translation options for Category model."""
    
    fields = (
        'name',
        'description',
        'meta_title',
        'meta_description'
    )

class BrandTranslationOptions(TranslationOptions):
    """Translation options for Brand model."""
    
    fields = (
        'name',
        'description',
        'meta_title',
        'meta_description'
    )

# Register models for translation
translator.register(Product, ProductTranslationOptions)
translator.register(Category, CategoryTranslationOptions)
translator.register(Brand, BrandTranslationOptions)

class ProductI18N:
    """Internationalization manager for products."""

    @staticmethod
    def get_translated_fields(model_class: Any) -> List[str]:
        """
        Get translatable fields for model.
        
        Args:
            model_class: Model class
            
        Returns:
            List[str]: Translatable fields
        """
        try:
            trans_opts = translator.get_options_for_model(model_class)
            return trans_opts.fields
        except Exception as e:
            logger.error(f"Error getting translated fields: {str(e)}")
            return []

    @staticmethod
    def get_language_choices() -> List[Tuple[str, str]]:
        """
        Get available language choices.
        
        Returns:
            List[Tuple[str, str]]: Language choices
        """
        return [
            (code, name)
            for code, name in settings.LANGUAGES
            if code in settings.MODELTRANSLATION_LANGUAGES
        ]

    @staticmethod
    def get_currency_display(
        amount: float,
        currency: str,
        locale: str = None
    ) -> str:
        """
        Get formatted currency display.
        
        Args:
            amount: Amount to format
            currency: Currency code
            locale: Locale code
            
        Returns:
            str: Formatted currency string
        """
        try:
            from babel.numbers import format_currency
            
            if locale is None:
                locale = settings.LANGUAGE_CODE
            
            return format_currency(
                amount,
                currency,
                locale=locale
            )
        except Exception as e:
            logger.error(f"Error formatting currency: {str(e)}")
            symbol = CURRENCY_SYMBOLS.get(currency, currency)
            return f"{symbol}{amount:.2f}"

    @staticmethod
    def get_translated_choices(choices: List[Tuple[Any, str]]) -> List[Tuple[Any, str]]:
        """
        Get translated choices.
        
        Args:
            choices: Choice tuples
            
        Returns:
            List[Tuple[Any, str]]: Translated choices
        """
        return [(value, _(label)) for value, label in choices]

class LocaleMiddleware:
    """Middleware to handle locale-specific functionality."""

    def __init__(self, get_response):
        """
        Initialize middleware.
        
        Args:
            get_response: Get response callable
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Process request and set locale.
        
        Args:
            request: HTTP request
            
        Returns:
            HttpResponse: HTTP response
        """
        # Get locale from user preferences or session
        locale = self.get_user_locale(request)
        
        # Set locale for request
        request.locale = locale
        
        # Set currency for request
        request.currency = self.get_user_currency(request)
        
        response = self.get_response(request)
        return response

    def get_user_locale(self, request) -> str:
        """
        Get user's preferred locale.
        
        Args:
            request: HTTP request
            
        Returns:
            str: Locale code
        """
        # Check user preferences if authenticated
        if request.user.is_authenticated:
            try:
                profile = request.user.profile
                if profile.preferred_language:
                    return profile.preferred_language
            except Exception:
                pass
        
        # Check session
        locale = request.session.get('django_language')
        if locale:
            return locale
        
        # Check Accept-Language header
        accept_lang = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
        if accept_lang:
            for lang in accept_lang.split(','):
                lang = lang.split(';')[0].strip()
                if lang in dict(settings.LANGUAGES):
                    return lang
        
        # Fall back to default language
        return settings.LANGUAGE_CODE

    def get_user_currency(self, request) -> str:
        """
        Get user's preferred currency.
        
        Args:
            request: HTTP request
            
        Returns:
            str: Currency code
        """
        # Check user preferences if authenticated
        if request.user.is_authenticated:
            try:
                profile = request.user.profile
                if profile.preferred_currency:
                    return profile.preferred_currency
            except Exception:
                pass
        
        # Check session
        currency = request.session.get('currency')
        if currency:
            return currency
        
        # Fall back to default currency
        return settings.DEFAULT_CURRENCY

class TranslationCache:
    """Cache manager for translations."""

    @staticmethod
    def get_translation(key: str, language: str) -> Optional[str]:
        """
        Get cached translation.
        
        Args:
            key: Translation key
            language: Language code
            
        Returns:
            Optional[str]: Cached translation
        """
        cache_key = f"translation_{language}_{key}"
        return cache.get(cache_key)

    @staticmethod
    def set_translation(key: str, language: str, value: str, timeout: int = 3600) -> None:
        """
        Set translation in cache.
        
        Args:
            key: Translation key
            language: Language code
            value: Translation value
            timeout: Cache timeout in seconds
        """
        cache_key = f"translation_{language}_{key}"
        cache.set(cache_key, value, timeout)

    @staticmethod
    def delete_translation(key: str, language: str) -> None:
        """
        Delete translation from cache.
        
        Args:
            key: Translation key
            language: Language code
        """
        cache_key = f"translation_{language}_{key}"
        cache.delete(cache_key)

    @staticmethod
    def clear_translations() -> None:
        """Clear all cached translations."""
        cache.delete_pattern("translation_*")

def get_translated_field(obj: Any, field: str, language: str = None) -> str:
    """
    Get translated field value.
    
    Args:
        obj: Model instance
        field: Field name
        language: Language code
        
    Returns:
        str: Translated value
    """
    if language is None:
        language = settings.LANGUAGE_CODE
    
    try:
        return getattr(obj, f"{field}_{language}")
    except AttributeError:
        return getattr(obj, field)

def set_translated_field(obj: Any, field: str, value: str, language: str = None) -> None:
    """
    Set translated field value.
    
    Args:
        obj: Model instance
        field: Field name
        value: Field value
        language: Language code
    """
    if language is None:
        language = settings.LANGUAGE_CODE
    
    try:
        setattr(obj, f"{field}_{language}", value)
    except AttributeError:
        setattr(obj, field, value)
