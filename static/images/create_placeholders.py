"""
Script to create placeholder images for the e-commerce website
"""
from PIL import Image, ImageDraw, ImageFont
import os

# Create images directory if it doesn't exist
os.makedirs('.', exist_ok=True)

# Define color scheme
PINK = (255, 63, 108)
PURPLE = (147, 51, 234)
GRAY = (107, 114, 128)
WHITE = (255, 255, 255)
LIGHT_GRAY = (245, 245, 246)

def create_gradient(width, height, color1, color2):
    """Create a gradient image"""
    img = Image.new('RGB', (width, height), color1)
    draw = ImageDraw.Draw(img)
    
    for i in range(height):
        r = int(color1[0] + (color2[0] - color1[0]) * i / height)
        g = int(color1[1] + (color2[1] - color1[1]) * i / height)
        b = int(color1[2] + (color2[2] - color1[2]) * i / height)
        draw.rectangle([(0, i), (width, i + 1)], fill=(r, g, b))
    
    return img

def add_text(img, text, position='center', color=WHITE, size=40):
    """Add text to image"""
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", size)
    except:
        font = ImageFont.load_default()
    
    # Get text size
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    if position == 'center':
        x = (img.width - text_width) // 2
        y = (img.height - text_height) // 2
    else:
        x, y = position
    
    # Add shadow
    shadow_offset = 2
    draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=(0, 0, 0, 128))
    draw.text((x, y), text, font=font, fill=color)
    
    return img

# Create hero banners
print("Creating hero banners...")
for i in range(1, 4):
    img = create_gradient(1920, 500, PINK, PURPLE)
    text = ["NEW COLLECTION", "SUMMER SALE", "PREMIUM FASHION"][i-1]
    img = add_text(img, text, size=60)
    img.save(f'hero-banner-{i}.jpg', quality=90)

# Create deal images
print("Creating deal images...")
for i in range(1, 5):
    img = Image.new('RGB', (400, 400), LIGHT_GRAY)
    draw = ImageDraw.Draw(img)
    
    # Add border
    draw.rectangle([(0, 0), (399, 399)], outline=PINK, width=2)
    
    # Add discount badge
    draw.ellipse([(300, 20), (380, 100)], fill=PINK)
    img = add_text(img, "-50%", position=(320, 40), size=24)
    
    # Add product text
    img = add_text(img, f"DEAL {i}", color=GRAY, size=36)
    
    img.save(f'deal-{i}.jpg', quality=90)

# Create category images
print("Creating category images...")
categories = ["Men", "Women", "Kids", "Beauty", "Home", "Sports"]
for i, category in enumerate(categories, 1):
    img = create_gradient(300, 300, PURPLE, PINK)
    img = add_text(img, category.upper(), size=32)
    img.save(f'category-{i}.jpg', quality=90)

# Create product placeholder
print("Creating product placeholder...")
img = Image.new('RGB', (800, 1000), LIGHT_GRAY)
draw = ImageDraw.Draw(img)
draw.rectangle([(0, 0), (799, 999)], outline=GRAY, width=1)
img = add_text(img, "PRODUCT\nIMAGE", color=GRAY, size=48)
img.save('product-placeholder.jpg', quality=90)

# Create logo
print("Creating logo...")
logo = Image.new('RGBA', (200, 60), (255, 255, 255, 0))
draw = ImageDraw.Draw(logo)
draw.rectangle([(10, 10), (190, 50)], fill=PINK)
logo = add_text(logo, "NEXUS", position='center', size=28)
logo.save('logo.png')

# Create favicon
print("Creating favicon...")
favicon = Image.new('RGB', (32, 32), PINK)
draw = ImageDraw.Draw(favicon)
draw.text((8, 4), "N", font=ImageFont.load_default(), fill=WHITE)
favicon.save('favicon.png')

# Create OG image
print("Creating OG image...")
og_img = create_gradient(1200, 630, PINK, PURPLE)
og_img = add_text(og_img, "NEXUS", size=80)
og_img = add_text(og_img, "Fashion & Lifestyle", position=(0, 400), size=40)
og_img.save('og-image.jpg', quality=90)

print("All placeholder images created successfully!")
