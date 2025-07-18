"""
SEO functionality for the products app.
"""

import logging
from typing import Any, Dict, List, Optional
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from django.utils.html import strip_tags
from django.template.loader import render_to_string

from .models import Product, Category, Brand
from .constants import (
    META_TITLE_MAX_LENGTH,
    META_DESCRIPTION_MAX_LENGTH,
    SITEMAP_CHANGEFREQ_CHOICES
)

logger = logging.getLogger(__name__)

class ProductSEO:
    """SEO manager for products."""

    @staticmethod
    def get_meta_tags(product: Product) -> Dict[str, str]:
        """
        Get meta tags for product.
        
        Args:
            product: Product instance
            
        Returns:
            Dict[str, str]: Meta tags
        """
        try:
            # Generate meta title
            meta_title = ProductSEO.generate_meta_title(product)
            
            # Generate meta description
            meta_description = ProductSEO.generate_meta_description(product)
            
            # Get canonical URL
            canonical_url = ProductSEO.get_canonical_url(product)
            
            # Get OpenGraph data
            og_data = ProductSEO.get_opengraph_data(product)
            
            # Get Twitter Card data
            twitter_data = ProductSEO.get_twitter_card_data(product)
            
            # Get JSON-LD data
            json_ld = ProductSEO.get_json_ld(product)
            
            return {
                'title': meta_title,
                'description': meta_description,
                'canonical': canonical_url,
                'og_title': og_data['title'],
                'og_description': og_data['description'],
                'og_image': og_data['image'],
                'og_type': og_data['type'],
                'og_url': og_data['url'],
                'twitter_card': twitter_data['card'],
                'twitter_title': twitter_data['title'],
                'twitter_description': twitter_data['description'],
                'twitter_image': twitter_data['image'],
                'json_ld': json_ld
            }
            
        except Exception as e:
            logger.error(f"Error generating meta tags: {str(e)}")
            return {}

    @staticmethod
    def generate_meta_title(product: Product) -> str:
        """
        Generate meta title for product.
        
        Args:
            product: Product instance
            
        Returns:
            str: Meta title
        """
        try:
            # Base title format: Product Name | Brand Name | Category | Site Name
            title_parts = [product.name]
            
            if product.brand:
                title_parts.append(product.brand.name)
            
            if product.category:
                title_parts.append(product.category.name)
            
            title_parts.append(settings.SITE_NAME)
            
            # Join parts and limit length
            title = ' | '.join(title_parts)
            if len(title) > META_TITLE_MAX_LENGTH:
                # Truncate to fit max length while keeping site name
                site_name = f" | {settings.SITE_NAME}"
                available_length = META_TITLE_MAX_LENGTH - len(site_name)
                title = f"{title[:available_length].rsplit('|', 1)[0].strip()}{site_name}"
            
            return title
            
        except Exception as e:
            logger.error(f"Error generating meta title: {str(e)}")
            return product.name

    @staticmethod
    def generate_meta_description(product: Product) -> str:
        """
        Generate meta description for product.
        
        Args:
            product: Product instance
            
        Returns:
            str: Meta description
        """
        try:
            # Start with product description
            description = strip_tags(product.description)
            
            # Add key features
            if product.key_features:
                description = f"{description} Features: {', '.join(product.key_features)}"
            
            # Add price if available
            if product.price:
                description = f"{description} Price: {product.get_formatted_price()}"
            
            # Truncate to fit max length
            if len(description) > META_DESCRIPTION_MAX_LENGTH:
                description = f"{description[:META_DESCRIPTION_MAX_LENGTH-3]}..."
            
            return description
            
        except Exception as e:
            logger.error(f"Error generating meta description: {str(e)}")
            return ""

    @staticmethod
    def get_canonical_url(product: Product) -> str:
        """
        Get canonical URL for product.
        
        Args:
            product: Product instance
            
        Returns:
            str: Canonical URL
        """
        try:
            return f"{settings.SITE_URL}{product.get_absolute_url()}"
        except Exception as e:
            logger.error(f"Error getting canonical URL: {str(e)}")
            return ""

    @staticmethod
    def get_opengraph_data(product: Product) -> Dict[str, str]:
        """
        Get OpenGraph data for product.
        
        Args:
            product: Product instance
            
        Returns:
            Dict[str, str]: OpenGraph data
        """
        try:
            return {
                'title': ProductSEO.generate_meta_title(product),
                'description': ProductSEO.generate_meta_description(product),
                'image': product.get_primary_image_url(),
                'type': 'product',
                'url': ProductSEO.get_canonical_url(product)
            }
        except Exception as e:
            logger.error(f"Error getting OpenGraph data: {str(e)}")
            return {}

    @staticmethod
    def get_twitter_card_data(product: Product) -> Dict[str, str]:
        """
        Get Twitter Card data for product.
        
        Args:
            product: Product instance
            
        Returns:
            Dict[str, str]: Twitter Card data
        """
        try:
            return {
                'card': 'summary_large_image',
                'title': ProductSEO.generate_meta_title(product),
                'description': ProductSEO.generate_meta_description(product),
                'image': product.get_primary_image_url()
            }
        except Exception as e:
            logger.error(f"Error getting Twitter Card data: {str(e)}")
            return {}

    @staticmethod
    def get_json_ld(product: Product) -> Dict[str, Any]:
        """
        Get JSON-LD structured data for product.
        
        Args:
            product: Product instance
            
        Returns:
            Dict[str, Any]: JSON-LD data
        """
        try:
            data = {
                '@context': 'https://schema.org/',
                '@type': 'Product',
                'name': product.name,
                'description': strip_tags(product.description),
                'sku': product.sku,
                'url': ProductSEO.get_canonical_url(product)
            }
            
            # Add brand
            if product.brand:
                data['brand'] = {
                    '@type': 'Brand',
                    'name': product.brand.name
                }
            
            # Add images
            if product.images.exists():
                data['image'] = [
                    img.image.url for img in product.images.all()
                ]
            
            # Add offers
            if product.price:
                data['offers'] = {
                    '@type': 'Offer',
                    'price': str(product.price),
                    'priceCurrency': settings.DEFAULT_CURRENCY,
                    'availability': (
                        'https://schema.org/InStock'
                        if product.stock > 0
                        else 'https://schema.org/OutOfStock'
                    )
                }
            
            # Add reviews
            if product.reviews.exists():
                data['aggregateRating'] = {
                    '@type': 'AggregateRating',
                    'ratingValue': str(product.average_rating),
                    'reviewCount': product.reviews.count()
                }
                
                data['review'] = [{
                    '@type': 'Review',
                    'reviewRating': {
                        '@type': 'Rating',
                        'ratingValue': str(review.rating)
                    },
                    'author': {
                        '@type': 'Person',
                        'name': review.user.get_full_name() or review.user.username
                    },
                    'reviewBody': review.text
                } for review in product.reviews.all()[:5]]  # Include first 5 reviews
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting JSON-LD data: {str(e)}")
            return {}

    @staticmethod
    def generate_sitemap_data() -> List[Dict[str, Any]]:
        """
        Generate sitemap data for products.
        
        Returns:
            List[Dict[str, Any]]: Sitemap data
        """
        try:
            sitemap_data = []
            
            # Add product URLs
            products = Product.objects.filter(is_active=True)
            for product in products:
                sitemap_data.append({
                    'location': ProductSEO.get_canonical_url(product),
                    'lastmod': product.updated_at.isoformat(),
                    'changefreq': 'daily',
                    'priority': 0.8
                })
            
            # Add category URLs
            categories = Category.objects.filter(is_active=True)
            for category in categories:
                sitemap_data.append({
                    'location': f"{settings.SITE_URL}{category.get_absolute_url()}",
                    'lastmod': category.updated_at.isoformat(),
                    'changefreq': 'weekly',
                    'priority': 0.6
                })
            
            # Add brand URLs
            brands = Brand.objects.filter(is_active=True)
            for brand in brands:
                sitemap_data.append({
                    'location': f"{settings.SITE_URL}{brand.get_absolute_url()}",
                    'lastmod': brand.updated_at.isoformat(),
                    'changefreq': 'weekly',
                    'priority': 0.6
                })
            
            return sitemap_data
            
        except Exception as e:
            logger.error(f"Error generating sitemap data: {str(e)}")
            return []

    @staticmethod
    def generate_robots_txt() -> str:
        """
        Generate robots.txt content.
        
        Returns:
            str: robots.txt content
        """
        try:
            return render_to_string('products/robots.txt', {
                'site_url': settings.SITE_URL,
                'sitemap_url': f"{settings.SITE_URL}/sitemap.xml"
            })
        except Exception as e:
            logger.error(f"Error generating robots.txt: {str(e)}")
            return ""
