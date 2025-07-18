from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from typing import Dict, Any, List
from .validators import (
    UserValidators,
    ProductValidators,
    OrderValidators,
    FileValidators,
    ReviewValidators
)

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer for user model."""

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[UserValidators.password_validator]
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True
    )

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'password', 'confirm_password', 'phone', 'date_joined',
            'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate user data."""
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError({
                'confirm_password': _("Passwords do not match.")
            })

        UserValidators.validate_password_strength(data.get('password'))
        return data

    def create(self, validated_data: Dict[str, Any]) -> User:
        """Create new user."""
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        return user

class ProductSerializer(serializers.ModelSerializer):
    """Serializer for product model."""

    class Meta:
        model = 'products.Product'
        fields = [
            'id', 'name', 'description', 'price', 'category',
            'brand', 'sku', 'stock_quantity', 'is_active',
            'created_at', 'updated_at', 'images', 'variants'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_price(self, value: float) -> float:
        """Validate product price."""
        ProductValidators.validate_price(value)
        return value

    def validate_stock_quantity(self, value: int) -> int:
        """Validate stock quantity."""
        ProductValidators.validate_stock_quantity(value)
        return value

class OrderSerializer(serializers.ModelSerializer):
    """Serializer for order model."""

    class Meta:
        model = 'orders.Order'
        fields = [
            'id', 'user', 'items', 'total_amount', 'status',
            'shipping_address', 'billing_address', 'payment_info',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_shipping_address(self, value: Dict[str, Any]) -> Dict[str, Any]:
        """Validate shipping address."""
        OrderValidators.validate_shipping_address(value)
        return value

    def validate_payment_info(self, value: Dict[str, Any]) -> Dict[str, Any]:
        """Validate payment information."""
        OrderValidators.validate_payment_info(value)
        return value

class CartSerializer(serializers.ModelSerializer):
    """Serializer for cart model."""

    class Meta:
        model = 'cart.Cart'
        fields = [
            'id', 'user', 'items', 'total_amount',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_amount', 'created_at', 'updated_at']

class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for cart item model."""

    class Meta:
        model = 'cart.CartItem'
        fields = ['id', 'cart', 'product', 'quantity', 'price']
        read_only_fields = ['id', 'price']

    def validate_quantity(self, value: int) -> int:
        """Validate item quantity."""
        if value < 1:
            raise serializers.ValidationError(
                _("Quantity must be at least 1.")
            )
        return value

class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for review model."""

    class Meta:
        model = 'products.Review'
        fields = [
            'id', 'product', 'user', 'rating', 'comment',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_rating(self, value: int) -> int:
        """Validate review rating."""
        ReviewValidators.validate_rating(value)
        return value

    def validate_comment(self, value: str) -> str:
        """Validate review comment."""
        ReviewValidators.validate_review_text(value)
        return value

class AddressSerializer(serializers.ModelSerializer):
    """Serializer for address model."""

    class Meta:
        model = 'users.Address'
        fields = [
            'id', 'user', 'type', 'street', 'city', 'state',
            'country', 'postal_code', 'is_default'
        ]
        read_only_fields = ['id']

    def validate_postal_code(self, value: str) -> str:
        """Validate postal code."""
        country = self.initial_data.get('country')
        if not country:
            raise serializers.ValidationError(
                _("Country is required to validate postal code.")
            )

        from .utils import ValidationUtils
        if not ValidationUtils.validate_postal_code(value, country):
            raise serializers.ValidationError(
                _("Invalid postal code for the specified country.")
            )
        return value

class WishlistSerializer(serializers.ModelSerializer):
    """Serializer for wishlist model."""

    class Meta:
        model = 'users.Wishlist'
        fields = ['id', 'user', 'products', 'created_at']
        read_only_fields = ['id', 'created_at']

class CategorySerializer(serializers.ModelSerializer):
    """Serializer for category model."""

    class Meta:
        model = 'products.Category'
        fields = [
            'id', 'name', 'slug', 'description', 'parent',
            'image', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

class BrandSerializer(serializers.ModelSerializer):
    """Serializer for brand model."""

    class Meta:
        model = 'products.Brand'
        fields = [
            'id', 'name', 'slug', 'description', 'logo',
            'website', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for product image model."""

    class Meta:
        model = 'products.ProductImage'
        fields = ['id', 'product', 'image', 'alt_text', 'order']
        read_only_fields = ['id']

    def validate_image(self, value):
        """Validate product image."""
        FileValidators.validate_image(value)
        return value

class ProductVariantSerializer(serializers.ModelSerializer):
    """Serializer for product variant model."""

    class Meta:
        model = 'products.ProductVariant'
        fields = [
            'id', 'product', 'size', 'color', 'sku',
            'price', 'stock_quantity', 'is_active'
        ]
        read_only_fields = ['id']

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate variant data."""
        if 'size' in data:
            ProductValidators.validate_size(
                data['size'],
                data['product'].category.name
            )

        if 'color' in data:
            ProductValidators.validate_color(data['color'])

        return data

class PaymentMethodSerializer(serializers.ModelSerializer):
    """Serializer for payment method model."""

    class Meta:
        model = 'payments.PaymentMethod'
        fields = [
            'id', 'user', 'type', 'provider', 'account_number',
            'expiry_date', 'is_default', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def validate_account_number(self, value: str) -> str:
        """Validate account number."""
        from .utils import ValidationUtils
        if not ValidationUtils.validate_credit_card(value):
            raise serializers.ValidationError(
                _("Invalid credit card number.")
            )
        return value
