"""
Monitoring functionality for the products app.
"""

import logging
import time
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from django.db.models import Count, Avg, Sum, F
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings
from datadog import statsd
from prometheus_client import Counter, Histogram, Gauge

logger = logging.getLogger(__name__)

# Prometheus metrics
PRODUCT_VIEWS = Counter(
    'product_views_total',
    'Total number of product views',
    ['product_id', 'category']
)

PRODUCT_SEARCHES = Counter(
    'product_searches_total',
    'Total number of product searches',
    ['query']
)

PRODUCT_STOCK_LEVEL = Gauge(
    'product_stock_level',
    'Current product stock level',
    ['product_id', 'name']
)

ORDER_PROCESSING_TIME = Histogram(
    'order_processing_seconds',
    'Time spent processing orders',
    ['status']
)

# StatsD metrics
class StatsdMetrics:
    """StatsD metrics for products."""

    @staticmethod
    def increment_view(product_id: int) -> None:
        """
        Increment product view counter.
        
        Args:
            product_id: Product ID
        """
        statsd.increment(
            'products.views',
            tags=[f'product:{product_id}']
        )

    @staticmethod
    def timing_order_processing(duration: float, status: str) -> None:
        """
        Record order processing time.
        
        Args:
            duration: Processing duration in seconds
            status: Order status
        """
        statsd.timing(
            'products.order_processing',
            duration,
            tags=[f'status:{status}']
        )

    @staticmethod
    def gauge_stock_level(product_id: int, level: int) -> None:
        """
        Record product stock level.
        
        Args:
            product_id: Product ID
            level: Stock level
        """
        statsd.gauge(
            'products.stock_level',
            level,
            tags=[f'product:{product_id}']
        )

class ProductMetrics:
    """Product monitoring metrics."""

    @staticmethod
    def track_request(
        path: str,
        method: str,
        status_code: int,
        duration: float
    ) -> None:
        """
        Track API request metrics.
        
        Args:
            path: Request path
            method: HTTP method
            status_code: Response status code
            duration: Request duration in seconds
        """
        try:
            # Log request
            logger.info(
                f"{method} {path} {status_code} {duration:.3f}s"
            )
            
            # StatsD metrics
            statsd.timing(
                'products.request_duration',
                duration * 1000,  # Convert to milliseconds
                tags=[
                    f'path:{path}',
                    f'method:{method}',
                    f'status:{status_code}'
                ]
            )
            
            # Increment request counter
            statsd.increment(
                'products.requests',
                tags=[
                    f'path:{path}',
                    f'method:{method}',
                    f'status:{status_code}'
                ]
            )
            
        except Exception as e:
            logger.error(f"Error tracking request metrics: {str(e)}")

    @staticmethod
    def track_view(product_id: int, category: str) -> None:
        """
        Track product view metrics.
        
        Args:
            product_id: Product ID
            category: Product category
        """
        try:
            # Prometheus counter
            PRODUCT_VIEWS.labels(
                product_id=product_id,
                category=category
            ).inc()
            
            # StatsD counter
            StatsdMetrics.increment_view(product_id)
            
        except Exception as e:
            logger.error(f"Error tracking view metrics: {str(e)}")

    @staticmethod
    def track_search(query: str) -> None:
        """
        Track search metrics.
        
        Args:
            query: Search query
        """
        try:
            # Prometheus counter
            PRODUCT_SEARCHES.labels(query=query).inc()
            
            # StatsD counter
            statsd.increment(
                'products.searches',
                tags=[f'query:{query}']
            )
            
        except Exception as e:
            logger.error(f"Error tracking search metrics: {str(e)}")

    @staticmethod
    def track_stock_level(product_id: int, name: str, level: int) -> None:
        """
        Track stock level metrics.
        
        Args:
            product_id: Product ID
            name: Product name
            level: Stock level
        """
        try:
            # Prometheus gauge
            PRODUCT_STOCK_LEVEL.labels(
                product_id=product_id,
                name=name
            ).set(level)
            
            # StatsD gauge
            StatsdMetrics.gauge_stock_level(product_id, level)
            
        except Exception as e:
            logger.error(f"Error tracking stock metrics: {str(e)}")

    @staticmethod
    def track_order_processing(duration: float, status: str) -> None:
        """
        Track order processing metrics.
        
        Args:
            duration: Processing duration in seconds
            status: Order status
        """
        try:
            # Prometheus histogram
            ORDER_PROCESSING_TIME.labels(status=status).observe(duration)
            
            # StatsD timing
            StatsdMetrics.timing_order_processing(duration, status)
            
        except Exception as e:
            logger.error(f"Error tracking order metrics: {str(e)}")

class PerformanceMonitor:
    """Monitor system performance."""

    @staticmethod
    def monitor_database_performance() -> Dict[str, Any]:
        """
        Monitor database performance metrics.
        
        Returns:
            Dict[str, Any]: Performance metrics
        """
        try:
            from django.db import connection
            
            # Get query statistics
            with connection.execute_wrapper(StatementLogger()):
                # Run sample queries
                pass
            
            return {
                'total_queries': len(connection.queries),
                'total_time': sum(
                    float(q['time']) for q in connection.queries
                ),
                'slow_queries': len([
                    q for q in connection.queries
                    if float(q['time']) > 1.0
                ])
            }
            
        except Exception as e:
            logger.error(f"Error monitoring database: {str(e)}")
            return {}

    @staticmethod
    def monitor_cache_performance() -> Dict[str, Any]:
        """
        Monitor cache performance metrics.
        
        Returns:
            Dict[str, Any]: Performance metrics
        """
        try:
            stats = cache.get_stats()
            
            return {
                'hits': stats.get('hits', 0),
                'misses': stats.get('misses', 0),
                'hit_rate': stats.get('hit_rate', 0),
                'size': stats.get('size', 0)
            }
            
        except Exception as e:
            logger.error(f"Error monitoring cache: {str(e)}")
            return {}

class AlertManager:
    """Manage system alerts."""

    @staticmethod
    def check_stock_alerts() -> List[Dict[str, Any]]:
        """
        Check for low stock alerts.
        
        Returns:
            List[Dict[str, Any]]: Stock alerts
        """
        from .models import Product
        
        try:
            alerts = []
            products = Product.objects.filter(
                is_active=True,
                stock__lte=F('low_stock_threshold')
            )
            
            for product in products:
                alerts.append({
                    'product_id': product.id,
                    'name': product.name,
                    'current_stock': product.stock,
                    'threshold': product.low_stock_threshold,
                    'severity': 'high' if product.stock == 0 else 'medium'
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error checking stock alerts: {str(e)}")
            return []

    @staticmethod
    def check_performance_alerts() -> List[Dict[str, Any]]:
        """
        Check for performance alerts.
        
        Returns:
            List[Dict[str, Any]]: Performance alerts
        """
        try:
            alerts = []
            
            # Check database performance
            db_metrics = PerformanceMonitor.monitor_database_performance()
            if db_metrics.get('slow_queries', 0) > 10:
                alerts.append({
                    'type': 'database',
                    'message': 'High number of slow queries detected',
                    'metrics': db_metrics,
                    'severity': 'high'
                })
            
            # Check cache performance
            cache_metrics = PerformanceMonitor.monitor_cache_performance()
            if cache_metrics.get('hit_rate', 100) < 50:
                alerts.append({
                    'type': 'cache',
                    'message': 'Low cache hit rate detected',
                    'metrics': cache_metrics,
                    'severity': 'medium'
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error checking performance alerts: {str(e)}")
            return []

class StatementLogger:
    """Log database statements."""

    def __call__(self, execute, sql, params, many, context):
        """
        Log database statement.
        
        Args:
            execute: Execute function
            sql: SQL statement
            params: Query parameters
            many: Execute many flag
            context: Execution context
            
        Returns:
            Any: Query result
        """
        start = time.time()
        try:
            result = execute(sql, params, many, context)
        finally:
            duration = time.time() - start
            logger.debug(
                f"SQL: {sql}\n"
                f"Params: {params}\n"
                f"Duration: {duration:.3f}s"
            )
        return result
