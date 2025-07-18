"""
Sitemaps for the products app.
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.db.models import QuerySet
from django.utils import timezone
from datetime import timedelta

from .models import Product, Category, Brand

class ProductSitemap(Sitemap):
    """Sitemap for Product model."""
    
    changefreq = 'daily'
    priority = 0.8
    protocol = 'https'

    def items(self) -> QuerySet:
        """Get active products."""
        return Product.objects.filter(is_active=True)

    def lastmod(self, obj: Product) -> timezone.datetime:
        """Get last modification date."""
        return obj.updated_at

    def location(self, obj: Product) -> str:
        """Get product URL."""
        return obj.get_absolute_url()

class CategorySitemap(Sitemap):
    """Sitemap for Category model."""
    
    changefreq = 'weekly'
    priority = 0.7
    protocol = 'https'

    def items(self) -> QuerySet:
        """Get active categories."""
        return Category.objects.filter(is_active=True)

    def lastmod(self, obj: Category) -> timezone.datetime:
        """
        Get last modification date based on most recent product.
        """
        latest_product = obj.products.filter(
            is_active=True
        ).order_by('-updated_at').first()
        
        return latest_product.updated_at if latest_product else obj.updated_at

    def location(self, obj: Category) -> str:
        """Get category URL."""
        return obj.get_absolute_url()

class BrandSitemap(Sitemap):
    """Sitemap for Brand model."""
    
    changefreq = 'weekly'
    priority = 0.6
    protocol = 'https'

    def items(self) -> QuerySet:
        """Get active brands."""
        return Brand.objects.filter(is_active=True)

    def lastmod(self, obj: Brand) -> timezone.datetime:
        """
        Get last modification date based on most recent product.
        """
        latest_product = obj.products.filter(
            is_active=True
        ).order_by('-updated_at').first()
        
        return latest_product.updated_at if latest_product else obj.updated_at

    def location(self, obj: Brand) -> str:
        """Get brand URL."""
        return obj.get_absolute_url()

class NewProductsSitemap(Sitemap):
    """Sitemap for new products."""
    
    changefreq = 'daily'
    priority = 0.9
    protocol = 'https'

    def items(self) -> QuerySet:
        """Get new products from last 30 days."""
        thirty_days_ago = timezone.now() - timedelta(days=30)
        return Product.objects.filter(
            is_active=True,
            created_at__gte=thirty_days_ago
        )

    def lastmod(self, obj: Product) -> timezone.datetime:
        """Get last modification date."""
        return obj.updated_at

    def location(self, obj: Product) -> str:
        """Get product URL."""
        return obj.get_absolute_url()

class SaleProductsSitemap(Sitemap):
    """Sitemap for products on sale."""
    
    changefreq = 'daily'
    priority = 0.8
    protocol = 'https'

    def items(self) -> QuerySet:
        """Get products on sale."""
        return Product.objects.filter(
            is_active=True,
            is_on_sale=True
        )

    def lastmod(self, obj: Product) -> timezone.datetime:
        """Get last modification date."""
        return obj.updated_at

    def location(self, obj: Product) -> str:
        """Get product URL."""
        return obj.get_absolute_url()

class StaticProductPagesSitemap(Sitemap):
    """Sitemap for static product-related pages."""
    
    changefreq = 'weekly'
    priority = 0.5
    protocol = 'https'

    def items(self) -> list:
        """Get static pages."""
        return [
            'products:product_list',
            'products:category_list',
            'products:brand_list',
            'products:new_arrivals',
            'products:sale',
            'products:trending',
            'products:size_guide'
        ]

    def location(self, item: str) -> str:
        """Get page URL."""
        return reverse(item)

# Combine all sitemaps
sitemaps = {
    'products': ProductSitemap,
    'categories': CategorySitemap,
    'brands': BrandSitemap,
    'new_products': NewProductsSitemap,
    'sale_products': SaleProductsSitemap,
    'static_product_pages': StaticProductPagesSitemap,
}
