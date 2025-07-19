from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid


class OrderStatus(models.Model):
    """Model to track order status progression."""
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('confirmed', _('Confirmed')),
        ('processing', _('Processing')),
        ('shipped', _('Shipped')),
        ('delivered', _('Delivered')),
        ('cancelled', _('Cancelled')),
        ('returned', _('Returned')),
        ('refunded', _('Refunded')),
    ]
    
    name = models.CharField(_('Status Name'), max_length=50, choices=STATUS_CHOICES, unique=True)
    description = models.TextField(_('Description'), blank=True)
    is_active = models.BooleanField(_('Active'), default=True)
    order = models.PositiveIntegerField(_('Display Order'), default=0)
    
    class Meta:
        verbose_name = _('Order Status')
        verbose_name_plural = _('Order Statuses')
        ordering = ['order']
    
    def __str__(self):
        return self.get_name_display()


class Order(models.Model):
    """Main order model for sales management."""
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled')),
        ('refunded', _('Refunded')),
    ]
    
    # Order identification
    order_number = models.CharField(_('Order Number'), max_length=50, unique=True)
    order_id = models.UUIDField(_('Order ID'), default=uuid.uuid4, editable=False, unique=True)
    
    # Customer information
    customer = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='sales_orders',
        verbose_name=_('Customer')
    )
    customer_email = models.EmailField(_('Customer Email'))
    customer_phone = models.CharField(_('Customer Phone'), max_length=20, blank=True)
    
    # Shipping information
    shipping_first_name = models.CharField(_('First Name'), max_length=100)
    shipping_last_name = models.CharField(_('Last Name'), max_length=100)
    shipping_address_line1 = models.CharField(_('Address Line 1'), max_length=255)
    shipping_address_line2 = models.CharField(_('Address Line 2'), max_length=255, blank=True)
    shipping_city = models.CharField(_('City'), max_length=100)
    shipping_state = models.CharField(_('State'), max_length=100)
    shipping_postal_code = models.CharField(_('Postal Code'), max_length=20)
    shipping_country = models.CharField(_('Country'), max_length=100, default='India')
    
    # Billing information (can be same as shipping)
    billing_first_name = models.CharField(_('Billing First Name'), max_length=100)
    billing_last_name = models.CharField(_('Billing Last Name'), max_length=100)
    billing_address_line1 = models.CharField(_('Billing Address Line 1'), max_length=255)
    billing_address_line2 = models.CharField(_('Billing Address Line 2'), max_length=255, blank=True)
    billing_city = models.CharField(_('Billing City'), max_length=100)
    billing_state = models.CharField(_('Billing State'), max_length=100)
    billing_postal_code = models.CharField(_('Billing Postal Code'), max_length=20)
    billing_country = models.CharField(_('Billing Country'), max_length=100, default='India')
    
    # Order totals
    subtotal = models.DecimalField(_('Subtotal'), max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(_('Tax Amount'), max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(_('Shipping Cost'), max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(_('Discount Amount'), max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(_('Total Amount'), max_digits=10, decimal_places=2)
    
    # Status tracking
    status = models.CharField(
        _('Order Status'),
        max_length=20,
        choices=OrderStatus.STATUS_CHOICES,
        default='pending'
    )
    payment_status = models.CharField(
        _('Payment Status'),
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    
    # Payment information
    payment_method = models.CharField(_('Payment Method'), max_length=50, blank=True)
    payment_gateway = models.CharField(_('Payment Gateway'), max_length=50, blank=True)
    payment_gateway_order_id = models.CharField(_('Gateway Order ID'), max_length=100, blank=True)
    
    # Order notes and tracking
    customer_notes = models.TextField(_('Customer Notes'), blank=True)
    admin_notes = models.TextField(_('Admin Notes'), blank=True)
    tracking_number = models.CharField(_('Tracking Number'), max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('Created at'), default=timezone.now)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)
    shipped_at = models.DateTimeField(_('Shipped at'), null=True, blank=True)
    delivered_at = models.DateTimeField(_('Delivered at'), null=True, blank=True)
    
    # Multi-vendor fields
    is_multi_vendor = models.BooleanField(_('Multi-vendor Order'), default=False)
    
    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.order_number}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number
            import time
            timestamp = str(int(time.time()))[-6:]
            self.order_number = f"ORD{timestamp}{self.pk or ''}"
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('sales:order_detail', kwargs={'order_number': self.order_number})
    
    @property
    def full_shipping_address(self):
        """Get formatted shipping address."""
        address_parts = [
            f"{self.shipping_first_name} {self.shipping_last_name}",
            self.shipping_address_line1,
        ]
        if self.shipping_address_line2:
            address_parts.append(self.shipping_address_line2)
        address_parts.extend([
            f"{self.shipping_city}, {self.shipping_state} {self.shipping_postal_code}",
            self.shipping_country
        ])
        return ", ".join(address_parts)
    
    @property
    def total_items(self):
        """Get total number of items in order."""
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0
    
    @property
    def vendors(self):
        """Get all vendors involved in this order."""
        from products.models import Brand
        brand_ids = self.items.values_list('product__brand_id', flat=True).distinct()
        return Brand.objects.filter(id__in=brand_ids, vendor__isnull=False)
    
    @property
    def vendor_count(self):
        """Get number of vendors in this order."""
        return self.vendors.count()
    
    def calculate_totals(self):
        """Recalculate order totals based on items."""
        items = self.items.all()
        self.subtotal = sum(item.total_price for item in items)
        
        # Calculate tax (assuming 18% GST for India)
        self.tax_amount = self.subtotal * Decimal('0.18')
        
        # Calculate total
        self.total_amount = self.subtotal + self.tax_amount + self.shipping_cost - self.discount_amount
        self.save()
    
    def can_be_cancelled(self):
        """Check if order can be cancelled."""
        return self.status in ['pending', 'confirmed']
    
    def can_be_shipped(self):
        """Check if order can be shipped."""
        return self.status in ['confirmed', 'processing'] and self.payment_status == 'completed'


class OrderItem(models.Model):
    """Individual items within an order."""
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Order')
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='sales_order_items',
        verbose_name=_('Product')
    )
    product_variant = models.ForeignKey(
        'products.ProductVariant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sales_order_items',
        verbose_name=_('Product Variant')
    )
    
    # Product details at time of purchase (for historical accuracy)
    product_name = models.CharField(_('Product Name'), max_length=200)
    product_sku = models.CharField(_('Product SKU'), max_length=100, blank=True)
    brand_name = models.CharField(_('Brand Name'), max_length=100, blank=True)
    size = models.CharField(_('Size'), max_length=50, blank=True)
    color = models.CharField(_('Color'), max_length=50, blank=True)
    
    # Pricing details
    unit_price = models.DecimalField(_('Unit Price'), max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(_('Quantity'), default=1)
    total_price = models.DecimalField(_('Total Price'), max_digits=10, decimal_places=2)
    
    # Vendor information
    vendor = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sold_items',
        verbose_name=_('Vendor')
    )
    vendor_commission_rate = models.DecimalField(
        _('Commission Rate'),
        max_digits=5,
        decimal_places=2,
        default=10.00
    )
    vendor_commission = models.DecimalField(
        _('Vendor Commission'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    
    # Item status (for multi-vendor orders)
    status = models.CharField(
        _('Item Status'),
        max_length=20,
        choices=OrderStatus.STATUS_CHOICES,
        default='pending'
    )
    
    created_at = models.DateTimeField(_('Created at'), default=timezone.now)
    
    class Meta:
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')
    
    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        # Calculate total price
        self.total_price = self.unit_price * self.quantity
        
        # Calculate vendor commission
        if self.vendor:
            self.vendor_commission = self.total_price * (self.vendor_commission_rate / 100)
        
        # Store product details at time of purchase
        if self.product:
            self.product_name = self.product.name
            if self.product.brand:
                self.brand_name = self.product.brand.name
                if self.product.brand.vendor:
                    self.vendor = self.product.brand.vendor
                    self.vendor_commission_rate = self.product.brand.effective_commission_rate
        
        if self.product_variant:
            self.product_sku = self.product_variant.sku
            self.size = self.product_variant.size
            self.color = self.product_variant.color
        
        super().save(*args, **kwargs)


class Payment(models.Model):
    """Payment tracking for orders."""
    
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', _('Credit Card')),
        ('debit_card', _('Debit Card')),
        ('upi', _('UPI')),
        ('net_banking', _('Net Banking')),
        ('wallet', _('Digital Wallet')),
        ('cod', _('Cash on Delivery')),
        ('bank_transfer', _('Bank Transfer')),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled')),
        ('refunded', _('Refunded')),
        ('partially_refunded', _('Partially Refunded')),
    ]
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_('Order')
    )
    payment_id = models.UUIDField(_('Payment ID'), default=uuid.uuid4, editable=False, unique=True)
    
    # Payment details
    amount = models.DecimalField(_('Amount'), max_digits=10, decimal_places=2)
    currency = models.CharField(_('Currency'), max_length=10, default='INR')
    payment_method = models.CharField(
        _('Payment Method'),
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES
    )
    status = models.CharField(
        _('Payment Status'),
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    
    # Gateway information
    gateway = models.CharField(_('Payment Gateway'), max_length=50, blank=True)
    gateway_transaction_id = models.CharField(_('Gateway Transaction ID'), max_length=100, blank=True)
    gateway_response = models.JSONField(_('Gateway Response'), default=dict, blank=True)
    
    # Additional details
    notes = models.TextField(_('Notes'), blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('Created at'), default=timezone.now)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)
    processed_at = models.DateTimeField(_('Processed at'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment {self.payment_id} - {self.amount} {self.currency}"


class Commission(models.Model):
    """Track vendor commissions for each sale."""
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('paid', _('Paid')),
        ('cancelled', _('Cancelled')),
    ]
    
    vendor = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='commissions',
        verbose_name=_('Vendor')
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='commissions',
        verbose_name=_('Order')
    )
    order_item = models.ForeignKey(
        OrderItem,
        on_delete=models.CASCADE,
        related_name='commissions',
        verbose_name=_('Order Item')
    )
    
    # Commission details
    gross_amount = models.DecimalField(_('Gross Amount'), max_digits=10, decimal_places=2)
    commission_rate = models.DecimalField(_('Commission Rate (%)'), max_digits=5, decimal_places=2)
    commission_amount = models.DecimalField(_('Commission Amount'), max_digits=10, decimal_places=2)
    platform_fee = models.DecimalField(_('Platform Fee'), max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(_('Net Amount'), max_digits=10, decimal_places=2)
    
    # Status and processing
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('Created at'), default=timezone.now)
    approved_at = models.DateTimeField(_('Approved at'), null=True, blank=True)
    paid_at = models.DateTimeField(_('Paid at'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Commission')
        verbose_name_plural = _('Commissions')
        ordering = ['-created_at']
        unique_together = ['vendor', 'order_item']
    
    def __str__(self):
        return f"Commission for {self.vendor.get_full_name()} - Order #{self.order.order_number}"
    
    def save(self, *args, **kwargs):
        # Calculate net amount after platform fee
        self.net_amount = self.commission_amount - self.platform_fee
        super().save(*args, **kwargs)


class Payout(models.Model):
    """Track vendor payouts."""
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled')),
    ]
    
    vendor = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='payouts',
        verbose_name=_('Vendor')
    )
    payout_id = models.UUIDField(_('Payout ID'), default=uuid.uuid4, editable=False, unique=True)
    
    # Payout details
    amount = models.DecimalField(_('Payout Amount'), max_digits=10, decimal_places=2)
    currency = models.CharField(_('Currency'), max_length=10, default='INR')
    
    # Bank details
    bank_account_number = models.CharField(_('Bank Account Number'), max_length=50)
    bank_name = models.CharField(_('Bank Name'), max_length=100)
    ifsc_code = models.CharField(_('IFSC Code'), max_length=20)
    account_holder_name = models.CharField(_('Account Holder Name'), max_length=100)
    
    # Status and processing
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # References
    commissions = models.ManyToManyField(
        Commission,
        related_name='payouts',
        verbose_name=_('Commissions')
    )
    
    # Processing details
    transaction_reference = models.CharField(_('Transaction Reference'), max_length=100, blank=True)
    processing_fee = models.DecimalField(_('Processing Fee'), max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(_('Net Amount Paid'), max_digits=10, decimal_places=2)
    
    # Notes
    notes = models.TextField(_('Notes'), blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('Created at'), default=timezone.now)
    processed_at = models.DateTimeField(_('Processed at'), null=True, blank=True)
    completed_at = models.DateTimeField(_('Completed at'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Payout')
        verbose_name_plural = _('Payouts')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payout {self.payout_id} - {self.vendor.get_full_name()}"
    
    def save(self, *args, **kwargs):
        # Calculate net amount after processing fee
        self.net_amount = self.amount - self.processing_fee
        super().save(*args, **kwargs)


class SalesReport(models.Model):
    """Pre-calculated sales reports for performance."""
    
    REPORT_TYPE_CHOICES = [
        ('daily', _('Daily')),
        ('weekly', _('Weekly')),
        ('monthly', _('Monthly')),
        ('yearly', _('Yearly')),
    ]
    
    # Report identification
    report_type = models.CharField(_('Report Type'), max_length=20, choices=REPORT_TYPE_CHOICES)
    report_date = models.DateField(_('Report Date'))
    vendor = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sales_reports',
        verbose_name=_('Vendor')
    )
    
    # Sales metrics
    total_orders = models.PositiveIntegerField(_('Total Orders'), default=0)
    total_revenue = models.DecimalField(_('Total Revenue'), max_digits=15, decimal_places=2, default=0)
    total_items_sold = models.PositiveIntegerField(_('Total Items Sold'), default=0)
    total_commissions = models.DecimalField(_('Total Commissions'), max_digits=15, decimal_places=2, default=0)
    
    # Order status breakdown
    pending_orders = models.PositiveIntegerField(_('Pending Orders'), default=0)
    completed_orders = models.PositiveIntegerField(_('Completed Orders'), default=0)
    cancelled_orders = models.PositiveIntegerField(_('Cancelled Orders'), default=0)
    returned_orders = models.PositiveIntegerField(_('Returned Orders'), default=0)
    
    # Financial metrics
    average_order_value = models.DecimalField(_('Average Order Value'), max_digits=10, decimal_places=2, default=0)
    total_refunds = models.DecimalField(_('Total Refunds'), max_digits=10, decimal_places=2, default=0)
    net_revenue = models.DecimalField(_('Net Revenue'), max_digits=15, decimal_places=2, default=0)
    
    # Timestamps
    created_at = models.DateTimeField(_('Created at'), default=timezone.now)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Sales Report')
        verbose_name_plural = _('Sales Reports')
        ordering = ['-report_date']
        unique_together = ['report_type', 'report_date', 'vendor']
    
    def __str__(self):
        vendor_str = f" - {self.vendor.get_full_name()}" if self.vendor else " - Platform"
        return f"{self.get_report_type_display()} Report {self.report_date}{vendor_str}"


class OrderStatusHistory(models.Model):
    """Track order status changes for audit trail."""
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='status_history',
        verbose_name=_('Order')
    )
    from_status = models.CharField(
        _('From Status'),
        max_length=20,
        choices=OrderStatus.STATUS_CHOICES,
        blank=True
    )
    to_status = models.CharField(
        _('To Status'),
        max_length=20,
        choices=OrderStatus.STATUS_CHOICES
    )
    changed_by = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_status_changes',
        verbose_name=_('Changed By')
    )
    notes = models.TextField(_('Notes'), blank=True)
    created_at = models.DateTimeField(_('Changed at'), default=timezone.now)
    
    class Meta:
        verbose_name = _('Order Status History')
        verbose_name_plural = _('Order Status Histories')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.order.order_number}: {self.from_status} → {self.to_status}"