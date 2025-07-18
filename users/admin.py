from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, Address

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin interface for CustomUser model."""
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_vendor_approved', 'is_staff')
    list_filter = ('user_type', 'is_vendor_approved', 'is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {
            'fields': (
                'first_name',
                'last_name',
                'email',
                'phone',
                'date_of_birth',
                'avatar',
                'bio'
            )
        }),
        (_('Vendor Settings'), {
            'fields': (
                'user_type',
                'is_vendor_approved',
                'vendor_commission_rate'
            )
        }),
        (_('Permissions'), {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            ),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type'),
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Vendors can only see their own profile
        if hasattr(request.user, 'is_vendor') and request.user.is_vendor:
            return qs.filter(id=request.user.id)
        return qs

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Admin interface for Address model."""
    
    list_display = (
        'user',
        'address_type',
        'first_name',
        'last_name',
        'city',
        'country',
        'is_default'
    )
    list_filter = ('address_type', 'country', 'is_default')
    search_fields = (
        'user__username',
        'first_name',
        'last_name',
        'street_address',
        'city',
        'state',
        'country'
    )
    raw_id_fields = ('user',)
