"""
Sitemap classes for the core app.
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone

from products.models import Product, Category, Brand

class StaticViewSitemap(Sitemap):
    """Sitemap for static pages."""
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return [
            'core:home',
            'core:about',
            'core:contact',
            'core:faq',
            'core:privacy',
            'core:terms',
            'core:shipping',
            'core:returns',
            'core:help',
            'core:support',
            'core:stores',
            'core:careers',
            'core:blog',
        ]

    def location(self, item):
        return reverse(item)

    def lastmod(self, item):
        # Return the last modification date for static pages
        if item == 'core:home':
            return timezone.now()  # Homepage is always considered fresh
        return None

class ProductSitemap(Sitemap):
    """Sitemap for product pages."""
    changefreq = 'daily'
    priority = 0.9

    def items(self):
        return Product.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()

    def priority(self, obj):
        # Higher priority for products with higher ratings or sales
        if obj.average_rating and obj.total_sales:
            base_priority = 0.7
            rating_boost = min(obj.average_rating / 5 * 0.2, 0.2)
            sales_boost = min(obj.total_sales / 1000 * 0.1, 0.1)
            return min(base_priority + rating_boost + sales_boost, 1.0)
        return 0.7

class CategorySitemap(Sitemap):
    """Sitemap for category pages."""
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Category.objects.filter(is_active=True)

    def lastmod(self, obj):
        # Last modification is the latest product update in this category
        latest_product = obj.products.filter(is_active=True).order_by('-updated_at').first()
        return latest_product.updated_at if latest_product else obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()

    def priority(self, obj):
        # Higher priority for parent categories
        if obj.parent is None:
            return 0.8
        return 0.6

class BrandSitemap(Sitemap):
    """Sitemap for brand pages."""
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Brand.objects.filter(is_active=True)

    def lastmod(self, obj):
        # Last modification is the latest product update for this brand
        latest_product = obj.products.filter(is_active=True).order_by('-updated_at').first()
        return latest_product.updated_at if latest_product else obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()

    def priority(self, obj):
        # Higher priority for featured brands
        if obj.is_featured:
            return 0.8
        return 0.6

class BlogSitemap(Sitemap):
    """Sitemap for blog posts."""
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        # If you have a Blog model, replace this with actual blog posts
        return []

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()

class NewsSitemap(Sitemap):
    """
    Sitemap for Google News.
    https://support.google.com/news/publisher-center/answer/74288
    """
    changefreq = 'always'
    priority = 0.9

    def items(self):
        # Return news articles from the last 2 days
        two_days_ago = timezone.now() - timezone.timedelta(days=2)
        # If you have a News model, replace this with actual news articles
        return []

    def lastmod(self, obj):
        return obj.published_at

    def location(self, obj):
        return obj.get_absolute_url()

class ImageSitemap(Sitemap):
    """
    Sitemap for images.
    https://developers.google.com/search/docs/advanced/sitemaps/image-sitemaps
    """
    def items(self):
        return Product.objects.filter(is_active=True).prefetch_related('images')

    def location(self, obj):
        return obj.get_absolute_url()

    def image_location(self, obj):
        return [image.image.url for image in obj.images.all()]

class VideoSitemap(Sitemap):
    """
    Sitemap for videos.
    https://developers.google.com/search/docs/advanced/sitemaps/video-sitemaps
    """
    def items(self):
        return Product.objects.filter(is_active=True, has_video=True)

    def location(self, obj):
        return obj.get_absolute_url()

    def video_location(self, obj):
        return obj.video_url

class LocalBusinessSitemap(Sitemap):
    """
    Sitemap for physical store locations.
    """
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        # If you have a Store model, replace this with actual store locations
        return []

    def location(self, obj):
        return obj.get_absolute_url()

    def lastmod(self, obj):
        return obj.updated_at
