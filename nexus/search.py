from django_elasticsearch_dsl import Document, Index, fields
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import analyzer, tokenizer
from products.models import Product
from django.conf import settings

# Custom analyzers
html_strip = analyzer(
    'html_strip',
    tokenizer="standard",
    filter=["lowercase", "stop", "snowball"],
    char_filter=["html_strip"]
)

ngram_analyzer = analyzer(
    'ngram_analyzer',
    tokenizer=tokenizer(
        'ngram_tokenizer',
        type='ngram',
        min_gram=3,
        max_gram=4,
        token_chars=['letter', 'digit']
    ),
    filter=['lowercase']
)

# Define Elasticsearch indices
products = Index('products')
products.settings(
    number_of_shards=1,
    number_of_replicas=0,
    blocks={'read_only_allow_delete': False},
    analysis={
        'analyzer': {
            'html_strip': html_strip,
            'ngram_analyzer': ngram_analyzer
        }
    }
)

@registry.register_document
@products.document
class ProductDocument(Document):
    """Elasticsearch document for Product model."""
    
    # Basic product information
    id = fields.IntegerField()
    name = fields.TextField(
        analyzer='ngram_analyzer',
        fields={
            'raw': fields.KeywordField(),
            'suggest': fields.CompletionField(),
        }
    )
    slug = fields.KeywordField()
    description = fields.TextField(
        analyzer='html_strip',
        fields={
            'raw': fields.KeywordField(),
        }
    )
    
    # Pricing fields
    price = fields.FloatField()
    sale_price = fields.FloatField(null=True)
    discount_percentage = fields.FloatField(null=True)
    
    # Category and classification
    category = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'name': fields.KeywordField(),
        'slug': fields.KeywordField(),
    })
    brand = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'name': fields.KeywordField(),
        'slug': fields.KeywordField(),
    })
    tags = fields.KeywordField(multi=True)
    
    # Product attributes
    sku = fields.KeywordField()
    color = fields.KeywordField(multi=True)
    size = fields.KeywordField(multi=True)
    gender = fields.KeywordField()
    
    # Stock information
    in_stock = fields.BooleanField()
    stock_quantity = fields.IntegerField()
    
    # Metadata
    created_at = fields.DateField()
    updated_at = fields.DateField()
    is_active = fields.BooleanField()
    
    # Rating and reviews
    average_rating = fields.FloatField(null=True)
    review_count = fields.IntegerField()
    
    # Images
    images = fields.NestedField(properties={
        'id': fields.IntegerField(),
        'url': fields.KeywordField(),
        'alt_text': fields.TextField(),
        'is_primary': fields.BooleanField(),
    })

    class Django:
        model = Product
        related_models = ['category', 'brand', 'tags', 'images']

    def get_instances_from_related(self, related_instance):
        """Get related Product instances for indexing."""
        if isinstance(related_instance, Product.category.field.related_model):
            return related_instance.products.all()
        elif isinstance(related_instance, Product.brand.field.related_model):
            return related_instance.products.all()
        elif isinstance(related_instance, Product.tags.field.related_model):
            return related_instance.product_set.all()
        elif isinstance(related_instance, Product.images.field.related_model):
            return [related_instance.product]

    def prepare_category(self, instance):
        """Prepare category data for indexing."""
        if instance.category:
            return {
                'id': instance.category.id,
                'name': instance.category.name,
                'slug': instance.category.slug,
            }
        return None

    def prepare_brand(self, instance):
        """Prepare brand data for indexing."""
        if instance.brand:
            return {
                'id': instance.brand.id,
                'name': instance.brand.name,
                'slug': instance.brand.slug,
            }
        return None

    def prepare_tags(self, instance):
        """Prepare tags for indexing."""
        return [tag.name for tag in instance.tags.all()]

    def prepare_images(self, instance):
        """Prepare image data for indexing."""
        return [{
            'id': img.id,
            'url': img.image.url if img.image else None,
            'alt_text': img.alt_text,
            'is_primary': img.is_primary,
        } for img in instance.images.all()]

    def prepare_average_rating(self, instance):
        """Calculate and prepare average rating."""
        return instance.calculate_average_rating()

    def prepare_review_count(self, instance):
        """Prepare review count."""
        return instance.reviews.count()

    def prepare_discount_percentage(self, instance):
        """Calculate discount percentage if sale price exists."""
        if instance.sale_price and instance.price:
            return ((instance.price - instance.sale_price) / instance.price) * 100
        return None

# Search configuration
class ProductSearch:
    """Product search functionality."""

    @staticmethod
    def search(query, filters=None, sort_by=None, page=1, per_page=20):
        """
        Search products with filters and sorting.
        
        Args:
            query (str): Search query
            filters (dict): Filter parameters
            sort_by (str): Sort field and direction
            page (int): Page number
            per_page (int): Items per page
        """
        s = ProductDocument.search()

        # Apply search query
        if query:
            s = s.query('multi_match', 
                query=query,
                fields=['name^3', 'description', 'brand.name^2', 'category.name^2', 'tags'],
                fuzziness='AUTO'
            )

        # Apply filters
        if filters:
            for field, value in filters.items():
                if isinstance(value, (list, tuple)):
                    s = s.filter('terms', **{field: value})
                else:
                    s = s.filter('term', **{field: value})

        # Apply sorting
        if sort_by:
            s = s.sort(sort_by)

        # Apply pagination
        start = (page - 1) * per_page
        s = s[start:start + per_page]

        # Execute search
        response = s.execute()

        return {
            'total': response.hits.total.value,
            'products': response.hits,
            'aggregations': response.aggregations,
            'page': page,
            'per_page': per_page,
        }

    @staticmethod
    def get_suggestions(query, limit=5):
        """Get search suggestions for autocomplete."""
        s = ProductDocument.search()
        s = s.suggest('name_suggest', 
            query,
            completion={
                'field': 'name.suggest',
                'size': limit,
                'fuzzy': {
                    'fuzziness': 2
                }
            }
        )
        response = s.execute()
        return [
            suggestion.text 
            for suggestion in response.suggest.name_suggest[0].options
        ]

    @staticmethod
    def get_filters():
        """Get available filter options."""
        s = ProductDocument.search()
        s.aggs.bucket('categories', 'terms', field='category.name')
        s.aggs.bucket('brands', 'terms', field='brand.name')
        s.aggs.bucket('colors', 'terms', field='color')
        s.aggs.bucket('sizes', 'terms', field='size')
        s.aggs.bucket('price_ranges', 'range', field='price', ranges=[
            {'to': 50},
            {'from': 50, 'to': 100},
            {'from': 100, 'to': 200},
            {'from': 200}
        ])
        
        response = s.execute()
        return response.aggregations
