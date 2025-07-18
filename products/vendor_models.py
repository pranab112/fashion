from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from decimal import Decimal

class VendorProfile(models.Model):
    """Extended vendor profile for users with vendor role."""
    
    PAYOUT_FREQUENCY_CHOICES = [
        ('weekly', _('Weekly')),
        ('biweekly', _('Bi-weekly')),
        ('monthly', _('Monthly')),
    ]
    
    user = models.OneToOneField(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='vendor_profile',
        verbose_name=_('User')
    )
    
    # Payout settings
    payout_frequency = models.CharField(
        _('Payout frequency'),
        max_length=20,
        choices=PAYOUT_FREQUENCY_CHOICES,
        default='monthly'
    )
    bank_account_name = models.CharField(
        _('Bank account name'),
        max_length=200,
        blank=True
    )
    bank_account_number = models.CharField(
        _('Bank account number'),
        max_length=50,
        blank=True
    )
    bank_name = models.CharField(
        _('Bank name'),
        max_length=100,
        blank=True
    )
    bank_routing_number = models.CharField(
        _('Bank routing number'),
        max_length=50,
        blank=True
    )
    
    # Statistics
    total_sales = models.DecimalField(
        _('Total sales'),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    total_orders = models.PositiveIntegerField(
        _('Total orders'),
        default=0
    )
    average_rating = models.DecimalField(
        _('Average rating'),
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.00')
    )
    total_reviews = models.PositiveIntegerField(
        _('Total reviews'),
        default=0
    )
    
    # Verification documents
    id_document = models.FileField(
        _('ID document'),
        upload_to='vendor_documents/id/',
        blank=True,
        null=True
    )
    business_license = models.FileField(
        _('Business license'),
        upload_to='vendor_documents/license/',
        blank=True,
        null=True
    )
    tax_document = models.FileField(
        _('Tax document'),
        upload_to='vendor_documents/tax/',
        blank=True,
        null=True
    )
    
    created_at = models.DateTimeField(_('Created at'), default=timezone.now)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Vendor profile')
        verbose_name_plural = _('Vendor profiles')
    
    def __str__(self):
        return f"Vendor Profile - {self.user.username}"


class VendorPayout(models.Model):
    """Track vendor payouts."""
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
    ]
    
    vendor = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='payouts',
        verbose_name=_('Vendor')
    )
    amount = models.DecimalField(
        _('Amount'),
        max_digits=10,
        decimal_places=2
    )
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    period_start = models.DateField(_('Period start'))
    period_end = models.DateField(_('Period end'))
    transaction_id = models.CharField(
        _('Transaction ID'),
        max_length=100,
        blank=True
    )
    notes = models.TextField(_('Notes'), blank=True)
    created_at = models.DateTimeField(_('Created at'), default=timezone.now)
    processed_at = models.DateTimeField(
        _('Processed at'),
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = _('Vendor payout')
        verbose_name_plural = _('Vendor payouts')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payout {self.vendor.username} - {self.amount}"


class VendorOrder(models.Model):
    """Track vendor-specific order information."""
    
    order = models.ForeignKey(
        'cart.Order',
        on_delete=models.CASCADE,
        related_name='vendor_orders'
    )
    vendor = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='vendor_orders'
    )
    subtotal = models.DecimalField(
        _('Subtotal'),
        max_digits=10,
        decimal_places=2
    )
    commission_amount = models.DecimalField(
        _('Commission amount'),
        max_digits=10,
        decimal_places=2
    )
    vendor_amount = models.DecimalField(
        _('Vendor amount'),
        max_digits=10,
        decimal_places=2
    )
    payout = models.ForeignKey(
        VendorPayout,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )
    created_at = models.DateTimeField(_('Created at'), default=timezone.now)
    
    class Meta:
        verbose_name = _('Vendor order')
        verbose_name_plural = _('Vendor orders')
        unique_together = ['order', 'vendor']
    
    def __str__(self):
        return f"Order {self.order.id} - Vendor {self.vendor.username}"
