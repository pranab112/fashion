"""
Analytics functionality for the products app.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from django.db.models import (
    Count,
    Avg,
    Sum,
    F,
    Q,
    Window,
    ExpressionWrapper,
    FloatField
)
from django.db.models.functions import (
    TruncDate,
    ExtractHour,
    Coalesce,
    Lag
)
from django.utils import timezone
from django.core.cache import cache

from .models import Product, ProductView, Review, SearchQuery
from .constants import TRENDING_SCORE_WEIGHTS

logger = logging.getLogger(__name__)

class ProductAnalytics:
    """Analytics for products."""
    
    @staticmethod
    def get_view_trends(
        days: int = 30,
        interval: str = 'day'
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get product view trends.
        
        Args:
            days: Number of days to analyze
            interval: Time interval ('hour', 'day', 'week', 'month')
            
        Returns:
            Dict containing view trends data
        """
        try:
            start_date = timezone.now() - timedelta(days=days)
            
            # Get views by interval
            views = ProductView.objects.filter(
                created_at__gte=start_date
            )
            
            if interval == 'hour':
                views = views.annotate(
                    interval=ExtractHour('created_at')
                )
            else:
                views = views.annotate(
                    interval=TruncDate('created_at')
                )
            
            views = views.values('interval').annotate(
                count=Count('id')
            ).order_by('interval')
            
            return {
                'interval': interval,
                'data': list(views)
            }
            
        except Exception as e:
            logger.error(f"Error getting view trends: {str(e)}")
            return {'interval': interval, 'data': []}

    @staticmethod
    def get_conversion_rates(
        days: int = 30
    ) -> Dict[str, float]:
        """
        Get product conversion rates.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict containing conversion rates
        """
        try:
            start_date = timezone.now() - timedelta(days=days)
            
            # Get total views
            total_views = ProductView.objects.filter(
                created_at__gte=start_date
            ).count()
            
            if total_views == 0:
                return {
                    'view_to_cart': 0.0,
                    'cart_to_order': 0.0,
                    'view_to_order': 0.0
                }
            
            # Get cart additions
            cart_adds = Product.objects.filter(
                cartitem__created_at__gte=start_date
            ).count()
            
            # Get orders
            orders = Product.objects.filter(
                orderitem__order__created_at__gte=start_date,
                orderitem__order__status='completed'
            ).count()
            
            return {
                'view_to_cart': (cart_adds / total_views) * 100,
                'cart_to_order': (orders / cart_adds) * 100 if cart_adds > 0 else 0.0,
                'view_to_order': (orders / total_views) * 100
            }
            
        except Exception as e:
            logger.error(f"Error getting conversion rates: {str(e)}")
            return {
                'view_to_cart': 0.0,
                'cart_to_order': 0.0,
                'view_to_order': 0.0
            }

    @staticmethod
    def get_trending_products(
        days: int = 7,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get trending products based on views, orders, and ratings.
        
        Args:
            days: Number of days to analyze
            limit: Number of products to return
            
        Returns:
            List of trending products with scores
        """
        try:
            start_date = timezone.now() - timedelta(days=days)
            
            products = Product.objects.filter(
                status='active'
            ).annotate(
                recent_views=Count(
                    'productview',
                    filter=Q(productview__created_at__gte=start_date)
                ),
                recent_orders=Count(
                    'orderitem',
                    filter=Q(
                        orderitem__order__created_at__gte=start_date,
                        orderitem__order__status='completed'
                    )
                ),
                recent_wishlist_adds=Count(
                    'wishlist_items',
                    filter=Q(wishlist_items__created_at__gte=start_date)
                ),
                recent_cart_adds=Count(
                    'cartitem',
                    filter=Q(cartitem__created_at__gte=start_date)
                )
            ).annotate(
                trending_score=ExpressionWrapper(
                    (F('recent_views') * TRENDING_SCORE_WEIGHTS['views']) +
                    (F('recent_orders') * TRENDING_SCORE_WEIGHTS['orders']) +
                    (F('recent_wishlist_adds') * TRENDING_SCORE_WEIGHTS['wishlist_adds']) +
                    (F('recent_cart_adds') * TRENDING_SCORE_WEIGHTS['cart_adds']),
                    output_field=FloatField()
                )
            ).order_by('-trending_score')[:limit]
            
            return list(products.values(
                'id',
                'name',
                'trending_score',
                'recent_views',
                'recent_orders'
            ))
            
        except Exception as e:
            logger.error(f"Error getting trending products: {str(e)}")
            return []

    @staticmethod
    def get_category_performance(
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get performance metrics by category.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            List of category performance data
        """
        try:
            start_date = timezone.now() - timedelta(days=days)
            
            return list(Product.objects.filter(
                orderitem__order__created_at__gte=start_date,
                orderitem__order__status='completed'
            ).values(
                'category__name'
            ).annotate(
                total_orders=Count('orderitem'),
                total_revenue=Sum(
                    F('orderitem__quantity') * F('orderitem__price')
                ),
                average_rating=Avg('reviews__rating')
            ).order_by('-total_revenue'))
            
        except Exception as e:
            logger.error(f"Error getting category performance: {str(e)}")
            return []

    @staticmethod
    def get_search_analytics(
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get search analytics.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict containing search analytics
        """
        try:
            start_date = timezone.now() - timedelta(days=days)
            
            queries = SearchQuery.objects.filter(
                last_searched__gte=start_date
            )
            
            popular_queries = queries.order_by('-count')[:10]
            zero_results = queries.filter(success_rate=0)
            
            return {
                'total_searches': queries.aggregate(
                    total=Sum('count')
                )['total'] or 0,
                'popular_queries': list(popular_queries.values(
                    'query',
                    'count',
                    'success_rate'
                )),
                'zero_results': list(zero_results.values_list(
                    'query',
                    flat=True
                ))
            }
            
        except Exception as e:
            logger.error(f"Error getting search analytics: {str(e)}")
            return {
                'total_searches': 0,
                'popular_queries': [],
                'zero_results': []
            }

    @staticmethod
    def get_review_analytics(
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get review analytics.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict containing review analytics
        """
        try:
            start_date = timezone.now() - timedelta(days=days)
            
            reviews = Review.objects.filter(
                created_at__gte=start_date
            )
            
            return {
                'total_reviews': reviews.count(),
                'average_rating': reviews.aggregate(
                    avg=Avg('rating')
                )['avg'] or 0.0,
                'rating_distribution': list(reviews.values(
                    'rating'
                ).annotate(
                    count=Count('id')
                ).order_by('rating')),
                'verified_percentage': (
                    reviews.filter(is_verified=True).count() /
                    reviews.count() * 100
                ) if reviews.exists() else 0.0
            }
            
        except Exception as e:
            logger.error(f"Error getting review analytics: {str(e)}")
            return {
                'total_reviews': 0,
                'average_rating': 0.0,
                'rating_distribution': [],
                'verified_percentage': 0.0
            }

    @staticmethod
    def get_inventory_analytics() -> Dict[str, Any]:
        """
        Get inventory analytics.
        
        Returns:
            Dict containing inventory analytics
        """
        try:
            products = Product.objects.all()
            
            return {
                'total_products': products.count(),
                'out_of_stock': products.filter(stock=0).count(),
                'low_stock': products.filter(
                    stock__gt=0,
                    stock__lte=F('low_stock_threshold')
                ).count(),
                'total_stock_value': products.aggregate(
                    value=Sum(F('stock') * F('price'))
                )['value'] or 0
            }
            
        except Exception as e:
            logger.error(f"Error getting inventory analytics: {str(e)}")
            return {
                'total_products': 0,
                'out_of_stock': 0,
                'low_stock': 0,
                'total_stock_value': 0
            }

    @staticmethod
    def get_dashboard_metrics() -> Dict[str, Any]:
        """
        Get metrics for dashboard.
        
        Returns:
            Dict containing dashboard metrics
        """
        try:
            # Try to get from cache
            cache_key = 'dashboard_metrics'
            metrics = cache.get(cache_key)
            
            if metrics is None:
                today = timezone.now()
                yesterday = today - timedelta(days=1)
                last_week = today - timedelta(days=7)
                
                metrics = {
                    'views': {
                        'today': ProductView.objects.filter(
                            created_at__date=today.date()
                        ).count(),
                        'yesterday': ProductView.objects.filter(
                            created_at__date=yesterday.date()
                        ).count(),
                        'last_week': ProductView.objects.filter(
                            created_at__gte=last_week
                        ).count()
                    },
                    'orders': {
                        'today': Product.objects.filter(
                            orderitem__order__created_at__date=today.date(),
                            orderitem__order__status='completed'
                        ).count(),
                        'yesterday': Product.objects.filter(
                            orderitem__order__created_at__date=yesterday.date(),
                            orderitem__order__status='completed'
                        ).count(),
                        'last_week': Product.objects.filter(
                            orderitem__order__created_at__gte=last_week,
                            orderitem__order__status='completed'
                        ).count()
                    },
                    'revenue': {
                        'today': Product.objects.filter(
                            orderitem__order__created_at__date=today.date(),
                            orderitem__order__status='completed'
                        ).aggregate(
                            total=Sum(
                                F('orderitem__quantity') * F('orderitem__price')
                            )
                        )['total'] or 0,
                        'yesterday': Product.objects.filter(
                            orderitem__order__created_at__date=yesterday.date(),
                            orderitem__order__status='completed'
                        ).aggregate(
                            total=Sum(
                                F('orderitem__quantity') * F('orderitem__price')
                            )
                        )['total'] or 0,
                        'last_week': Product.objects.filter(
                            orderitem__order__created_at__gte=last_week,
                            orderitem__order__status='completed'
                        ).aggregate(
                            total=Sum(
                                F('orderitem__quantity') * F('orderitem__price')
                            )
                        )['total'] or 0
                    }
                }
                
                # Cache for 1 hour
                cache.set(cache_key, metrics, 3600)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting dashboard metrics: {str(e)}")
            return {
                'views': {'today': 0, 'yesterday': 0, 'last_week': 0},
                'orders': {'today': 0, 'yesterday': 0, 'last_week': 0},
                'revenue': {'today': 0, 'yesterday': 0, 'last_week': 0}
            }
