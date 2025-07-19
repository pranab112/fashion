from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from mptt.admin import MPTTModelAdmin
from .models import (
    Category,
    Brand,
    Tag,
    Product,
    ProductImage,
    ProductVariant,
    FeaturedProduct,
    FeaturedBrand,
    FeaturedCategory
)

@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    """Admin configuration for Category model."""
    list_display = (
        'name', 
        'parent', 
        'slug', 
        'show_in_mega_menu', 
        'mega_menu_order',
        'is_active'
    )
    list_filter = ('show_in_mega_menu', 'is_active', 'parent')
    search_fields = ('name', 'slug', 'mega_menu_column_title')
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'slug', 'description', 'parent', 'image', 'is_active')
        }),
        (_('Mega Menu Settings'), {
            'fields': (
                'show_in_mega_menu',
                'mega_menu_order',
                'mega_menu_column_title',
                'mega_menu_icon'
            ),
            'description': 'Configure how this category appears in the mega dropdown menu'
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset for admin."""
        return super().get_queryset(request).select_related('parent')

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """Admin configuration for Brand model."""
    list_display = ('name', 'website', 'slug', 'vendor', 'is_verified')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('is_verified', 'vendor')
    
    def get_queryset(self, request):
        """Restrict vendors to only see their own brands."""
        qs = super().get_queryset(request)
        
        # If user is a vendor, only show their own brands
        if request.user.user_type == 'vendor':
            qs = qs.filter(vendor=request.user)
        
        return qs
    
    def get_readonly_fields(self, request, obj=None):
        """Make vendor field readonly for vendors."""
        readonly_fields = ['created_at', 'updated_at']
        
        if request.user.user_type == 'vendor':
            readonly_fields.extend(['vendor', 'is_verified', 'commission_rate'])
        
        return readonly_fields
    
    def save_model(self, request, obj, form, change):
        """Automatically assign vendor when creating brand."""
        if not change and request.user.user_type == 'vendor':
            obj.vendor = request.user
        super().save_model(request, obj, form, change)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin configuration for Tag model."""
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

class ProductImageInline(admin.TabularInline):
    """Inline admin for ProductImage model."""
    model = ProductImage
    extra = 1
    
    def get_queryset(self, request):
        """Ensure vendor only sees their own product images in inline."""
        qs = super().get_queryset(request)
        if request.user.user_type == 'vendor':
            user_brands = Brand.objects.filter(vendor=request.user)
            qs = qs.filter(product__brand__in=user_brands)
        return qs

class ProductVariantInline(admin.TabularInline):
    """Inline admin for ProductVariant model."""
    model = ProductVariant
    extra = 1
    
    def get_queryset(self, request):
        """Ensure vendor only sees their own product variants in inline."""
        qs = super().get_queryset(request)
        if request.user.user_type == 'vendor':
            user_brands = Brand.objects.filter(vendor=request.user)
            qs = qs.filter(product__brand__in=user_brands)
        return qs

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin configuration for Product model."""
    list_display = (
        'name',
        'category',
        'brand',
        'base_price',
        'discount_percentage',
        'get_stock_status',
        'is_active',
        'is_featured',
        'created_at'
    )
    list_filter = (
        'is_active',
        'is_featured',
        'is_new_arrival',
        'category',
        'brand',
        'gender',
        'created_at'
    )
    search_fields = ('name', 'description', 'category__name', 'brand__name')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductVariantInline]
    filter_horizontal = ('tags',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description')
        }),
        (_('Categorization'), {
            'fields': ('category', 'brand', 'tags', 'gender')
        }),
        (_('Pricing'), {
            'fields': ('base_price', 'discount_percentage')
        }),
        (_('Stock Management'), {
            'fields': ('simple_stock', 'manage_stock', 'low_stock_threshold'),
            'description': 'For simple products, use the stock field below. For products with sizes/colors, use the Variants section.'
        }),
        (_('Status'), {
            'fields': ('is_active', 'is_featured', 'is_new_arrival')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ('created_at', 'updated_at')
        return ()
    
    def get_queryset(self, request):
        """Restrict vendors to only see their own brand's products."""
        qs = super().get_queryset(request)
        
        # If user is a vendor, only show products from their brands
        if request.user.user_type == 'vendor':
            user_brands = Brand.objects.filter(vendor=request.user)
            qs = qs.filter(brand__in=user_brands)
        
        return qs
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Restrict brand choices for vendors to only their own brands."""
        if db_field.name == "brand" and request.user.user_type == 'vendor':
            kwargs["queryset"] = Brand.objects.filter(vendor=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def save_model(self, request, obj, form, change):
        """Automatically assign vendor's brand if creating new product."""
        if not change and request.user.user_type == 'vendor':
            # For new products, assign the first brand owned by the vendor
            vendor_brand = Brand.objects.filter(vendor=request.user).first()
            if vendor_brand:
                obj.brand = vendor_brand
        super().save_model(request, obj, form, change)
    
    def get_stock_status(self, obj):
        """Display stock status with color coding."""
        stock = obj.stock
        if stock == 0:
            return format_html('<span style="color: red;">Out of Stock</span>')
        elif obj.is_low_stock:
            return format_html('<span style="color: orange;">Low Stock ({0})</span>', stock)
        else:
            return format_html('<span style="color: green;">In Stock ({0})</span>', stock)
    get_stock_status.short_description = 'Stock Status'

# Not registered as standalone - only available as inline
class ProductImageAdmin(admin.ModelAdmin):
    """Admin configuration for ProductImage model."""
    list_display = ('product', 'alt_text', 'is_primary', 'created_at')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('product__name', 'alt_text')
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        """Restrict vendors to only see images from their own brand's products."""
        qs = super().get_queryset(request)
        
        # If user is a vendor, only show images from their brands' products
        if request.user.user_type == 'vendor':
            user_brands = Brand.objects.filter(vendor=request.user)
            qs = qs.filter(product__brand__in=user_brands)
        
        return qs
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Restrict product choices for vendors to only their own products."""
        if db_field.name == "product" and request.user.user_type == 'vendor':
            user_brands = Brand.objects.filter(vendor=request.user)
            kwargs["queryset"] = Product.objects.filter(brand__in=user_brands)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class ProductVariantAdmin(admin.ModelAdmin):
    """Admin configuration for ProductVariant model."""
    list_display = ('product', 'sku', 'size', 'color', 'stock')
    list_filter = ('size', 'color')
    search_fields = ('product__name', 'sku', 'size', 'color')
    
    def get_queryset(self, request):
        """Restrict vendors to only see variants from their own brand's products."""
        qs = super().get_queryset(request)
        
        # If user is a vendor, only show variants from their brands' products
        if request.user.user_type == 'vendor':
            user_brands = Brand.objects.filter(vendor=request.user)
            qs = qs.filter(product__brand__in=user_brands)
        
        return qs
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Restrict product choices for vendors to only their own products."""
        if db_field.name == "product" and request.user.user_type == 'vendor':
            user_brands = Brand.objects.filter(vendor=request.user)
            kwargs["queryset"] = Product.objects.filter(brand__in=user_brands)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# Featured Models Admin
@admin.register(FeaturedProduct)
class FeaturedProductAdmin(admin.ModelAdmin):
    """Admin configuration for FeaturedProduct model."""
    list_display = ('product', 'section', 'order', 'is_active', 'featured_until', 'created_at')
    list_filter = ('section', 'is_active', 'featured_until')
    search_fields = ('product__name',)
    ordering = ('section', 'order')
    autocomplete_fields = ['product']
    
    fieldsets = (
        (None, {
            'fields': ('product', 'section')
        }),
        (_('Display Settings'), {
            'fields': ('is_active', 'order', 'featured_until')
        }),
    )


@admin.register(FeaturedBrand)
class FeaturedBrandAdmin(admin.ModelAdmin):
    """Admin configuration for FeaturedBrand model."""
    list_display = ('brand', 'section', 'title', 'order', 'is_active', 'featured_until')
    list_filter = ('section', 'is_active')
    search_fields = ('brand__name', 'title')
    ordering = ('section', 'order')
    autocomplete_fields = ['brand']
    
    fieldsets = (
        (None, {
            'fields': ('brand', 'section')
        }),
        (_('Custom Content'), {
            'fields': ('title', 'subtitle', 'discount_text', 'custom_image')
        }),
        (_('Display Settings'), {
            'fields': ('is_active', 'order', 'featured_until')
        }),
    )


@admin.register(FeaturedCategory)
class FeaturedCategoryAdmin(admin.ModelAdmin):
    """Admin configuration for FeaturedCategory model."""
    list_display = ('category', 'title', 'order', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('category__name', 'title')
    ordering = ('order',)
    autocomplete_fields = ['category']
    
    fieldsets = (
        (None, {
            'fields': ('category',)
        }),
        (_('Custom Content'), {
            'fields': ('title', 'custom_image')
        }),
        (_('Display Settings'), {
            'fields': ('is_active', 'order')
        }),
    )


# For better UX, we'll only register these as inlines, not standalone
# This prevents duplication in the admin menu
# admin.site.register(ProductVariant, ProductVariantAdmin)  # Commented out - only use as inline
# admin.site.register(ProductImage, ProductImageAdmin)      # Commented out - only use as inline
