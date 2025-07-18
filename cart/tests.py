from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
from products.models import Product, Category, ProductVariant, Brand
from .models import Cart, CartItem, Wishlist, Order, OrderItem

User = get_user_model()

class CartModelTest(TestCase):
    """Test cases for Cart model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Test Category')
        self.brand = Brand.objects.create(name='Test Brand')
        self.product = Product.objects.create(
            name='Test Product',
            brand=self.brand,
            category=self.category,
            price=Decimal('99.99')
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            size='M',
            color='Blue',
            sku='TEST-SKU-001',
            stock=10
        )
        self.cart = Cart.objects.create(user=self.user)
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            product_variant=self.variant,
            quantity=2
        )

    def test_cart_creation(self):
        """Test cart creation."""
        self.assertEqual(self.cart.user, self.user)
        self.assertTrue(self.cart.created_at)

    def test_cart_str_representation(self):
        """Test cart string representation."""
        expected = f"Cart for {self.user.username}"
        self.assertEqual(str(self.cart), expected)

    def test_cart_total_items(self):
        """Test cart total items calculation."""
        self.assertEqual(self.cart.total_items, 2)
        
        # Add another item
        CartItem.objects.create(
            cart=self.cart,
            product_variant=self.variant,
            quantity=3
        )
        self.assertEqual(self.cart.total_items, 5)

    def test_cart_subtotal(self):
        """Test cart subtotal calculation."""
        expected_subtotal = self.product.price * self.cart_item.quantity
        self.assertEqual(self.cart.subtotal, expected_subtotal)

    def test_cart_total(self):
        """Test cart total calculation."""
        self.assertEqual(self.cart.total, self.cart.subtotal)

class CartItemModelTest(TestCase):
    """Test cases for CartItem model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Test Category')
        self.brand = Brand.objects.create(name='Test Brand')
        self.product = Product.objects.create(
            name='Test Product',
            brand=self.brand,
            category=self.category,
            price=Decimal('99.99'),
            sale_price=Decimal('79.99')
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            size='M',
            color='Blue',
            sku='TEST-SKU-001',
            stock=10
        )
        self.cart = Cart.objects.create(user=self.user)
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            product_variant=self.variant,
            quantity=2
        )

    def test_cart_item_creation(self):
        """Test cart item creation."""
        self.assertEqual(self.cart_item.quantity, 2)
        self.assertEqual(self.cart_item.product_variant, self.variant)

    def test_cart_item_str_representation(self):
        """Test cart item string representation."""
        expected = f"2 x {self.variant}"
        self.assertEqual(str(self.cart_item), expected)

    def test_cart_item_unit_price(self):
        """Test cart item unit price calculation."""
        self.assertEqual(self.cart_item.unit_price, self.product.sale_price)

    def test_cart_item_total_price(self):
        """Test cart item total price calculation."""
        expected_total = self.product.sale_price * self.cart_item.quantity
        self.assertEqual(self.cart_item.total_price, expected_total)

class WishlistModelTest(TestCase):
    """Test cases for Wishlist model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Test Category')
        self.brand = Brand.objects.create(name='Test Brand')
        self.product = Product.objects.create(
            name='Test Product',
            brand=self.brand,
            category=self.category,
            price=Decimal('99.99')
        )
        self.wishlist = Wishlist.objects.create(user=self.user)
        self.wishlist.products.add(self.product)

    def test_wishlist_creation(self):
        """Test wishlist creation."""
        self.assertEqual(self.wishlist.user, self.user)
        self.assertEqual(self.wishlist.products.count(), 1)

    def test_wishlist_str_representation(self):
        """Test wishlist string representation."""
        expected = f"Wishlist for {self.user.username}"
        self.assertEqual(str(self.wishlist), expected)

class OrderModelTest(TestCase):
    """Test cases for Order model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Test Category')
        self.brand = Brand.objects.create(name='Test Brand')
        self.product = Product.objects.create(
            name='Test Product',
            brand=self.brand,
            category=self.category,
            price=Decimal('99.99')
        )
        self.order = Order.objects.create(
            user=self.user,
            shipping_address='Test Address',
            phone='1234567890',
            email='test@example.com',
            subtotal=Decimal('99.99'),
            shipping_cost=Decimal('10.00'),
            total=Decimal('109.99')
        )

    def test_order_creation(self):
        """Test order creation."""
        self.assertEqual(self.order.user, self.user)
        self.assertTrue(self.order.order_number)
        self.assertEqual(self.order.status, 'pending')

    def test_order_str_representation(self):
        """Test order string representation."""
        self.assertEqual(str(self.order), self.order.order_number)

    def test_order_total_calculation(self):
        """Test order total calculation."""
        self.assertEqual(
            self.order.total,
            self.order.subtotal + self.order.shipping_cost
        )

class CartViewTest(TestCase):
    """Test cases for cart views."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Test Category')
        self.brand = Brand.objects.create(name='Test Brand')
        self.product = Product.objects.create(
            name='Test Product',
            brand=self.brand,
            category=self.category,
            price=Decimal('99.99')
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            size='M',
            color='Blue',
            sku='TEST-SKU-001',
            stock=10
        )
        self.client.login(username='testuser', password='testpass123')

    def test_cart_detail_view(self):
        """Test cart detail view."""
        response = self.client.get(reverse('cart:detail'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cart/cart_detail.html')

    def test_add_to_cart(self):
        """Test adding item to cart."""
        response = self.client.post(
            reverse('cart:add'),
            {
                'product_variant_id': self.variant.id,
                'quantity': 1
            }
        )
        self.assertEqual(response.status_code, 302)
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.items.count(), 1)

    def test_remove_from_cart(self):
        """Test removing item from cart."""
        cart = Cart.objects.create(user=self.user)
        cart_item = CartItem.objects.create(
            cart=cart,
            product_variant=self.variant,
            quantity=1
        )
        response = self.client.post(
            reverse('cart:remove'),
            {'item_id': cart_item.id}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(cart.items.count(), 0)

    def test_update_cart(self):
        """Test updating cart item quantity."""
        cart = Cart.objects.create(user=self.user)
        cart_item = CartItem.objects.create(
            cart=cart,
            product_variant=self.variant,
            quantity=1
        )
        response = self.client.post(
            reverse('cart:update'),
            {
                'item_id': cart_item.id,
                'quantity': 2
            }
        )
        self.assertEqual(response.status_code, 302)
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 2)

class WishlistViewTest(TestCase):
    """Test cases for wishlist views."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Test Category')
        self.brand = Brand.objects.create(name='Test Brand')
        self.product = Product.objects.create(
            name='Test Product',
            brand=self.brand,
            category=self.category,
            price=Decimal('99.99')
        )
        self.client.login(username='testuser', password='testpass123')

    def test_wishlist_detail_view(self):
        """Test wishlist detail view."""
        response = self.client.get(reverse('cart:wishlist'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cart/wishlist.html')

    def test_add_to_wishlist(self):
        """Test adding product to wishlist."""
        response = self.client.post(
            reverse('cart:add_to_wishlist'),
            {'product_id': self.product.id}
        )
        self.assertEqual(response.status_code, 302)
        wishlist = Wishlist.objects.get(user=self.user)
        self.assertEqual(wishlist.products.count(), 1)

    def test_remove_from_wishlist(self):
        """Test removing product from wishlist."""
        wishlist = Wishlist.objects.create(user=self.user)
        wishlist.products.add(self.product)
        response = self.client.post(
            reverse('cart:remove_from_wishlist'),
            {'product_id': self.product.id}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(wishlist.products.count(), 0)
