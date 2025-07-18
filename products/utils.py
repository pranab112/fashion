"""
Utility functions for the products app.
"""

import os
import uuid
import re
from typing import Any, Dict, List, Optional, Tuple
from decimal import Decimal
from PIL import Image
from io import BytesIO
from django.core.files import File
from django.utils.text import slugify
from django.conf import settings
from django.utils import timezone
from django.core.files.storage import default_storage
from django.utils.translation import gettext_lazy as _

from .constants import (
    THUMBNAIL_SIZES,
    CURRENCY_SYMBOLS,
    DEFAULT_CURRENCY,
    CURRENCY_DECIMAL_PLACES
)

def generate_unique_slug(model_class: Any, title: str, instance_id: Optional[int] = None) -> str:
    """
    Generate unique slug for a model instance.
    
    Args:
        model_class: Model class
        title: Title to generate slug from
        instance_id: Instance ID to exclude from uniqueness check
        
    Returns:
        str: Unique slug
    """
    slug = slugify(title)
    unique_slug = slug
    counter = 1
    
    while True:
        if instance_id:
            exists = model_class.objects.filter(
                slug=unique_slug
            ).exclude(
                id=instance_id
            ).exists()
        else:
            exists = model_class.objects.filter(
                slug=unique_slug
            ).exists()
            
        if not exists:
            break
            
        unique_slug = f'{slug}-{counter}'
        counter += 1
    
    return unique_slug

def generate_sku() -> str:
    """
    Generate unique SKU.
    
    Returns:
        str: Unique SKU
    """
    return str(uuid.uuid4()).split('-')[0].upper()

def format_currency(
    amount: Decimal,
    currency: str = DEFAULT_CURRENCY,
    decimal_places: int = CURRENCY_DECIMAL_PLACES
) -> str:
    """
    Format currency amount.
    
    Args:
        amount: Amount to format
        currency: Currency code
        decimal_places: Number of decimal places
        
    Returns:
        str: Formatted currency string
    """
    symbol = CURRENCY_SYMBOLS.get(currency, '')
    formatted = '{:,.{prec}f}'.format(float(amount), prec=decimal_places)
    return f'{symbol}{formatted}'

def process_product_image(
    image: File,
    filename: str,
    sizes: Dict[str, Tuple[int, int]] = THUMBNAIL_SIZES
) -> Tuple[Dict[str, File], File]:
    """
    Process product image and generate thumbnails.
    
    Args:
        image: Image file
        filename: Original filename
        sizes: Dictionary of thumbnail sizes
        
    Returns:
        Tuple[Dict[str, File], File]: Thumbnails and primary image
    """
    # Open image
    img = Image.open(image)
    
    # Convert to RGB if necessary
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Generate thumbnails
    thumbnails = {}
    for size_name, dimensions in sizes.items():
        thumb = img.copy()
        thumb.thumbnail(dimensions)
        
        # Save thumbnail to BytesIO
        thumb_io = BytesIO()
        thumb.save(thumb_io, format='JPEG', quality=85)
        
        # Create Django file
        thumb_file = File(
            thumb_io,
            name=f'{os.path.splitext(filename)[0]}_{size_name}.jpg'
        )
        thumbnails[size_name] = thumb_file
    
    # Process primary image
    output_io = BytesIO()
    img.save(output_io, format='JPEG', quality=85)
    primary = File(
        output_io,
        name=f'{os.path.splitext(filename)[0]}.jpg'
    )
    
    return thumbnails, primary

def clean_search_query(query: str) -> str:
    """
    Clean search query.
    
    Args:
        query: Search query
        
    Returns:
        str: Cleaned query
    """
    # Remove special characters
    query = re.sub(r'[^\w\s-]', '', query)
    
    # Convert to lowercase
    query = query.lower()
    
    # Remove extra whitespace
    query = ' '.join(query.split())
    
    return query

def calculate_discount_percentage(original_price: Decimal, sale_price: Decimal) -> int:
    """
    Calculate discount percentage.
    
    Args:
        original_price: Original price
        sale_price: Sale price
        
    Returns:
        int: Discount percentage
    """
    if not original_price or not sale_price or sale_price >= original_price:
        return 0
    
    discount = ((original_price - sale_price) / original_price) * 100
    return int(round(discount))

def get_upload_path(instance: Any, filename: str) -> str:
    """
    Get upload path for file.
    
    Args:
        instance: Model instance
        filename: Original filename
        
    Returns:
        str: Upload path
    """
    # Get the file extension
    ext = filename.split('.')[-1]
    
    # Generate unique filename
    unique_filename = f'{uuid.uuid4().hex}.{ext}'
    
    # Get model name
    model_name = instance.__class__.__name__.lower()
    
    # Get current date
    now = timezone.now()
    date_path = now.strftime('%Y/%m/%d')
    
    return os.path.join('products', model_name, date_path, unique_filename)

def get_client_ip(request: Any) -> str:
    """
    Get client IP address.
    
    Args:
        request: HTTP request
        
    Returns:
        str: IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_page_range(page: int, num_pages: int, window: int = 5) -> List[Optional[int]]:
    """
    Get page range for pagination.
    
    Args:
        page: Current page number
        num_pages: Total number of pages
        window: Number of pages to show around current page
        
    Returns:
        List[Optional[int]]: Page range with None for ellipsis
    """
    if num_pages <= window + 6:
        return list(range(1, num_pages + 1))
    
    # Always include first and last pages
    pages = [1]
    
    # Add pages around current page
    start = max(2, page - window // 2)
    end = min(num_pages - 1, page + window // 2)
    
    # Add ellipsis if needed
    if start > 2:
        pages.append(None)
    
    pages.extend(range(start, end + 1))
    
    if end < num_pages - 1:
        pages.append(None)
    
    pages.append(num_pages)
    
    return pages

def format_file_size(size: int) -> str:
    """
    Format file size.
    
    Args:
        size: Size in bytes
        
    Returns:
        str: Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f'{size:.1f} {unit}'
        size /= 1024
    return f'{size:.1f} TB'

def is_valid_color_code(code: str) -> bool:
    """
    Check if color code is valid.
    
    Args:
        code: Color code
        
    Returns:
        bool: True if valid
    """
    if not code.startswith('#'):
        return False
    
    if len(code) != 7:
        return False
    
    try:
        int(code[1:], 16)
        return True
    except ValueError:
        return False

def parse_size_range(size_range: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Parse size range string.
    
    Args:
        size_range: Size range string (e.g., '10-12', '< 10', '> 12')
        
    Returns:
        Tuple[Optional[float], Optional[float]]: Min and max sizes
    """
    if not size_range:
        return None, None
    
    size_range = size_range.strip()
    
    if size_range.startswith('<'):
        return None, float(size_range[1:].strip())
    
    if size_range.startswith('>'):
        return float(size_range[1:].strip()), None
    
    if '-' in size_range:
        min_size, max_size = size_range.split('-')
        return float(min_size.strip()), float(max_size.strip())
    
    return float(size_range), float(size_range)

def get_breadcrumbs(category: Any) -> List[Dict[str, str]]:
    """
    Get category breadcrumbs.
    
    Args:
        category: Category instance
        
    Returns:
        List[Dict[str, str]]: Breadcrumb list
    """
    breadcrumbs = []
    current = category
    
    while current:
        breadcrumbs.append({
            'name': current.name,
            'url': current.get_absolute_url()
        })
        current = current.parent
    
    return list(reversed(breadcrumbs))

def clean_html(html: str) -> str:
    """
    Clean HTML content.
    
    Args:
        html: HTML content
        
    Returns:
        str: Cleaned HTML
    """
    import bleach
    
    allowed_tags = [
        'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'a', 'img', 'table', 'thead', 'tbody', 'tr', 'td', 'th'
    ]
    
    allowed_attributes = {
        'a': ['href', 'title'],
        'img': ['src', 'alt', 'title']
    }
    
    return bleach.clean(
        html,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True
    )
