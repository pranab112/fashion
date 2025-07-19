#!/usr/bin/env python
"""
Debug script to check category structure and mega menu data.
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nexus.settings')
django.setup()

from products.models import Category


def debug_categories():
    """Debug category structure."""
    
    print("=== DEBUGGING CATEGORY STRUCTURE ===\n")
    
    # Check all categories
    all_categories = Category.objects.all()
    print(f"Total categories in database: {all_categories.count()}")
    
    # Check mega menu categories
    mega_menu_categories = Category.get_mega_menu_categories()
    print(f"Mega menu main categories: {mega_menu_categories.count()}")
    
    print("\n=== MEGA MENU MAIN CATEGORIES ===")
    for category in mega_menu_categories:
        print(f"- {category.name} (slug: {category.slug})")
        print(f"  Show in mega menu: {category.show_in_mega_menu}")
        print(f"  Order: {category.mega_menu_order}")
        print(f"  Icon: {category.mega_menu_icon}")
        
        # Check children
        children = category.get_mega_menu_children()
        print(f"  Children count: {children.count()}")
        
        for child in children:
            print(f"    - {child.name} (order: {child.mega_menu_order})")
            grandchildren = child.get_mega_menu_children()
            print(f"      Grandchildren: {grandchildren.count()}")
            for grandchild in grandchildren[:3]:  # Show first 3
                print(f"        - {grandchild.name}")
            if grandchildren.count() > 3:
                print(f"        ... and {grandchildren.count() - 3} more")
        print()
    
    # Check categories with show_in_mega_menu=True
    print("\n=== ALL CATEGORIES WITH MEGA MENU ENABLED ===")
    mega_enabled = Category.objects.filter(show_in_mega_menu=True)
    print(f"Total mega menu enabled categories: {mega_enabled.count()}")
    
    for cat in mega_enabled:
        parent_name = cat.parent.name if cat.parent else "None"
        print(f"- {cat.name} (parent: {parent_name}, level: {cat.level})")
    
    # Test context processor
    print("\n=== TESTING CONTEXT PROCESSOR ===")
    from core.context_processors import site_settings
    
    class MockRequest:
        pass
    
    request = MockRequest()
    context = site_settings(request)
    
    print(f"Main categories in context: {len(context.get('main_categories', []))}")
    print(f"Mega menu categories in context: {len(context.get('mega_menu_categories', []))}")
    
    for cat in context.get('mega_menu_categories', []):
        print(f"- Context category: {cat.name}")


if __name__ == '__main__':
    debug_categories()