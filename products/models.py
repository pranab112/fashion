from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from mptt.models import MPTTModel, TreeForeignKey

class Category(MPTTModel):
    """Product category model."""
    
    name = models.CharField(_('Name'), max_length=100)
    slug = models.SlugField(_('Slug'), unique=True)
    description = models.TextField(_('Description'), blank=True)
    image = models.ImageField(
        _('Image'),
        upload_to='categories/',
        blank=True,
        null=True
    )
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_('Parent category')
    )
    is_active = models.BooleanField(_('Active'), default=True)
    
    # Mega menu fields
    show_in_mega_menu = models.BooleanField(
        _('Show in Mega Menu'),
        default=False,
        help_text=_('Display this category in the mega dropdown menu')
    )
    mega_menu_order = models.PositiveIntegerField(
        _('Mega Menu Order'),
        default=0,
        help_text=_('Order in mega menu (lower numbers appear first)')
    )
    mega_menu_column_title = models.CharField(
        _('Mega Menu Column Title'),
        max_length=100,
        blank=True,
        help_text=_('Custom title for mega menu column (leave blank to use category name)')
    )
    mega_menu_icon = models.CharField(
        _('Mega Menu Icon'),
        max_length=50,
        blank=True,
        help_text=_('FontAwesome icon class (e.g., fa-tshirt)')
    )
    
    created_at = models.DateTimeField(_('Created at'), default=timezone.now)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)
    
    # MPTT fields with defaults
    level = models.PositiveIntegerField(default=0)
    lft = models.PositiveIntegerField(default=0)
    rght = models.PositiveIntegerField(default=0)
    tree_id = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
    
    class MPTTMeta:
        order_insertion_by = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('products:category_detail', kwargs={'slug': self.slug})
    
    @property
    def mega_menu_title(self):
        """Get the title to display in mega menu."""
        return self.mega_menu_column_title or self.name
    
    def get_mega_menu_children(self):
        """Get children categories for mega menu display."""
        return self.children.filter(
            is_active=True,
            show_in_mega_menu=True
        ).order_by('mega_menu_order', 'name')
    
    @classmethod
    def get_mega_menu_categories(cls):
        """Get all main categories for mega menu."""
        return cls.objects.filter(
            is_active=True,
            show_in_mega_menu=True,
            parent=None
        ).order_by('mega_menu_order', 'name')

class Brand(models.Model):
    """Product brand model."""
    
    name = models.CharField(_('Name'), max_length=100)
    slug = models.SlugField(_('Slug'), unique=True)
    description = models.TextField(_('Description'), blank=True)
    logo = models.ImageField(
        _('Logo'),
        upload_to='brands/',
        blank=True,
        null=True
    )
    website = models.URLField(_('Website'), blank=True)
    
    # Multi-vendor fields
    vendor = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='brands',
        verbose_name=_('Vendor'),
        help_text=_('The vendor who owns this brand')
    )
    is_verified = models.BooleanField(
        _('Verified'),
        default=False,
        help_text=_('Designates whether this brand has been verified by admin')
    )
    commission_rate = models.DecimalField(
        _('Commission rate'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Custom commission rate for this brand (overrides vendor default)')
    )
    
    # Shop settings
    shop_banner = models.ImageField(
        _('Shop banner'),
        upload_to='brands/banners/',
        blank=True,
        null=True
    )
    shop_description = models.TextField(
        _('Shop description'),
        blank=True,
        help_text=_('Detailed description for the brand shop page')
    )
    return_policy = models.TextField(
        _('Return policy'),
        blank=True,
        help_text=_('Brand-specific return policy')
    )
    shipping_info = models.TextField(
        _('Shipping information'),
        blank=True,
        help_text=_('Brand-specific shipping information')
    )
    
    # Contact information
    contact_email = models.EmailField(
        _('Contact email'),
        blank=True
    )
    contact_phone = models.CharField(
        _('Contact phone'),
        max_length=20,
        blank=True
    )
    
    # Business information
    business_name = models.CharField(
        _('Business name'),
        max_length=200,
        blank=True
    )
    tax_id = models.CharField(
        _('Tax ID'),
        max_length=50,
        blank=True
    )
    
    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(_('Created at'), default=timezone.now)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Brand')
        verbose_name_plural = _('Brands')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('products:brand_detail', kwargs={'slug': self.slug})
    
    def get_shop_url(self):
        """Get the URL for the brand's shop page."""
        return reverse('products:brand_shop', kwargs={'slug': self.slug})
    
    @property
    def is_vendor_brand(self):
        """Check if this brand belongs to a vendor."""
        return self.vendor is not None
    
    @property
    def effective_commission_rate(self):
        """Get the effective commission rate for this brand."""
        if self.commission_rate:
            return self.commission_rate
        elif self.vendor:
            return self.vendor.vendor_commission_rate
        return 10.00  # Default commission rate

class Tag(models.Model):
    """Product tag model."""
    
    name = models.CharField(_('Name'), max_length=100)
    slug = models.SlugField(_('Slug'), unique=True)
    
    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('products:tag_detail', kwargs={'slug': self.slug})

class ProductQuerySet(models.QuerySet):
    def active(self):
        """Return only active products."""
        return self.filter(is_active=True)
    
    def with_related(self):
        """Return products with related fields."""
        return self.select_related(
            'category',
            'brand'
        ).prefetch_related(
            'tags',
            'images',
            'variants'
        )

class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)
    
    def active(self):
        """Return only active products."""
        return self.get_queryset().active()
    
    def with_related(self):
        """Return products with related fields."""
        return self.get_queryset().with_related()

class Product(models.Model):
    """Product model."""
    
    GENDER_CHOICES = [
        ('M', _('Men')),
        ('W', _('Women')),
        ('U', _('Unisex')),
        ('K', _('Kids')),
    ]
    
    name = models.CharField(_('Name'), max_length=200)
    slug = models.SlugField(_('Slug'), unique=True)
    description = models.TextField(_('Description'))
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name=_('Category')
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name=_('Brand')
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='products',
        verbose_name=_('Tags')
    )
    gender = models.CharField(
        _('Gender'),
        max_length=1,
        choices=GENDER_CHOICES,
        default='U'
    )
    base_price = models.DecimalField(
        _('Base price'),
        max_digits=10,
        decimal_places=2
    )
    discount_percentage = models.IntegerField(
        _('Discount percentage'),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0
    )
    # Simple stock field for products without variants
    simple_stock = models.PositiveIntegerField(
        _('Stock (for products without variants)'),
        default=0,
        help_text=_('Use this for simple products. For products with sizes/colors, use variants instead.')
    )
    manage_stock = models.BooleanField(
        _('Manage stock'),
        default=True,
        help_text=_('Track inventory for this product')
    )
    low_stock_threshold = models.PositiveIntegerField(
        _('Low stock alert threshold'),
        default=10,
        help_text=_('Alert when stock falls below this number')
    )
    is_active = models.BooleanField(_('Active'), default=True)
    is_featured = models.BooleanField(_('Featured'), default=False)
    is_new_arrival = models.BooleanField(_('New Arrival'), default=False)
    created_at = models.DateTimeField(_('Created at'), default=timezone.now)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)
    
    objects = ProductManager()
    
    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.slug})
    
    @property
    def discounted_price(self):
        """Calculate discounted price."""
        if self.discount_percentage:
            from decimal import Decimal
            discount = (Decimal(str(self.discount_percentage)) / Decimal('100')) * self.base_price
            return self.base_price - discount
        return self.base_price
    
    @property
    def savings(self):
        """Calculate savings amount."""
        return self.base_price - self.discounted_price
    
    @property
    def is_on_sale(self):
        """Check if product is on sale."""
        return self.discount_percentage > 0
    
    def get_primary_image(self):
        """Get the primary image for the product."""
        primary_image = self.images.filter(is_primary=True).first()
        if primary_image:
            return primary_image
        # Return first image if no primary image set
        return self.images.first()
    
    @property
    def price(self):
        """Get the current price (for template compatibility)."""
        return self.discounted_price
    
    @property
    def sale_price(self):
        """Get the sale price if product is on sale."""
        if self.is_on_sale:
            return self.discounted_price
        return None
    
    @property
    def average_rating(self):
        """Get average rating for the product."""
        # TODO: Implement when reviews are added
        return 4.5
    
    @property
    def available_sizes(self):
        """Get available sizes for the product."""
        return self.variants.filter(stock__gt=0).values_list('size', flat=True).distinct()
    
    @property
    def available_colors(self):
        """Get available colors for the product."""
        return self.variants.filter(stock__gt=0).values_list('color', flat=True).distinct()
    
    def get_color_choices(self):
        """Get color choices with hex values."""
        colors = self.available_colors
        # TODO: Implement proper color mapping
        color_map = {
            'red': '#FF0000',
            'blue': '#0000FF',
            'green': '#00FF00',
            'black': '#000000',
            'white': '#FFFFFF',
        }
        return [(color, color_map.get(color.lower(), '#CCCCCC')) for color in colors if color]
    
    @property
    def has_variants(self):
        """Check if product has size/color variants."""
        return self.variants.exists()
    
    @property
    def is_in_stock(self):
        """Check if product is in stock."""
        if self.has_variants:
            return self.variants.filter(stock__gt=0).exists()
        return self.simple_stock > 0
    
    @property
    def stock(self):
        """Get total stock count."""
        if self.has_variants:
            return self.variants.aggregate(total=models.Sum('stock'))['total'] or 0
        return self.simple_stock
    
    @property
    def is_low_stock(self):
        """Check if product has low stock."""
        return 0 < self.stock <= self.low_stock_threshold

class ProductImage(models.Model):
    """Product image model."""
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('Product')
    )
    image = models.ImageField(_('Image'), upload_to='products/')
    alt_text = models.CharField(_('Alt text'), max_length=200)
    is_primary = models.BooleanField(_('Primary image'), default=False)
    created_at = models.DateTimeField(_('Created at'), default=timezone.now)
    
    class Meta:
        verbose_name = _('Product image')
        verbose_name_plural = _('Product images')
        ordering = ['-is_primary', 'created_at']
    
    def __str__(self):
        return f"{self.product.name} - {'Primary' if self.is_primary else 'Secondary'}"
    
    def save(self, *args, **kwargs):
        if self.is_primary:
            # Ensure only one primary image per product
            self.__class__.objects.filter(
                product=self.product,
                is_primary=True
            ).update(is_primary=False)
        super().save(*args, **kwargs)
    
    def get_thumbnail_url(self):
        """Get thumbnail URL for the image."""
        # For now, return the original image URL
        # TODO: Implement proper thumbnail generation
        return self.image.url if self.image else None
    
    @property
    def url(self):
        """Get the image URL."""
        return self.image.url if self.image else None

class ProductVariant(models.Model):
    """Product variant model."""
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants',
        verbose_name=_('Product')
    )
    sku = models.CharField(_('SKU'), max_length=100, unique=True)
    size = models.CharField(_('Size'), max_length=50, null=True, blank=True)
    color = models.CharField(_('Color'), max_length=50, null=True, blank=True)
    stock = models.PositiveIntegerField(_('Stock'), default=0)
    weight = models.DecimalField(
        _('Weight (kg)'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(_('Created at'), default=timezone.now)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Product variant')
        verbose_name_plural = _('Product variants')
        unique_together = ['product', 'size', 'color']
    
    def __str__(self):
        variant_parts = []
        if self.size:
            variant_parts.append(self.size)
        if self.color:
            variant_parts.append(self.color)
        variant_str = " - ".join(variant_parts) if variant_parts else "Default"
        return f"{self.product.name} - {variant_str}"
    
    @property
    def is_in_stock(self):
        """Check if variant is in stock."""
        return self.stock > 0


# Homepage Featured Models
class FeaturedProduct(models.Model):
    """Model to feature products in different homepage sections."""
    
    SECTION_CHOICES = [
        ('deal_of_day', _('Deal of the Day')),
        ('top_picks', _('Top Picks')),
        ('trending_now', _('Trending Now')),
        ('indian_wear', _('Indian Wear')),
        ('sports_wear', _('Sports Wear')),
        ('footwear', _('Footwear')),
    ]
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='featured_in'
    )
    section = models.CharField(
        _('Section'),
        max_length=50,
        choices=SECTION_CHOICES
    )
    is_active = models.BooleanField(_('Active'), default=True)
    order = models.PositiveIntegerField(_('Display Order'), default=0)
    featured_until = models.DateTimeField(
        _('Featured Until'),
        null=True,
        blank=True,
        help_text=_('Leave blank for permanent featuring')
    )
    created_at = models.DateTimeField(_('Created at'), default=timezone.now)
    
    class Meta:
        verbose_name = _('Featured Product')
        verbose_name_plural = _('Featured Products')
        ordering = ['section', 'order', 'created_at']
        unique_together = ['product', 'section']
    
    def __str__(self):
        return f"{self.product.name} in {self.get_section_display()}"
    
    @property
    def is_expired(self):
        """Check if the featured product has expired."""
        if self.featured_until:
            return timezone.now() > self.featured_until
        return False


class FeaturedBrand(models.Model):
    """Model to feature brands in different homepage sections."""
    
    SECTION_CHOICES = [
        ('exclusive_brands', _('Exclusive Brands')),
        ('brand_deals', _('Brand Deals')),
        ('new_brands', _('New Brands')),
    ]
    
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name='featured_in'
    )
    section = models.CharField(
        _('Section'),
        max_length=50,
        choices=SECTION_CHOICES
    )
    title = models.CharField(_('Custom Title'), max_length=200, blank=True)
    subtitle = models.CharField(_('Subtitle'), max_length=300, blank=True)
    discount_text = models.CharField(_('Discount Text'), max_length=100, blank=True)
    custom_image = models.ImageField(
        _('Custom Image'),
        upload_to='featured_brands/',
        blank=True,
        null=True,
        help_text=_('Leave blank to use brand logo')
    )
    is_active = models.BooleanField(_('Active'), default=True)
    order = models.PositiveIntegerField(_('Display Order'), default=0)
    featured_until = models.DateTimeField(
        _('Featured Until'),
        null=True,
        blank=True,
        help_text=_('Leave blank for permanent featuring')
    )
    created_at = models.DateTimeField(_('Created at'), default=timezone.now)
    
    class Meta:
        verbose_name = _('Featured Brand')
        verbose_name_plural = _('Featured Brands')
        ordering = ['section', 'order', 'created_at']
        unique_together = ['brand', 'section']
    
    def __str__(self):
        return f"{self.brand.name} in {self.get_section_display()}"
    
    @property
    def display_image(self):
        """Get the image to display (custom or brand logo)."""
        return self.custom_image if self.custom_image else self.brand.logo
    
    @property
    def display_title(self):
        """Get the title to display (custom or brand name)."""
        return self.title if self.title else self.brand.name
    
    @property
    def is_expired(self):
        """Check if the featured brand has expired."""
        if self.featured_until:
            return timezone.now() > self.featured_until
        return False


class FeaturedCategory(models.Model):
    """Model to feature categories in Shop by Category section."""
    
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='featured_in'
    )
    title = models.CharField(_('Custom Title'), max_length=200, blank=True)
    custom_image = models.ImageField(
        _('Custom Image'),
        upload_to='featured_categories/',
        blank=True,
        null=True,
        help_text=_('Leave blank to use category image')
    )
    is_active = models.BooleanField(_('Active'), default=True)
    order = models.PositiveIntegerField(_('Display Order'), default=0)
    created_at = models.DateTimeField(_('Created at'), default=timezone.now)
    
    class Meta:
        verbose_name = _('Featured Category')
        verbose_name_plural = _('Featured Categories')
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"Featured: {self.category.name}"
    
    @property
    def display_image(self):
        """Get the image to display (custom or category image)."""
        return self.custom_image if self.custom_image else self.category.image
    
    @property
    def display_title(self):
        """Get the title to display (custom or category name)."""
        return self.title if self.title else self.category.name
