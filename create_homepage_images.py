#!/usr/bin/env python3
"""
Script to create placeholder images for the Myntra-style homepage
"""

import os
from PIL import Image, ImageDraw, ImageFont
import random

# Create static/images directory if it doesn't exist
images_dir = "static/images"
os.makedirs(images_dir, exist_ok=True)

def create_gradient_image(width, height, color1, color2, text="", filename=""):
    """Create a gradient image with text overlay"""
    # Create image
    img = Image.new('RGB', (width, height), color1)
    draw = ImageDraw.Draw(img)
    
    # Create gradient effect
    for y in range(height):
        ratio = y / height
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Add text if provided
    if text:
        try:
            # Try to use a nice font
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            # Fallback to default font
            font = ImageFont.load_default()
        
        # Get text size
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center text
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # Add text with shadow
        draw.text((x+2, y+2), text, fill=(0, 0, 0), font=font)
        draw.text((x, y), text, fill=(255, 255, 255), font=font)
    
    # Save image
    img.save(os.path.join(images_dir, filename))
    print(f"Created: {filename}")

def create_solid_image(width, height, color, text="", filename=""):
    """Create a solid color image with text"""
    img = Image.new('RGB', (width, height), color)
    draw = ImageDraw.Draw(img)
    
    if text:
        try:
            font = ImageFont.truetype("arial.ttf", 30)
        except:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # Choose contrasting text color
        text_color = (255, 255, 255) if sum(color) < 400 else (0, 0, 0)
        draw.text((x, y), text, fill=text_color, font=font)
    
    img.save(os.path.join(images_dir, filename))
    print(f"Created: {filename}")

# Hero banner images (4 slides)
hero_colors = [
    ((255, 63, 108), (255, 20, 95)),  # Pink gradient
    ((138, 43, 226), (75, 0, 130)),   # Purple gradient
    ((255, 140, 0), (255, 69, 0)),    # Orange gradient
    ((34, 193, 195), (253, 187, 45))  # Teal to yellow
]

hero_texts = [
    "FLAT ₹400 OFF",
    "BIGGEST SALE",
    "PREMIUM BRANDS", 
    "NEW ARRIVALS"
]

for i in range(4):
    create_gradient_image(
        1200, 500, 
        hero_colors[i][0], hero_colors[i][1],
        hero_texts[i],
        f"hero-banner-{i+1}.jpg"
    )

# Deal images (8 deals)
deal_colors = [
    (255, 182, 193), (255, 160, 122), (255, 218, 185), (221, 160, 221),
    (173, 216, 230), (144, 238, 144), (255, 228, 181), (255, 192, 203)
]

for i in range(8):
    create_solid_image(
        300, 200,
        deal_colors[i],
        f"DEAL {i+1}",
        f"deal-{i+1}.jpg"
    )

# Exclusive brand images (6 brands)
brand_colors = [
    (72, 61, 139), (106, 90, 205), (123, 104, 238),
    (147, 112, 219), (138, 43, 226), (148, 0, 211)
]

for i in range(6):
    create_gradient_image(
        400, 250,
        brand_colors[i], (min(255, brand_colors[i][0] + 50), min(255, brand_colors[i][1] + 50), min(255, brand_colors[i][2] + 50)),
        f"EXCLUSIVE {i+1}",
        f"exclusive-brand-{i+1}.jpg"
    )

# Top picks (4 images)
top_pick_colors = [
    ((255, 99, 132), (255, 159, 64)),
    ((54, 162, 235), (153, 102, 255)),
    ((255, 205, 86), (75, 192, 192)),
    ((201, 203, 207), (255, 99, 132))
]

for i in range(4):
    create_gradient_image(
        350, 350,
        top_pick_colors[i][0], top_pick_colors[i][1],
        f"TOP PICK {i+1}",
        f"top-pick-{i+1}.jpg"
    )

# Category images (16 categories)
category_names = [
    "MEN", "WOMEN", "KIDS", "SHOES", "BAGS", "WATCHES", 
    "JEWELRY", "BEAUTY", "SPORTS", "HOME", "ETHNIC", "WESTERN",
    "CASUAL", "FORMAL", "PARTY", "WINTER"
]

category_colors = [
    (220, 20, 60), (255, 20, 147), (255, 105, 180), (255, 182, 193),
    (106, 90, 205), (72, 61, 139), (123, 104, 238), (147, 112, 219),
    (34, 139, 34), (50, 205, 50), (144, 238, 144), (152, 251, 152),
    (255, 140, 0), (255, 165, 0), (255, 215, 0), (255, 255, 0)
]

for i in range(16):
    create_solid_image(
        200, 150,
        category_colors[i],
        category_names[i],
        f"category-{i+1}.jpg"
    )

# Brand deal images (16 brands)
brand_names = [
    "NIKE", "ADIDAS", "PUMA", "REEBOK", "ZARA", "H&M", 
    "UNIQLO", "MANGO", "LEVIS", "TOMMY", "CALVIN", "POLO",
    "GUCCI", "PRADA", "ARMANI", "VERSACE"
]

for i in range(16):
    color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
    create_solid_image(
        250, 180,
        color,
        brand_names[i],
        f"brand-{i+1}.jpg"
    )

# Indian wear images (6 images)
indian_wear_items = ["SAREES", "LEHENGAS", "KURTAS", "SHERWANIS", "ANARKALIS", "PALAZZO"]

for i in range(6):
    color = (random.randint(100, 255), random.randint(50, 150), random.randint(50, 150))
    create_solid_image(
        300, 220,
        color,
        indian_wear_items[i],
        f"indian-wear-{i+1}.jpg"
    )

# Sports wear images (6 images)
sports_items = ["RUNNING", "GYM", "YOGA", "CRICKET", "FOOTBALL", "TENNIS"]

for i in range(6):
    color = (random.randint(50, 150), random.randint(100, 255), random.randint(50, 150))
    create_solid_image(
        300, 220,
        color,
        sports_items[i],
        f"sports-wear-{i+1}.jpg"
    )

# Footwear images (6 images)
footwear_items = ["SNEAKERS", "BOOTS", "SANDALS", "HEELS", "FLATS", "LOAFERS"]

for i in range(6):
    color = (random.randint(50, 150), random.randint(50, 150), random.randint(100, 255))
    create_solid_image(
        300, 220,
        color,
        footwear_items[i],
        f"footwear-{i+1}.jpg"
    )

# New brand images (4 images)
new_brands = ["NEW BRAND 1", "NEW BRAND 2", "NEW BRAND 3", "NEW BRAND 4"]

for i in range(4):
    create_gradient_image(
        400, 300,
        (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)),
        (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)),
        new_brands[i],
        f"new-brand-{i+1}.jpg"
    )

# Create a placeholder image for missing products
create_solid_image(
    400, 400,
    (240, 240, 240),
    "NO IMAGE",
    "placeholder.jpg"
)

print("\n✅ All homepage images created successfully!")
print(f"📁 Images saved in: {images_dir}/")
print("🎨 Total images created: 75+")
