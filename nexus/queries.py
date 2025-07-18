from django.db.models import Q, F, Count, Sum, Avg, Min, Max
from django.db.models.functions import ExtractMonth, ExtractYear, Coalesce
from django.utils import timezone
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal

class ProductQueries:
    """Query builder for product-related queries."""

    @staticmethod
    def search_products(
        query: str,
        category_id: Optional[int] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        brand_ids: Optional[List[int]] = None,
        sizes: Optional[List[str]] = None,
        colors: Optional[List[str]] = None,
        in_stock: Optional[bool] = None
    ) -> Q:
        """Build product search query."""
        filters = Q()

        # Search in name and description
        if query:
            filters &= (
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(brand__name__icontains=query)
            )

        # Category filter
        if category_id:
            filters &= (
                Q(category_id=category_id) |
                Q(category__parent_id=category_id)
            )

        # Price range filter
        if min_price is not None:
            filters &= Q(price__gte=min_price)
        if max_price is not None:
            filters &= Q(price__lte=max_price)

        # Brand filter
        if brand_ids:
            filters &= Q(brand_id__in=brand_ids)

        # Size and color filters
        if sizes:
            filters &= Q(variants__size__in=sizes)
        if colors:
            filters &= Q(variants__color__in=colors)

        # Stock filter
        if in_stock is not None:
            if in_stock:
                filters &= Q(stock_quantity__gt=0)
            else:
                filters &= Q(stock_quantity=0)

        return filters

    @staticmethod
    def get_trending_products(days: int = 7, limit: int = 10) -> Q:
        """Get trending products query."""
        date_threshold = timezone.now() - timedelta(days=days)
        return (
            Q(order_items__order__created_at__gte=date_threshold) &
            Q(order_items__order__status='completed')
        )

    @staticmethod
    def get_related_products(product_id: int, limit: int = 4) -> Q:
        """Get related products query."""
        from products.models import Product
        product = Product.objects.get(id=product_id)
        
        return (
            Q(category=product.category) &
            ~Q(id=product_id)
        )

class OrderQueries:
    """Query builder for order-related queries."""

    @staticmethod
    def get_user_orders(
        user_id: int,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Q:
        """Build user orders query."""
        filters = Q(user_id=user_id)

        if status:
            filters &= Q(status=status)

        if start_date:
            filters &= Q(created_at__gte=start_date)
        if end_date:
            filters &= Q(created_at__lte=end_date)

        return filters

    @staticmethod
    def get_sales_metrics(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get sales metrics query."""
        filters = Q(status='completed')

        if start_date:
            filters &= Q(created_at__gte=start_date)
        if end_date:
            filters &= Q(created_at__lte=end_date)

        return {
            'filters': filters,
            'annotations': {
                'total_sales': Sum('total_amount'),
                'avg_order_value': Avg('total_amount'),
                'orders_count': Count('id'),
                'items_sold': Sum('items__quantity')
            }
        }

    @staticmethod
    def get_monthly_sales(year: int) -> Dict[str, Any]:
        """Get monthly sales query."""
        return {
            'filters': Q(
                status='completed',
                created_at__year=year
            ),
            'annotations': {
                'month': ExtractMonth('created_at'),
                'total_sales': Sum('total_amount'),
                'orders_count': Count('id')
            }
        }

class UserQueries:
    """Query builder for user-related queries."""

    @staticmethod
    def get_active_users(days: int = 30) -> Q:
        """Get active users query."""
        date_threshold = timezone.now() - timedelta(days=days)
        return Q(last_login__gte=date_threshold)

    @staticmethod
    def get_customer_metrics(user_id: int) -> Dict[str, Any]:
        """Get customer metrics query."""
        return {
            'filters': Q(id=user_id),
            'annotations': {
                'total_orders': Count('orders'),
                'total_spent': Sum('orders__total_amount'),
                'avg_order_value': Avg('orders__total_amount'),
                'wishlist_count': Count('wishlist__products')
            }
        }

class AnalyticsQueries:
    """Query builder for analytics-related queries."""

    @staticmethod
    def get_product_performance(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get product performance query."""
        filters = Q(order_items__order__status='completed')

        if start_date:
            filters &= Q(order_items__order__created_at__gte=start_date)
        if end_date:
            filters &= Q(order_items__order__created_at__lte=end_date)

        return {
            'filters': filters,
            'annotations': {
                'revenue': Sum('order_items__total_price'),
                'units_sold': Sum('order_items__quantity'),
                'orders_count': Count('order_items__order', distinct=True),
                'avg_rating': Avg('reviews__rating')
            }
        }

    @staticmethod
    def get_category_performance() -> Dict[str, Any]:
        """Get category performance query."""
        return {
            'filters': Q(products__order_items__order__status='completed'),
            'annotations': {
                'revenue': Sum('products__order_items__total_price'),
                'units_sold': Sum('products__order_items__quantity'),
                'products_count': Count('products', distinct=True),
                'avg_product_rating': Avg('products__reviews__rating')
            }
        }

class InventoryQueries:
    """Query builder for inventory-related queries."""

    @staticmethod
    def get_low_stock_products(threshold: Optional[int] = None) -> Q:
        """Get low stock products query."""
        if threshold is None:
            return Q(
                stock_quantity__gt=0,
                stock_quantity__lte=F('low_stock_threshold')
            )
        return Q(stock_quantity__lte=threshold)

    @staticmethod
    def get_stock_value() -> Dict[str, Any]:
        """Get stock value query."""
        return {
            'annotations': {
                'total_value': Sum(F('stock_quantity') * F('price')),
                'avg_unit_value': Avg('price'),
                'total_units': Sum('stock_quantity')
            }
        }

class CartQueries:
    """Query builder for cart-related queries."""

    @staticmethod
    def get_abandoned_carts(hours: int = 24) -> Q:
        """Get abandoned carts query."""
        threshold = timezone.now() - timedelta(hours=hours)
        return (
            Q(status='active') &
            Q(updated_at__lt=threshold) &
            Q(items__isnull=False)
        )

    @staticmethod
    def get_cart_metrics() -> Dict[str, Any]:
        """Get cart metrics query."""
        return {
            'annotations': {
                'total_value': Sum(F('items__quantity') * F('items__product__price')),
                'items_count': Sum('items__quantity'),
                'avg_value': Avg(F('items__quantity') * F('items__product__price'))
            }
        }

class ReviewQueries:
    """Query builder for review-related queries."""

    @staticmethod
    def get_product_reviews(
        product_id: int,
        rating: Optional[int] = None,
        verified_only: bool = False
    ) -> Q:
        """Get product reviews query."""
        filters = Q(product_id=product_id, status='approved')

        if rating:
            filters &= Q(rating=rating)

        if verified_only:
            filters &= Q(user__orders__items__product_id=product_id)

        return filters

    @staticmethod
    def get_review_metrics(product_id: int) -> Dict[str, Any]:
        """Get review metrics query."""
        return {
            'filters': Q(product_id=product_id, status='approved'),
            'annotations': {
                'avg_rating': Avg('rating'),
                'total_reviews': Count('id'),
                'rating_distribution': Count('rating')
            }
        }
