from typing import Any, Dict, List, Optional, Union
from decimal import Decimal
import re
import uuid
import hashlib
import json
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.text import slugify
import logging

logger = logging.getLogger(__name__)

class ValidationUtils:
    """Utility class for validation functions."""

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format."""
        pattern = r'^\+?1?\d{9,15}$'
        return bool(re.match(pattern, phone))

    @staticmethod
    def validate_postal_code(postal_code: str, country_code: str) -> bool:
        """Validate postal code format for different countries."""
        patterns = {
            'US': r'^\d{5}(-\d{4})?$',
            'UK': r'^[A-Z]{1,2}\d[A-Z\d]? ?\d[A-Z]{2}$',
            'CA': r'^[A-Z]\d[A-Z] ?\d[A-Z]\d$',
            # Add more country patterns as needed
        }
        pattern = patterns.get(country_code.upper(), r'^\w+$')
        return bool(re.match(pattern, postal_code, re.IGNORECASE))

    @staticmethod
    def validate_credit_card(number: str) -> bool:
        """Validate credit card number using Luhn algorithm."""
        digits = [int(d) for d in str(number) if d.isdigit()]
        if not digits:
            return False
            
        # Luhn algorithm
        for i in range(len(digits)-2, -1, -2):
            digits[i] *= 2
            if digits[i] > 9:
                digits[i] -= 9

        return sum(digits) % 10 == 0

    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, bool]:
        """
        Validate password strength.
        Returns dict with validation results.
        """
        return {
            'length': len(password) >= 8,
            'uppercase': bool(re.search(r'[A-Z]', password)),
            'lowercase': bool(re.search(r'[a-z]', password)),
            'numbers': bool(re.search(r'\d', password)),
            'special': bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        }

class FormattingUtils:
    """Utility class for formatting functions."""

    @staticmethod
    def format_price(
        amount: Union[int, float, Decimal],
        currency: str = 'USD',
        locale: str = 'en_US'
    ) -> str:
        """Format price with currency symbol."""
        from babel.numbers import format_currency
        return format_currency(amount, currency, locale=locale)

    @staticmethod
    def format_date(
        date: datetime,
        format_str: str = '%Y-%m-%d',
        locale: str = 'en_US'
    ) -> str:
        """Format date according to locale."""
        from babel.dates import format_date
        return format_date(date, format=format_str, locale=locale)

    @staticmethod
    def format_file_size(size_in_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_in_bytes < 1024:
                return f"{size_in_bytes:.1f} {unit}"
            size_in_bytes /= 1024
        return f"{size_in_bytes:.1f} TB"

    @staticmethod
    def format_phone(phone: str, country_code: str = 'US') -> str:
        """Format phone number according to country."""
        import phonenumbers
        try:
            parsed = phonenumbers.parse(phone, country_code)
            return phonenumbers.format_number(
                parsed,
                phonenumbers.PhoneNumberFormat.INTERNATIONAL
            )
        except Exception:
            return phone

class SecurityUtils:
    """Utility class for security functions."""

    @staticmethod
    def generate_token() -> str:
        """Generate secure random token."""
        return hashlib.sha256(uuid.uuid4().bytes).hexdigest()

    @staticmethod
    def hash_string(text: str, salt: Optional[str] = None) -> str:
        """Hash string with optional salt."""
        if salt:
            text = f"{text}{salt}"
        return hashlib.sha256(text.encode()).hexdigest()

    @staticmethod
    def mask_credit_card(number: str) -> str:
        """Mask credit card number."""
        return f"{'*' * 12}{number[-4:]}"

    @staticmethod
    def mask_email(email: str) -> str:
        """Mask email address."""
        username, domain = email.split('@')
        masked_username = f"{username[0]}{'*' * (len(username)-2)}{username[-1]}"
        return f"{masked_username}@{domain}"

class DataUtils:
    """Utility class for data manipulation."""

    @staticmethod
    def to_decimal(value: Any) -> Optional[Decimal]:
        """Convert value to Decimal."""
        try:
            return Decimal(str(value))
        except (TypeError, ValueError):
            return None

    @staticmethod
    def to_bool(value: Any) -> bool:
        """Convert value to boolean."""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return bool(value)

    @staticmethod
    def clean_dict(data: Dict) -> Dict:
        """Remove None values from dict."""
        return {k: v for k, v in data.items() if v is not None}

    @staticmethod
    def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
        """Deep merge two dictionaries."""
        result = dict1.copy()
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = DataUtils.merge_dicts(result[key], value)
            else:
                result[key] = value
        return result

class TimeUtils:
    """Utility class for time-related functions."""

    @staticmethod
    def is_expired(date: datetime, minutes: int = 0, hours: int = 0, days: int = 0) -> bool:
        """Check if date is expired."""
        expiry = date + timedelta(
            minutes=minutes,
            hours=hours,
            days=days
        )
        return timezone.now() > expiry

    @staticmethod
    def time_since(date: datetime) -> str:
        """Get human-readable time since date."""
        now = timezone.now()
        diff = now - date

        if diff.days > 365:
            years = diff.days // 365
            return f"{years}y ago"
        if diff.days > 30:
            months = diff.days // 30
            return f"{months}mo ago"
        if diff.days > 0:
            return f"{diff.days}d ago"
        if diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours}h ago"
        if diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes}m ago"
        return "just now"

    @staticmethod
    def get_next_business_day(date: datetime = None) -> datetime:
        """Get next business day."""
        if date is None:
            date = timezone.now()
        
        # Skip weekends
        while date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
            date += timedelta(days=1)
        return date

class URLUtils:
    """Utility class for URL-related functions."""

    @staticmethod
    def build_url(base: str, path: str, params: Dict = None) -> str:
        """Build URL with parameters."""
        from urllib.parse import urlencode, urlparse, urlunparse
        
        # Parse base URL
        url_parts = list(urlparse(base))
        
        # Add path
        url_parts[2] = path.lstrip('/')
        
        # Add query parameters
        if params:
            url_parts[4] = urlencode(params)
        
        return urlunparse(url_parts)

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if URL is valid."""
        from urllib.parse import urlparse
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    @staticmethod
    def get_domain(url: str) -> Optional[str]:
        """Extract domain from URL."""
        from urllib.parse import urlparse
        try:
            return urlparse(url).netloc
        except ValueError:
            return None

class TextUtils:
    """Utility class for text manipulation."""

    @staticmethod
    def truncate(text: str, length: int = 100, suffix: str = '...') -> str:
        """Truncate text to specified length."""
        if len(text) <= length:
            return text
        return text[:length].rsplit(' ', 1)[0] + suffix

    @staticmethod
    def strip_html(text: str) -> str:
        """Remove HTML tags from text."""
        import re
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)

    @staticmethod
    def generate_random_string(length: int = 10) -> str:
        """Generate random string."""
        import random
        import string
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    @staticmethod
    def to_snake_case(text: str) -> str:
        """Convert string to snake_case."""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

class GeoUtils:
    """Utility class for geographic functions."""

    @staticmethod
    def calculate_distance(
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """Calculate distance between coordinates in kilometers."""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1 = map(radians, [lat1, lon1])
        lat2, lon2 = map(radians, [lat2, lon2])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c

    @staticmethod
    def get_coordinates_from_address(address: str) -> Optional[Dict[str, float]]:
        """Get coordinates from address using geocoding."""
        try:
            from geopy.geocoders import Nominatim
            geolocator = Nominatim(user_agent="nexus_fashion")
            location = geolocator.geocode(address)
            
            if location:
                return {
                    'latitude': location.latitude,
                    'longitude': location.longitude
                }
            return None
        except Exception as e:
            logger.error(f"Geocoding error: {str(e)}")
            return None
