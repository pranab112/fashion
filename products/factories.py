"""
Test factories for the products app.
"""

import factory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyText, FuzzyDecimal, FuzzyInteger, FuzzyChoice
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from .models import (
    Product,
    Category,
    Brand,
    ProductImage,
    Review,
    Tag,
    SearchQuery,
    ProductView
)
from .constants import (
    STATUS_CHOICES,
    GENDER_CHOICES,
    RATING_CHOICES,
    COLORS,
    SIZES_CLOTHING
)

User = get_user_model()

class CategoryFactory(DjangoModelFactory):
    """Factory for Category model."""
    
    class Meta:
        model = Category
    
    name = factory.Sequence(lambda n: f'Category {n}')
    slug = factory.LazyAttribute(lambda obj: f'category-{obj.name.lower()}')
    description = factory.Faker('paragraph')
    is_active = True
    order = factory.Sequence(lambda n: n)
    meta_title = factory.LazyAttribute(lambda obj: f'Buy {obj.name}')
    meta_description = factory.Faker('sentence')
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)

    @factory.post_generation
    def image(self, create, extracted, **kwargs):
        """Add image after generation."""
        if not create:
            return

        if extracted:
            self.image = extracted
        else:
            # Generate a dummy image
            from PIL import Image
            import io
            file = io.BytesIO()
            image = Image.new('RGB', (100, 100), 'blue')
            image.save(file, 'PNG')
            self.image.save(f'{self.name}.png', ContentFile(file.getvalue()), save=False)

class BrandFactory(DjangoModelFactory):
    """Factory for Brand model."""
    
    class Meta:
        model = Brand
    
    name = factory.Sequence(lambda n: f'Brand {n}')
    slug = factory.LazyAttribute(lambda obj: f'brand-{obj.name.lower()}')
    description = factory.Faker('paragraph')
    website = factory.Faker('url')
    is_active = True
    meta_title = factory.LazyAttribute(lambda obj: f'Buy {obj.name} Products')
    meta_description = factory.Faker('sentence')
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)

    @factory.post_generation
    def logo(self, create, extracted, **kwargs):
        """Add logo after generation."""
        if not create:
            return

        if extracted:
            self.logo = extracted
        else:
            # Generate a dummy logo
            from PIL import Image
            import io
            file = io.BytesIO()
            image = Image.new('RGB', (100, 100), 'red')
            image.save(file, 'PNG')
            self.logo.save(f'{self.name}_logo.png', ContentFile(file.getvalue()), save=False)

class TagFactory(DjangoModelFactory):
    """Factory for Tag model."""
    
    class Meta:
        model = Tag
    
    name = factory.Sequence(lambda n: f'Tag {n}')
    slug = factory.LazyAttribute(lambda obj: f'tag-{obj.name.lower()}')

class ProductFactory(DjangoModelFactory):
    """Factory for Product model."""
    
    class Meta:
        model = Product
    
    name = factory.Sequence(lambda n: f'Product {n}')
    slug = factory.LazyAttribute(lambda obj: f'product-{obj.name.lower()}')
    sku = factory.Sequence(lambda n: f'SKU{n:06d}')
    description = factory.Faker('paragraph')
    price = FuzzyDecimal(10.0, 1000.0, 2)
    sale_price = factory.LazyAttribute(lambda obj: obj.price * 0.8 if factory.Faker('boolean') else None)
    category = factory.SubFactory(CategoryFactory)
    brand = factory.SubFactory(BrandFactory)
    stock = FuzzyInteger(0, 100)
    low_stock_threshold = 10
    status = FuzzyChoice(dict(STATUS_CHOICES).keys())
    gender = FuzzyChoice(dict(GENDER_CHOICES).keys())
    weight = FuzzyDecimal(0.1, 5.0, 2)
    available_sizes = factory.List([factory.Iterator(SIZES_CLOTHING) for _ in range(3)])
    available_colors = factory.List([factory.Iterator(COLORS.keys()) for _ in range(3)])
    is_featured = factory.Faker('boolean')
    is_new_arrival = factory.Faker('boolean')
    is_on_sale = factory.LazyAttribute(lambda obj: bool(obj.sale_price))
    meta_title = factory.LazyAttribute(lambda obj: f'Buy {obj.name}')
    meta_description = factory.Faker('sentence')
    view_count = FuzzyInteger(0, 1000)
    average_rating = FuzzyDecimal(1.0, 5.0, 1)
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        """Add tags after generation."""
        if not create:
            return

        if extracted:
            for tag in extracted:
                self.tags.add(tag)
        else:
            self.tags.add(TagFactory())

class ProductImageFactory(DjangoModelFactory):
    """Factory for ProductImage model."""
    
    class Meta:
        model = ProductImage
    
    product = factory.SubFactory(ProductFactory)
    alt_text = factory.LazyAttribute(lambda obj: f'Image of {obj.product.name}')
    is_primary = factory.Faker('boolean')
    order = factory.Sequence(lambda n: n)
    created_at = factory.LazyFunction(timezone.now)

    @factory.post_generation
    def image(self, create, extracted, **kwargs):
        """Add image after generation."""
        if not create:
            return

        if extracted:
            self.image = extracted
        else:
            # Generate a dummy product image
            from PIL import Image
            import io
            file = io.BytesIO()
            image = Image.new('RGB', (800, 800), 'green')
            image.save(file, 'PNG')
            self.image.save(f'product_{self.product.id}.png', ContentFile(file.getvalue()), save=False)

class ReviewFactory(DjangoModelFactory):
    """Factory for Review model."""
    
    class Meta:
        model = Review
    
    product = factory.SubFactory(ProductFactory)
    user = factory.SubFactory('users.factories.UserFactory')  # Assuming you have a UserFactory
    title = factory.Faker('sentence')
    text = factory.Faker('paragraph')
    rating = FuzzyChoice(dict(RATING_CHOICES).keys())
    is_verified = factory.Faker('boolean')
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)

class SearchQueryFactory(DjangoModelFactory):
    """Factory for SearchQuery model."""
    
    class Meta:
        model = SearchQuery
    
    query = FuzzyText(length=10)
    count = FuzzyInteger(1, 1000)
    success_rate = FuzzyDecimal(0.0, 1.0, 2)
    last_searched = factory.LazyFunction(timezone.now)

class ProductViewFactory(DjangoModelFactory):
    """Factory for ProductView model."""
    
    class Meta:
        model = ProductView
    
    product = factory.SubFactory(ProductFactory)
    user = factory.SubFactory('users.factories.UserFactory', null=True)  # Optional user
    session_key = factory.Faker('sha1')
    ip_address = factory.Faker('ipv4')
    user_agent = factory.Faker('user_agent')
    referrer = factory.Faker('url')
    created_at = factory.LazyFunction(timezone.now)

def create_sample_products(count: int = 10) -> list:
    """
    Create sample products with related objects.
    
    Args:
        count: Number of products to create
        
    Returns:
        list: Created products
    """
    # Create categories
    categories = CategoryFactory.create_batch(3)
    
    # Create brands
    brands = BrandFactory.create_batch(3)
    
    # Create tags
    tags = TagFactory.create_batch(5)
    
    # Create products
    products = []
    for _ in range(count):
        product = ProductFactory(
            category=factory.random.choice(categories),
            brand=factory.random.choice(brands)
        )
        
        # Add random tags
        product.tags.add(*factory.random.sample(tags, factory.random.randint(1, 3)))
        
        # Add images
        ProductImageFactory.create_batch(
            factory.random.randint(1, 4),
            product=product
        )
        
        # Add reviews
        ReviewFactory.create_batch(
            factory.random.randint(0, 5),
            product=product
        )
        
        products.append(product)
    
    return products
