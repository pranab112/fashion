"""
Admin customization to hide certain models from vendors.
This keeps the admin cleaner and prevents confusion.
"""
from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.db.models import QuerySet


def customize_admin_for_vendors():
    """
    Hide certain admin models from vendors to keep their interface clean.
    They can still manage these through inline forms.
    """
    from products.models import ProductVariant, ProductImage
    
    # Store original get_queryset methods
    original_variant_get_queryset = admin.site._registry[ProductVariant].get_queryset
    original_image_get_queryset = admin.site._registry[ProductImage].get_queryset
    
    def vendor_aware_get_queryset_variant(self, request):
        """Hide ProductVariant from main list for vendors."""
        qs = original_variant_get_queryset(request)
        if hasattr(request.user, 'user_type') and request.user.user_type == 'vendor':
            # Return empty queryset to hide from menu but keep inline functionality
            return qs.none()
        return qs
    
    def vendor_aware_get_queryset_image(self, request):
        """Hide ProductImage from main list for vendors."""
        qs = original_image_get_queryset(request)
        if hasattr(request.user, 'user_type') and request.user.user_type == 'vendor':
            # Return empty queryset to hide from menu but keep inline functionality
            return qs.none()
        return qs
    
    # Apply the customization
    admin.site._registry[ProductVariant].get_queryset = vendor_aware_get_queryset_variant
    admin.site._registry[ProductImage].get_queryset = vendor_aware_get_queryset_image