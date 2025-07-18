import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nexus.settings')
django.setup()

from products.models import Product, Brand, Category, FeaturedProduct, FeaturedBrand, FeaturedCategory
from django.utils import timezone

def add_featured_items():
    # Get some products, brands, and categories
    products = Product.objects.filter(is_active=True)[:20]
    brands = Brand.objects.filter(is_active=True)[:10]
    categories = Category.objects.filter(is_active=True)[:10]
    
    if not products:
        print("No products found. Please add some products first.")
        return
    
    # Clear existing featured items
    FeaturedProduct.objects.all().delete()
    FeaturedBrand.objects.all().delete()
    FeaturedCategory.objects.all().delete()
    
    # Add Featured Products
    sections = [
        ('deal_of_day', 4),
        ('top_picks', 6),
        ('trending_now', 6),
        ('indian_wear', 4),
        ('sports_wear', 4),
        ('footwear', 4)
    ]
    
    product_index = 0
    for section, count in sections:
        for i in range(count):
            if product_index < len(products):
                FeaturedProduct.objects.create(
                    product=products[product_index],
                    section=section,
                    is_active=True,
                    order=i
                )
                product_index += 1
                
    print(f"Added {FeaturedProduct.objects.count()} featured products")
    
    # Add Featured Brands
    if brands:
        brand_sections = [
            ('exclusive_brands', 4),
            ('brand_deals', 4),
            ('new_brands', 2)
        ]
        
        brand_index = 0
        for section, count in brand_sections:
            for i in range(count):
                if brand_index < len(brands):
                    FeaturedBrand.objects.create(
                        brand=brands[brand_index],
                        section=section,
                        is_active=True,
                        order=i,
                        title=f"{brands[brand_index].name} Collection",
                        subtitle="Exclusive offers",
                        discount_text="Up to 50% OFF"
                    )
                    brand_index += 1
                    
    print(f"Added {FeaturedBrand.objects.count()} featured brands")
    
    # Add Featured Categories
    if categories:
        for i, category in enumerate(categories[:8]):
            FeaturedCategory.objects.create(
                category=category,
                is_active=True,
                order=i,
                title=category.name
            )
            
    print(f"Added {FeaturedCategory.objects.count()} featured categories")
    
    print("\nFeatured items added successfully!")

if __name__ == "__main__":
    add_featured_items()
