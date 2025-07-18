"""
Complex database queries for the products app.
"""

from typing import Any, Dict, List, Optional, Tuple
from django.db.models import (
    Q,
    F,
    Count,
    Avg,
    Sum,
    Min,
    Max,
    ExpressionWrapper,
    DecimalField,
    IntegerField,
    Case,
    When,
    Value,
    Window,
    DateTimeField
)
from django.db.models.functions import (
    Coalesce,
    ExtractMonth,
    ExtractYear,
    TruncDate,
    TruncMonth,
    Now
)
from django.utils import timezone
from datetime import datetime, timedelta

from .models import (
    Product,
    Category,
    Brand,
    Review,
    ProductView,
    SearchQuery
)

class ProductQueries:
    """Complex queries for Product model."""

    @staticmethod
    def get_trending_products(
        days: int = 7,
        limit: int = 10
    ) -> List[Product]:
        """
        Get trending products based on views and sales.
        
        Args:
            days: Time period in days
            limit: Number of products to return
            
        Returns:
            List[Product]: Trending products
        """
        cutoff = timezone.now() - timedelta(days=days)
        
        return Product.objects.filter(
            is_active=True
        ).annotate(
            recent_views=Count(
                'productview',
                filter=Q(productview__created_at__gte=cutoff)
            ),
            recent_sales=Sum(
                'orderitem__quantity',
                filter=Q(
                    orderitem__order__created_at__gte=cutoff,
                    orderitem__order__status='completed'
                )
            ),
            trend_score=ExpressionWrapper(
                F('recent_views') * 0.4 + Coalesce(F('recent_sales'), 0) * 0.6,
                output_field=DecimalField()
            )
        ).order_by(
            '-trend_score',
            '-created_at'
        )[:limit]

    @staticmethod
    def get_best_selling_products(
        period: str = 'month',
        limit: int = 10
    ) -> List[Product]:
        """
        Get best selling products.
        
        Args:
            period: Time period ('week', 'month', 'year')
            limit: Number of products to return
            
        Returns:
            List[Product]: Best selling products
        """
        if period == 'week':
            cutoff = timezone.now() - timedelta(days=7)
        elif period == 'month':
            cutoff = timezone.now() - timedelta(days=30)
        else:  # year
            cutoff = timezone.now() - timedelta(days=365)
        
        return Product.objects.filter(
            is_active=True,
            orderitem__order__created_at__gte=cutoff,
            orderitem__order__status='completed'
        ).annotate(
            total_quantity=Sum('orderitem__quantity'),
            total_revenue=Sum(
                F('orderitem__quantity') * F('orderitem__price'),
                output_field=DecimalField()
            )
        ).order_by(
            '-total_quantity',
            '-total_revenue'
        )[:limit]

    @staticmethod
    def get_price_range_stats() -> Dict[str, Any]:
        """
        Get product price range statistics.
        
        Returns:
            Dict[str, Any]: Price statistics
        """
        return Product.objects.filter(
            is_active=True
        ).aggregate(
            min_price=Min('price'),
            max_price=Max('price'),
            avg_price=Avg('price'),
            total_products=Count('id'),
            total_value=Sum('price')
        )

    @staticmethod
    def get_category_performance(
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get category performance metrics.
        
        Args:
            days: Time period in days
            
        Returns:
            List[Dict[str, Any]]: Category metrics
        """
        cutoff = timezone.now() - timedelta(days=days)
        
        return Category.objects.filter(
            is_active=True
        ).annotate(
            product_count=Count(
                'products',
                filter=Q(products__is_active=True)
            ),
            total_views=Count(
                'products__productview',
                filter=Q(products__productview__created_at__gte=cutoff)
            ),
            total_sales=Sum(
                'products__orderitem__quantity',
                filter=Q(
                    products__orderitem__order__created_at__gte=cutoff,
                    products__orderitem__order__status='completed'
                )
            ),
            total_revenue=Sum(
                F('products__orderitem__quantity') * F('products__orderitem__price'),
                filter=Q(
                    products__orderitem__order__created_at__gte=cutoff,
                    products__orderitem__order__status='completed'
                ),
                output_field=DecimalField()
            ),
            average_rating=Avg(
                'products__reviews__rating',
                filter=Q(products__reviews__is_verified=True)
            )
        ).order_by('-total_revenue')

    @staticmethod
    def get_monthly_sales_trend(
        months: int = 12
    ) -> List[Dict[str, Any]]:
        """
        Get monthly sales trend.
        
        Args:
            months: Number of months
            
        Returns:
            List[Dict[str, Any]]: Monthly sales data
        """
        cutoff = timezone.now() - timedelta(days=months * 30)
        
        return Product.objects.filter(
            orderitem__order__created_at__gte=cutoff,
            orderitem__order__status='completed'
        ).annotate(
            month=TruncMonth('orderitem__order__created_at')
        ).values(
            'month'
        ).annotate(
            total_sales=Sum('orderitem__quantity'),
            total_revenue=Sum(
                F('orderitem__quantity') * F('orderitem__price'),
                output_field=DecimalField()
            ),
            unique_customers=Count(
                'orderitem__order__user',
                distinct=True
            )
        ).order_by('month')

    @staticmethod
    def get_stock_alerts() -> List[Dict[str, Any]]:
        """
        Get stock alert data.
        
        Returns:
            List[Dict[str, Any]]: Stock alerts
        """
        return Product.objects.filter(
            is_active=True
        ).annotate(
            days_until_stockout=Case(
                When(
                    total_sales__gt=0,
                    then=ExpressionWrapper(
                        F('stock') / (F('total_sales') / 30),
                        output_field=IntegerField()
                    )
                ),
                default=Value(999),
                output_field=IntegerField()
            )
        ).filter(
            Q(stock__lte=F('low_stock_threshold')) |
            Q(days_until_stockout__lte=14)
        ).order_by(
            'days_until_stockout',
            'stock'
        )

    @staticmethod
    def get_review_analytics() -> Dict[str, Any]:
        """
        Get review analytics.
        
        Returns:
            Dict[str, Any]: Review statistics
        """
        return Review.objects.filter(
            is_verified=True
        ).aggregate(
            total_reviews=Count('id'),
            average_rating=Avg('rating'),
            rating_distribution=Count(
                'id',
                filter=Q(rating__gte=1),
                output_field=IntegerField()
            ),
            recent_reviews=Count(
                'id',
                filter=Q(
                    created_at__gte=timezone.now() - timedelta(days=30)
                )
            ),
            verified_percentage=ExpressionWrapper(
                Count(
                    'id',
                    filter=Q(is_verified=True)
                ) * 100.0 / Count('id'),
                output_field=DecimalField()
            )
        )

    @staticmethod
    def get_search_analytics(
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get search analytics.
        
        Args:
            days: Time period in days
            
        Returns:
            List[Dict[str, Any]]: Search statistics
        """
        cutoff = timezone.now() - timedelta(days=days)
        
        return SearchQuery.objects.filter(
            last_searched__gte=cutoff
        ).annotate(
            success_rate=ExpressionWrapper(
                Count(
                    'searchresult',
                    filter=Q(searchresult__clicked=True)
                ) * 100.0 / Count('searchresult'),
                output_field=DecimalField()
            )
        ).values(
            'query',
            'count',
            'success_rate'
        ).order_by('-count')

    @staticmethod
    def get_product_performance(
        product: Product,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get detailed product performance metrics.
        
        Args:
            product: Product instance
            days: Time period in days
            
        Returns:
            Dict[str, Any]: Performance metrics
        """
        cutoff = timezone.now() - timedelta(days=days)
        
        views = ProductView.objects.filter(
            product=product,
            created_at__gte=cutoff
        )
        
        return {
            'total_views': views.count(),
            'unique_views': views.values('session_key').distinct().count(),
            'conversion_rate': ExpressionWrapper(
                Count(
                    'orderitem',
                    filter=Q(
                        orderitem__order__created_at__gte=cutoff,
                        orderitem__order__status='completed'
                    )
                ) * 100.0 / Count('productview'),
                output_field=DecimalField()
            ),
            'average_order_value': Avg(
                F('orderitem__quantity') * F('orderitem__price'),
                filter=Q(
                    orderitem__order__created_at__gte=cutoff,
                    orderitem__order__status='completed'
                ),
                output_field=DecimalField()
            ),
            'review_stats': Review.objects.filter(
                product=product,
                created_at__gte=cutoff,
                is_verified=True
            ).aggregate(
                total_reviews=Count('id'),
                average_rating=Avg('rating'),
                positive_reviews=Count(
                    'id',
                    filter=Q(rating__gte=4)
                )
            )
        }
