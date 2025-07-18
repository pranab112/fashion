from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.utils import timezone
from django.db.models import Q, F, Count, Avg
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from decimal import Decimal

class UserManager(BaseUserManager):
    """Custom manager for User model."""

    def create_user(
        self,
        email: str,
        password: Optional[str] = None,
        **extra_fields
    ):
        """Create and save a regular user."""
        if not email:
            raise ValueError(_('The Email field must be set'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        
        if password:
            user.set_password(password)
        
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email: str,
        password: str,
        **extra_fields
    ):
        """Create and save a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)

    def active(self):
        """Get active users."""
        return self.filter(is_active=True)

    def staff(self):
        """Get staff users."""
        return self.filter(is_staff=True)

    def with_orders_count(self):
        """Annotate users with orders count."""
        return self.annotate(orders_count=Count('orders'))

class ProductManager(models.Manager):
    """Custom manager for Product model."""

    def active(self):
        """Get active products."""
        return self.filter(is_active=True)

    def with_stock(self):
        """Get products with stock."""
        return self.filter(stock_quantity__gt=0)

    def low_stock(self):
        """Get products with low stock."""
        return self.filter(
            stock_quantity__gt=0,
            stock_quantity__lte=F('low_stock_threshold')
        )

    def out_of_stock(self):
        """Get out of stock products."""
        return self.filter(stock_quantity=0)

    def by_category(self, category_id: int):
        """Get products by category."""
        return self.filter(
            Q(category_id=category_id) |
            Q(category__parent_id=category_id)
        )

    def by_price_range(
        self,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None
    ):
        """Get products within price range."""
        queryset = self.all()
        
        if min_price is not None:
            queryset = queryset.filter(price__gte=min_price)
        if max_price is not None:
            queryset = queryset.filter(price__lte=max_price)
        
        return queryset

    def with_ratings(self):
        """Annotate products with ratings data."""
        return self.annotate(
            avg_rating=Avg('reviews__rating'),
            reviews_count=Count('reviews')
        )

    def trending(self, days: int = 7, limit: int = 10):
        """Get trending products based on recent orders."""
        date_threshold = timezone.now() - timedelta(days=days)
        return (
            self.filter(
                order_items__order__created_at__gte=date_threshold
            )
            .annotate(order_count=Count('order_items'))
            .order_by('-order_count')[:limit]
        )

class OrderManager(models.Manager):
    """Custom manager for Order model."""

    def pending(self):
        """Get pending orders."""
        return self.filter(status='pending')

    def processing(self):
        """Get processing orders."""
        return self.filter(status='processing')

    def completed(self):
        """Get completed orders."""
        return self.filter(status='completed')

    def cancelled(self):
        """Get cancelled orders."""
        return self.filter(status='cancelled')

    def by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ):
        """Get orders within date range."""
        return self.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        )

    def with_items(self):
        """Get orders with prefetched items."""
        return self.prefetch_related('items', 'items__product')

    def with_total_amount(self):
        """Annotate orders with total amount."""
        return self.annotate(
            total_amount=Sum('items__price')
        )

class ReviewManager(models.Manager):
    """Custom manager for Review model."""

    def approved(self):
        """Get approved reviews."""
        return self.filter(status='approved')

    def pending(self):
        """Get pending reviews."""
        return self.filter(status='pending')

    def by_rating(self, rating: int):
        """Get reviews by rating."""
        return self.filter(rating=rating)

    def with_user(self):
        """Get reviews with user data."""
        return self.select_related('user')

class CartManager(models.Manager):
    """Custom manager for Cart model."""

    def active(self):
        """Get active carts."""
        return self.filter(status='active')

    def abandoned(self):
        """Get abandoned carts."""
        threshold = timezone.now() - timedelta(hours=24)
        return self.filter(
            status='active',
            updated_at__lt=threshold
        )

    def with_items(self):
        """Get carts with prefetched items."""
        return self.prefetch_related('items', 'items__product')

    def with_total(self):
        """Annotate carts with total amount."""
        return self.annotate(
            total_amount=Sum('items__price')
        )

class CategoryManager(models.Manager):
    """Custom manager for Category model."""

    def active(self):
        """Get active categories."""
        return self.filter(is_active=True)

    def root_categories(self):
        """Get root categories (no parent)."""
        return self.filter(parent__isnull=True)

    def with_products_count(self):
        """Annotate categories with products count."""
        return self.annotate(
            products_count=Count('products')
        )

    def with_subcategories(self):
        """Get categories with prefetched subcategories."""
        return self.prefetch_related('children')

class WishlistManager(models.Manager):
    """Custom manager for Wishlist model."""

    def with_products(self):
        """Get wishlists with prefetched products."""
        return self.prefetch_related('products')

    def with_available_products(self):
        """Get wishlists with available products."""
        return self.prefetch_related(
            models.Prefetch(
                'products',
                queryset=Product.objects.filter(
                    is_active=True,
                    stock_quantity__gt=0
                )
            )
        )

class AddressManager(models.Manager):
    """Custom manager for Address model."""

    def default(self):
        """Get default addresses."""
        return self.filter(is_default=True)

    def shipping(self):
        """Get shipping addresses."""
        return self.filter(type='shipping')

    def billing(self):
        """Get billing addresses."""
        return self.filter(type='billing')

class PaymentMethodManager(models.Manager):
    """Custom manager for PaymentMethod model."""

    def active(self):
        """Get active payment methods."""
        return self.filter(is_active=True)

    def default(self):
        """Get default payment methods."""
        return self.filter(is_default=True)

    def by_type(self, payment_type: str):
        """Get payment methods by type."""
        return self.filter(type=payment_type)
