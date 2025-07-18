from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from mptt.admin import MPTTModelAdmin
from .models import (
    Category,
    Brand,
    Tag,
    Product,
    ProductImage,
    ProductVariant
)
from .vendor_models import (
    VendorProfile,
    VendorPayout,
    VendorOrder
)

@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    """Admin configuration for Category model."""
    list_display = ('name', 'parent', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """Admin configuration for Brand model."""
    list_display = ('name', 'vendor', 'is_verified', 'is_active', 'commission_rate', 'website', 'slug')
    list_filter = ('is_verified', 'is_active', 'vendor')
    search_fields = ('name', 'slug', 'vendor__username', 'vendor__email')
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ('vendor',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'logo', 'website')
        }),
        (_('Vendor Information'), {
            'fields': ('vendor', 'is_verified', 'commission_rate', 'is_active')
        }),
        (_('Shop Settings'), {
            'fields': ('shop_banner', 'shop_description', 'return_policy', 'shipping_info')
        }),
        (_('Contact Information'), {
            'fields': ('contact_email', 'contact_phone')
        }),
        (_('Business Information'), {
            'fields': ('business_name', 'tax_id')
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # If user is a vendor, only show their brands
        if hasattr(request.user, 'is_vendor') and request.user.is_vendor:
            return qs.filter(vendor=request.user)
        return qs

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

class ProductVariantInline(admin.TabularInline):
    """Inline admin for ProductVariant model."""
    model = ProductVariant
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin configuration for Product model."""
    list_display = (
        'name',
        'category',
        'brand',
        'get_vendor',
        'base_price',
        'discount_percentage',
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
        'brand__vendor',
        'gender',
        'created_at'
    )
    search_fields = ('name', 'description', 'category__name', 'brand__name', 'brand__vendor__username')
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
        (_('Status'), {
            'fields': ('is_active', 'is_featured', 'is_new_arrival')
        }),
    )
    
    def get_vendor(self, obj):
        """Get the vendor of the product's brand."""
        if obj.brand and obj.brand.vendor:
            return obj.brand.vendor.username
        return '-'
    get_vendor.short_description = _('Vendor')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # If user is a vendor, only show products from their brands
        if hasattr(request.user, 'is_vendor') and request.user.is_vendor:
            return qs.filter(brand__vendor=request.user)
        return qs
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # If user is a vendor, limit brand choices to their own brands
        if db_field.name == "brand" and hasattr(request.user, 'is_vendor') and request.user.is_vendor:
            kwargs["queryset"] = Brand.objects.filter(vendor=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = []
        if obj:  # Editing an existing object
            readonly_fields.extend(['created_at', 'updated_at'])
        # Vendors cannot change featured status
        if hasattr(request.user, 'is_vendor') and request.user.is_vendor:
            readonly_fields.extend(['is_featured'])
        return readonly_fields

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Admin configuration for ProductImage model."""
    list_display = ('product', 'alt_text', 'is_primary', 'created_at')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('product__name', 'alt_text')
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # If user is a vendor, only show images from their products
        if hasattr(request.user, 'is_vendor') and request.user.is_vendor:
            return qs.filter(product__brand__vendor=request.user)
        return qs

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    """Admin configuration for ProductVariant model."""
    list_display = ('product', 'sku', 'size', 'color', 'stock')
    list_filter = ('size', 'color')
    search_fields = ('product__name', 'sku', 'size', 'color')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # If user is a vendor, only show variants from their products
        if hasattr(request.user, 'is_vendor') and request.user.is_vendor:
            return qs.filter(product__brand__vendor=request.user)
        return qs

@admin.register(VendorProfile)
class VendorProfileAdmin(admin.ModelAdmin):
    """Admin configuration for VendorProfile model."""
    list_display = ('user', 'total_sales', 'total_orders', 'average_rating', 'payout_frequency')
    list_filter = ('payout_frequency', 'created_at')
    search_fields = ('user__username', 'user__email', 'bank_account_name')
    readonly_fields = ('total_sales', 'total_orders', 'average_rating', 'total_reviews', 'created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('user',)
        }),
        (_('Statistics'), {
            'fields': ('total_sales', 'total_orders', 'average_rating', 'total_reviews')
        }),
        (_('Payout Settings'), {
            'fields': ('payout_frequency', 'bank_account_name', 'bank_account_number', 'bank_name', 'bank_routing_number')
        }),
        (_('Verification Documents'), {
            'fields': ('id_document', 'business_license', 'tax_document')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(VendorPayout)
class VendorPayoutAdmin(admin.ModelAdmin):
    """Admin configuration for VendorPayout model."""
    list_display = ('vendor', 'amount', 'status', 'period_start', 'period_end', 'created_at')
    list_filter = ('status', 'created_at', 'period_start')
    search_fields = ('vendor__username', 'vendor__email', 'transaction_id')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('vendor', 'amount', 'status')
        }),
        (_('Period'), {
            'fields': ('period_start', 'period_end')
        }),
        (_('Transaction Details'), {
            'fields': ('transaction_id', 'processed_at', 'notes')
        }),
        (_('Timestamps'), {
            'fields': ('created_at',)
        }),
    )

@admin.register(VendorOrder)
class VendorOrderAdmin(admin.ModelAdmin):
    """Admin configuration for VendorOrder model."""
    list_display = ('order', 'vendor', 'subtotal', 'commission_amount', 'vendor_amount', 'created_at')
    list_filter = ('created_at', 'vendor')
    search_fields = ('order__id', 'vendor__username', 'vendor__email')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # If user is a vendor, only show their orders
        if hasattr(request.user, 'is_vendor') and request.user.is_vendor:
            return qs.filter(vendor=request.user)
        return qs
