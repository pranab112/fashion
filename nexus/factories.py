import factory
from factory.django import DjangoModelFactory
from factory import fuzzy, Faker, SubFactory, LazyAttribute
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import random
from .models import (
    Product,
    Category,
    Order,
    OrderItem,
    Cart,
    CartItem,
    Review,
    Address,
    Brand,
    ProductVariant,
    PaymentMethod
)

User = get_user_model()

class UserFactory(DjangoModelFactory):
    """Factory for User model."""

    class Meta:
        model = User

    email = factory.Sequence(lambda n: f'user{n}@example.com')
    username = factory.Sequence(lambda n: f'user{n}')
    first_name = Faker('first_name')
    last_name = Faker('last_name')
    password = factory.PostGenerationMethodCall('set_password', 'password123')
    is_active = True
    date_joined = Faker('date_time_this_year', tzinfo=timezone.utc)

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        """Add groups to user."""
        if not create:
            return

        if extracted:
            for group in extracted:
                self.groups.add(group)

class CategoryFactory(DjangoModelFactory):
    """Factory for Category model."""

    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f'Category {n}')
    slug = factory.LazyAttribute(lambda obj: factory.Faker('slug').generate({}) + str(random.randint(1, 1000)))
    description = Faker('paragraph')
    is_active = True
    parent = None
    image = factory.django.ImageField(color='blue')

class BrandFactory(DjangoModelFactory):
    """Factory for Brand model."""

    class Meta:
        model = Brand

    name = factory.Sequence(lambda n: f'Brand {n}')
    slug = factory.LazyAttribute(lambda obj: factory.Faker('slug').generate({}) + str(random.randint(1, 1000)))
    description = Faker('paragraph')
    website = Faker('url')
    logo = factory.django.ImageField(color='red')
    is_active = True

class ProductFactory(DjangoModelFactory):
    """Factory for Product model."""

    class Meta:
        model = Product

    name = factory.Sequence(lambda n: f'Product {n}')
    slug = factory.LazyAttribute(lambda obj: factory.Faker('slug').generate({}) + str(random.randint(1, 1000)))
    description = Faker('paragraph')
    price = fuzzy.FuzzyDecimal(10.0, 1000.0, precision=2)
    category = SubFactory(CategoryFactory)
    brand = SubFactory(BrandFactory)
    sku = factory.Sequence(lambda n: f'SKU{n:06d}')
    stock_quantity = fuzzy.FuzzyInteger(0, 100)
    is_active = True
    created_at = Faker('date_time_this_year', tzinfo=timezone.utc)

    @factory.post_generation
    def images(self, create, extracted, **kwargs):
        """Add images to product."""
        if not create:
            return

        if extracted:
            for image in extracted:
                self.images.add(image)

class ProductVariantFactory(DjangoModelFactory):
    """Factory for ProductVariant model."""

    class Meta:
        model = ProductVariant

    product = SubFactory(ProductFactory)
    size = fuzzy.FuzzyChoice(['XS', 'S', 'M', 'L', 'XL'])
    color = fuzzy.FuzzyChoice(['Red', 'Blue', 'Green', 'Black', 'White'])
    sku = factory.Sequence(lambda n: f'VAR{n:06d}')
    price = fuzzy.FuzzyDecimal(10.0, 1000.0, precision=2)
    stock_quantity = fuzzy.FuzzyInteger(0, 100)
    is_active = True

class AddressFactory(DjangoModelFactory):
    """Factory for Address model."""

    class Meta:
        model = Address

    user = SubFactory(UserFactory)
    type = fuzzy.FuzzyChoice(['shipping', 'billing'])
    street = Faker('street_address')
    city = Faker('city')
    state = Faker('state')
    country = Faker('country_code')
    postal_code = Faker('postcode')
    is_default = False

class CartFactory(DjangoModelFactory):
    """Factory for Cart model."""

    class Meta:
        model = Cart

    user = SubFactory(UserFactory)
    created_at = Faker('date_time_this_year', tzinfo=timezone.utc)
    updated_at = Faker('date_time_this_year', tzinfo=timezone.utc)
    status = fuzzy.FuzzyChoice(['active', 'abandoned', 'converted'])

class CartItemFactory(DjangoModelFactory):
    """Factory for CartItem model."""

    class Meta:
        model = CartItem

    cart = SubFactory(CartFactory)
    product = SubFactory(ProductFactory)
    quantity = fuzzy.FuzzyInteger(1, 5)
    price = factory.LazyAttribute(lambda obj: obj.product.price)

class OrderFactory(DjangoModelFactory):
    """Factory for Order model."""

    class Meta:
        model = Order

    user = SubFactory(UserFactory)
    status = fuzzy.FuzzyChoice([
        'pending',
        'processing',
        'shipped',
        'delivered',
        'cancelled'
    ])
    total_amount = fuzzy.FuzzyDecimal(10.0, 1000.0, precision=2)
    shipping_address = SubFactory(AddressFactory)
    billing_address = SubFactory(AddressFactory)
    created_at = Faker('date_time_this_year', tzinfo=timezone.utc)
    payment_status = fuzzy.FuzzyChoice(['pending', 'paid', 'failed'])

class OrderItemFactory(DjangoModelFactory):
    """Factory for OrderItem model."""

    class Meta:
        model = OrderItem

    order = SubFactory(OrderFactory)
    product = SubFactory(ProductFactory)
    quantity = fuzzy.FuzzyInteger(1, 5)
    price = factory.LazyAttribute(lambda obj: obj.product.price)
    total_price = factory.LazyAttribute(
        lambda obj: obj.price * obj.quantity
    )

class ReviewFactory(DjangoModelFactory):
    """Factory for Review model."""

    class Meta:
        model = Review

    product = SubFactory(ProductFactory)
    user = SubFactory(UserFactory)
    rating = fuzzy.FuzzyInteger(1, 5)
    comment = Faker('paragraph')
    created_at = Faker('date_time_this_year', tzinfo=timezone.utc)
    status = fuzzy.FuzzyChoice(['pending', 'approved', 'rejected'])

class PaymentMethodFactory(DjangoModelFactory):
    """Factory for PaymentMethod model."""

    class Meta:
        model = PaymentMethod

    user = SubFactory(UserFactory)
    type = fuzzy.FuzzyChoice(['card', 'paypal', 'bank_transfer'])
    provider = fuzzy.FuzzyChoice(['stripe', 'paypal', 'bank'])
    account_number = factory.LazyAttribute(
        lambda _: ''.join([str(random.randint(0, 9)) for _ in range(16)])
    )
    expiry_date = Faker('future_date')
    is_default = False
    is_active = True

def create_sample_data(
    num_users: int = 10,
    num_categories: int = 5,
    num_brands: int = 5,
    num_products: int = 20,
    num_orders: int = 10
):
    """Create sample data for testing."""
    # Create users
    users = UserFactory.create_batch(num_users)

    # Create categories
    categories = CategoryFactory.create_batch(num_categories)

    # Create brands
    brands = BrandFactory.create_batch(num_brands)

    # Create products
    products = []
    for _ in range(num_products):
        product = ProductFactory(
            category=random.choice(categories),
            brand=random.choice(brands)
        )
        products.append(product)

        # Create variants
        for size in ['S', 'M', 'L']:
            for color in ['Red', 'Blue', 'Black']:
                ProductVariantFactory(
                    product=product,
                    size=size,
                    color=color
                )

    # Create orders
    for _ in range(num_orders):
        user = random.choice(users)
        
        # Create addresses
        shipping_address = AddressFactory(user=user, type='shipping')
        billing_address = AddressFactory(user=user, type='billing')

        # Create order
        order = OrderFactory(
            user=user,
            shipping_address=shipping_address,
            billing_address=billing_address
        )

        # Add order items
        num_items = random.randint(1, 5)
        order_products = random.sample(products, num_items)
        
        for product in order_products:
            OrderItemFactory(
                order=order,
                product=product
            )

        # Create reviews
        if order.status == 'delivered':
            for item in order.items.all():
                ReviewFactory(
                    product=item.product,
                    user=user
                )

    # Create carts
    for user in users:
        cart = CartFactory(user=user)
        num_items = random.randint(1, 3)
        cart_products = random.sample(products, num_items)
        
        for product in cart_products:
            CartItemFactory(
                cart=cart,
                product=product
            )

    # Create payment methods
    for user in users:
        PaymentMethodFactory(
            user=user,
            is_default=True
        )
