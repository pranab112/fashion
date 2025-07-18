from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Sum, Avg
from typing import List, Tuple, Dict, Any
from .models import (
    Product,
    Category,
    Order,
    OrderItem,
    Cart,
    CartItem,
    Review,
    Brand,
    Address,
    PaymentMethod,
    ProductVariant
)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin configuration for Product model."""

    list_display = [
        'name',
        'category',
        'brand',
        'price',
        'stock_quantity',
        'is_active',
        'created_at'
    ]
    list_filter = ['category', 'brand', 'is_active']
    search_fields = ['name', 'description', 'sku']
    readonly_fields = ['created_at', 'updated_at']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'slug', 'description', 'price')
        }),
        (_('Categorization'), {
            'fields': ('category', 'brand')
        }),
        (_('Inventory'), {
            'fields': ('sku', 'stock_quantity', 'low_stock_threshold')
        }),
        (_('Status'), {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )

    def get_queryset(self, request):
        """Optimize queryset with annotations."""
        return super().get_queryset(request).annotate(
            variants_count=Count('variants'),
            orders_count=Count('order_items'),
            avg_rating=Avg('reviews__rating')
        )

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for Category model."""

    list_display = ['name', 'parent', 'products_count', 'is_active']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

    def products_count(self, obj):
        """Get number of products in category."""
        return obj.products.count()
    products_count.short_description = _('Products')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin configuration for Order model."""

    list_display = [
        'id',
        'user',
        'total_amount',
        'status',
        'payment_status',
        'created_at'
    ]
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['id', 'user__email']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        (_('Order Information'), {
            'fields': ('user', 'status', 'total_amount')
        }),
        (_('Payment'), {
            'fields': ('payment_status', 'payment_method')
        }),
        (_('Addresses'), {
            'fields': ('shipping_address', 'billing_address')
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def get_queryset(self, request):
        """Optimize queryset with prefetch_related."""
        return super().get_queryset(request).prefetch_related(
            'items',
            'items__product'
        )

class OrderItemInline(admin.TabularInline):
    """Inline admin for OrderItem model."""

    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']
    raw_id_fields = ['product']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin configuration for Cart model."""

    list_display = [
        'user',
        'status',
        'items_count',
        'total_amount',
        'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['user__email']
    readonly_fields = ['created_at', 'updated_at']

    def items_count(self, obj):
        """Get number of items in cart."""
        return obj.items.count()
    items_count.short_description = _('Items')

    def total_amount(self, obj):
        """Get total amount of cart."""
        return sum(item.quantity * item.product.price for item in obj.items.all())
    total_amount.short_description = _('Total Amount')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin configuration for Review model."""

    list_display = [
        'product',
        'user',
        'rating',
        'status',
        'created_at'
    ]
    list_filter = ['rating', 'status', 'created_at']
    search_fields = ['product__name', 'user__email', 'comment']
    readonly_fields = ['created_at']

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'product',
            'user'
        )

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """Admin configuration for Brand model."""

    list_display = [
        'name',
        'website',
        'products_count',
        'is_active'
    ]
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

    def products_count(self, obj):
        """Get number of products for brand."""
        return obj.products.count()
    products_count.short_description = _('Products')

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Admin configuration for Address model."""

    list_display = [
        'user',
        'type',
        'city',
        'country',
        'is_default'
    ]
    list_filter = ['type', 'country', 'is_default']
    search_fields = ['user__email', 'street', 'city']

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    """Admin configuration for PaymentMethod model."""

    list_display = [
        'user',
        'type',
        'provider',
        'is_default',
        'is_active'
    ]
    list_filter = ['type', 'provider', 'is_active']
    search_fields = ['user__email']
    readonly_fields = ['created_at']

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    """Admin configuration for ProductVariant model."""

    list_display = [
        'product',
        'size',
        'color',
        'price',
        'stock_quantity',
        'is_active'
    ]
    list_filter = ['size', 'color', 'is_active']
    search_fields = ['product__name', 'sku']
    raw_id_fields = ['product']

# Admin site customization
admin.site.site_header = _('NEXUS Fashion Store Administration')
admin.site.site_title = _('NEXUS Admin')
admin.site.index_title = _('Administration')

# Admin actions
@admin.action(description=_('Mark selected products as active'))
def make_active(modeladmin, request, queryset):
    """Mark selected products as active."""
    queryset.update(is_active=True)

@admin.action(description=_('Mark selected products as inactive'))
def make_inactive(modeladmin, request, queryset):
    """Mark selected products as inactive."""
    queryset.update(is_active=False)

@admin.action(description=_('Update stock quantity'))
def update_stock(modeladmin, request, queryset):
    """Update stock quantity for selected products."""
    from django.core.exceptions import ValidationError
    from django import forms

    class StockUpdateForm(forms.Form):
        """Form for updating stock quantity."""
        _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
        stock_quantity = forms.IntegerField(min_value=0)

    form = None
    if 'apply' in request.POST:
        form = StockUpdateForm(request.POST)
        if form.is_valid():
            stock_quantity = form.cleaned_data['stock_quantity']
            queryset.update(stock_quantity=stock_quantity)
            modeladmin.message_user(
                request,
                _('Successfully updated stock quantity')
            )
            return None

    if not form:
        form = StockUpdateForm(
            initial={
                '_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
            }
        )

    return render(
        request,
        'admin/stock_update.html',
        context={'items': queryset, 'form': form}
    )

# Register actions
ProductAdmin.actions = [make_active, make_inactive, update_stock]
