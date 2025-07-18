import logging
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from prometheus_client import Counter, Histogram, Gauge
from functools import wraps
import time
import json
from typing import Any, Dict, Optional
from django.conf import settings
from django.core.exceptions import ValidationError
import structlog
from datetime import datetime

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Initialize logger
logger = structlog.get_logger(__name__)

# Prometheus metrics
HTTP_REQUESTS = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_USERS = Gauge(
    'active_users',
    'Number of active users'
)

DB_QUERY_DURATION = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['query_type']
)

CACHE_HITS = Counter(
    'cache_hits_total',
    'Total cache hits'
)

CACHE_MISSES = Counter(
    'cache_misses_total',
    'Total cache misses'
)

ORDER_VALUE = Histogram(
    'order_value_dollars',
    'Order value in dollars',
    buckets=[10, 50, 100, 500, 1000, 5000]
)

class Monitoring:
    """Centralized monitoring and logging functionality."""

    @staticmethod
    def init_sentry():
        """Initialize Sentry SDK."""
        if settings.SENTRY_DSN:
            sentry_sdk.init(
                dsn=settings.SENTRY_DSN,
                integrations=[
                    DjangoIntegration(),
                    RedisIntegration(),
                    CeleryIntegration(),
                    LoggingIntegration(
                        level=logging.INFO,
                        event_level=logging.ERROR
                    ),
                ],
                traces_sample_rate=1.0,
                send_default_pii=True,
                environment=settings.ENVIRONMENT,
                release=settings.VERSION,
                max_breadcrumbs=50,
                attach_stacktrace=True,
                before_send=lambda event, hint: Monitoring.before_sentry_send(event, hint)
            )

    @staticmethod
    def before_sentry_send(event: Dict, hint: Dict) -> Optional[Dict]:
        """Process and filter Sentry events before sending."""
        if 'exc_info' in hint:
            exc_type, exc_value, tb = hint['exc_info']
            if isinstance(exc_value, ValidationError):
                # Don't send validation errors to Sentry
                return None
        return event

    @staticmethod
    def log_request(request, response, duration):
        """Log HTTP request details."""
        logger.info(
            'http_request',
            method=request.method,
            path=request.path,
            status=response.status_code,
            duration=duration,
            user_id=getattr(request.user, 'id', None),
            ip=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )

        # Update Prometheus metrics
        HTTP_REQUESTS.labels(
            method=request.method,
            endpoint=request.path,
            status=response.status_code
        ).inc()

        REQUEST_DURATION.labels(
            method=request.method,
            endpoint=request.path
        ).observe(duration)

    @staticmethod
    def monitor_database(func):
        """Decorator to monitor database operations."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Record query duration
                DB_QUERY_DURATION.labels(
                    query_type=func.__name__
                ).observe(duration)
                
                return result
            except Exception as e:
                logger.error(
                    'database_error',
                    error=str(e),
                    function=func.__name__,
                    args=args,
                    kwargs=kwargs
                )
                raise
        return wrapper

    @staticmethod
    def monitor_cache(func):
        """Decorator to monitor cache operations."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                if result is not None:
                    CACHE_HITS.inc()
                else:
                    CACHE_MISSES.inc()
                return result
            except Exception as e:
                logger.error(
                    'cache_error',
                    error=str(e),
                    function=func.__name__,
                    args=args,
                    kwargs=kwargs
                )
                raise
        return wrapper

    @staticmethod
    def log_order(order):
        """Log order details."""
        logger.info(
            'order_placed',
            order_id=order.id,
            user_id=order.user_id,
            total_amount=float(order.total_amount),
            items_count=order.items.count()
        )

        # Record order value
        ORDER_VALUE.observe(float(order.total_amount))

    @staticmethod
    def track_user_activity(user_id: int, action: str, metadata: Dict = None):
        """Track user activity."""
        logger.info(
            'user_activity',
            user_id=user_id,
            action=action,
            metadata=metadata or {}
        )

    @staticmethod
    def monitor_performance(func):
        """Decorator to monitor function performance."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.info(
                    'function_performance',
                    function=func.__name__,
                    duration=duration,
                    args=args,
                    kwargs=kwargs
                )
                
                return result
            except Exception as e:
                logger.error(
                    'function_error',
                    error=str(e),
                    function=func.__name__,
                    args=args,
                    kwargs=kwargs
                )
                raise
        return wrapper

    @staticmethod
    def log_error(error: Exception, context: Dict = None):
        """Log error with context."""
        logger.error(
            'application_error',
            error=str(error),
            error_type=type(error).__name__,
            context=context or {}
        )

    @staticmethod
    def audit_log(user_id: int, action: str, resource_type: str, resource_id: str, changes: Dict = None):
        """Create audit log entry."""
        logger.info(
            'audit_log',
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            changes=changes or {},
            timestamp=datetime.utcnow().isoformat()
        )

    @staticmethod
    def monitor_api(func):
        """Decorator to monitor API endpoints."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Get request from args (assuming DRF view)
                request = args[1] if len(args) > 1 else None
                
                if request:
                    logger.info(
                        'api_request',
                        endpoint=request.path,
                        method=request.method,
                        duration=duration,
                        user_id=getattr(request.user, 'id', None),
                        params=dict(request.query_params),
                        status_code=getattr(result, 'status_code', 200)
                    )
                
                return result
            except Exception as e:
                logger.error(
                    'api_error',
                    error=str(e),
                    endpoint=getattr(request, 'path', None),
                    method=getattr(request, 'method', None)
                )
                raise
        return wrapper

    @staticmethod
    def health_check() -> Dict[str, Any]:
        """Perform system health check."""
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'components': {
                'database': True,
                'cache': True,
                'celery': True,
                'elasticsearch': True
            },
            'metrics': {
                'active_users': ACTIVE_USERS._value.get(),
                'cache_hit_ratio': (
                    CACHE_HITS._value.get() /
                    (CACHE_HITS._value.get() + CACHE_MISSES._value.get())
                    if (CACHE_HITS._value.get() + CACHE_MISSES._value.get()) > 0
                    else 0
                )
            }
        }

        try:
            # Check database
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute('SELECT 1')
        except Exception as e:
            health_status['components']['database'] = False
            health_status['status'] = 'degraded'
            logger.error('database_health_check_failed', error=str(e))

        try:
            # Check Redis
            from django.core.cache import cache
            cache.get('health_check')
        except Exception as e:
            health_status['components']['cache'] = False
            health_status['status'] = 'degraded'
            logger.error('cache_health_check_failed', error=str(e))

        try:
            # Check Celery
            from celery.app.control import Control
            from nexus.celery import app
            control = Control(app)
            workers = control.inspect().active()
            if not workers:
                health_status['components']['celery'] = False
                health_status['status'] = 'degraded'
        except Exception as e:
            health_status['components']['celery'] = False
            health_status['status'] = 'degraded'
            logger.error('celery_health_check_failed', error=str(e))

        try:
            # Check Elasticsearch
            from elasticsearch_dsl import connections
            connections.get_connection().cluster.health()
        except Exception as e:
            health_status['components']['elasticsearch'] = False
            health_status['status'] = 'degraded'
            logger.error('elasticsearch_health_check_failed', error=str(e))

        return health_status

# Initialize monitoring on module load
Monitoring.init_sentry()
