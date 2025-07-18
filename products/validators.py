"""
Custom validators for the products app.
"""

import os
import re
from typing import Any, Optional
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import BaseValidator
from PIL import Image

from .constants import (
    ALLOWED_IMAGE_TYPES,
    MAX_IMAGE_SIZE,
    MIN_REVIEW_LENGTH,
    MAX_REVIEW_LENGTH,
    MIN_REVIEW_TITLE_LENGTH,
    MAX_REVIEW_TITLE_LENGTH,
    COLORS
)

def validate_image_file(value: Any) -> None:
    """
    Validate uploaded image file.
    
    Args:
        value: File to validate
        
    Raises:
        ValidationError: If file is invalid
    """
    # Check file type
    if value.content_type not in ALLOWED_IMAGE_TYPES:
        raise ValidationError(
            _('Please upload a valid image file (JPG, PNG, or WebP).')
        )
    
    # Check file size
    if value.size > MAX_IMAGE_SIZE:
        raise ValidationError(
            _('Image file size cannot exceed 5MB.')
        )
    
    # Verify it's a valid image
    try:
        img = Image.open(value)
        img.verify()
    except Exception:
        raise ValidationError(
            _('The uploaded file is not a valid image.')
        )

def validate_price(value: Decimal) -> None:
    """
    Validate product price.
    
    Args:
        value: Price to validate
        
    Raises:
        ValidationError: If price is invalid
    """
    if value <= 0:
        raise ValidationError(
            _('Price must be greater than 0.')
        )
    
    if value > 999999.99:
        raise ValidationError(
            _('Price cannot exceed 999,999.99.')
        )

def validate_discount_percentage(value: int) -> None:
    """
    Validate discount percentage.
    
    Args:
        value: Percentage to validate
        
    Raises:
        ValidationError: If percentage is invalid
    """
    if not 0 <= value <= 100:
        raise ValidationError(
            _('Discount percentage must be between 0 and 100.')
        )

def validate_stock_level(value: int) -> None:
    """
    Validate stock level.
    
    Args:
        value: Stock level to validate
        
    Raises:
        ValidationError: If stock level is invalid
    """
    if value < 0:
        raise ValidationError(
            _('Stock level cannot be negative.')
        )
    
    if value > 9999:
        raise ValidationError(
            _('Stock level cannot exceed 9,999.')
        )

def validate_sku(value: str) -> None:
    """
    Validate product SKU.
    
    Args:
        value: SKU to validate
        
    Raises:
        ValidationError: If SKU is invalid
    """
    if not re.match(r'^[A-Z0-9]{6,12}$', value):
        raise ValidationError(
            _('SKU must be 6-12 characters long and contain only uppercase letters and numbers.')
        )

def validate_color_code(value: str) -> None:
    """
    Validate color hex code.
    
    Args:
        value: Color code to validate
        
    Raises:
        ValidationError: If color code is invalid
    """
    if not re.match(r'^#[0-9A-Fa-f]{6}$', value):
        raise ValidationError(
            _('Color code must be a valid hex color (e.g., #FF0000).')
        )

class ColorValidator(BaseValidator):
    """Validator for product colors."""
    
    def __init__(self) -> None:
        """Initialize validator."""
        super().__init__(COLORS.keys())
    
    def __call__(self, value: str) -> None:
        """
        Validate color.
        
        Args:
            value: Color to validate
            
        Raises:
            ValidationError: If color is invalid
        """
        if value not in COLORS:
            raise ValidationError(
                _('%(value)s is not a valid color. Choose from: %(valid_colors)s'),
                params={
                    'value': value,
                    'valid_colors': ', '.join(COLORS.keys())
                }
            )

class SizeValidator(BaseValidator):
    """Validator for product sizes."""
    
    def __init__(self, valid_sizes: list) -> None:
        """
        Initialize validator.
        
        Args:
            valid_sizes: List of valid sizes
        """
        super().__init__(valid_sizes)
    
    def __call__(self, value: str) -> None:
        """
        Validate size.
        
        Args:
            value: Size to validate
            
        Raises:
            ValidationError: If size is invalid
        """
        if value not in self.limit_value:
            raise ValidationError(
                _('%(value)s is not a valid size. Choose from: %(valid_sizes)s'),
                params={
                    'value': value,
                    'valid_sizes': ', '.join(self.limit_value)
                }
            )

def validate_review_text(value: str) -> None:
    """
    Validate review text.
    
    Args:
        value: Text to validate
        
    Raises:
        ValidationError: If text is invalid
    """
    if len(value) < MIN_REVIEW_LENGTH:
        raise ValidationError(
            _('Review must be at least %(min)d characters long.'),
            params={'min': MIN_REVIEW_LENGTH}
        )
    
    if len(value) > MAX_REVIEW_LENGTH:
        raise ValidationError(
            _('Review cannot exceed %(max)d characters.'),
            params={'max': MAX_REVIEW_LENGTH}
        )

def validate_review_title(value: str) -> None:
    """
    Validate review title.
    
    Args:
        value: Title to validate
        
    Raises:
        ValidationError: If title is invalid
    """
    if len(value) < MIN_REVIEW_TITLE_LENGTH:
        raise ValidationError(
            _('Title must be at least %(min)d characters long.'),
            params={'min': MIN_REVIEW_TITLE_LENGTH}
        )
    
    if len(value) > MAX_REVIEW_TITLE_LENGTH:
        raise ValidationError(
            _('Title cannot exceed %(max)d characters.'),
            params={'max': MAX_REVIEW_TITLE_LENGTH}
        )

def validate_meta_title(value: str) -> None:
    """
    Validate meta title.
    
    Args:
        value: Title to validate
        
    Raises:
        ValidationError: If title is invalid
    """
    if len(value) > 60:
        raise ValidationError(
            _('Meta title cannot exceed 60 characters.')
        )

def validate_meta_description(value: str) -> None:
    """
    Validate meta description.
    
    Args:
        value: Description to validate
        
    Raises:
        ValidationError: If description is invalid
    """
    if len(value) > 160:
        raise ValidationError(
            _('Meta description cannot exceed 160 characters.')
        )

def validate_slug(value: str) -> None:
    """
    Validate slug.
    
    Args:
        value: Slug to validate
        
    Raises:
        ValidationError: If slug is invalid
    """
    if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', value):
        raise ValidationError(
            _('Slug can only contain lowercase letters, numbers, and hyphens.')
        )

def validate_file_extension(value: Any, allowed_extensions: list) -> None:
    """
    Validate file extension.
    
    Args:
        value: File to validate
        allowed_extensions: List of allowed extensions
        
    Raises:
        ValidationError: If extension is invalid
    """
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in allowed_extensions:
        raise ValidationError(
            _('File type not supported. Allowed types: %(types)s'),
            params={'types': ', '.join(allowed_extensions)}
        )

def validate_dimensions(
    image: Any,
    min_width: Optional[int] = None,
    min_height: Optional[int] = None,
    max_width: Optional[int] = None,
    max_height: Optional[int] = None
) -> None:
    """
    Validate image dimensions.
    
    Args:
        image: Image to validate
        min_width: Minimum width
        min_height: Minimum height
        max_width: Maximum width
        max_height: Maximum height
        
    Raises:
        ValidationError: If dimensions are invalid
    """
    width, height = image.width, image.height
    
    if min_width and width < min_width:
        raise ValidationError(
            _('Image width must be at least %(min)dpx.'),
            params={'min': min_width}
        )
    
    if min_height and height < min_height:
        raise ValidationError(
            _('Image height must be at least %(min)dpx.'),
            params={'min': min_height}
        )
    
    if max_width and width > max_width:
        raise ValidationError(
            _('Image width cannot exceed %(max)dpx.'),
            params={'max': max_width}
        )
    
    if max_height and height > max_height:
        raise ValidationError(
            _('Image height cannot exceed %(max)dpx.'),
            params={'max': max_height}
        )
