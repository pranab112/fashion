"""
Forms for the products app.
"""

from typing import Any, Dict, List
from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from .models import Product, Review, Category, Brand, ProductVariant
from .validators import (
    validate_price,
    validate_discount_percentage,
    validate_review_text,
    validate_review_title,
    validate_stock_level
)

class ProductForm(forms.ModelForm):
    """Form for creating/editing products."""

    class Meta:
        model = Product
        fields = [
            'name',
            'category',
            'brand',
            'description',
            'base_price',
            'discount_percentage',
            'gender',
            'tags',
            'status',
            'is_featured'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'tags': forms.SelectMultiple(attrs={'class': 'select2'})
        }

    def clean(self) -> Dict[str, Any]:
        """Validate form data."""
        cleaned_data = super().clean()
        
        # Validate discount percentage
        base_price = cleaned_data.get('base_price')
        discount_percentage = cleaned_data.get('discount_percentage')
        
        if base_price and discount_percentage:
            if discount_percentage < 0 or discount_percentage > 100:
                raise ValidationError(
                    _('Discount percentage must be between 0 and 100.')
                )
        
        return cleaned_data

class ProductVariantForm(forms.ModelForm):
    """Form for creating/editing product variants."""

    class Meta:
        model = ProductVariant
        fields = [
            'name',
            'sku',
            'stock',
            'price_adjustment',
            'is_active'
        ]

    def clean(self) -> Dict[str, Any]:
        """Validate form data."""
        cleaned_data = super().clean()
        
        # Validate price adjustment
        price_adjustment = cleaned_data.get('price_adjustment')
        if price_adjustment:
            product = self.instance.product if self.instance else None
            if product and price_adjustment >= product.base_price:
                raise ValidationError(
                    _('Price adjustment cannot be greater than or equal to base price.')
                )
        
        return cleaned_data

class ProductImageForm(forms.Form):
    """Form for uploading product images."""

    image = forms.ImageField(
        label=_('Image'),
        help_text=_('Upload a product image (max 5MB).')
    )
    
    is_primary = forms.BooleanField(
        required=False,
        initial=False,
        label=_('Set as primary image')
    )

    def clean_image(self) -> Any:
        """Validate uploaded image."""
        image = self.cleaned_data['image']
        
        if image.size > 5 * 1024 * 1024:  # 5MB
            raise ValidationError(
                _('Image size cannot exceed 5MB.')
            )
        
        return image

class ReviewForm(forms.ModelForm):
    """Form for creating/editing reviews."""

    class Meta:
        model = Review
        fields = ['title', 'text', 'rating']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4}),
            'rating': forms.RadioSelect()
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize form."""
        self.user = kwargs.pop('user', None)
        self.product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)

    def clean(self) -> Dict[str, Any]:
        """Validate form data."""
        cleaned_data = super().clean()
        
        if self.user and self.product:
            # Check if user has already reviewed this product
            if not self.instance.pk and Review.objects.filter(
                user=self.user,
                product=self.product
            ).exists():
                raise ValidationError(
                    _('You have already reviewed this product.')
                )
        
        return cleaned_data

class ProductFilterForm(forms.Form):
    """Form for filtering products."""

    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        empty_label=_('All Categories')
    )
    
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.filter(is_active=True),
        required=False,
        empty_label=_('All Brands')
    )
    
    min_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'placeholder': _('Min Price')})
    )
    
    max_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'placeholder': _('Max Price')})
    )
    
    gender = forms.ChoiceField(
        required=False,
        choices=[('', _('All'))] + Product.GENDER_CHOICES
    )
    
    rating = forms.ChoiceField(
        required=False,
        choices=[
            ('', _('Any Rating')),
            ('4', _('4+ Stars')),
            ('3', _('3+ Stars')),
            ('2', _('2+ Stars')),
            ('1', _('1+ Stars'))
        ]
    )
    
    sort = forms.ChoiceField(
        required=False,
        choices=[
            ('', _('Default')),
            ('price_asc', _('Price: Low to High')),
            ('price_desc', _('Price: High to Low')),
            ('name_asc', _('Name: A to Z')),
            ('name_desc', _('Name: Z to A')),
            ('newest', _('Newest First')),
            ('rating', _('Highest Rated'))
        ]
    )
    
    in_stock = forms.BooleanField(
        required=False,
        label=_('In Stock Only')
    )
    
    on_sale = forms.BooleanField(
        required=False,
        label=_('On Sale Only')
    )

    def clean(self) -> Dict[str, Any]:
        """Validate form data."""
        cleaned_data = super().clean()
        
        min_price = cleaned_data.get('min_price')
        max_price = cleaned_data.get('max_price')
        
        if min_price and max_price and min_price > max_price:
            raise ValidationError(
                _('Minimum price cannot be greater than maximum price.')
            )
        
        return cleaned_data

class BulkProductUpdateForm(forms.Form):
    """Form for bulk updating products."""

    action = forms.ChoiceField(
        choices=[
            ('activate', _('Set Active')),
            ('deactivate', _('Set Inactive')),
            ('delete', _('Delete')),
            ('update_price', _('Update Price')),
            ('update_discount', _('Update Discount'))
        ]
    )
    
    products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.all(),
        widget=forms.CheckboxSelectMultiple()
    )
    
    base_price = forms.DecimalField(
        required=False,
        validators=[validate_price],
        help_text=_('New base price for selected products')
    )
    
    discount_percentage = forms.IntegerField(
        required=False,
        validators=[validate_discount_percentage],
        help_text=_('Discount percentage to apply')
    )

    def clean(self) -> Dict[str, Any]:
        """Validate form data."""
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        
        if action == 'update_price' and not cleaned_data.get('base_price'):
            raise ValidationError(
                _('Base price is required for price update action.')
            )
        
        if action == 'update_discount' and not cleaned_data.get('discount_percentage'):
            raise ValidationError(
                _('Discount percentage is required for discount update action.')
            )
        
        return cleaned_data

class ProductImportForm(forms.Form):
    """Form for importing products from CSV/Excel."""

    file = forms.FileField(
        help_text=_('Upload CSV or Excel file')
    )
    
    update_existing = forms.BooleanField(
        required=False,
        initial=False,
        help_text=_('Update existing products if SKU matches')
    )

    def clean_file(self) -> Any:
        """Validate uploaded file."""
        file = self.cleaned_data['file']
        ext = file.name.split('.')[-1].lower()
        
        if ext not in ['csv', 'xlsx', 'xls']:
            raise ValidationError(
                _('Only CSV and Excel files are supported.')
            )
        
        if file.size > 10 * 1024 * 1024:  # 10MB
            raise ValidationError(
                _('File size cannot exceed 10MB.')
            )
        
        return file
