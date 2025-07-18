from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from unittest.mock import patch, MagicMock
import json
from products.models import Product, Review
from cart.models import Order, Cart
from .services import OrderService, CartService, PaymentService
from .exceptions import PaymentError, InventoryError

User = get_user_model()

class ProductTests(TestCase):
    """Test cases for product functionality."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=Decimal('99.99'),
            stock_quantity=10
        )

    def test_product_list_view(self):
        """Test product listing view."""
        response = self.client.get(reverse('products:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_list.html')
        self.assertContains(response, self.product.name)

    def test_product_detail_view(self):
        """Test product detail view."""
        response = self.client.get(
            reverse('products:detail', args=[self.product.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_detail.html')
        self.assertContains(response, self.product.name)
        self.assertContains(response, self.product.description)

    def test_product_search(self):
        """Test product search functionality."""
        response = self.client.get(
            reverse('products:search'),
            {'q': 'Test'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)

    def test_out_of_stock_product(self):
        """Test out of stock product handling."""
        self.product.stock_quantity = 0
        self.product.save()
        
        response = self.client.get(
            reverse('products:detail', args=[self.product.id])
        )
        self.assertContains(response, 'Out of Stock')

class OrderTests(TestCase):
    """Test cases for order functionality."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.product = Product.objects.create(
            name='Test Product',
            price=Decimal('99.99'),
            stock_quantity=10
        )
        self.client.login(
            email='test@example.com',
            password='testpass123'
        )

    @patch('services.PaymentService.process_payment')
    def test_create_order(self, mock_process_payment):
        """Test order creation."""
        mock_process_payment.return_value = {
            'status': 'success',
            'transaction_id': 'test_transaction'
        }

        order_data = {
            'items': [{'product_id': self.product.id, 'quantity': 1}],
            'shipping_address': {
                'street': '123 Test St',
                'city': 'Test City',
                'country': 'US',
                'postal_code': '12345'
            },
            'payment_method': 'card'
        }

        response = self.client.post(
            reverse('orders:create'),
            data=json.dumps(order_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        
        order = Order.objects.first()
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.status, 'paid')

    def test_order_validation(self):
        """Test order validation."""
        invalid_order_data = {
            'items': [],  # Empty items
            'shipping_address': {},  # Empty address
            'payment_method': 'invalid'
        }

        response = self.client.post(
            reverse('orders:create'),
            data=json.dumps(invalid_order_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_history(self):
        """Test order history view."""
        Order.objects.create(
            user=self.user,
            total_amount=Decimal('99.99'),
            status='completed'
        )

        response = self.client.get(reverse('orders:history'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/order_history.html')

class CartTests(TestCase):
    """Test cases for shopping cart functionality."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.product = Product.objects.create(
            name='Test Product',
            price=Decimal('99.99'),
            stock_quantity=10
        )
        self.client.login(
            email='test@example.com',
            password='testpass123'
        )
        self.cart = Cart.objects.create(user=self.user)

    def test_add_to_cart(self):
        """Test adding item to cart."""
        response = self.client.post(
            reverse('cart:add'),
            {'product_id': self.product.id, 'quantity': 1}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.cart.items.count(), 1)
        self.assertEqual(
            self.cart.items.first().product,
            self.product
        )

    def test_update_cart_quantity(self):
        """Test updating cart item quantity."""
        self.cart.add_item(self.product, 1)
        
        response = self.client.post(
            reverse('cart:update'),
            {
                'item_id': self.cart.items.first().id,
                'quantity': 2
            }
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.cart.items.first().quantity,
            2
        )

    def test_remove_from_cart(self):
        """Test removing item from cart."""
        self.cart.add_item(self.product, 1)
        
        response = self.client.post(
            reverse('cart:remove'),
            {'item_id': self.cart.items.first().id}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.cart.items.count(), 0)

class PaymentTests(TestCase):
    """Test cases for payment functionality."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.order = Order.objects.create(
            user=self.user,
            total_amount=Decimal('99.99')
        )

    @patch('services.PaymentService.process_payment')
    def test_successful_payment(self, mock_process_payment):
        """Test successful payment processing."""
        mock_process_payment.return_value = {
            'status': 'success',
            'transaction_id': 'test_transaction'
        }

        payment_data = {
            'payment_method': 'card',
            'card_number': '4242424242424242',
            'expiry_month': '12',
            'expiry_year': '2024',
            'cvv': '123'
        }

        response = self.client.post(
            reverse('payments:process', args=[self.order.id]),
            data=json.dumps(payment_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'paid')

    @patch('services.PaymentService.process_payment')
    def test_failed_payment(self, mock_process_payment):
        """Test failed payment processing."""
        mock_process_payment.side_effect = PaymentError(
            "Payment processing failed"
        )

        payment_data = {
            'payment_method': 'card',
            'card_number': '4242424242424242',
            'expiry_month': '12',
            'expiry_year': '2024',
            'cvv': '123'
        }

        response = self.client.post(
            reverse('payments:process', args=[self.order.id]),
            data=json.dumps(payment_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.order.refresh_from_db()
        self.assertNotEqual(self.order.status, 'paid')

class ReviewTests(TestCase):
    """Test cases for review functionality."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.product = Product.objects.create(
            name='Test Product',
            price=Decimal('99.99')
        )
        self.client.login(
            email='test@example.com',
            password='testpass123'
        )

    def test_create_review(self):
        """Test review creation."""
        response = self.client.post(
            reverse('products:review', args=[self.product.id]),
            {
                'rating': 5,
                'comment': 'Great product!'
            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(
            Review.objects.first().rating,
            5
        )

    def test_invalid_review(self):
        """Test invalid review submission."""
        response = self.client.post(
            reverse('products:review', args=[self.product.id]),
            {
                'rating': 6,  # Invalid rating
                'comment': ''  # Empty comment
            }
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Review.objects.count(), 0)

class APITests(APITestCase):
    """Test cases for API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.product = Product.objects.create(
            name='Test Product',
            price=Decimal('99.99')
        )

    def test_product_list_api(self):
        """Test product listing API."""
        response = self.client.get(reverse('api:products-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_product_detail_api(self):
        """Test product detail API."""
        response = self.client.get(
            reverse('api:products-detail', args=[self.product.id])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.product.name)

    def test_cart_api(self):
        """Test cart API endpoints."""
        # Add to cart
        response = self.client.post(
            reverse('api:cart-add'),
            {'product_id': self.product.id, 'quantity': 1}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Get cart
        response = self.client.get(reverse('api:cart-detail'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 1)

    def test_order_api(self):
        """Test order API endpoints."""
        order_data = {
            'items': [{'product_id': self.product.id, 'quantity': 1}],
            'shipping_address': {
                'street': '123 Test St',
                'city': 'Test City',
                'country': 'US',
                'postal_code': '12345'
            }
        }

        response = self.client.post(
            reverse('api:orders-create'),
            data=order_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
