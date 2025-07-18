from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from typing import Dict, Any, Optional
from .validators import (
    UserValidators,
    ProductValidators,
    OrderValidators,
    FileValidators
)

User = get_user_model()

class UserRegistrationForm(forms.ModelForm):
    """Form for user registration."""

    password = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput,
        validators=[UserValidators.password_validator]
    )
    confirm_password = forms.CharField(
        label=_('Confirm Password'),
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = [
            'email', 'username', 'first_name',
            'last_name', 'password', 'confirm_password'
        ]

    def clean(self) -> Dict[str, Any]:
        """Validate form data."""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password:
            if password != confirm_password:
                raise ValidationError({
                    'confirm_password': _("Passwords do not match.")
                })

            UserValidators.validate_password_strength(password)

        return cleaned_data

class UserProfileForm(forms.ModelForm):
    """Form for user profile updates."""

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email',
            'phone', 'date_of_birth', 'avatar'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'avatar': forms.FileInput(attrs={'accept': 'image/*'})
        }

    def clean_avatar(self):
        """Validate avatar image."""
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            FileValidators.validate_image(avatar)
        return avatar

class AddressForm(forms.ModelForm):
    """Form for user addresses."""

    class Meta:
        model = 'users.Address'
        fields = [
            'type', 'street', 'city', 'state',
            'country', 'postal_code', 'is_default'
        ]

    def clean(self) -> Dict[str, Any]:
        """Validate address data."""
        cleaned_data = super().clean()
        OrderValidators.validate_shipping_address(cleaned_data)
        return cleaned_data

class ProductForm(forms.ModelForm):
    """Form for product management."""

    class Meta:
        model = 'products.Product'
        fields = [
            'name', 'description', 'price', 'category',
            'brand', 'sku', 'stock_quantity', 'images',
            'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'images': forms.FileInput(attrs={
                'multiple': True,
                'accept': 'image/*'
            })
        }

    def clean_price(self):
        """Validate product price."""
        price = self.cleaned_data.get('price')
        ProductValidators.validate_price(price)
        return price

    def clean_stock_quantity(self):
        """Validate stock quantity."""
        quantity = self.cleaned_data.get('stock_quantity')
        ProductValidators.validate_stock_quantity(quantity)
        return quantity

    def clean_images(self):
        """Validate product images."""
        images = self.cleaned_data.get('images')
        if images:
            for image in images:
                FileValidators.validate_image(image)
        return images

class ProductVariantForm(forms.ModelForm):
    """Form for product variants."""

    class Meta:
        model = 'products.ProductVariant'
        fields = [
            'product', 'size', 'color', 'sku',
            'price', 'stock_quantity', 'is_active'
        ]

    def clean(self) -> Dict[str, Any]:
        """Validate variant data."""
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        size = cleaned_data.get('size')
        color = cleaned_data.get('color')

        if product and size:
            ProductValidators.validate_size(size, product.category.name)

        if color:
            ProductValidators.validate_color(color)

        return cleaned_data

class ReviewForm(forms.ModelForm):
    """Form for product reviews."""

    class Meta:
        model = 'products.Review'
        fields = ['product', 'rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={
                'min': '1',
                'max': '5'
            }),
            'comment': forms.Textarea(attrs={'rows': 3})
        }

    def clean_rating(self):
        """Validate review rating."""
        rating = self.cleaned_data.get('rating')
        if rating:
            ReviewValidators.validate_rating(rating)
        return rating

    def clean_comment(self):
        """Validate review comment."""
        comment = self.cleaned_data.get('comment')
        if comment:
            ReviewValidators.validate_review_text(comment)
        return comment

class ContactForm(forms.Form):
    """Form for contact messages."""

    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    subject = forms.CharField(max_length=200)
    message = forms.CharField(widget=forms.Textarea)

    def clean_message(self):
        """Validate contact message."""
        message = self.cleaned_data.get('message')
        if len(message) < 20:
            raise ValidationError(
                _("Message must be at least 20 characters long.")
            )
        return message

class NewsletterForm(forms.Form):
    """Form for newsletter subscription."""

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': _('Enter your email')
        })
    )

class SearchForm(forms.Form):
    """Form for product search."""

    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': _('Search products...')
        })
    )
    category = forms.ModelChoiceField(
        queryset='products.Category'.objects.all(),
        required=False
    )
    min_price = forms.DecimalField(required=False)
    max_price = forms.DecimalField(required=False)
    sort_by = forms.ChoiceField(
        choices=[
            ('price_asc', _('Price: Low to High')),
            ('price_desc', _('Price: High to Low')),
            ('newest', _('Newest First')),
            ('popular', _('Most Popular')),
            ('rating', _('Highest Rated'))
        ],
        required=False
    )

class PaymentMethodForm(forms.ModelForm):
    """Form for payment methods."""

    class Meta:
        model = 'payments.PaymentMethod'
        fields = [
            'type', 'card_number', 'expiry_month',
            'expiry_year', 'cvv', 'name_on_card',
            'is_default'
        ]
        widgets = {
            'card_number': forms.TextInput(attrs={
                'autocomplete': 'cc-number'
            }),
            'cvv': forms.TextInput(attrs={
                'autocomplete': 'cc-csc'
            }),
            'name_on_card': forms.TextInput(attrs={
                'autocomplete': 'cc-name'
            })
        }

    def clean(self) -> Dict[str, Any]:
        """Validate payment method data."""
        cleaned_data = super().clean()
        card_number = cleaned_data.get('card_number')
        
        if card_number:
            from .utils import ValidationUtils
            if not ValidationUtils.validate_credit_card(card_number):
                raise ValidationError({
                    'card_number': _("Invalid credit card number.")
                })

        return cleaned_data

class OrderNoteForm(forms.ModelForm):
    """Form for order notes."""

    class Meta:
        model = 'orders.OrderNote'
        fields = ['order', 'note', 'is_public']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 3})
        }

class ReturnRequestForm(forms.ModelForm):
    """Form for return requests."""

    class Meta:
        model = 'orders.ReturnRequest'
        fields = ['order', 'items', 'reason', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4})
        }

    def clean_items(self):
        """Validate return items."""
        items = self.cleaned_data.get('items')
        if not items:
            raise ValidationError(
                _("Please select at least one item to return.")
            )
        return items
