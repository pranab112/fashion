from rest_framework import serializers
from .models import Product, ProductVariant, Category, Brand, Tag, ProductImage

class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'parent']

class BrandSerializer(serializers.ModelSerializer):
    """Serializer for Brand model."""
    
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'description', 'logo', 'website']

class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag model."""
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']

class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for ProductImage model."""
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary']

class ProductVariantSerializer(serializers.ModelSerializer):
    """Serializer for ProductVariant model."""
    
    class Meta:
        model = ProductVariant
        fields = ['id', 'sku', 'size', 'color', 'stock', 'weight']

class ProductListSerializer(serializers.ModelSerializer):
    """Serializer for Product model (list view)."""
    
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    primary_image = serializers.SerializerMethodField()
    discounted_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'slug',
            'category',
            'brand',
            'base_price',
            'discount_percentage',
            'discounted_price',
            'primary_image',
            'is_featured',
            'is_new_arrival'
        ]
    
    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return ProductImageSerializer(primary_image).data
        return None

class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model (detail view)."""
    
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    discounted_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'slug',
            'description',
            'category',
            'brand',
            'tags',
            'gender',
            'base_price',
            'discount_percentage',
            'discounted_price',
            'images',
            'variants',
            'is_active',
            'is_featured',
            'is_new_arrival',
            'created_at',
            'updated_at'
        ]
