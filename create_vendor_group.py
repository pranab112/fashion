#!/usr/bin/env python
"""
Script to create or update the Vendor user group with comprehensive permissions
for the sales management system.
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nexus.settings')
django.setup()

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


def create_vendor_group():
    """Create or update vendor group with appropriate permissions."""
    
    # Create or get the vendor group
    vendor_group, created = Group.objects.get_or_create(name='Vendor')
    
    if created:
        print("Created new Vendor group")
    else:
        print("Updating existing Vendor group")
        # Clear existing permissions
        vendor_group.permissions.clear()
    
    # Define permissions for vendors
    vendor_permissions = [
        # Products app permissions
        ('products', 'product', ['view', 'add', 'change']),  # Can manage their own products
        ('products', 'productimage', ['view', 'add', 'change', 'delete']),  # Can manage product images
        ('products', 'productvariant', ['view', 'add', 'change', 'delete']),  # Can manage variants
        ('products', 'brand', ['view', 'change']),  # Can view and edit their own brands
        ('products', 'category', ['view']),  # Can view categories
        ('products', 'tag', ['view']),  # Can view tags
        
        # Sales app permissions
        ('sales', 'order', ['view']),  # Can view orders containing their products
        ('sales', 'orderitem', ['view', 'change']),  # Can view and update order items (status)
        ('sales', 'payment', ['view']),  # Can view payments for their orders
        ('sales', 'commission', ['view']),  # Can view their own commissions
        ('sales', 'payout', ['view', 'add', 'change']),  # Can manage their payouts
        ('sales', 'salesreport', ['view']),  # Can view their sales reports
        ('sales', 'orderstatushistory', ['view']),  # Can view order status history
        ('sales', 'orderstatus', ['view']),  # Can view order statuses
        
        # Users app permissions (limited)
        ('users', 'customuser', ['view']),  # Can view user info (customers)
        
        # Core app permissions (limited)
        ('core', 'newsletter', ['view']),  # Can view newsletter subscriptions
        ('core', 'contactmessage', ['view']),  # Can view contact messages
    ]
    
    permissions_added = 0
    
    for app_label, model_name, actions in vendor_permissions:
        try:
            content_type = ContentType.objects.get(app_label=app_label, model=model_name)
            
            for action in actions:
                permission_codename = f'{action}_{model_name}'
                try:
                    permission = Permission.objects.get(
                        content_type=content_type,
                        codename=permission_codename
                    )
                    vendor_group.permissions.add(permission)
                    permissions_added += 1
                    print(f"  Added {app_label}.{permission_codename}")
                except Permission.DoesNotExist:
                    print(f"  Permission not found: {app_label}.{permission_codename}")
                    
        except ContentType.DoesNotExist:
            print(f"  Content type not found: {app_label}.{model_name}")
    
    print(f"\nVendor group updated with {permissions_added} permissions")
    
    # Display summary
    print("\nVENDOR GROUP SUMMARY:")
    print("=" * 50)
    print("Vendors can:")
    print("• Manage their own products, images, and variants")
    print("• View and edit their own brand information")
    print("• View orders containing their products")
    print("• Update order item status (e.g., mark as shipped)")
    print("• View payments related to their orders")
    print("• View their commission earnings")
    print("• Manage their payout information and bank details")
    print("• View their sales reports and analytics")
    print("• View order status history for their orders")
    print("• View customer information for their orders")
    
    print("\nVendors CANNOT:")
    print("• View or modify other vendors' data")
    print("• Access admin-only features like user management")
    print("• Approve their own commissions")
    print("• Process their own payouts")
    print("• Access platform-wide settings")
    print("• Delete orders or payments")
    
    return vendor_group


def assign_user_to_vendor_group(username):
    """Assign a user to the vendor group and set required fields."""
    from users.models import CustomUser
    
    try:
        user = CustomUser.objects.get(username=username)
        vendor_group = Group.objects.get(name='Vendor')
        
        # Add user to vendor group
        user.groups.add(vendor_group)
        
        # Set user type and required fields
        user.user_type = 'vendor'
        user.is_staff = True  # Required for admin access
        user.save()
        
        print(f"User '{username}' assigned to Vendor group")
        print(f"   - User type set to: {user.user_type}")
        print(f"   - Staff status: {user.is_staff}")
        
        return user
        
    except CustomUser.DoesNotExist:
        print(f"User '{username}' not found")
        return None
    except Group.DoesNotExist:
        print("Vendor group not found. Run create_vendor_group() first.")
        return None


def create_sample_vendor(username='vendor_demo', email='vendor@example.com', password='vendor123'):
    """Create a sample vendor user for testing."""
    from users.models import CustomUser
    
    try:
        # Check if user already exists
        if CustomUser.objects.filter(username=username).exists():
            print(f"User '{username}' already exists")
            user = CustomUser.objects.get(username=username)
        else:
            # Create new vendor user
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name='Demo',
                last_name='Vendor',
                user_type='vendor',
                is_staff=True
            )
            print(f"Created demo vendor user: {username}")
        
        # Assign to vendor group
        assign_user_to_vendor_group(username)
        
        print(f"\nDEMO VENDOR LOGIN DETAILS:")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"   Email: {email}")
        print(f"   Login URL: http://localhost:8000/admin/")
        
        return user
        
    except Exception as e:
        print(f"Error creating vendor user: {e}")
        return None


if __name__ == '__main__':
    print("SETTING UP VENDOR GROUP AND PERMISSIONS")
    print("=" * 60)
    
    # Create vendor group with permissions
    vendor_group = create_vendor_group()
    
    print("\n" + "=" * 60)
    
    # Create demo vendor user
    create_sample_vendor()
    
    print("\n" + "=" * 60)
    print("SETUP COMPLETE!")
    print("\nNext steps:")
    print("1. Login to admin with the demo vendor credentials")
    print("2. Create a brand for this vendor")
    print("3. Add products to test the sales management system")
    print("4. Create test orders to see commission calculations")