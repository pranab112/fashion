from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from .models import Address

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'phone',
            'date_of_birth',
            'avatar',
            'bio'
        )
        read_only_fields = ('id',)

class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users."""
    
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password',
            'password2',
            'first_name',
            'last_name'
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {'password2': _("The two password fields didn't match.")}
            )
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class AddressSerializer(serializers.ModelSerializer):
    """Serializer for Address model."""
    
    class Meta:
        model = Address
        fields = (
            'id',
            'address_type',
            'first_name',
            'last_name',
            'phone',
            'street_address',
            'apartment',
            'city',
            'state',
            'postal_code',
            'country',
            'is_default'
        )
        read_only_fields = ('id',)

class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change."""
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password2 = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError(
                {'new_password2': _("The two password fields didn't match.")}
            )
        return attrs
