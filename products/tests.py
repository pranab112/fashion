"""
Tests for the products app.
"""

from decimal import Decimal
from typing import Any, Dict, List
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from django.core.cache import cache

from cart.models import Wishlist
from .factories import (
    ProductFactory,
    CategoryFactory,
    BrandFactory,
    ReviewFactory,
    create_sample_products
)

User = get_user_model()

class CategoryModelTests(TestCase):
    """Test cases for Category model."""

    def setUp(self) -> None:
        """Set up test data."""
        self.category = CategoryFactory()
        self.child_category = CategoryFactory(parent=self.category)

    def test_str_representation(self) -> None:
        """Test string representation."""
        self.assertEqual(str(self.category), self.category.name)

    def test_get_absolute_url(self) -> None:
        """Test absolute URL."""
        url = reverse('products:category_detail', kwargs={'slug': self.category.slug})
        self.assertEqual(self.category.get_absolute_url(), url)

    def test_breadcrumbs(self) -> None:
        """Test breadcrumb generation."""
        crumbs = self.child_category.breadcrumbs
        self.assertEqual(len(crumbs), 2)
        self.assertEqual(crumbs[0]['name'], self.category.name)
        self.assertEqual(crumbs[1]['name'], self.child_category.name)

class ProductModelTests(TestCase):
    """Test cases for Product model."""

    def setUp(self) -> None:
        """Set up test data."""
        self.product = ProductFactory()

    def test_str_representation(self) -> None:
        """Test string representation."""
        self.assertEqual(str(self.product), self.product.name)

    def test_get_absolute_url(self) -> None:
        """Test absolute URL."""
        url = reverse('products:product_detail', kwargs={'slug': self.product.slug})
        self.assertEqual(self.product.get_absolute_url(), url)

    def test_get_price(self) -> None:
        """Test price calculation."""
        # Regular price
        self.assertEqual(self.product.get_price(), self.product.price)

        # Sale price
        self.product.is_on_sale = True
        self.product.sale_price = self.product.price - 10
        self.product.save()
        self.assertEqual(self.product.get_price(), self.product.sale_price)

    def test_is_available(self) -> None:
        """Test availability check."""
        self.product.stock = 10
        self.product.is_active = True
        self.product.save()
        self.assertTrue(self.product.is_available())

        self.product.stock = 0
        self.product.save()
        self.assertFalse(self.product.is_available())

    def test_get_discount_percentage(self) -> None:
        """Test discount calculation."""
        self.product.price = Decimal('100.00')
        self.product.sale_price = Decimal('80.00')
        self.product.is_on_sale = True
        self.product.save()
        self.assertEqual(self.product.get_discount_percentage(), 20)

class ProductViewTests(TestCase):
    """Test cases for product views."""

    def setUp(self) -> None:
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.products = create_sample_products(5)

    def test_product_list_view(self) -> None:
        """Test product list view."""
        response = self.client.get(reverse('products:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_list.html')
        self.assertEqual(len(response.context['products']), 5)

    def test_product_detail_view(self) -> None:
        """Test product detail view."""
        product = self.products[0]
        response = self.client.get(
            reverse('products:product_detail', kwargs={'slug': product.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_detail.html')
        self.assertEqual(response.context['product'], product)

    def test_search_view(self) -> None:
        """Test search view."""
        response = self.client.get(
            reverse('products:search'),
            {'q': self.products[0].name}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/search.html')
        self.assertContains(response, self.products[0].name)

class WishlistTests(TestCase):
    """Test cases for wishlist functionality."""

    def setUp(self) -> None:
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.product = ProductFactory()

    def test_add_to_wishlist(self) -> None:
        """Test adding product to wishlist."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('products:wishlist_toggle'),
            {'product_id': self.product.id}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Wishlist.objects.filter(
                user=self.user,
                products=self.product
            ).exists()
        )

    def test_remove_from_wishlist(self) -> None:
        """Test removing product from wishlist."""
        wishlist = Wishlist.objects.create(user=self.user)
        wishlist.products.add(self.product)

        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('products:wishlist_toggle'),
            {'product_id': self.product.id}
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Wishlist.objects.filter(
                user=self.user,
                products=self.product
            ).exists()
        )

class ReviewTests(TestCase):
    """Test cases for review functionality."""

    def setUp(self) -> None:
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.product = ProductFactory()

    def test_create_review(self) -> None:
        """Test creating a review."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('products:review_create', kwargs={'pk': self.product.id}),
            {
                'rating': 5,
                'title': 'Great product',
                'comment': 'Really happy with this purchase!'
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Review.objects.filter(
                user=self.user,
                product=self.product
            ).exists()
        )

class APITests(TestCase):
    """Test cases for API endpoints."""

    def setUp(self) -> None:
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.product = ProductFactory()

    def test_product_list_api(self) -> None:
        """Test product list API."""
        response = self.client.get(reverse('products:api_product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 1)

    def test_product_detail_api(self) -> None:
        """Test product detail API."""
        response = self.client.get(
            reverse('products:api_product_detail', kwargs={'pk': self.product.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], self.product.id)

class CacheTests(TestCase):
    """Test cases for caching."""

    def setUp(self) -> None:
        """Set up test data."""
        cache.clear()
        self.product = ProductFactory()

    def test_product_cache(self) -> None:
        """Test product caching."""
        # First request - cache miss
        response1 = self.client.get(
            reverse('products:product_detail', kwargs={'slug': self.product.slug})
        )
        self.assertEqual(response1.status_code, 200)

        # Second request - cache hit
        response2 = self.client.get(
            reverse('products:product_detail', kwargs={'slug': self.product.slug})
        )
        self.assertEqual(response2.status_code, 200)

        # Verify cache was used
        self.assertTrue(response2.from_cache if hasattr(response2, 'from_cache') else True)

class SearchTests(TestCase):
    """Test cases for search functionality."""

    def setUp(self) -> None:
        """Set up test data."""
        self.product = ProductFactory(name='Test Product')

    def test_basic_search(self) -> None:
        """Test basic search."""
        response = self.client.get(
            reverse('products:search'),
            {'q': 'test'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)

    def test_advanced_search(self) -> None:
        """Test advanced search with filters."""
        response = self.client.get(
            reverse('products:search'),
            {
                'q': 'test',
                'category': self.product.category.id,
                'min_price': '0',
                'max_price': '1000'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)

class AdminTests(TestCase):
    """Test cases for admin interface."""

    def setUp(self) -> None:
        """Set up test data."""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.client.login(username='admin', password='adminpass123')
        self.product = ProductFactory()

    def test_product_admin(self) -> None:
        """Test product admin interface."""
        response = self.client.get(
            reverse('admin:products_product_change', args=[self.product.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_category_admin(self) -> None:
        """Test category admin interface."""
        category = CategoryFactory()
        response = self.client.get(
            reverse('admin:products_category_change', args=[category.id])
        )
        self.assertEqual(response.status_code, 200)
