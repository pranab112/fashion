#!/usr/bin/env python
"""
Script to fix the mega menu parent-child relationships.
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nexus.settings')
django.setup()

from products.models import Category


def fix_mega_menu_relationships():
    """Fix the parent-child relationships for mega menu."""
    
    print("Fixing mega menu parent-child relationships...")
    
    # Define the correct structure
    structure = {
        'men': {
            'children': [
                'topwear', 'bottomwear', 'footwear', 'innerwear-sleepwear', 'accessories'
            ]
        },
        'women': {
            'children': [
                'indian-fusion-wear', 'western-wear', 'footwear', 'lingerie-sleepwear', 'beauty-personal-care'
            ]
        },
        'kids': {
            'children': [
                'boys-clothing', 'girls-clothing', 'footwear', 'toys-games', 'infants'
            ]
        }
    }
    
    # Fix Men's category children
    men_category = Category.objects.filter(slug='men').first()
    if men_category:
        print(f"\nFixing {men_category.name} category...")
        
        # Find and link children
        topwear = Category.objects.filter(name='Topwear').first()
        if topwear:
            topwear.parent = men_category
            topwear.show_in_mega_menu = True
            topwear.mega_menu_order = 1
            topwear.mega_menu_icon = 'fa-tshirt'
            topwear.save()
            print(f"  - Linked {topwear.name}")
        
        bottomwear = Category.objects.filter(name='Bottomwear').first()
        if bottomwear:
            bottomwear.parent = men_category
            bottomwear.show_in_mega_menu = True
            bottomwear.mega_menu_order = 2
            bottomwear.save()
            print(f"  - Linked {bottomwear.name}")
        
        footwear = Category.objects.filter(name='Footwear', parent=None).first()
        if footwear:
            footwear.parent = men_category
            footwear.show_in_mega_menu = True
            footwear.mega_menu_order = 3
            footwear.mega_menu_icon = 'fa-shoe-prints'
            footwear.save()
            print(f"  - Linked {footwear.name}")
        
        innerwear = Category.objects.filter(name='Innerwear & Sleepwear').first()
        if innerwear:
            innerwear.parent = men_category
            innerwear.show_in_mega_menu = True
            innerwear.mega_menu_order = 4
            innerwear.save()
            print(f"  - Linked {innerwear.name}")
        
        accessories = Category.objects.filter(name='Accessories').first()
        if accessories:
            accessories.parent = men_category
            accessories.show_in_mega_menu = True
            accessories.mega_menu_order = 5
            accessories.mega_menu_icon = 'fa-glasses'
            accessories.save()
            print(f"  - Linked {accessories.name}")
    
    # Fix Women's category children
    women_category = Category.objects.filter(slug='women').first()
    if women_category:
        print(f"\nFixing {women_category.name} category...")
        
        # Find and link children
        indian_wear = Category.objects.filter(name='Indian & Fusion Wear').first()
        if indian_wear:
            indian_wear.parent = women_category
            indian_wear.show_in_mega_menu = True
            indian_wear.mega_menu_order = 1
            indian_wear.save()
            print(f"  - Linked {indian_wear.name}")
        
        western_wear = Category.objects.filter(name='Western Wear').first()
        if western_wear:
            western_wear.parent = women_category
            western_wear.show_in_mega_menu = True
            western_wear.mega_menu_order = 2
            western_wear.save()
            print(f"  - Linked {western_wear.name}")
        
        # Create separate footwear for women or link existing
        women_footwear = Category.objects.filter(name='Footwear', parent=None).exclude(
            children__name__in=['Casual Shoes', 'Sports Shoes']  # Exclude men's footwear
        ).first()
        if not women_footwear:
            # Find women's specific footwear or create
            women_footwear = Category.objects.filter(
                name='Footwear',
                children__name__in=['Flats', 'Heels']
            ).first()
        
        if women_footwear:
            women_footwear.parent = women_category
            women_footwear.show_in_mega_menu = True
            women_footwear.mega_menu_order = 3
            women_footwear.mega_menu_icon = 'fa-shoe-prints'
            women_footwear.save()
            print(f"  - Linked {women_footwear.name}")
        
        lingerie = Category.objects.filter(name='Lingerie & Sleepwear').first()
        if lingerie:
            lingerie.parent = women_category
            lingerie.show_in_mega_menu = True
            lingerie.mega_menu_order = 4
            lingerie.save()
            print(f"  - Linked {lingerie.name}")
        
        beauty = Category.objects.filter(name='Beauty & Personal Care').first()
        if beauty:
            beauty.parent = women_category
            beauty.show_in_mega_menu = True
            beauty.mega_menu_order = 5
            beauty.mega_menu_icon = 'fa-spa'
            beauty.save()
            print(f"  - Linked {beauty.name}")
    
    # Fix Kids' category children
    kids_category = Category.objects.filter(slug='kids').first()
    if kids_category:
        print(f"\nFixing {kids_category.name} category...")
        
        # Find and link children
        boys_clothing = Category.objects.filter(name='Boys Clothing').first()
        if boys_clothing:
            boys_clothing.parent = kids_category
            boys_clothing.show_in_mega_menu = True
            boys_clothing.mega_menu_order = 1
            boys_clothing.save()
            print(f"  - Linked {boys_clothing.name}")
        
        girls_clothing = Category.objects.filter(name='Girls Clothing').first()
        if girls_clothing:
            girls_clothing.parent = kids_category
            girls_clothing.show_in_mega_menu = True
            girls_clothing.mega_menu_order = 2
            girls_clothing.save()
            print(f"  - Linked {girls_clothing.name}")
        
        # Find kids footwear
        kids_footwear = Category.objects.filter(
            name='Footwear',
            children__name__in=['Flipflops']
        ).first()
        if kids_footwear:
            kids_footwear.parent = kids_category
            kids_footwear.show_in_mega_menu = True
            kids_footwear.mega_menu_order = 3
            kids_footwear.mega_menu_icon = 'fa-shoe-prints'
            kids_footwear.save()
            print(f"  - Linked {kids_footwear.name}")
        
        toys = Category.objects.filter(name='Toys & Games').first()
        if toys:
            toys.parent = kids_category
            toys.show_in_mega_menu = True
            toys.mega_menu_order = 4
            toys.mega_menu_icon = 'fa-gamepad'
            toys.save()
            print(f"  - Linked {toys.name}")
        
        infants = Category.objects.filter(name='Infants').first()
        if infants:
            infants.parent = kids_category
            infants.show_in_mega_menu = True
            infants.mega_menu_order = 5
            infants.mega_menu_icon = 'fa-baby'
            infants.save()
            print(f"  - Linked {infants.name}")
    
    # Rebuild MPTT tree
    Category.objects.rebuild()
    
    print("\nMega menu relationships fixed!")
    print("Now testing the structure...")
    
    # Test the structure
    mega_menu_categories = Category.get_mega_menu_categories()
    print(f"\nMega menu main categories: {mega_menu_categories.count()}")
    
    for category in mega_menu_categories:
        children = category.get_mega_menu_children()
        print(f"- {category.name}: {children.count()} children")
        for child in children:
            grandchildren = child.get_mega_menu_children()
            print(f"  - {child.name}: {grandchildren.count()} items")


if __name__ == '__main__':
    fix_mega_menu_relationships()