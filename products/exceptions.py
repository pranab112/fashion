"""
Custom exceptions for the products app.
"""

from typing import Any, Optional
from django.utils.translation import gettext_lazy as _

class ProductError(Exception):
    """Base exception for product-related errors."""
    
    def __init__(self, message: str = None) -> None:
        """
        Initialize exception.
        
        Args:
            message: Error message
        """
        self.message = message or _('An error occurred with the product.')
        super().__init__(self.message)

class ProductNotFoundError(ProductError):
    """Exception raised when a product is not found."""
    
    def __init__(self, product_id: Any = None) -> None:
        """
        Initialize exception.
        
        Args:
            product_id: ID of product that wasn't found
        """
        message = _('Product not found.')
        if product_id:
            message = _(f'Product with ID {product_id} not found.')
        super().__init__(message)

class InvalidProductDataError(ProductError):
    """Exception raised when product data is invalid."""
    
    def __init__(self, field: Optional[str] = None) -> None:
        """
        Initialize exception.
        
        Args:
            field: Name of invalid field
        """
        message = _('Invalid product data.')
        if field:
            message = _(f'Invalid product data: {field}')
        super().__init__(message)

class ProductOutOfStockError(ProductError):
    """Exception raised when a product is out of stock."""
    
    def __init__(self, product_name: Optional[str] = None) -> None:
        """
        Initialize exception.
        
        Args:
            product_name: Name of out-of-stock product
        """
        message = _('Product is out of stock.')
        if product_name:
            message = _(f'{product_name} is out of stock.')
        super().__init__(message)

class InsufficientStockError(ProductError):
    """Exception raised when there is insufficient stock."""
    
    def __init__(
        self,
        product_name: Optional[str] = None,
        requested: Optional[int] = None,
        available: Optional[int] = None
    ) -> None:
        """
        Initialize exception.
        
        Args:
            product_name: Name of product
            requested: Requested quantity
            available: Available quantity
        """
        message = _('Insufficient stock available.')
        if all([product_name, requested, available]):
            message = _(
                f'Insufficient stock for {product_name}. '
                f'Requested: {requested}, Available: {available}'
            )
        super().__init__(message)

class ImageProcessingError(ProductError):
    """Exception raised when processing product images."""
    
    def __init__(self, filename: str, error: str) -> None:
        """
        Initialize exception.
        
        Args:
            filename: Name of file that caused error
            error: Error description
        """
        message = _(f'Error processing image {filename}: {error}')
        super().__init__(message)

class InvalidImageError(ProductError):
    """Exception raised when an image is invalid."""
    
    def __init__(self, reason: str) -> None:
        """
        Initialize exception.
        
        Args:
            reason: Reason image is invalid
        """
        message = _(f'Invalid image: {reason}')
        super().__init__(message)

class CategoryError(ProductError):
    """Base exception for category-related errors."""
    
    def __init__(self, message: Optional[str] = None) -> None:
        """
        Initialize exception.
        
        Args:
            message: Error message
        """
        self.message = message or _('An error occurred with the category.')
        super().__init__(self.message)

class CategoryNotFoundError(CategoryError):
    """Exception raised when a category is not found."""
    
    def __init__(self, category_id: Optional[Any] = None) -> None:
        """
        Initialize exception.
        
        Args:
            category_id: ID of category that wasn't found
        """
        message = _('Category not found.')
        if category_id:
            message = _(f'Category with ID {category_id} not found.')
        super().__init__(message)

class BrandError(ProductError):
    """Base exception for brand-related errors."""
    
    def __init__(self, message: Optional[str] = None) -> None:
        """
        Initialize exception.
        
        Args:
            message: Error message
        """
        self.message = message or _('An error occurred with the brand.')
        super().__init__(self.message)

class BrandNotFoundError(BrandError):
    """Exception raised when a brand is not found."""
    
    def __init__(self, brand_id: Optional[Any] = None) -> None:
        """
        Initialize exception.
        
        Args:
            brand_id: ID of brand that wasn't found
        """
        message = _('Brand not found.')
        if brand_id:
            message = _(f'Brand with ID {brand_id} not found.')
        super().__init__(message)

class ReviewError(ProductError):
    """Base exception for review-related errors."""
    
    def __init__(self, message: Optional[str] = None) -> None:
        """
        Initialize exception.
        
        Args:
            message: Error message
        """
        self.message = message or _('An error occurred with the review.')
        super().__init__(self.message)

class DuplicateReviewError(ReviewError):
    """Exception raised when a user tries to submit multiple reviews."""
    
    def __init__(self) -> None:
        """Initialize exception."""
        message = _('You have already reviewed this product.')
        super().__init__(message)

class ReviewNotAllowedError(ReviewError):
    """Exception raised when a user is not allowed to review."""
    
    def __init__(self) -> None:
        """Initialize exception."""
        message = _('You must purchase this product before reviewing it.')
        super().__init__(message)

class SearchError(ProductError):
    """Base exception for search-related errors."""
    
    def __init__(self, message: Optional[str] = None) -> None:
        """
        Initialize exception.
        
        Args:
            message: Error message
        """
        self.message = message or _('An error occurred during search.')
        super().__init__(self.message)

class InvalidSearchQueryError(SearchError):
    """Exception raised when a search query is invalid."""
    
    def __init__(self, query: str) -> None:
        """
        Initialize exception.
        
        Args:
            query: Invalid search query
        """
        message = _(f'Invalid search query: {query}')
        super().__init__(message)

class CacheError(ProductError):
    """Base exception for cache-related errors."""
    
    def __init__(self, message: Optional[str] = None) -> None:
        """
        Initialize exception.
        
        Args:
            message: Error message
        """
        self.message = message or _('An error occurred with the cache.')
        super().__init__(self.message)

class ImportError(ProductError):
    """Base exception for import-related errors."""
    
    def __init__(self, message: Optional[str] = None) -> None:
        """
        Initialize exception.
        
        Args:
            message: Error message
        """
        self.message = message or _('An error occurred during import.')
        super().__init__(self.message)

class ExportError(ProductError):
    """Base exception for export-related errors."""
    
    def __init__(self, message: Optional[str] = None) -> None:
        """
        Initialize exception.
        
        Args:
            message: Error message
        """
        self.message = message or _('An error occurred during export.')
        super().__init__(self.message)
