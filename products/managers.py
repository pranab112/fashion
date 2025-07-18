"""
Custom model managers for the products app.
"""

from typing import Any, Dict, List, Optional
from django.db.models import QuerySet
from django.db import models
from django.db.models import Q, F, Count, Avg, Sum
from django.utils import timezone
from django.core.cache import cache

class ProductQuerySet(models.QuerySet):
    """Custom queryset for Product model."""

    def active(self) -> 'ProductQuerySet':
        """Get active products."""
        return self.filter(is_active=True)

    def featured(self) -> 'ProductQuerySet':
        """Get featured products."""
        return self.filter(is_featured=True)

    def new_arrivals(self) -> 'ProductQuerySet':
        """Get new arrival products."""
        return self.filter(is_new_arrival=True)

    def on_sale(self) -> 'ProductQuerySet':
        """Get products on sale."""
        return self.filter(discount_percentage__gt=0)

    def in_stock(self) -> 'ProductQuerySet':
        """Get products in stock."""
        return self.filter(variants__stock__gt=0).distinct()

    def low_stock(self) -> 'ProductQuerySet':
        """Get products with low stock."""
        return self.filter(variants__stock__gt=0).annotate(
            total_stock=Sum('variants__stock')
        ).filter(total_stock__lte=10).distinct()

    def by_category(self, category_id: int) -> 'ProductQuerySet':
        """
        Get products by category.
        
        Args:
            category_id: Category ID
        """
        return self.filter(
            Q(category_id=category_id) |
            Q(category__parent_id=category_id)
        )

    def by_brand(self, brand_id: int) -> 'ProductQuerySet':
        """
        Get products by brand.
        
        Args:
            brand_id: Brand ID
        """
        return self.filter(brand_id=brand_id)

    def by_price_range(
        self,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> 'ProductQuerySet':
        """
        Get products within price range.
        
        Args:
            min_price: Minimum price
            max_price: Maximum price
        """
        queryset = self
        if min_price is not None:
            queryset = queryset.filter(base_price__gte=min_price)
        if max_price is not None:
            queryset = queryset.filter(base_price__lte=max_price)
        return queryset

    def by_rating(self, min_rating: float) -> 'ProductQuerySet':
        """
        Get products with minimum rating.
        
        Args:
            min_rating: Minimum rating
        """
        return self.filter(average_rating__gte=min_rating)

    def trending(self) -> 'ProductQuerySet':
        """Get trending products."""
        return self.order_by('-trending_score', '-view_count')

    def with_full_text_search(self, query: str) -> 'ProductQuerySet':
        """
        Get products matching search query.
        
        Args:
            query: Search query
        """
        return self.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(brand__name__icontains=query) |
            Q(category__name__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()

    def with_related(self) -> 'ProductQuerySet':
        """Get products with related data."""
        return self.select_related(
            'category',
            'brand'
        ).prefetch_related(
            'images',
            'tags',
            'reviews'
        )

class ProductManager(models.Manager):
    """Custom manager for Product model."""

    def get_queryset(self) -> ProductQuerySet:
        """Get custom queryset."""
        return ProductQuerySet(self.model, using=self._db)

    def active(self) -> ProductQuerySet:
        """Get active products."""
        return self.get_queryset().active()

    def featured(self) -> ProductQuerySet:
        """Get featured products."""
        return self.get_queryset().featured()

    def new_arrivals(self) -> ProductQuerySet:
        """Get new arrival products."""
        return self.get_queryset().new_arrivals()

    def on_sale(self) -> ProductQuerySet:
        """Get products on sale."""
        return self.get_queryset().on_sale()

    def in_stock(self) -> ProductQuerySet:
        """Get products in stock."""
        return self.get_queryset().in_stock()

    def low_stock(self) -> ProductQuerySet:
        """Get products with low stock."""
        return self.get_queryset().low_stock()

    def by_category(self, category_id: int) -> ProductQuerySet:
        """Get products by category."""
        return self.get_queryset().by_category(category_id)

    def by_brand(self, brand_id: int) -> ProductQuerySet:
        """Get products by brand."""
        return self.get_queryset().by_brand(brand_id)

    def by_price_range(
        self,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> ProductQuerySet:
        """Get products within price range."""
        return self.get_queryset().by_price_range(min_price, max_price)

    def by_rating(self, min_rating: float) -> ProductQuerySet:
        """Get products with minimum rating."""
        return self.get_queryset().by_rating(min_rating)

    def trending(self) -> ProductQuerySet:
        """Get trending products."""
        return self.get_queryset().trending()

    def search(self, query: str) -> ProductQuerySet:
        """Search products."""
        return self.get_queryset().with_full_text_search(query)

    def with_related(self) -> ProductQuerySet:
        """Get products with related data."""
        return self.get_queryset().with_related()

class CategoryQuerySet(models.QuerySet):
    """Custom queryset for Category model."""

    def active(self) -> 'CategoryQuerySet':
        """Get active categories."""
        return self.filter(is_active=True)

    def root_nodes(self) -> 'CategoryQuerySet':
        """Get root categories."""
        return self.filter(parent=None)

    def with_products_count(self) -> 'CategoryQuerySet':
        """Get categories with products count."""
        return self.annotate(products_count=Count('products'))

    def with_tree_path(self) -> 'CategoryQuerySet':
        """Get categories with tree path."""
        return self.annotate(
            tree_path=models.F('name'),
            depth=models.Value(0, output_field=models.IntegerField())
        )

class CategoryManager(models.Manager):
    """Custom manager for Category model."""

    def get_queryset(self) -> CategoryQuerySet:
        """Get custom queryset."""
        return CategoryQuerySet(self.model, using=self._db)

    def active(self) -> CategoryQuerySet:
        """Get active categories."""
        return self.get_queryset().active()

    def root_nodes(self) -> CategoryQuerySet:
        """Get root categories."""
        return self.get_queryset().root_nodes()

    def with_products_count(self) -> CategoryQuerySet:
        """Get categories with products count."""
        return self.get_queryset().with_products_count()

    def with_tree_path(self) -> CategoryQuerySet:
        """Get categories with tree path."""
        return self.get_queryset().with_tree_path()

class BrandQuerySet(models.QuerySet):
    """Custom queryset for Brand model."""

    def active(self) -> 'BrandQuerySet':
        """Get active brands."""
        return self.filter(is_active=True)

    def with_products_count(self) -> 'BrandQuerySet':
        """Get brands with products count."""
        return self.annotate(products_count=Count('products'))

class BrandManager(models.Manager):
    """Custom manager for Brand model."""

    def get_queryset(self) -> BrandQuerySet:
        """Get custom queryset."""
        return BrandQuerySet(self.model, using=self._db)

    def active(self) -> BrandQuerySet:
        """Get active brands."""
        return self.get_queryset().active()

    def with_products_count(self) -> BrandQuerySet:
        """Get brands with products count."""
        return self.get_queryset().with_products_count()

class ReviewQuerySet(models.QuerySet):
    """Custom queryset for Review model."""

    def verified(self) -> 'ReviewQuerySet':
        """Get verified reviews."""
        return self.filter(is_verified=True)

    def by_rating(self, rating: int) -> 'ReviewQuerySet':
        """
        Get reviews by rating.
        
        Args:
            rating: Rating value
        """
        return self.filter(rating=rating)

    def recent(self) -> 'ReviewQuerySet':
        """Get recent reviews."""
        return self.order_by('-created_at')

class ReviewManager(models.Manager):
    """Custom manager for Review model."""

    def get_queryset(self) -> ReviewQuerySet:
        """Get custom queryset."""
        return ReviewQuerySet(self.model, using=self._db)

    def verified(self) -> ReviewQuerySet:
        """Get verified reviews."""
        return self.get_queryset().verified()

    def by_rating(self, rating: int) -> ReviewQuerySet:
        """Get reviews by rating."""
        return self.get_queryset().by_rating(rating)

    def recent(self) -> ReviewQuerySet:
        """Get recent reviews."""
        return self.get_queryset().recent()
