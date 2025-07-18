# Homepage Admin Management Guide

## Overview
This guide explains how administrators can manage all homepage sections dynamically from the Django admin interface. The homepage content is now fully manageable without touching code.

## Homepage Sections Available

### 1. Hero Banner
- **Location**: Top of homepage (slider)
- **Admin Section**: Hero Banners
- **Features**:
  - Multiple slides with images
  - Title and subtitle for each slide
  - Optional call-to-action links
  - Order management
  - Active/inactive toggle

### 2. Deal of the Day
- **Location**: First product section
- **Admin Section**: Featured Products (section: "Deal of the Day")
- **Features**:
  - Select specific products to feature
  - Set expiration dates for deals
  - Order products by priority

### 3. Exclusive Brands
- **Location**: Brand showcase section
- **Admin Section**: Featured Brands (section: "Exclusive Brands")
- **Features**:
  - Select brands to highlight
  - Custom titles and descriptions
  - Custom images (or use brand logos)
  - Discount text display

### 4. Top Picks
- **Location**: Curated product selection
- **Admin Section**: Featured Products (section: "Top Picks")
- **Features**:
  - Hand-picked products
  - Priority ordering
  - Time-based featuring

### 5. Shop by Category
- **Location**: Category grid section
- **Admin Section**: Featured Categories
- **Features**:
  - Select categories to display
  - Custom category images
  - Custom titles
  - Order management

### 6. Brand Deals
- **Location**: Brand deals section
- **Admin Section**: Featured Brands (section: "Brand Deals")
- **Features**:
  - Promotional brand content
  - Discount information
  - Custom promotional images

### 7. Trending Now
- **Location**: Trending products section
- **Admin Section**: Featured Products (section: "Trending Now")
- **Features**:
  - Current trending items
  - Dynamic product selection
  - Automatic expiration

### 8. Category-Specific Sections
- **Indian Wear**: Featured Products (section: "Indian Wear")
- **Sports Wear**: Featured Products (section: "Sports Wear")
- **Footwear**: Featured Products (section: "Footwear")

### 9. New Brands
- **Location**: New brand showcase
- **Admin Section**: Featured Brands (section: "New Brands")
- **Features**:
  - Highlight new brand partnerships
  - Custom promotional content

## How to Manage Each Section

### Managing Hero Banners

1. **Access**: Admin → Core → Hero Banners
2. **Add New Banner**:
   - Click "Add Hero Banner"
   - Enter title and subtitle
   - Upload banner image (recommended: 1920x500px)
   - Set link URL and text (optional)
   - Set display order
   - Mark as active
3. **Best Practices**:
   - Use high-quality images
   - Keep titles concise
   - Test on mobile devices
   - Limit to 4-5 active banners

### Managing Featured Products

1. **Access**: Admin → Core → Featured Products
2. **Add Products to Section**:
   - Click "Add Featured Product"
   - Select the product
   - Choose the section (Deal of Day, Top Picks, etc.)
   - Set display order
   - Set expiration date (optional)
   - Mark as active
3. **Tips**:
   - Use high-performing products
   - Rotate products regularly
   - Set expiration dates for seasonal items
   - Monitor product availability

### Managing Featured Brands

1. **Access**: Admin → Core → Featured Brands
2. **Add Brand to Section**:
   - Click "Add Featured Brand"
   - Select the brand
   - Choose section (Exclusive Brands, Brand Deals, New Brands)
   - Add custom title/subtitle (optional)
   - Upload custom image (optional)
   - Add discount text
   - Set display order and expiration
3. **Best Practices**:
   - Coordinate with brand partners
   - Use compelling discount text
   - Update promotional images regularly

### Managing Featured Categories

1. **Access**: Admin → Core → Featured Categories
2. **Add Category**:
   - Click "Add Featured Category"
   - Select the category
   - Add custom title (optional)
   - Upload custom image (optional)
   - Set display order
   - Mark as active
3. **Tips**:
   - Choose popular categories
   - Use appealing category images
   - Update seasonally

### Homepage Settings

1. **Access**: Admin → Core → Homepage Settings
2. **Global Settings**:
   - Site name and description
   - Hero banner auto-play settings
   - Number of items per section
   - Slide duration timing

## Admin Workflow Examples

### Example 1: Setting up a Flash Sale

1. **Create Hero Banner**:
   - Title: "Flash Sale - 70% Off"
   - Image: Sale banner
   - Link: Sale category page

2. **Feature Sale Products**:
   - Go to Featured Products
   - Add 8 sale products to "Deal of the Day"
   - Set expiration to end of sale

3. **Update Brand Deals**:
   - Add participating brands to "Brand Deals"
   - Set discount text: "Up to 70% Off"

### Example 2: Seasonal Update (Winter Collection)

1. **Update Hero Banners**:
   - Replace summer banners with winter themes
   - Update titles and links

2. **Feature Winter Products**:
   - Add winter wear to "Trending Now"
   - Update "Indian Wear" with winter ethnic wear
   - Feature winter footwear in "Footwear" section

3. **Update Categories**:
   - Feature winter categories
   - Update category images with winter themes

### Example 3: New Brand Launch

1. **Add to New Brands**:
   - Feature the new brand in "New Brands" section
   - Add compelling description
   - Set promotional image

2. **Feature Brand Products**:
   - Add brand's best products to "Top Picks"
   - Feature in relevant category sections

## Best Practices

### Content Management
- **Regular Updates**: Refresh content weekly
- **Seasonal Relevance**: Update for festivals, seasons, trends
- **Performance Monitoring**: Track which products/brands perform best
- **A/B Testing**: Try different arrangements and measure results

### Image Guidelines
- **Hero Banners**: 1920x500px, high quality, mobile-friendly text
- **Product Images**: Use existing product images (managed in Products)
- **Brand Images**: 400x300px, brand-focused, clear logos
- **Category Images**: 300x300px, representative of category

### SEO Considerations
- Use descriptive titles and alt text
- Keep loading times fast
- Ensure mobile responsiveness
- Update meta descriptions seasonally

### Performance Tips
- **Limit Active Items**: Don't exceed recommended limits per section
- **Use Expiration Dates**: Automatically remove outdated content
- **Optimize Images**: Compress images before uploading
- **Monitor Load Times**: Check homepage speed regularly

## Troubleshooting

### Common Issues

1. **Products Not Showing**:
   - Check if product is active
   - Verify product has images
   - Check if featured item is active
   - Ensure expiration date hasn't passed

2. **Images Not Loading**:
   - Verify image file format (JPG, PNG, WebP)
   - Check file size (keep under 2MB)
   - Ensure proper file permissions

3. **Order Not Working**:
   - Check order numbers (lower numbers appear first)
   - Verify items are active
   - Clear cache if using caching

### Getting Help

- Check Django admin logs for errors
- Verify database migrations are applied
- Contact technical support for complex issues
- Review this guide for step-by-step instructions

## Migration Requirements

Before using these features, ensure you've run:

```bash
python manage.py migrate core
python manage.py migrate products
python manage.py migrate users
```

This will create all necessary database tables for homepage management.
