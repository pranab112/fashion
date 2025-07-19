#!/usr/bin/env python
"""
Script to set up sample mega menu categories for demonstration.
Run this after adding the mega menu fields to see how the system works.
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nexus.settings')
django.setup()

from products.models import Category


def create_mega_menu_structure():
    """Create a sample mega menu structure."""
    
    print("Setting up mega menu categories...")
    
    # Men's Category Structure
    men_data = {
        'name': 'Men',
        'slug': 'men',
        'show_in_mega_menu': True,
        'mega_menu_order': 1,
        'mega_menu_icon': 'fa-mars',
        'children': [
            {
                'name': 'Topwear',
                'slug': 'men-topwear',
                'mega_menu_column_title': 'Topwear',
                'mega_menu_icon': 'fa-tshirt',
                'mega_menu_order': 1,
                'children': [
                    'T-Shirts', 'Casual Shirts', 'Formal Shirts', 'Sweatshirts',
                    'Sweaters', 'Jackets', 'Blazers & Coats', 'Suits', 'Rain Jackets'
                ]
            },
            {
                'name': 'Bottomwear',
                'slug': 'men-bottomwear',
                'mega_menu_column_title': 'Bottomwear',
                'mega_menu_icon': 'fa-user-tie',
                'mega_menu_order': 2,
                'children': [
                    'Jeans', 'Casual Trousers', 'Formal Trousers', 'Shorts', 'Track Pants & Joggers'
                ]
            },
            {
                'name': 'Footwear',
                'slug': 'men-footwear',
                'mega_menu_column_title': 'Footwear',
                'mega_menu_icon': 'fa-shoe-prints',
                'mega_menu_order': 3,
                'children': [
                    'Casual Shoes', 'Sports Shoes', 'Formal Shoes', 'Sneakers',
                    'Sandals & Floaters', 'Flip Flops', 'Socks'
                ]
            },
            {
                'name': 'Innerwear & Sleepwear',
                'slug': 'men-innerwear',
                'mega_menu_column_title': 'Innerwear & Sleepwear',
                'mega_menu_order': 4,
                'children': [
                    'Briefs & Trunks', 'Boxers', 'Vests', 'Sleepwear & Loungewear', 'Thermals'
                ]
            },
            {
                'name': 'Accessories',
                'slug': 'men-accessories',
                'mega_menu_column_title': 'Accessories',
                'mega_menu_icon': 'fa-glasses',
                'mega_menu_order': 5,
                'children': [
                    'Sunglasses', 'Watches', 'Wallets', 'Belts'
                ]
            }
        ]
    }
    
    # Women's Category Structure
    women_data = {
        'name': 'Women',
        'slug': 'women',
        'show_in_mega_menu': True,
        'mega_menu_order': 2,
        'mega_menu_icon': 'fa-venus',
        'children': [
            {
                'name': 'Indian & Fusion Wear',
                'slug': 'women-indian-wear',
                'mega_menu_column_title': 'Indian & Fusion Wear',
                'mega_menu_order': 1,
                'children': [
                    'Kurtas & Suits', 'Kurtis, Tunics & Tops', 'Sarees', 'Ethnic Wear',
                    'Leggings, Salwars & Churidars', 'Skirts & Palazzos', 'Dress Materials',
                    'Lehenga Cholis', 'Dupattas & Shawls'
                ]
            },
            {
                'name': 'Western Wear',
                'slug': 'women-western-wear',
                'mega_menu_column_title': 'Western Wear',
                'mega_menu_order': 2,
                'children': [
                    'Dresses', 'Tops', 'Tshirts', 'Jeans', 'Trousers & Capris',
                    'Shorts & Skirts', 'Co-ords', 'Playsuits', 'Jumpsuits'
                ]
            },
            {
                'name': 'Footwear',
                'slug': 'women-footwear',
                'mega_menu_column_title': 'Footwear',
                'mega_menu_icon': 'fa-shoe-prints',
                'mega_menu_order': 3,
                'children': [
                    'Flats', 'Casual Shoes', 'Heels', 'Boots', 'Sports Shoes & Sneakers', 'Sandals'
                ]
            },
            {
                'name': 'Lingerie & Sleepwear',
                'slug': 'women-lingerie',
                'mega_menu_column_title': 'Lingerie & Sleepwear',
                'mega_menu_order': 4,
                'children': [
                    'Bra', 'Briefs', 'Shapewear', 'Sleepwear & Loungewear', 'Swimwear', 'Camisoles'
                ]
            },
            {
                'name': 'Beauty & Personal Care',
                'slug': 'women-beauty',
                'mega_menu_column_title': 'Beauty & Personal Care',
                'mega_menu_icon': 'fa-spa',
                'mega_menu_order': 5,
                'children': [
                    'Makeup', 'Skincare', 'Premium Beauty', 'Lipsticks', 'Fragrances'
                ]
            }
        ]
    }
    
    # Kids Category Structure
    kids_data = {
        'name': 'Kids',
        'slug': 'kids',
        'show_in_mega_menu': True,
        'mega_menu_order': 3,
        'mega_menu_icon': 'fa-child',
        'children': [
            {
                'name': 'Boys Clothing',
                'slug': 'boys-clothing',
                'mega_menu_column_title': 'Boys Clothing',
                'mega_menu_order': 1,
                'children': [
                    'T-Shirts', 'Shirts', 'Shorts', 'Jeans', 'Trousers', 'Clothing Sets',
                    'Ethnic Wear', 'Track Pants & Pyjamas', 'Jacket, Sweater & Sweatshirts'
                ]
            },
            {
                'name': 'Girls Clothing',
                'slug': 'girls-clothing',
                'mega_menu_column_title': 'Girls Clothing',
                'mega_menu_order': 2,
                'children': [
                    'Dresses', 'Tops', 'Tshirts', 'Clothing Sets', 'Lehenga choli',
                    'Kurta Sets', 'Party wear', 'Dungarees & Jumpsuits', 'Skirts & shorts'
                ]
            },
            {
                'name': 'Footwear',
                'slug': 'kids-footwear',
                'mega_menu_column_title': 'Footwear',
                'mega_menu_icon': 'fa-shoe-prints',
                'mega_menu_order': 3,
                'children': [
                    'Casual Shoes', 'Flipflops', 'Sports Shoes', 'Flats', 'Sandals', 'Heels', 'Socks'
                ]
            },
            {
                'name': 'Toys & Games',
                'slug': 'toys-games',
                'mega_menu_column_title': 'Toys & Games',
                'mega_menu_icon': 'fa-gamepad',
                'mega_menu_order': 4,
                'children': [
                    'Learning & Development', 'Activity Toys', 'Soft Toys', 'Action Figure / Play set'
                ]
            },
            {
                'name': 'Infants',
                'slug': 'infants',
                'mega_menu_column_title': 'Infants',
                'mega_menu_icon': 'fa-baby',
                'mega_menu_order': 5,
                'children': [
                    'Bodysuits', 'Rompers & Sleepsuits', 'Clothing Sets',
                    'Tshirts & Tops', 'Dresses', 'Bottom wear'
                ]
            }
        ]
    }
    
    def create_category_tree(data, parent=None):
        """Create category tree recursively."""
        # Create or get the main category
        category, created = Category.objects.get_or_create(
            slug=data['slug'],
            defaults={
                'name': data['name'],
                'parent': parent,
                'show_in_mega_menu': data.get('show_in_mega_menu', False),
                'mega_menu_order': data.get('mega_menu_order', 0),
                'mega_menu_column_title': data.get('mega_menu_column_title', ''),
                'mega_menu_icon': data.get('mega_menu_icon', ''),
                'is_active': True
            }
        )
        
        if created:
            print(f"Created category: {category.name}")
        else:
            # Update existing category with mega menu settings
            category.show_in_mega_menu = data.get('show_in_mega_menu', False)
            category.mega_menu_order = data.get('mega_menu_order', 0)
            category.mega_menu_column_title = data.get('mega_menu_column_title', '')
            category.mega_menu_icon = data.get('mega_menu_icon', '')
            category.save()
            print(f"Updated category: {category.name}")
        
        # Create children
        if 'children' in data:
            for child_data in data['children']:
                if isinstance(child_data, str):
                    # Simple string child
                    child_slug = child_data.lower().replace(' ', '-').replace('&', 'and')
                    child_category, child_created = Category.objects.get_or_create(
                        slug=child_slug,
                        defaults={
                            'name': child_data,
                            'parent': category,
                            'show_in_mega_menu': True,
                            'is_active': True
                        }
                    )
                    if child_created:
                        print(f"  - Created subcategory: {child_category.name}")
                else:
                    # Nested category data
                    create_category_tree(child_data, category)
        
        return category
    
    # Create the category structures
    create_category_tree(men_data)
    create_category_tree(women_data)
    create_category_tree(kids_data)
    
    print("\nMega menu setup complete!")
    print("\nTo see the mega menu in action:")
    print("1. Go to admin panel (/admin/)")
    print("2. Navigate to Products > Categories")
    print("3. You'll see the new mega menu fields")
    print("4. Visit your homepage to see the dynamic mega dropdown!")
    print("\nNote: You can customize the categories, add icons, and reorder them from the admin.")


if __name__ == '__main__':
    create_mega_menu_structure()