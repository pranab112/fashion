"""
Security-related functionality for the products app.
"""

import logging
from typing import Any, Dict, List, Optional
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import hashlib
import hmac

logger = logging.getLogger(__name__)
User = get_user_model()

class ProductSecurity:
    """Security manager for product-related operations."""

    RATE_LIMIT_PREFIX = 'rate_limit'
    ABUSE_DETECTION_PREFIX = 'abuse_detection'
    
    @staticmethod
    def verify_product_access(
        user: Optional[User],
        product: Any
    ) -> bool:
        """
        Verify user's access to product.
        
        Args:
            user: User instance or None
            product: Product instance
            
        Returns:
            bool: True if access is allowed
            
        Raises:
            PermissionDenied: If access is not allowed
        """
        # Check if product is active
        if not product.is_active:
            if not (user and user.is_staff):
                raise PermissionDenied(_('This product is not available.'))
        
        # Check if product is in preview mode
        if getattr(product, 'is_preview', False):
            if not (user and user.is_staff):
                raise PermissionDenied(_('This product is in preview mode.'))
        
        # Check geographic restrictions
        if hasattr(settings, 'PRODUCT_GEO_RESTRICTIONS'):
            from .utils import get_user_country
            user_country = get_user_country()
            if user_country in product.restricted_countries:
                raise PermissionDenied(
                    _('This product is not available in your country.')
                )
        
        return True

    @classmethod
    def check_rate_limit(
        cls,
        request: HttpRequest,
        action: str,
        limit: int,
        period: int
    ) -> bool:
        """
        Check rate limiting for actions.
        
        Args:
            request: HTTP request
            action: Action identifier
            limit: Maximum attempts
            period: Time period in seconds
            
        Returns:
            bool: True if within limit
            
        Raises:
            PermissionDenied: If rate limit exceeded
        """
        client_ip = request.META.get('REMOTE_ADDR')
        cache_key = f"{cls.RATE_LIMIT_PREFIX}:{action}:{client_ip}"
        
        # Get current count
        count = cache.get(cache_key, 0)
        
        if count >= limit:
            raise PermissionDenied(
                _('Too many attempts. Please try again later.')
            )
        
        # Increment count
        cache.set(cache_key, count + 1, period)
        return True

    @classmethod
    def detect_abuse(
        cls,
        request: HttpRequest,
        action: str,
        threshold: int = 10
    ) -> bool:
        """
        Detect potential abuse patterns.
        
        Args:
            request: HTTP request
            action: Action identifier
            threshold: Abuse threshold
            
        Returns:
            bool: True if no abuse detected
            
        Raises:
            PermissionDenied: If abuse detected
        """
        client_ip = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Generate client fingerprint
        fingerprint = cls.generate_client_fingerprint(client_ip, user_agent)
        cache_key = f"{cls.ABUSE_DETECTION_PREFIX}:{action}:{fingerprint}"
        
        # Check patterns
        patterns = cache.get(cache_key, [])
        current_time = timezone.now()
        
        # Remove old patterns
        patterns = [p for p in patterns if p > current_time - timedelta(hours=1)]
        
        if len(patterns) >= threshold:
            raise PermissionDenied(_('Suspicious activity detected.'))
        
        # Add current timestamp
        patterns.append(current_time)
        cache.set(cache_key, patterns, 3600)  # 1 hour
        
        return True

    @staticmethod
    def generate_client_fingerprint(ip: str, user_agent: str) -> str:
        """
        Generate unique client fingerprint.
        
        Args:
            ip: Client IP address
            user_agent: User agent string
            
        Returns:
            str: Client fingerprint
        """
        key = settings.SECRET_KEY.encode()
        message = f"{ip}:{user_agent}".encode()
        
        return hmac.new(
            key,
            message,
            hashlib.sha256
        ).hexdigest()

    @staticmethod
    def sanitize_product_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize product data for security.
        
        Args:
            data: Product data dictionary
            
        Returns:
            Dict[str, Any]: Sanitized data
        """
        from django.utils.html import strip_tags
        
        # Fields to sanitize
        text_fields = ['name', 'description', 'meta_description']
        
        for field in text_fields:
            if field in data:
                # Strip HTML tags
                data[field] = strip_tags(data[field])
                
                # Limit length
                max_length = {
                    'name': 255,
                    'description': 5000,
                    'meta_description': 160
                }.get(field)
                
                if max_length:
                    data[field] = data[field][:max_length]
        
        return data

    @staticmethod
    def validate_image_security(file: Any) -> bool:
        """
        Validate image file security.
        
        Args:
            file: Uploaded file
            
        Returns:
            bool: True if image is safe
            
        Raises:
            ValidationError: If image is unsafe
        """
        from django.core.exceptions import ValidationError
        from PIL import Image
        import magic
        
        try:
            # Check file type
            mime = magic.from_buffer(file.read(1024), mime=True)
            file.seek(0)
            
            if mime not in ['image/jpeg', 'image/png', 'image/webp']:
                raise ValidationError(_('Invalid image format.'))
            
            # Check file size
            max_size = getattr(settings, 'PRODUCT_IMAGE_MAX_SIZE', 5 * 1024 * 1024)
            if file.size > max_size:
                raise ValidationError(_('Image file too large.'))
            
            # Verify image data
            img = Image.open(file)
            img.verify()
            
            return True
            
        except Exception as e:
            raise ValidationError(f"Image validation failed: {str(e)}")

class ReviewSecurity:
    """Security manager for review-related operations."""

    @staticmethod
    def verify_review_permission(
        user: User,
        product: Any
    ) -> bool:
        """
        Verify if user can review product.
        
        Args:
            user: User instance
            product: Product instance
            
        Returns:
            bool: True if allowed
            
        Raises:
            PermissionDenied: If not allowed
        """
        # Check if user has purchased the product
        has_purchased = user.orders.filter(
            items__product=product,
            status='completed'
        ).exists()
        
        if not has_purchased:
            raise PermissionDenied(
                _('You must purchase this product before reviewing it.')
            )
        
        # Check if user has already reviewed
        has_reviewed = product.reviews.filter(user=user).exists()
        
        if has_reviewed:
            raise PermissionDenied(
                _('You have already reviewed this product.')
            )
        
        return True

    @staticmethod
    def sanitize_review_content(content: str) -> str:
        """
        Sanitize review content.
        
        Args:
            content: Review content
            
        Returns:
            str: Sanitized content
        """
        from django.utils.html import strip_tags
        from bleach import clean
        
        # Strip HTML tags
        content = strip_tags(content)
        
        # Clean text
        content = clean(
            content,
            tags=[],
            strip=True
        )
        
        return content

def setup_security():
    """Set up security configuration."""
    try:
        # Verify security settings
        required_settings = [
            'PRODUCT_IMAGE_MAX_SIZE',
            'PRODUCT_GEO_RESTRICTIONS',
            'RATE_LIMIT_ENABLED'
        ]
        
        for setting in required_settings:
            if not hasattr(settings, setting):
                logger.warning(f"Missing security setting: {setting}")
        
        logger.info("Product security setup complete")
        
    except Exception as e:
        logger.error(f"Error setting up product security: {str(e)}")
        raise
