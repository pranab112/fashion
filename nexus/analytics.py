from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Avg, F, Q
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import logging
from .monitoring import Monitoring
from .cache import CacheService
from decimal import Decimal

logger = logging.getLogger(__name__)
User = get_user_model()

class AnalyticsService:
    """Service class for handling analytics and tracking."""

    @staticmethod
    @Monitoring.monitor_performance
    def track_event(
        event_type: str,
        user_id: Optional[int],
        data: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> None:
        """
        Track an analytics event.
        
        Args:
            event_type: Type of event (e.g., 'page_view', 'add_to_cart')
            user_id: User ID if authenticated
            data: Event data
            session_id: Session ID for anonymous users
        """
        from analytics.models import Event
        try:
            Event.objects.create(
                event_type=event_type,
                user_id=user_id,
                session_id=session_id,
                data=data,
                timestamp=timezone.now()
            )
        except Exception as e:
            logger.error(
                'event_tracking_failed',
                error=str(e),
                event_type=event_type,
                user_id=user_id
            )

    @staticmethod
    @CacheService.cache_decorator('analytics', timeout=300)
    def get_sales_metrics(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get sales metrics for a given period."""
        from orders.models import Order
        
        if not start_date:
            start_date = timezone.now() - timedelta(days=30)
        if not end_date:
            end_date = timezone.now()

        orders = Order.objects.filter(
            created_at__range=(start_date, end_date),
            status='completed'
        )

        return {
            'total_sales': orders.aggregate(
                total=Sum('total_amount')
            )['total'] or Decimal('0'),
            'order_count': orders.count(),
            'average_order_value': orders.aggregate(
                avg=Avg('total_amount')
            )['avg'] or Decimal('0'),
            'items_sold': orders.aggregate(
                total=Sum('items__quantity')
            )['total'] or 0,
        }

    @staticmethod
    def get_user_metrics() -> Dict[str, Any]:
        """Get user-related metrics."""
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)

        return {
            'total_users': User.objects.count(),
            'new_users': User.objects.filter(
                date_joined__gte=thirty_days_ago
            ).count(),
            'active_users': User.objects.filter(
                last_login__gte=thirty_days_ago
            ).count(),
        }

    @staticmethod
    def get_product_metrics() -> Dict[str, Any]:
        """Get product-related metrics."""
        from products.models import Product, ProductView
        
        return {
            'total_products': Product.objects.count(),
            'out_of_stock': Product.objects.filter(
                stock_quantity=0
            ).count(),
            'low_stock': Product.objects.filter(
                stock_quantity__gt=0,
                stock_quantity__lte=F('low_stock_threshold')
            ).count(),
            'most_viewed': ProductView.objects.values(
                'product__name'
            ).annotate(
                views=Count('id')
            ).order_by('-views')[:10],
        }

    @staticmethod
    def get_cart_metrics() -> Dict[str, Any]:
        """Get shopping cart metrics."""
        from cart.models import Cart
        
        return {
            'active_carts': Cart.objects.filter(
                status='active'
            ).count(),
            'abandoned_carts': Cart.objects.filter(
                status='abandoned'
            ).count(),
            'average_items': Cart.objects.filter(
                status='active'
            ).annotate(
                item_count=Count('items')
            ).aggregate(
                avg=Avg('item_count')
            )['avg'] or 0,
        }

    @staticmethod
    def get_conversion_metrics() -> Dict[str, Any]:
        """Get conversion-related metrics."""
        from analytics.models import Event
        
        # Get total page views
        page_views = Event.objects.filter(
            event_type='page_view'
        ).count()

        # Get checkout events
        checkouts = Event.objects.filter(
            event_type='checkout_complete'
        ).count()

        return {
            'page_views': page_views,
            'conversion_rate': (
                (checkouts / page_views * 100)
                if page_views > 0 else 0
            ),
        }

    @staticmethod
    def get_category_performance() -> List[Dict[str, Any]]:
        """Get performance metrics by category."""
        from products.models import Category
        from orders.models import OrderItem
        
        categories = Category.objects.all()
        results = []

        for category in categories:
            sales = OrderItem.objects.filter(
                product__category=category,
                order__status='completed'
            ).aggregate(
                total_sales=Sum('total_price'),
                items_sold=Sum('quantity')
            )

            results.append({
                'category': category.name,
                'total_sales': sales['total_sales'] or Decimal('0'),
                'items_sold': sales['items_sold'] or 0,
            })

        return sorted(
            results,
            key=lambda x: x['total_sales'],
            reverse=True
        )

    @staticmethod
    def get_search_analytics() -> Dict[str, Any]:
        """Get search-related analytics."""
        from analytics.models import SearchEvent
        
        return {
            'top_searches': SearchEvent.objects.values(
                'query'
            ).annotate(
                count=Count('id')
            ).order_by('-count')[:10],
            'zero_results': SearchEvent.objects.filter(
                results_count=0
            ).values('query').annotate(
                count=Count('id')
            ).order_by('-count')[:10],
        }

    @staticmethod
    def get_user_behavior(user_id: int) -> Dict[str, Any]:
        """Get behavior analytics for a specific user."""
        from analytics.models import Event
        
        events = Event.objects.filter(user_id=user_id)
        
        return {
            'page_views': events.filter(
                event_type='page_view'
            ).count(),
            'products_viewed': events.filter(
                event_type='product_view'
            ).values('data__product_id').distinct().count(),
            'cart_additions': events.filter(
                event_type='add_to_cart'
            ).count(),
            'purchases': events.filter(
                event_type='purchase'
            ).count(),
        }

    @staticmethod
    def generate_daily_report() -> Dict[str, Any]:
        """Generate daily analytics report."""
        yesterday = timezone.now() - timedelta(days=1)
        start = yesterday.replace(hour=0, minute=0, second=0)
        end = yesterday.replace(hour=23, minute=59, second=59)

        report = {
            'date': yesterday.date().isoformat(),
            'sales': AnalyticsService.get_sales_metrics(start, end),
            'users': {
                'new_signups': User.objects.filter(
                    date_joined__range=(start, end)
                ).count(),
                'active_users': User.objects.filter(
                    last_login__range=(start, end)
                ).count(),
            },
            'orders': {
                'completed': Order.objects.filter(
                    status='completed',
                    completed_at__range=(start, end)
                ).count(),
                'cancelled': Order.objects.filter(
                    status='cancelled',
                    updated_at__range=(start, end)
                ).count(),
            },
            'products': {
                'new': Product.objects.filter(
                    created_at__range=(start, end)
                ).count(),
                'updated': Product.objects.filter(
                    updated_at__range=(start, end)
                ).count(),
            },
        }

        # Cache the report
        cache_key = f"daily_report:{yesterday.date().isoformat()}"
        CacheService.set_cache(cache_key, report, timeout=86400)  # 24 hours

        return report

    @staticmethod
    def track_search(
        query: str,
        results_count: int,
        user_id: Optional[int] = None,
        filters: Optional[Dict] = None
    ) -> None:
        """Track search events."""
        from analytics.models import SearchEvent
        
        try:
            SearchEvent.objects.create(
                query=query,
                results_count=results_count,
                user_id=user_id,
                filters=filters or {},
                timestamp=timezone.now()
            )
        except Exception as e:
            logger.error(
                'search_tracking_failed',
                error=str(e),
                query=query
            )

    @staticmethod
    def track_product_view(
        product_id: int,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None,
        source: Optional[str] = None
    ) -> None:
        """Track product view events."""
        from products.models import ProductView
        
        try:
            ProductView.objects.create(
                product_id=product_id,
                user_id=user_id,
                session_id=session_id,
                source=source,
                timestamp=timezone.now()
            )
        except Exception as e:
            logger.error(
                'product_view_tracking_failed',
                error=str(e),
                product_id=product_id
            )

    @staticmethod
    def track_cart_event(
        cart_id: int,
        event_type: str,
        user_id: Optional[int] = None,
        data: Optional[Dict] = None
    ) -> None:
        """Track cart-related events."""
        from cart.models import CartEvent
        
        try:
            CartEvent.objects.create(
                cart_id=cart_id,
                event_type=event_type,
                user_id=user_id,
                data=data or {},
                timestamp=timezone.now()
            )
        except Exception as e:
            logger.error(
                'cart_event_tracking_failed',
                error=str(e),
                cart_id=cart_id,
                event_type=event_type
            )
