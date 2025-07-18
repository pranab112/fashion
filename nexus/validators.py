from typing import Any, Dict, List, Optional, Union
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import (
    RegexValidator,
    EmailValidator,
    URLValidator,
    MinValueValidator,
    MaxValueValidator
)
import re
from decimal import Decimal
from datetime import datetime
from .constants import (
    ProductConstants,
    SecurityConstants,
    FileConstants
)

class UserValidators:
    """Validators for user-related data."""

    username_validator = RegexValidator(
        regex=r'^[\w.@+-]+$',
        message=_('Enter a valid username. This value may contain only letters, '
                 'numbers, and @/./+/-/_ characters.')
    )

    password_validator = RegexValidator(
        regex=r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$',
        message=_('Password must contain at least 8 characters, including '
                 'letters, numbers, and special characters.')
    )

    phone_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_('Enter a valid phone number.')
    )

    @classmethod
    def validate_password_strength(cls, password: str) -> None:
        """Validate password strength."""
        if len(password) < SecurityConstants.MIN_PASSWORD_LENGTH:
            raise ValidationError(
                _('Password must be at least %(min_length)d characters long.'),
                params={'min_length': SecurityConstants.MIN_PASSWORD_LENGTH}
            )

        if len(password) > SecurityConstants.MAX_PASSWORD_LENGTH:
            raise ValidationError(
                _('Password must be at most %(max_length)d characters long.'),
                params={'max_length': SecurityConstants.MAX_PASSWORD_LENGTH}
            )

        if not any(char.isupper() for char in password):
            raise ValidationError(
                _('Password must contain at least one uppercase letter.')
            )

        if not any(char.islower() for char in password):
            raise ValidationError(
                _('Password must contain at least one lowercase letter.')
            )

        if not any(char.isdigit() for char in password):
            raise ValidationError(
                _('Password must contain at least one number.')
            )

        if not any(char in '!@#$%^&*(),.?":{}|<>' for char in password):
            raise ValidationError(
                _('Password must contain at least one special character.')
            )

    @classmethod
    def validate_age(cls, birth_date: datetime) -> None:
        """Validate user age."""
        from datetime import date
        today = date.today()
        age = (
            today.year - birth_date.year -
            ((today.month, today.day) < (birth_date.month, birth_date.day))
        )

        if age < 13:
            raise ValidationError(
                _('You must be at least 13 years old to register.')
            )

        if age > 120:
            raise ValidationError(
                _('Please enter a valid birth date.')
            )

class ProductValidators:
    """Validators for product-related data."""

    sku_validator = RegexValidator(
        regex=r'^[A-Z0-9]{6,12}$',
        message=_('SKU must be 6-12 characters long and contain only uppercase letters and numbers.')
    )

    @classmethod
    def validate_price(cls, price: Decimal) -> None:
        """Validate product price."""
        if price <= Decimal('0'):
            raise ValidationError(
                _('Price must be greater than zero.')
            )

        if price >= Decimal('1000000'):
            raise ValidationError(
                _('Price cannot exceed 1,000,000.')
            )

    @classmethod
    def validate_stock_quantity(cls, quantity: int) -> None:
        """Validate stock quantity."""
        if quantity < 0:
            raise ValidationError(
                _('Stock quantity cannot be negative.')
            )

        if quantity > 10000:
            raise ValidationError(
                _('Stock quantity cannot exceed 10,000 units.')
            )

    @classmethod
    def validate_size(cls, size: str, category: str) -> None:
        """Validate product size."""
        valid_sizes = ProductConstants.SIZE_CHART.get(category, [])
        if size not in valid_sizes:
            raise ValidationError(
                _('Invalid size for category %(category)s.'),
                params={'category': category}
            )

    @classmethod
    def validate_color(cls, color: str) -> None:
        """Validate product color."""
        valid_colors = [color[0] for color in ProductConstants.COLORS]
        if color not in valid_colors:
            raise ValidationError(
                _('Invalid color choice.')
            )

class OrderValidators:
    """Validators for order-related data."""

    @classmethod
    def validate_shipping_address(cls, address: Dict) -> None:
        """Validate shipping address."""
        required_fields = ['street', 'city', 'state', 'postal_code', 'country']
        
        for field in required_fields:
            if not address.get(field):
                raise ValidationError(
                    _('%(field)s is required.'),
                    params={'field': field.replace('_', ' ').title()}
                )

        # Validate postal code format
        postal_code = address.get('postal_code')
        country = address.get('country')
        
        if postal_code and country:
            from .utils import ValidationUtils
            if not ValidationUtils.validate_postal_code(postal_code, country):
                raise ValidationError(
                    _('Invalid postal code for %(country)s.'),
                    params={'country': country}
                )

    @classmethod
    def validate_payment_info(cls, payment_info: Dict) -> None:
        """Validate payment information."""
        if 'card_number' in payment_info:
            from .utils import ValidationUtils
            if not ValidationUtils.validate_credit_card(payment_info['card_number']):
                raise ValidationError(
                    _('Invalid credit card number.')
                )

        if 'expiry_date' in payment_info:
            try:
                month, year = map(int, payment_info['expiry_date'].split('/'))
                if not (1 <= month <= 12 and year >= datetime.now().year % 100):
                    raise ValidationError(
                        _('Invalid expiry date.')
                    )
            except ValueError:
                raise ValidationError(
                    _('Invalid expiry date format. Use MM/YY.')
                )

class FileValidators:
    """Validators for file uploads."""

    @classmethod
    def validate_image(cls, image) -> None:
        """Validate image file."""
        # Check file size
        if image.size > FileConstants.MAX_IMAGE_SIZE:
            raise ValidationError(
                _('Image file too large. Maximum size is %(max_size)s MB.'),
                params={'max_size': FileConstants.MAX_IMAGE_SIZE / (1024 * 1024)}
            )

        # Check file extension
        ext = image.name.lower().split('.')[-1]
        if f'.{ext}' not in FileConstants.ALLOWED_IMAGE_EXTENSIONS:
            raise ValidationError(
                _('Invalid image format. Allowed formats: %(formats)s'),
                params={'formats': ', '.join(FileConstants.ALLOWED_IMAGE_EXTENSIONS)}
            )

        # Check image dimensions
        from PIL import Image
        img = Image.open(image)
        if img.size[0] > 4096 or img.size[1] > 4096:
            raise ValidationError(
                _('Image dimensions too large. Maximum size is 4096x4096 pixels.')
            )

    @classmethod
    def validate_document(cls, document) -> None:
        """Validate document file."""
        # Check file size
        if document.size > FileConstants.MAX_DOCUMENT_SIZE:
            raise ValidationError(
                _('Document file too large. Maximum size is %(max_size)s MB.'),
                params={'max_size': FileConstants.MAX_DOCUMENT_SIZE / (1024 * 1024)}
            )

        # Check file extension
        ext = document.name.lower().split('.')[-1]
        if f'.{ext}' not in FileConstants.ALLOWED_DOCUMENT_EXTENSIONS:
            raise ValidationError(
                _('Invalid document format. Allowed formats: %(formats)s'),
                params={'formats': ', '.join(FileConstants.ALLOWED_DOCUMENT_EXTENSIONS)}
            )

class ReviewValidators:
    """Validators for review-related data."""

    @classmethod
    def validate_rating(cls, rating: int) -> None:
        """Validate review rating."""
        if not isinstance(rating, int):
            raise ValidationError(
                _('Rating must be a whole number.')
            )

        if rating < 1 or rating > 5:
            raise ValidationError(
                _('Rating must be between 1 and 5.')
            )

    @classmethod
    def validate_review_text(cls, text: str) -> None:
        """Validate review text."""
        if len(text) < 10:
            raise ValidationError(
                _('Review text must be at least 10 characters long.')
            )

        if len(text) > 1000:
            raise ValidationError(
                _('Review text cannot exceed 1000 characters.')
            )

class DiscountValidators:
    """Validators for discount-related data."""

    @classmethod
    def validate_discount_percentage(cls, percentage: Decimal) -> None:
        """Validate discount percentage."""
        if percentage <= Decimal('0'):
            raise ValidationError(
                _('Discount percentage must be greater than zero.')
            )

        if percentage > Decimal('100'):
            raise ValidationError(
                _('Discount percentage cannot exceed 100%.')
            )

    @classmethod
    def validate_discount_dates(cls, start_date: datetime, end_date: datetime) -> None:
        """Validate discount dates."""
        if start_date >= end_date:
            raise ValidationError(
                _('End date must be after start date.')
            )

        if start_date < datetime.now():
            raise ValidationError(
                _('Start date cannot be in the past.')
            )

class ContactValidators:
    """Validators for contact-related data."""

    @classmethod
    def validate_message(cls, message: str) -> None:
        """Validate contact message."""
        if len(message) < 20:
            raise ValidationError(
                _('Message must be at least 20 characters long.')
            )

        if len(message) > 5000:
            raise ValidationError(
                _('Message cannot exceed 5000 characters.')
            )

    @classmethod
    def validate_subject(cls, subject: str) -> None:
        """Validate message subject."""
        if len(subject) < 5:
            raise ValidationError(
                _('Subject must be at least 5 characters long.')
            )

        if len(subject) > 200:
            raise ValidationError(
                _('Subject cannot exceed 200 characters.')
            )
