from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _

class VendorAdminSite(AdminSite):
    """Custom admin site for vendors with restricted access."""
    site_header = _('Vendor Portal')
    site_title = _('Vendor Portal')
    index_title = _('Welcome to your Vendor Dashboard')
    
    def has_permission(self, request):
        """Check if the user has vendor permissions."""
        return (
            request.user.is_active and 
            request.user.is_staff and 
            request.user.user_type == 'vendor'
        )

# Create vendor admin site instance
vendor_admin_site = VendorAdminSite(name='vendor_admin')

# Import and register only the models vendors should access
from products.models import Product, ProductImage, ProductVariant, Brand
from products.admin import (
    ProductAdmin, 
    ProductImageAdmin, 
    ProductVariantAdmin,
    BrandAdmin
)

# Register models to vendor admin
vendor_admin_site.register(Product, ProductAdmin)
vendor_admin_site.register(ProductImage, ProductImageAdmin)
vendor_admin_site.register(ProductVariant, ProductVariantAdmin)
vendor_admin_site.register(Brand, BrandAdmin)