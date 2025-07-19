from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.db.models import Sum, Count, Q
from .models import (
    Order, OrderItem, OrderStatus, Payment, Commission, 
    Payout, SalesReport, OrderStatusHistory
)
from products.models import Brand


class OrderItemInline(admin.TabularInline):
    """Inline admin for OrderItem model."""
    model = OrderItem
    extra = 0
    readonly_fields = ('vendor', 'vendor_commission', 'total_price')
    
    def get_queryset(self, request):
        """Ensure vendor only sees their own items in inline."""
        qs = super().get_queryset(request)
        if hasattr(request.user, 'user_type') and request.user.user_type == 'vendor':
            user_brands = Brand.objects.filter(vendor=request.user)
            qs = qs.filter(product__brand__in=user_brands)
        return qs


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin configuration for Order model."""
    list_display = (
        'order_number', 
        'customer', 
        'get_total_items',
        'total_amount',
        'get_status_badge',
        'get_payment_status_badge',
        'is_multi_vendor',
        'created_at'
    )
    list_filter = (
        'status', 
        'payment_status', 
        'is_multi_vendor',
        'created_at',
        'shipped_at',
        'delivered_at'
    )
    search_fields = (
        'order_number', 
        'customer__email', 
        'customer__first_name', 
        'customer__last_name',
        'customer_email',
        'tracking_number'
    )
    readonly_fields = (
        'order_id', 
        'order_number', 
        'created_at', 
        'updated_at',
        'get_vendor_summary'
    )
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (_('Order Information'), {
            'fields': (
                ('order_number', 'order_id'),
                ('customer', 'customer_email', 'customer_phone'),
                ('status', 'payment_status'),
                'is_multi_vendor',
                'get_vendor_summary'
            )
        }),
        (_('Shipping Address'), {
            'fields': (
                ('shipping_first_name', 'shipping_last_name'),
                'shipping_address_line1',
                'shipping_address_line2',
                ('shipping_city', 'shipping_state', 'shipping_postal_code'),
                'shipping_country'
            )
        }),
        (_('Billing Address'), {
            'fields': (
                ('billing_first_name', 'billing_last_name'),
                'billing_address_line1',
                'billing_address_line2',
                ('billing_city', 'billing_state', 'billing_postal_code'),
                'billing_country'
            ),
            'classes': ('collapse',)
        }),
        (_('Order Totals'), {
            'fields': (
                ('subtotal', 'tax_amount'),
                ('shipping_cost', 'discount_amount'),
                'total_amount'
            )
        }),
        (_('Payment Information'), {
            'fields': (
                ('payment_method', 'payment_gateway'),
                'payment_gateway_order_id'
            )
        }),
        (_('Tracking & Notes'), {
            'fields': (
                'tracking_number',
                'customer_notes',
                'admin_notes'
            )
        }),
        (_('Timestamps'), {
            'fields': (
                ('created_at', 'updated_at'),
                ('shipped_at', 'delivered_at')
            ),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Restrict vendors to only see orders containing their products."""
        qs = super().get_queryset(request)
        
        if hasattr(request.user, 'user_type') and request.user.user_type == 'vendor':
            # Show orders that contain items from vendor's brands
            user_brands = Brand.objects.filter(vendor=request.user)
            qs = qs.filter(items__product__brand__in=user_brands).distinct()
        
        return qs
    
    def get_status_badge(self, obj):
        """Display order status with color coding."""
        colors = {
            'pending': 'orange',
            'confirmed': 'blue',
            'processing': 'purple',
            'shipped': 'green',
            'delivered': 'darkgreen',
            'cancelled': 'red',
            'returned': 'brown',
            'refunded': 'gray'
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    get_status_badge.short_description = 'Status'
    
    def get_payment_status_badge(self, obj):
        """Display payment status with color coding."""
        colors = {
            'pending': 'orange',
            'processing': 'blue',
            'completed': 'green',
            'failed': 'red',
            'cancelled': 'gray',
            'refunded': 'purple'
        }
        color = colors.get(obj.payment_status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_payment_status_display()
        )
    get_payment_status_badge.short_description = 'Payment Status'
    
    def get_total_items(self, obj):
        """Get total number of items in order."""
        return obj.total_items
    get_total_items.short_description = 'Items'
    
    def get_vendor_summary(self, obj):
        """Show vendor summary for multi-vendor orders."""
        vendors = obj.vendors.all()
        if vendors:
            vendor_list = []
            for vendor in vendors:
                vendor_items = obj.items.filter(product__brand__vendor=vendor).count()
                vendor_total = obj.items.filter(product__brand__vendor=vendor).aggregate(
                    total=Sum('total_price')
                )['total'] or 0
                vendor_list.append(
                    f"{vendor.get_full_name()}: {vendor_items} items (₹{vendor_total})"
                )
            return format_html('<br>'.join(vendor_list))
        return "No vendors"
    get_vendor_summary.short_description = 'Vendor Summary'
    
    def save_model(self, request, obj, form, change):
        """Track status changes."""
        if change:
            original = Order.objects.get(pk=obj.pk)
            if original.status != obj.status:
                # Create status history entry
                OrderStatusHistory.objects.create(
                    order=obj,
                    from_status=original.status,
                    to_status=obj.status,
                    changed_by=request.user,
                    notes=f"Status changed by {request.user.get_full_name()}"
                )
                
                # Update timestamp fields
                if obj.status == 'shipped' and not obj.shipped_at:
                    obj.shipped_at = timezone.now()
                elif obj.status == 'delivered' and not obj.delivered_at:
                    obj.delivered_at = timezone.now()
        
        super().save_model(request, obj, form, change)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin configuration for OrderItem model."""
    list_display = (
        'order', 
        'product_name', 
        'brand_name',
        'size', 
        'color',
        'quantity', 
        'unit_price',
        'total_price',
        'vendor',
        'vendor_commission',
        'status'
    )
    list_filter = (
        'status',
        'vendor',
        'brand_name',
        'size',
        'color',
        'created_at'
    )
    search_fields = (
        'order__order_number',
        'product_name',
        'brand_name',
        'product_sku',
        'vendor__first_name',
        'vendor__last_name'
    )
    readonly_fields = (
        'total_price', 
        'vendor_commission',
        'created_at'
    )
    
    def get_queryset(self, request):
        """Restrict vendors to only see their own items."""
        qs = super().get_queryset(request)
        
        if hasattr(request.user, 'user_type') and request.user.user_type == 'vendor':
            user_brands = Brand.objects.filter(vendor=request.user)
            qs = qs.filter(product__brand__in=user_brands)
        
        return qs


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin configuration for Payment model."""
    list_display = (
        'payment_id',
        'order',
        'amount',
        'currency',
        'payment_method',
        'get_status_badge',
        'gateway',
        'created_at'
    )
    list_filter = (
        'status',
        'payment_method',
        'gateway',
        'currency',
        'created_at'
    )
    search_fields = (
        'order__order_number',
        'gateway_transaction_id',
        'payment_id'
    )
    readonly_fields = (
        'payment_id',
        'created_at',
        'updated_at',
        'processed_at'
    )
    
    def get_queryset(self, request):
        """Restrict vendors to payments for their orders."""
        qs = super().get_queryset(request)
        
        if hasattr(request.user, 'user_type') and request.user.user_type == 'vendor':
            user_brands = Brand.objects.filter(vendor=request.user)
            qs = qs.filter(order__items__product__brand__in=user_brands).distinct()
        
        return qs
    
    def get_status_badge(self, obj):
        """Display payment status with color coding."""
        colors = {
            'pending': 'orange',
            'processing': 'blue',
            'completed': 'green',
            'failed': 'red',
            'cancelled': 'gray',
            'refunded': 'purple',
            'partially_refunded': 'brown'
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    get_status_badge.short_description = 'Status'


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    """Admin configuration for Commission model."""
    list_display = (
        'vendor',
        'order',
        'gross_amount',
        'commission_rate',
        'commission_amount',
        'platform_fee',
        'net_amount',
        'get_status_badge',
        'created_at'
    )
    list_filter = (
        'status',
        'vendor',
        'commission_rate',
        'created_at',
        'approved_at',
        'paid_at'
    )
    search_fields = (
        'vendor__first_name',
        'vendor__last_name',
        'vendor__email',
        'order__order_number'
    )
    readonly_fields = (
        'net_amount',
        'created_at',
        'approved_at',
        'paid_at'
    )
    
    def get_queryset(self, request):
        """Restrict vendors to only see their own commissions."""
        qs = super().get_queryset(request)
        
        if hasattr(request.user, 'user_type') and request.user.user_type == 'vendor':
            qs = qs.filter(vendor=request.user)
        
        return qs
    
    def get_status_badge(self, obj):
        """Display commission status with color coding."""
        colors = {
            'pending': 'orange',
            'approved': 'blue',
            'paid': 'green',
            'cancelled': 'red'
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    get_status_badge.short_description = 'Status'
    
    def save_model(self, request, obj, form, change):
        """Track approval and payment timestamps."""
        if change:
            original = Commission.objects.get(pk=obj.pk)
            if original.status != obj.status:
                if obj.status == 'approved' and not obj.approved_at:
                    obj.approved_at = timezone.now()
                elif obj.status == 'paid' and not obj.paid_at:
                    obj.paid_at = timezone.now()
        
        super().save_model(request, obj, form, change)


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    """Admin configuration for Payout model."""
    list_display = (
        'payout_id',
        'vendor',
        'amount',
        'processing_fee',
        'net_amount',
        'get_status_badge',
        'bank_name',
        'created_at'
    )
    list_filter = (
        'status',
        'vendor',
        'bank_name',
        'created_at',
        'processed_at',
        'completed_at'
    )
    search_fields = (
        'vendor__first_name',
        'vendor__last_name',
        'vendor__email',
        'payout_id',
        'transaction_reference',
        'bank_account_number',
        'account_holder_name'
    )
    readonly_fields = (
        'payout_id',
        'net_amount',
        'created_at',
        'processed_at',
        'completed_at'
    )
    filter_horizontal = ('commissions',)
    
    def get_queryset(self, request):
        """Restrict vendors to only see their own payouts."""
        qs = super().get_queryset(request)
        
        if hasattr(request.user, 'user_type') and request.user.user_type == 'vendor':
            qs = qs.filter(vendor=request.user)
        
        return qs
    
    def get_status_badge(self, obj):
        """Display payout status with color coding."""
        colors = {
            'pending': 'orange',
            'processing': 'blue',
            'completed': 'green',
            'failed': 'red',
            'cancelled': 'gray'
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    get_status_badge.short_description = 'Status'
    
    def save_model(self, request, obj, form, change):
        """Track processing timestamps."""
        if change:
            original = Payout.objects.get(pk=obj.pk)
            if original.status != obj.status:
                if obj.status == 'processing' and not obj.processed_at:
                    obj.processed_at = timezone.now()
                elif obj.status == 'completed' and not obj.completed_at:
                    obj.completed_at = timezone.now()
        
        super().save_model(request, obj, form, change)


@admin.register(SalesReport)
class SalesReportAdmin(admin.ModelAdmin):
    """Admin configuration for SalesReport model."""
    list_display = (
        'report_type',
        'report_date',
        'vendor',
        'total_orders',
        'total_revenue',
        'total_items_sold',
        'average_order_value',
        'total_commissions'
    )
    list_filter = (
        'report_type',
        'vendor',
        'report_date',
        'created_at'
    )
    search_fields = (
        'vendor__first_name',
        'vendor__last_name',
        'vendor__email'
    )
    readonly_fields = (
        'created_at',
        'updated_at'
    )
    date_hierarchy = 'report_date'
    
    def get_queryset(self, request):
        """Restrict vendors to only see their own reports."""
        qs = super().get_queryset(request)
        
        if hasattr(request.user, 'user_type') and request.user.user_type == 'vendor':
            qs = qs.filter(vendor=request.user)
        
        return qs


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    """Admin configuration for OrderStatusHistory model."""
    list_display = (
        'order',
        'from_status',
        'to_status',
        'changed_by',
        'created_at'
    )
    list_filter = (
        'from_status',
        'to_status',
        'changed_by',
        'created_at'
    )
    search_fields = (
        'order__order_number',
        'changed_by__first_name',
        'changed_by__last_name',
        'notes'
    )
    readonly_fields = (
        'created_at',
    )
    
    def get_queryset(self, request):
        """Restrict vendors to status history of their orders."""
        qs = super().get_queryset(request)
        
        if hasattr(request.user, 'user_type') and request.user.user_type == 'vendor':
            user_brands = Brand.objects.filter(vendor=request.user)
            qs = qs.filter(order__items__product__brand__in=user_brands).distinct()
        
        return qs
    
    def has_add_permission(self, request):
        """Disable manual creation of status history."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Disable deletion of status history."""
        return False


@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    """Admin configuration for OrderStatus model."""
    list_display = ('name', 'description', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('order',)