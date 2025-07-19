from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

class CustomUser(AbstractUser):
    """Custom user model."""
    
    USER_TYPE_CHOICES = [
        ('customer', _('Customer')),
        ('vendor', _('Vendor')),
        ('admin', _('Admin')),
    ]
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    user_type = models.CharField(
        _('User type'),
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='customer'
    )
    phone = models.CharField(
        _('Phone number'),
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True
    )
    date_of_birth = models.DateField(
        _('Date of birth'),
        blank=True,
        null=True
    )
    avatar = models.ImageField(
        _('Avatar'),
        upload_to='avatars/',
        blank=True,
        null=True
    )
    bio = models.TextField(
        _('Bio'),
        blank=True
    )
    is_vendor_approved = models.BooleanField(
        _('Vendor approved'),
        default=False,
        help_text=_('Designates whether this vendor has been approved to sell products.')
    )
    vendor_commission_rate = models.DecimalField(
        _('Vendor commission rate'),
        max_digits=5,
        decimal_places=2,
        default=10.00,
        help_text=_('Commission percentage charged on vendor sales')
    )
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
    
    def __str__(self):
        return self.email or self.username
    
    @property
    def is_vendor(self):
        """Check if user is a vendor."""
        return self.user_type == 'vendor' and self.is_vendor_approved
    
    @property
    def is_customer(self):
        """Check if user is a customer."""
        return self.user_type == 'customer'

class Address(models.Model):
    """User address model."""
    
    ADDRESS_TYPES = [
        ('H', _('Home')),
        ('W', _('Work')),
        ('O', _('Other')),
    ]
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name=_('User')
    )
    address_type = models.CharField(
        _('Address type'),
        max_length=1,
        choices=ADDRESS_TYPES,
        default='H'
    )
    first_name = models.CharField(
        _('First name'),
        max_length=100,
        default=''
    )
    last_name = models.CharField(
        _('Last name'),
        max_length=100,
        default=''
    )
    phone = models.CharField(
        _('Phone number'),
        max_length=17,
        validators=[CustomUser.phone_regex],
        default=''
    )
    street_address = models.CharField(
        _('Street address'),
        max_length=255,
        default=''
    )
    apartment = models.CharField(
        _('Apartment, suite, etc.'),
        max_length=100,
        blank=True,
        default=''
    )
    city = models.CharField(
        _('City'),
        max_length=100,
        default=''
    )
    state = models.CharField(
        _('State/Province'),
        max_length=100,
        default=''
    )
    postal_code = models.CharField(
        _('Postal code'),
        max_length=20,
        default=''
    )
    country = models.CharField(
        _('Country'),
        max_length=100,
        default=''
    )
    is_default = models.BooleanField(
        _('Default address'),
        default=False
    )
    
    class Meta:
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses')
        ordering = ['-is_default', 'id']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.get_address_type_display()}"
    
    def save(self, *args, **kwargs):
        if self.is_default:
            # Ensure only one default address per user
            Address.objects.filter(
                user=self.user,
                is_default=True
            ).update(is_default=False)
        super().save(*args, **kwargs)


