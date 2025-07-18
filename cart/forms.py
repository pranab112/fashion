from django import forms
from django.utils.translation import gettext_lazy as _
from products.models import ProductVariant

class CartAddProductForm(forms.Form):
    """Form for adding products to cart."""
    
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'value': 1
        })
    )
    variant = forms.ModelChoiceField(
        queryset=ProductVariant.objects.none(),
        required=False,
        empty_label=_("Select variant"),
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    def __init__(self, *args, product=None, **kwargs):
        super().__init__(*args, **kwargs)
        if product:
            self.fields['variant'].queryset = product.variants.filter(is_active=True)

class CheckoutForm(forms.Form):
    """Form for checkout process."""
    
    # Contact Information
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Email address')
        })
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Phone number')
        })
    )
    
    # Billing Information
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('First name')
        })
    )
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Last name')
        })
    )
    address = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Street address')
        })
    )
    apartment = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Apartment, suite, etc. (optional)')
        })
    )
    city = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('City')
        })
    )
    state = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('State/Province')
        })
    )
    postal_code = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('ZIP/Postal code')
        })
    )
    country = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Country')
        })
    )
    
    # Shipping Information
    different_shipping = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    shipping_first_name = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('First name')
        })
    )
    shipping_last_name = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Last name')
        })
    )
    shipping_address = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Street address')
        })
    )
    shipping_apartment = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Apartment, suite, etc. (optional)')
        })
    )
    shipping_city = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('City')
        })
    )
    shipping_state = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('State/Province')
        })
    )
    shipping_postal_code = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('ZIP/Postal code')
        })
    )
    shipping_country = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Country')
        })
    )
    
    # Additional Information
    order_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': _('Notes about your order, e.g. special notes for delivery')
        })
    )
    
    # Terms and Newsletter
    accept_terms = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    subscribe_newsletter = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        different_shipping = cleaned_data.get('different_shipping')
        
        if different_shipping:
            shipping_fields = [
                'shipping_first_name', 'shipping_last_name', 'shipping_address',
                'shipping_city', 'shipping_state', 'shipping_postal_code',
                'shipping_country'
            ]
            
            for field in shipping_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, _('This field is required for different shipping address.'))
        
        return cleaned_data
