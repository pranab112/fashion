from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
from .cache import CacheService

class SEOService:
    """Service class for handling SEO and metadata."""

    # Default metadata
    DEFAULT_META = {
        'title': 'NEXUS Fashion Store',
        'description': 'Your one-stop destination for fashion. Discover the latest trends in clothing and accessories.',
        'keywords': ['fashion', 'clothing', 'accessories', 'online shopping'],
        'author': 'NEXUS Fashion Store',
        'robots': 'index, follow',
    }

    # Social media metadata
    SOCIAL_META = {
        'og:site_name': 'NEXUS Fashion Store',
        'og:type': 'website',
        'twitter:card': 'summary_large_image',
        'twitter:site': '@nexusfashion',
    }

    @classmethod
    def get_meta_tags(
        cls,
        page_type: str,
        data: Optional[Dict] = None
    ) -> Dict[str, str]:
        """Generate meta tags for a page."""
        meta = cls.DEFAULT_META.copy()
        
        if page_type == 'product':
            meta.update(cls._get_product_meta(data))
        elif page_type == 'category':
            meta.update(cls._get_category_meta(data))
        elif page_type == 'blog_post':
            meta.update(cls._get_blog_meta(data))
        
        # Add social media meta tags
        meta.update(cls.SOCIAL_META)
        
        # Add canonical URL
        if data and 'url' in data:
            meta['canonical'] = f"{settings.SITE_URL}{data['url']}"
        
        return meta

    @classmethod
    def _get_product_meta(cls, product: Dict) -> Dict[str, str]:
        """Generate meta tags for product page."""
        return {
            'title': f"{product['name']} | NEXUS Fashion Store",
            'description': product.get('description', '')[:160],
            'keywords': [
                product['name'],
                product.get('brand', ''),
                product.get('category', ''),
                'fashion', 'clothing'
            ],
            'og:title': product['name'],
            'og:description': product.get('description', '')[:160],
            'og:type': 'product',
            'og:image': product.get('image_url', ''),
            'product:price:amount': str(product.get('price', '')),
            'product:price:currency': settings.DEFAULT_CURRENCY,
        }

    @classmethod
    def _get_category_meta(cls, category: Dict) -> Dict[str, str]:
        """Generate meta tags for category page."""
        return {
            'title': f"{category['name']} | NEXUS Fashion Store",
            'description': category.get('description', '')[:160],
            'keywords': [
                category['name'],
                'fashion',
                'clothing',
                'collection'
            ],
            'og:title': f"{category['name']} Collection",
            'og:description': category.get('description', '')[:160],
            'og:type': 'website',
            'og:image': category.get('image_url', ''),
        }

    @classmethod
    def _get_blog_meta(cls, post: Dict) -> Dict[str, str]:
        """Generate meta tags for blog post."""
        return {
            'title': f"{post['title']} | NEXUS Fashion Blog",
            'description': post.get('excerpt', '')[:160],
            'keywords': post.get('tags', []) + ['fashion', 'blog'],
            'author': post.get('author', ''),
            'og:title': post['title'],
            'og:description': post.get('excerpt', '')[:160],
            'og:type': 'article',
            'og:image': post.get('image_url', ''),
            'article:published_time': post.get('published_at', ''),
            'article:author': post.get('author_url', ''),
        }

    @classmethod
    def generate_structured_data(
        cls,
        page_type: str,
        data: Dict
    ) -> Dict[str, Any]:
        """Generate structured data (JSON-LD)."""
        if page_type == 'product':
            return cls._get_product_structured_data(data)
        elif page_type == 'category':
            return cls._get_category_structured_data(data)
        elif page_type == 'blog_post':
            return cls._get_blog_structured_data(data)
        
        return cls._get_organization_structured_data()

    @classmethod
    def _get_product_structured_data(cls, product: Dict) -> Dict[str, Any]:
        """Generate structured data for product."""
        return {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": product['name'],
            "description": product.get('description', ''),
            "image": product.get('image_url', ''),
            "sku": product.get('sku', ''),
            "brand": {
                "@type": "Brand",
                "name": product.get('brand', '')
            },
            "offers": {
                "@type": "Offer",
                "url": f"{settings.SITE_URL}{product.get('url', '')}",
                "priceCurrency": settings.DEFAULT_CURRENCY,
                "price": str(product.get('price', '')),
                "availability": (
                    "https://schema.org/InStock"
                    if product.get('in_stock', False)
                    else "https://schema.org/OutOfStock"
                )
            }
        }

    @classmethod
    def _get_category_structured_data(cls, category: Dict) -> Dict[str, Any]:
        """Generate structured data for category."""
        return {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": category['name'],
            "description": category.get('description', ''),
            "image": category.get('image_url', ''),
            "url": f"{settings.SITE_URL}{category.get('url', '')}",
            "numberOfItems": category.get('product_count', 0),
        }

    @classmethod
    def _get_blog_structured_data(cls, post: Dict) -> Dict[str, Any]:
        """Generate structured data for blog post."""
        return {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": post['title'],
            "image": post.get('image_url', ''),
            "author": {
                "@type": "Person",
                "name": post.get('author', '')
            },
            "publisher": cls._get_organization_structured_data(),
            "datePublished": post.get('published_at', ''),
            "dateModified": post.get('updated_at', ''),
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": f"{settings.SITE_URL}{post.get('url', '')}"
            },
            "description": post.get('excerpt', '')
        }

    @classmethod
    def _get_organization_structured_data(cls) -> Dict[str, Any]:
        """Generate structured data for organization."""
        return {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": "NEXUS Fashion Store",
            "url": settings.SITE_URL,
            "logo": f"{settings.SITE_URL}/static/images/logo.png",
            "sameAs": [
                "https://facebook.com/nexusfashion",
                "https://twitter.com/nexusfashion",
                "https://instagram.com/nexusfashion"
            ],
            "contactPoint": {
                "@type": "ContactPoint",
                "telephone": settings.CONTACT_PHONE,
                "contactType": "customer service",
                "availableLanguage": ["English", "Spanish", "French"]
            }
        }

    @classmethod
    @CacheService.cache_decorator('sitemap')
    def generate_sitemap_urls(cls) -> List[Dict[str, Any]]:
        """Generate URLs for sitemap."""
        urls = []

        # Add static pages
        for page in ['about', 'contact', 'faq', 'terms', 'privacy']:
            urls.append({
                'loc': reverse(f'core:{page}'),
                'priority': 0.5,
                'changefreq': 'monthly'
            })

        # Add product pages
        from products.models import Product
        for product in Product.objects.filter(is_active=True):
            urls.append({
                'loc': product.get_absolute_url(),
                'priority': 0.8,
                'changefreq': 'daily',
                'lastmod': product.updated_at.isoformat()
            })

        # Add category pages
        from products.models import Category
        for category in Category.objects.all():
            urls.append({
                'loc': category.get_absolute_url(),
                'priority': 0.7,
                'changefreq': 'weekly',
                'lastmod': category.updated_at.isoformat()
            })

        # Add blog posts
        from blog.models import Post
        for post in Post.objects.filter(status='published'):
            urls.append({
                'loc': post.get_absolute_url(),
                'priority': 0.6,
                'changefreq': 'monthly',
                'lastmod': post.updated_at.isoformat()
            })

        return urls

    @staticmethod
    def generate_breadcrumbs(items: List[Dict[str, str]]) -> Dict[str, Any]:
        """Generate breadcrumb structured data."""
        return {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "name": item['name'],
                    "item": f"{settings.SITE_URL}{item['url']}"
                }
                for i, item in enumerate(items)
            ]
        }

    @staticmethod
    def generate_slug(text: str) -> str:
        """Generate SEO-friendly slug."""
        return slugify(text)

    @staticmethod
    def clean_html(html: str) -> str:
        """Clean HTML for meta descriptions."""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        return soup.get_text()[:160].strip()
