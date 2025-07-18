from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from products.models import Product, ProductVariant

class CartManager(models.Manager):
    def get_or_create_from_session(self, request):
        """Get or create cart from session."""
        cart_id = request.session.get('cart_id')
        if cart_id:
            try:
                cart = self.get(id=cart_id)
            except Cart.DoesNotExist:
                cart = self.create()
        else:
            cart = self.create()
        
        request.session['cart_id'] = cart.id
        return cart

class Cart(models.Model):
    """Shopping cart model."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='carts'
    )
    created_at = models.DateTimeField(_('Created at'), default=timezone.now)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)

    objects = CartManager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Cart {self.id}"

    @property
    def total_items(self):
        """Get total number of items in cart."""
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        """Calculate cart subtotal."""
        return sum(item.total for item in self.items.all())

    @property
    def total(self):
        """Calculate cart total including shipping and tax."""
        subtotal = self.subtotal
        
        # Add shipping cost if below free shipping threshold
        if subtotal < settings.FREE_SHIPPING_THRESHOLD:
            subtotal += settings.BASE_SHIPPING_RATE
            
        # Add tax
        tax = subtotal * (settings.TAX_RATE / 100)
        
        return subtotal + tax

    def add(self, product, variant=None, quantity=1):
        """Add product to cart."""
        item, created = self.items.get_or_create(
            product=product,
            variant=variant,
            defaults={'quantity': quantity}
        )
        
        if not created:
            item.quantity += quantity
            item.save()

    def remove(self, product, variant=None):
        """Remove product from cart."""
        self.items.filter(product=product, variant=variant).delete()

    def update(self, product, variant=None, quantity=1):
        """Update product quantity in cart."""
        self.items.filter(product=product, variant=variant).update(quantity=quantity)

    def clear(self):
        """Remove all items from cart."""
        self.items.all().delete()

class CartItem(models.Model):
    """Shopping cart item model."""
    
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='cart_items'
    )
    quantity = models.PositiveIntegerField(_('Quantity'), default=1)
    created_at = models.DateTimeField(_('Created at'), default=timezone.now)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['cart', 'product', 'variant']

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def price(self):
        """Get item price."""
        if self.variant:
            return self.variant.final_price
        return self.product.discounted_price if self.product.is_on_sale else self.product.base_price

    @property
    def total(self):
        """Calculate item total."""
        return self.price * self.quantity

class Order(models.Model):
    """Order model."""
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('shipped', _('Shipped')),
        ('delivered', _('Delivered')),
        ('cancelled', _('Cancelled')),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Contact Information
    email = models.EmailField(_('Email'), default='')
    phone = models.CharField(_('Phone'), max_length=20, default='')
    
    # Billing Information
    billing_first_name = models.CharField(_('First name'), max_length=100, default='')
    billing_last_name = models.CharField(_('Last name'), max_length=100, default='')
    billing_address = models.CharField(_('Address'), max_length=250, default='')
    billing_apartment = models.CharField(_('Apartment'), max_length=100, blank=True)
    billing_city = models.CharField(_('City'), max_length=100, default='')
    billing_state = models.CharField(_('State'), max_length=100, default='')
    billing_postal_code = models.CharField(_('Postal code'), max_length=20, default='')
    billing_country = models.CharField(_('Country'), max_length=100, default='')
    
    # Shipping Information
    different_shipping = models.BooleanField(_('Different shipping address'), default=False)
    shipping_first_name = models.CharField(_('First name'), max_length=100, blank=True)
    shipping_last_name = models.CharField(_('Last name'), max_length=100, blank=True)
    shipping_address = models.CharField(_('Address'), max_length=250, blank=True)
    shipping_apartment = models.CharField(_('Apartment'), max_length=100, blank=True)
    shipping_city = models.CharField(_('City'), max_length=100, blank=True)
    shipping_state = models.CharField(_('State'), max_length=100, blank=True)
    shipping_postal_code = models.CharField(_('Postal code'), max_length=20, blank=True)
    shipping_country = models.CharField(_('Country'), max_length=100, blank=True)
    
    # Order Information
    subtotal = models.DecimalField(_('Subtotal'), max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(_('Shipping cost'), max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(_('Tax'), max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(_('Total'), max_digits=10, decimal_places=2, default=0)
    
    order_notes = models.TextField(_('Order notes'), blank=True)
    tracking_number = models.CharField(_('Tracking number'), max_length=100, blank=True)
    
    created_at = models.DateTimeField(_('Created at'), default=timezone.now)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.id}"

    def save(self, *args, **kwargs):
        if not self.shipping_first_name and not self.different_shipping:
            # Copy billing address to shipping address if not different
            self.shipping_first_name = self.billing_first_name
            self.shipping_last_name = self.billing_last_name
            self.shipping_address = self.billing_address
            self.shipping_apartment = self.billing_apartment
            self.shipping_city = self.billing_city
            self.shipping_state = self.billing_state
            self.shipping_postal_code = self.billing_postal_code
            self.shipping_country = self.billing_country
        
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    """Order item model."""
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        related_name='order_items'
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_items'
    )
    quantity = models.PositiveIntegerField(_('Quantity'), default=1)
    price = models.DecimalField(_('Price'), max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(_('Total'), max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(_('Created at'), default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.quantity}x {self.product.name if self.product else 'Deleted product'}"

    def save(self, *args, **kwargs):
        self.total = self.price * self.quantity
        super().save(*args, **kwargs)
