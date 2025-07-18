from celery import shared_task
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q, F
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from .monitoring import Monitoring
from .analytics import AnalyticsService
from .notifications import NotificationManager
from .cache import CacheService

logger = logging.getLogger(__name__)

@shared_task
def process_abandoned_carts():
    """Process abandoned shopping carts."""
    try:
        from cart.models import Cart
        threshold = timezone.now() - timedelta(hours=24)
        
        abandoned_carts = Cart.objects.filter(
            status='active',
            updated_at__lt=threshold,
            items__isnull=False
        ).distinct()

        for cart in abandoned_carts:
            NotificationManager.send_abandoned_cart_reminder(cart)
            
            # Track analytics
            AnalyticsService.track_abandoned_cart(cart)

        logger.info(f"Processed {abandoned_carts.count()} abandoned carts")

    except Exception as e:
        logger.error(f"Error processing abandoned carts: {str(e)}")
        Monitoring.log_error('abandoned_carts_error', e)

@shared_task
def update_product_rankings():
    """Update product rankings based on sales and ratings."""
    try:
        from products.models import Product
        from django.db.models import Count, Avg

        products = Product.objects.annotate(
            sales_count=Count('order_items'),
            avg_rating=Avg('reviews__rating')
        )

        for product in products:
            # Calculate ranking score
            score = (
                (product.sales_count * 0.6) +
                ((product.avg_rating or 0) * 0.4)
            )
            
            product.ranking_score = score
            product.save(update_fields=['ranking_score'])

            # Update cache
            CacheService.set_cache(
                f'product_ranking:{product.id}',
                score,
                timeout=86400  # 24 hours
            )

        logger.info(f"Updated rankings for {products.count()} products")

    except Exception as e:
        logger.error(f"Error updating product rankings: {str(e)}")
        Monitoring.log_error('product_rankings_error', e)

@shared_task
def generate_daily_reports():
    """Generate daily business reports."""
    try:
        yesterday = timezone.now() - timedelta(days=1)
        
        # Generate sales report
        sales_report = AnalyticsService.generate_sales_report(yesterday)
        
        # Generate inventory report
        inventory_report = AnalyticsService.generate_inventory_report()
        
        # Generate customer report
        customer_report = AnalyticsService.generate_customer_report(yesterday)

        # Send reports to administrators
        NotificationManager.send_daily_reports(
            sales_report,
            inventory_report,
            customer_report
        )

        logger.info("Generated and sent daily reports")

    except Exception as e:
        logger.error(f"Error generating daily reports: {str(e)}")
        Monitoring.log_error('daily_reports_error', e)

@shared_task
def process_order_shipments():
    """Process orders ready for shipment."""
    try:
        from orders.models import Order
        
        orders = Order.objects.filter(
            status='processing',
            payment_status='paid'
        )

        for order in orders:
            # Check inventory
            if order.check_inventory():
                # Update inventory
                order.update_inventory()
                
                # Update order status
                order.status = 'shipped'
                order.save()

                # Send notification
                NotificationManager.send_shipment_confirmation(order)

        logger.info(f"Processed {orders.count()} orders for shipment")

    except Exception as e:
        logger.error(f"Error processing order shipments: {str(e)}")
        Monitoring.log_error('order_shipments_error', e)

@shared_task
def update_exchange_rates():
    """Update currency exchange rates."""
    try:
        from .utils import get_exchange_rates
        
        rates = get_exchange_rates(settings.DEFAULT_CURRENCY)
        
        # Update cache
        CacheService.set_cache(
            'exchange_rates',
            rates,
            timeout=3600  # 1 hour
        )

        logger.info("Updated exchange rates")

    except Exception as e:
        logger.error(f"Error updating exchange rates: {str(e)}")
        Monitoring.log_error('exchange_rates_error', e)

@shared_task
def clean_expired_sessions():
    """Clean expired user sessions."""
    try:
        from django.contrib.sessions.models import Session
        
        expired_sessions = Session.objects.filter(
            expire_date__lt=timezone.now()
        )
        count = expired_sessions.count()
        expired_sessions.delete()

        logger.info(f"Cleaned {count} expired sessions")

    except Exception as e:
        logger.error(f"Error cleaning expired sessions: {str(e)}")
        Monitoring.log_error('session_cleanup_error', e)

@shared_task
def send_review_reminders():
    """Send review reminders for delivered orders."""
    try:
        from orders.models import Order
        threshold = timezone.now() - timedelta(days=7)
        
        orders = Order.objects.filter(
            status='delivered',
            delivered_at__lt=threshold,
            reviews__isnull=True
        )

        for order in orders:
            NotificationManager.send_review_reminder(order)

        logger.info(f"Sent review reminders for {orders.count()} orders")

    except Exception as e:
        logger.error(f"Error sending review reminders: {str(e)}")
        Monitoring.log_error('review_reminders_error', e)

@shared_task
def update_search_index():
    """Update Elasticsearch search index."""
    try:
        from .search import ProductDocument, CategoryDocument
        
        # Update product index
        ProductDocument().update()
        
        # Update category index
        CategoryDocument().update()

        logger.info("Updated search indices")

    except Exception as e:
        logger.error(f"Error updating search index: {str(e)}")
        Monitoring.log_error('search_index_error', e)

@shared_task
def process_refunds():
    """Process pending refund requests."""
    try:
        from orders.models import RefundRequest
        
        requests = RefundRequest.objects.filter(status='pending')
        
        for request in requests:
            try:
                # Process refund
                from .payments import PaymentService
                result = PaymentService.process_refund(request)
                
                if result['status'] == 'success':
                    request.status = 'approved'
                    request.order.status = 'refunded'
                    request.save()
                    request.order.save()
                    
                    # Send notification
                    NotificationManager.send_refund_confirmation(request)
                else:
                    request.status = 'failed'
                    request.save()
                    
                    # Send notification
                    NotificationManager.send_refund_failed(request)

            except Exception as e:
                logger.error(f"Error processing refund {request.id}: {str(e)}")
                continue

        logger.info(f"Processed {requests.count()} refund requests")

    except Exception as e:
        logger.error(f"Error processing refunds: {str(e)}")
        Monitoring.log_error('refunds_error', e)

@shared_task
def sync_inventory():
    """Sync inventory with external systems."""
    try:
        from products.models import Product
        from .inventory import InventoryService
        
        products = Product.objects.filter(is_active=True)
        
        for product in products:
            # Get external inventory
            external_stock = InventoryService.get_external_stock(product)
            
            if external_stock != product.stock_quantity:
                product.stock_quantity = external_stock
                product.save()
                
                # Check low stock
                if product.stock_quantity <= product.low_stock_threshold:
                    NotificationManager.notify_low_stock(product)

        logger.info(f"Synced inventory for {products.count()} products")

    except Exception as e:
        logger.error(f"Error syncing inventory: {str(e)}")
        Monitoring.log_error('inventory_sync_error', e)

@shared_task
def cleanup_temporary_files():
    """Clean up temporary files."""
    try:
        import os
        from django.conf import settings
        
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
        threshold = timezone.now() - timedelta(days=1)
        
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                path = os.path.join(root, file)
                if os.path.getmtime(path) < threshold.timestamp():
                    os.remove(path)

        logger.info("Cleaned up temporary files")

    except Exception as e:
        logger.error(f"Error cleaning up temporary files: {str(e)}")
        Monitoring.log_error('file_cleanup_error', e)
