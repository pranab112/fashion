from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Cart, CartItem, Order, OrderItem

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_items', 'subtotal', 'total', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'variant', 'quantity', 'price', 'total')
    list_filter = ('created_at',)
    search_fields = ('cart__user__username', 'product__name')
    raw_id_fields = ('cart', 'product', 'variant')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = (
        'user__username', 'user__email',
        'billing_first_name', 'billing_last_name',
        'shipping_first_name', 'shipping_last_name'
    )
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('user', 'status', 'tracking_number')
        }),
        (_('Contact Information'), {
            'fields': ('email', 'phone')
        }),
        (_('Billing Information'), {
            'fields': (
                'billing_first_name', 'billing_last_name',
                'billing_address', 'billing_apartment',
                'billing_city', 'billing_state',
                'billing_postal_code', 'billing_country'
            )
        }),
        (_('Shipping Information'), {
            'fields': (
                'different_shipping',
                'shipping_first_name', 'shipping_last_name',
                'shipping_address', 'shipping_apartment',
                'shipping_city', 'shipping_state',
                'shipping_postal_code', 'shipping_country'
            )
        }),
        (_('Order Information'), {
            'fields': (
                'subtotal', 'shipping_cost', 'tax', 'total',
                'order_notes'
            )
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at')
        })
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'variant', 'quantity', 'price', 'total')
    list_filter = ('created_at',)
    search_fields = ('order__user__username', 'product__name')
    raw_id_fields = ('order', 'product', 'variant')
    readonly_fields = ('created_at',)
