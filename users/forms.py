from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, Address

class CustomUserCreationForm(UserCreationForm):
    """Form for creating new users."""
    
    phone = forms.CharField(
        max_length=17,
        required=False,
        help_text=_('Optional. Enter your phone number.')
    )
    
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'phone')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make email required
        self.fields['email'].required = True
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(_('A user with this email already exists.'))
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        # Use email as username
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class CustomUserChangeForm(UserChangeForm):
    """Form for updating users."""
    
    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name')

class UserProfileForm(forms.ModelForm):
    """Form for updating user profile information."""
    
    class Meta:
        model = CustomUser
        fields = (
            'first_name',
            'last_name',
            'email',
            'phone',
            'date_of_birth',
            'avatar',
            'bio'
        )
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

class AddressForm(forms.ModelForm):
    """Form for creating/updating user addresses."""
    
    class Meta:
        model = Address
        fields = (
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
        widgets = {
            'apartment': forms.TextInput(
                attrs={'placeholder': _('Apartment, suite, unit, etc. (optional)')}
            ),
        }
