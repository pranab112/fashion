"""
Service classes for the products app.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union
from decimal import Decimal
from django.db.models import Q, F, Count, Avg, Sum
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings
from django.core.files import File
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import (
    Product,
    Category,
    Brand,
    ProductImage,
    Review,
    SearchQuery,
    ProductView
)
from .utils import (
    process_product_image,
    clean_search_query,
    calculate_discount_percentage
)
from .exceptions import (
    ProductNotFoundError,
    ProductOutOfStockError,
    InsufficientStockError,
    InvalidProductDataError
)

logger = logging.getLogger(__name__)

class ProductService:
    """Service class for product-related operations."""

    @staticmethod
    def create_product(data: Dict[str, Any], images: List[File] = None) -> Product:
        """
        Create new product.
        
        Args:
            data: Product data
            images: List of image files
            
        Returns:
            Product: Created product
            
        Raises:
            InvalidProductDataError: If data is invalid
        """
        try:
            # Create product
            product = Product.objects.create(**data)
            
            # Process images
            if images:
                for image in images:
                    thumbnails, primary = process_product_image(
                        image,
                        image.name
                    )
                    
                    # Create product image
                    product_image = ProductImage.objects.create(
                        product=product,
                        image=primary,
                        is_primary=not product.images.exists()
                    )
                    
                    # Create thumbnails
                    for size, thumb in thumbnails.items():
                        product_image.thumbnails.create(
                            size=size,
                            image=thumb
                        )
            
            return product
            
        except ValidationError as e:
            raise InvalidProductDataError(e.message_dict)
        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            raise

    @staticmethod
    def update_product(
        product: Product,
        data: Dict[str, Any],
        images: List[File] = None
    ) -> Product:
        """
        Update product.
        
        Args:
            product: Product instance
            data: Updated data
            images: New image files
            
        Returns:
            Product: Updated product
            
        Raises:
            InvalidProductDataError: If data is invalid
        """
        try:
            # Update product fields
            for key, value in data.items():
                setattr(product, key, value)
            
            product.save()
            
            # Process new images
            if images:
                for image in images:
                    thumbnails, primary = process_product_image(
                        image,
                        image.name
                    )
                    
                    # Create product image
                    product_image = ProductImage.objects.create(
                        product=product,
                        image=primary,
                        is_primary=not product.images.exists()
                    )
                    
                    # Create thumbnails
                    for size, thumb in thumbnails.items():
                        product_image.thumbnails.create(
                            size=size,
                            image=thumb
                        )
            
            return product
            
        except ValidationError as e:
            raise InvalidProductDataError(e.message_dict)
        except Exception as e:
            logger.error(f"Error updating product: {str(e)}")
            raise

    @staticmethod
    def delete_product(product: Product) -> None:
        """
        Delete product.
        
        Args:
            product: Product instance
        """
        try:
            product.delete()
        except Exception as e:
            logger.error(f"Error deleting product: {str(e)}")
            raise

    @staticmethod
    def search_products(query: str, filters: Dict[str, Any] = None) -> List[Product]:
        """
        Search products.
        
        Args:
            query: Search query
            filters: Optional filters
            
        Returns:
            List[Product]: Search results
        """
        try:
            # Clean query
            query = clean_search_query(query)
            
            # Track search query
            SearchQuery.objects.update_search(query)
            
            # Build search filter
            search_filter = Q(name__icontains=query) | \
                          Q(description__icontains=query) | \
                          Q(brand__name__icontains=query) | \
                          Q(category__name__icontains=query) | \
                          Q(tags__name__icontains=query)
            
            # Apply additional filters
            queryset = Product.objects.filter(
                search_filter,
                is_active=True
            ).distinct()
            
            if filters:
                queryset = ProductService.apply_filters(queryset, filters)
            
            return queryset
            
        except Exception as e:
            logger.error(f"Error searching products: {str(e)}")
            return []

    @staticmethod
    def apply_filters(queryset: Any, filters: Dict[str, Any]) -> Any:
        """
        Apply filters to queryset.
        
        Args:
            queryset: Product queryset
            filters: Filter parameters
            
        Returns:
            Any: Filtered queryset
        """
        # Category filter
        if category_id := filters.get('category'):
            queryset = queryset.filter(
                Q(category_id=category_id) |
                Q(category__parent_id=category_id)
            )
        
        # Brand filter
        if brand_id := filters.get('brand'):
            queryset = queryset.filter(brand_id=brand_id)
        
        # Price range filter
        if min_price := filters.get('min_price'):
            queryset = queryset.filter(price__gte=min_price)
        if max_price := filters.get('max_price'):
            queryset = queryset.filter(price__lte=max_price)
        
        # Size filter
        if sizes := filters.get('sizes', []):
            queryset = queryset.filter(available_sizes__in=sizes)
        
        # Color filter
        if colors := filters.get('colors', []):
            queryset = queryset.filter(available_colors__in=colors)
        
        # Tag filter
        if tags := filters.get('tags', []):
            queryset = queryset.filter(tags__in=tags)
        
        # Rating filter
        if min_rating := filters.get('min_rating'):
            queryset = queryset.filter(average_rating__gte=min_rating)
        
        # Stock filter
        if filters.get('in_stock'):
            queryset = queryset.filter(stock__gt=0)
        
        # Sale filter
        if filters.get('on_sale'):
            queryset = queryset.filter(is_on_sale=True)
        
        # Sort filter
        if sort := filters.get('sort'):
            if sort == 'price_asc':
                queryset = queryset.order_by('price')
            elif sort == 'price_desc':
                queryset = queryset.order_by('-price')
            elif sort == 'name_asc':
                queryset = queryset.order_by('name')
            elif sort == 'name_desc':
                queryset = queryset.order_by('-name')
            elif sort == 'newest':
                queryset = queryset.order_by('-created_at')
            elif sort == 'popular':
                queryset = queryset.order_by('-view_count')
            elif sort == 'rating':
                queryset = queryset.order_by('-average_rating')
        
        return queryset

    @staticmethod
    def track_product_view(
        product: Product,
        user: Optional[Any] = None,
        session_key: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        referrer: Optional[str] = None
    ) -> None:
        """
        Track product view.
        
        Args:
            product: Product instance
            user: User instance
            session_key: Session key
            ip_address: IP address
            user_agent: User agent string
            referrer: Referrer URL
        """
        try:
            ProductView.objects.create(
                product=product,
                user=user,
                session_key=session_key,
                ip_address=ip_address,
                user_agent=user_agent,
                referrer=referrer
            )
            
            # Update view count
            Product.objects.filter(id=product.id).update(
                view_count=F('view_count') + 1
            )
            
        except Exception as e:
            logger.error(f"Error tracking product view: {str(e)}")

    @staticmethod
    def get_related_products(product: Product, limit: int = 4) -> List[Product]:
        """
        Get related products.
        
        Args:
            product: Product instance
            limit: Number of products to return
            
        Returns:
            List[Product]: Related products
        """
        try:
            return Product.objects.filter(
                Q(category=product.category) |
                Q(brand=product.brand) |
                Q(tags__in=product.tags.all())
            ).exclude(
                id=product.id
            ).distinct()[:limit]
            
        except Exception as e:
            logger.error(f"Error getting related products: {str(e)}")
            return []

    @staticmethod
    def get_popular_searches(limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get popular search queries.
        
        Args:
            limit: Number of queries to return
            
        Returns:
            List[Dict[str, Any]]: Popular searches
        """
        try:
            return SearchQuery.objects.order_by(
                '-count'
            ).values(
                'query',
                'count'
            )[:limit]
            
        except Exception as e:
            logger.error(f"Error getting popular searches: {str(e)}")
            return []

    @staticmethod
    def check_stock(product: Product, quantity: int) -> None:
        """
        Check product stock.
        
        Args:
            product: Product instance
            quantity: Requested quantity
            
        Raises:
            ProductOutOfStockError: If product is out of stock
            InsufficientStockError: If requested quantity exceeds available stock
        """
        if product.stock == 0:
            raise ProductOutOfStockError(product)
            
        if quantity > product.stock:
            raise InsufficientStockError(
                product,
                quantity,
                product.stock
            )
