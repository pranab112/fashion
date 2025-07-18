from django.contrib import admin
from django.utils.translation import gettext_lazy as _
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
    list_display = ('name', 'parent', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """Admin configuration for Brand model."""
    list_display = ('name', 'website', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

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
        (_('Status'), {
            'fields': ('is_active', 'is_featured', 'is_new_arrival')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ('created_at', 'updated_at')
        return ()

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Admin configuration for ProductImage model."""
    list_display = ('product', 'alt_text', 'is_primary', 'created_at')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('product__name', 'alt_text')
    date_hierarchy = 'created_at'

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    """Admin configuration for ProductVariant model."""
    list_display = ('product', 'sku', 'size', 'color', 'stock')
    list_filter = ('size', 'color')
    search_fields = ('product__name', 'sku', 'size', 'color')


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
