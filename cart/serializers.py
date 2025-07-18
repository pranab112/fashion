from rest_framework import serializers
from products.serializers import ProductSerializer, ProductVariantSerializer
from .models import Cart, CartItem

class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for cart items."""
    
    product = ProductSerializer(read_only=True)
    variant = ProductVariantSerializer(read_only=True)
    total = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = CartItem
        fields = [
            'id',
            'product',
            'variant',
            'quantity',
            'price',
            'total',
            'created_at',
            'updated_at'
        ]

class CartSerializer(serializers.ModelSerializer):
    """Serializer for shopping cart."""
    
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    subtotal = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    total = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Cart
        fields = [
            'id',
            'user',
            'items',
            'total_items',
            'subtotal',
            'total',
            'created_at',
            'updated_at'
        ]
