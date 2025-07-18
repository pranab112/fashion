"""
Script to populate sample homepage data for admin demonstration.
Run with: python manage.py shell < populate_homepage_data.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nexus.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from core.models import HeroBanner, HomepageSettings
from products.models import (
    Product, Brand, Category,
    FeaturedProduct, FeaturedBrand, FeaturedCategory
)

def create_homepage_settings():
    """Create or update homepage settings."""
    settings, created = HomepageSettings.objects.get_or_create(
        pk=1,  # HomepageSettings is a singleton
        defaults={
            'site_name': 'Fashion Nexus',
            'site_description': 'Your premier destination for fashion and style',
            'hero_auto_play': True,
            'hero_slide_duration': 4,
            'products_per_section': 8,
            'brands_per_section': 6,
            'categories_per_section': 8,
        }
    )
    print(f"Homepage settings {'created' if created else 'updated'}")
    return settings

def create_hero_banners():
    """Create sample hero banners."""
    banners_data = [
        {
            'title': 'Summer Collection 2025',
            'subtitle': 'Up to 70% Off on Premium Brands',
            'link_url': '/products/?season=summer',
            'link_text': 'Shop Now',
            'order': 1,
        },
        {
            'title': 'New Arrivals',
            'subtitle': 'Fresh Styles for the Modern You',
            'link_url': '/products/?sort=newest',
            'link_text': 'Explore',
            'order': 2,
        },
        {
            'title': 'Exclusive Brands',
            'subtitle': 'Premium Quality, Unbeatable Prices',
            'link_url': '/brands/',
            'link_text': 'Discover Brands',
            'order': 3,
        },
    ]
    
    created_count = 0
    for banner_data in banners_data:
        banner, created = HeroBanner.objects.get_or_create(
            title=banner_data['title'],
            defaults={
                'subtitle': banner_data['subtitle'],
                'link_url': banner_data['link_url'],
                'link_text': banner_data['link_text'],
                'order': banner_data['order'],
                'is_active': True,
            }
        )
        if created:
            created_count += 1
            print(f"Created hero banner: {banner.title}")
    
    print(f"Created {created_count} hero banners")

def create_featured_products():
    """Create featured products for different sections."""
    sections = [
        ('deal_of_day', 8),
        ('top_picks', 4),
        ('trending_now', 8),
        ('indian_wear', 6),
        ('sports_wear', 6),
        ('footwear', 6),
    ]
    
    # Get some products to feature
    products = Product.objects.filter(is_active=True)[:30]
    
    if not products:
        print("No products found. Please create some products first.")
        return
    
    featured_until = timezone.now() + timedelta(days=7)
    created_count = 0
    
    for section, count in sections:
        # Get products for this section
        section_products = products[:count]
        
        for i, product in enumerate(section_products):
            featured, created = FeaturedProduct.objects.get_or_create(
                product=product,
                section=section,
                defaults={
                    'order': i + 1,
                    'featured_until': featured_until,
                    'is_active': True,
                }
            )
            if created:
                created_count += 1
        
        print(f"Featured {len(section_products)} products in {section}")
    
    print(f"Created {created_count} featured product entries")

def create_featured_brands():
    """Create featured brands for different sections."""
    sections = [
        ('exclusive_brands', 6),
        ('brand_deals', 8),
        ('new_brands', 4),
    ]
    
    # Get some brands to feature
    brands = Brand.objects.filter(is_active=True)[:20]
    
    if not brands:
        print("No brands found. Please create some brands first.")
        return
    
    featured_until = timezone.now() + timedelta(days=14)
    created_count = 0
    
    for section, count in sections:
        # Get brands for this section
        section_brands = brands[:count]
        
        for i, brand in enumerate(section_brands):
            discount_text = ''
            if section == 'brand_deals':
                discount_text = f"Up to {30 + (i * 5)}% Off"
            
            featured, created = FeaturedBrand.objects.get_or_create(
                brand=brand,
                section=section,
                defaults={
                    'order': i + 1,
                    'featured_until': featured_until,
                    'is_active': True,
                    'discount_text': discount_text if discount_text else '',
                }
            )
            if created:
                created_count += 1
        
        print(f"Featured {len(section_brands)} brands in {section}")
    
    print(f"Created {created_count} featured brand entries")

def create_featured_categories():
    """Create featured categories."""
    categories = Category.objects.filter(is_active=True)[:8]
    
    if not categories:
        print("No categories found. Please create some categories first.")
        return
    
    created_count = 0
    for i, category in enumerate(categories):
        featured, created = FeaturedCategory.objects.get_or_create(
            category=category,
            defaults={
                'order': i + 1,
                'is_active': True,
            }
        )
        if created:
            created_count += 1
    
    print(f"Created {created_count} featured category entries")

def main():
    """Main function to populate all homepage data."""
    print("Starting homepage data population...")
    print("-" * 50)
    
    # Create homepage settings
    create_homepage_settings()
    
    # Create hero banners
    create_hero_banners()
    
    # Create featured products
    create_featured_products()
    
    # Create featured brands
    create_featured_brands()
    
    # Create featured categories
    create_featured_categories()
    
    print("-" * 50)
    print("Homepage data population completed!")
    print("\nNOTE: Remember to upload images for hero banners through the admin interface.")
    print("You can access the admin at: http://localhost:8000/admin/")

if __name__ == "__main__":
    main()