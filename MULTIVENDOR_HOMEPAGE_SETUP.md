# Multivendor & Homepage Admin Setup Guide

## Quick Start

Your system already has both multivendor and homepage admin features fully implemented! Here's how to get started:

### 1. Access the Admin Interface

```bash
# Start the development server
python manage.py runserver

# Access admin at: http://localhost:8000/admin/
```

### 2. Populate Sample Homepage Data

```bash
# Run the population script
python manage.py shell < populate_homepage_data.py
```

This will create:
- Homepage settings
- Sample hero banners (you'll need to add images)
- Featured products, brands, and categories

### 3. Managing Homepage Content

#### Hero Banners
- Go to: Admin → Core → Hero Banners
- Add images, titles, and links
- Set display order
- Toggle active/inactive

#### Featured Products
- Go to: Admin → Core → Featured Products
- Select products for different sections:
  - Deal of the Day
  - Top Picks
  - Trending Now
  - Indian Wear
  - Sports Wear
  - Footwear

#### Featured Brands
- Go to: Admin → Core → Featured Brands
- Add brands to sections:
  - Exclusive Brands
  - Brand Deals
  - New Brands
- Add custom images and discount text

#### Featured Categories
- Go to: Admin → Core → Featured Categories
- Select categories to display
- Add custom images and titles

### 4. Creating Vendor Accounts

#### Step 1: Create Vendor User
1. Go to: Admin → Users → Custom Users
2. Click "Add Custom User"
3. Set:
   - User Type: "Vendor"
   - Is Vendor Approved: ✓ (checked)
   - Vendor Commission Rate: (e.g., 10.00)

#### Step 2: Create Vendor Brand
1. Go to: Admin → Products → Brands
2. Click "Add Brand"
3. Fill in:
   - Name, Slug, Description
   - **Vendor**: Select the vendor user
   - **Is Verified**: ✓ (checked)
   - Shop details (banner, policies, etc.)

#### Step 3: Add Products
1. Go to: Admin → Products → Products
2. Create products under the vendor's brand

### 5. Vendor Permissions

When logged in as a vendor, they can:
- ✅ Manage their own brands
- ✅ Add/edit products under their brands
- ✅ View their orders
- ✅ Update shop information
- ❌ Cannot see other vendors' data
- ❌ Cannot change featured status
- ❌ Cannot modify commission rates

### 6. Commission System

Commission hierarchy:
1. **Brand-specific rate** (if set)
2. **Vendor-specific rate** (if set)
3. **Default rate** (10%)

### 7. Testing the Setup

1. **View Homepage**: Visit http://localhost:8000/
2. **Check Dynamic Content**: All sections should show data from admin
3. **Test Vendor Access**: 
   - Create a vendor account
   - Log in as vendor
   - Access admin to see limited permissions

### 8. Next Steps

1. **Upload Images**:
   - Hero banner images (1920x500px recommended)
   - Brand logos
   - Category images

2. **Create Content**:
   - Add real products
   - Set up actual vendor accounts
   - Configure featured sections

3. **Customize**:
   - Adjust homepage settings
   - Modify section limits
   - Update slide durations

### 9. Troubleshooting

**Homepage shows static content:**
- Run the populate script
- Check if featured items are active
- Verify expiration dates haven't passed

**Vendor can't access admin:**
- Ensure is_staff is True
- Check is_vendor_approved is True
- Verify user_type is set to "vendor"

**Images not showing:**
- Check MEDIA_URL settings
- Ensure media files are served in development
- Upload images through admin

### 10. Important URLs

- **Homepage**: http://localhost:8000/
- **Admin**: http://localhost:8000/admin/
- **Products**: http://localhost:8000/products/
- **Brands**: http://localhost:8000/brands/

## Summary

Your multivendor system is ready to use! The homepage is fully dynamic and controlled through the admin interface. Simply log in as an admin, add content, and watch it appear on your site instantly.