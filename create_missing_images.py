from PIL import Image, ImageDraw, ImageFont
import os

# Change to static/images directory
os.chdir('static/images')

# Create missing hero banner images
for i in range(1, 4):
    img = Image.new('RGB', (1920, 500), (255, 63, 108))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype('arial.ttf', 60)
    except:
        font = ImageFont.load_default()
    
    text = ['NEW COLLECTION', 'SUMMER SALE', 'PREMIUM FASHION'][i-1]
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (1920 - text_width) // 2
    y = (500 - text_height) // 2
    
    draw.text((x+2, y+2), text, font=font, fill=(0, 0, 0, 128))
    draw.text((x, y), text, font=font, fill=(255, 255, 255))
    
    img.save(f'hero-banner-{i}.jpg', quality=90)
    print(f'Created hero-banner-{i}.jpg')

# Create missing deal images
for i in range(1, 5):
    img = Image.new('RGB', (400, 400), (245, 245, 246))
    draw = ImageDraw.Draw(img)
    
    # Add border
    draw.rectangle([(0, 0), (399, 399)], outline=(255, 63, 108), width=2)
    
    # Add discount badge
    draw.ellipse([(300, 20), (380, 100)], fill=(255, 63, 108))
    
    try:
        font = ImageFont.truetype('arial.ttf', 24)
        font_large = ImageFont.truetype('arial.ttf', 36)
    except:
        font = ImageFont.load_default()
        font_large = ImageFont.load_default()
    
    # Add discount text
    draw.text((320, 40), '-50%', font=font, fill=(255, 255, 255))
    
    # Add deal text
    text = f'DEAL {i}'
    bbox = draw.textbbox((0, 0), text, font=font_large)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (400 - text_width) // 2
    y = (400 - text_height) // 2
    
    draw.text((x, y), text, font=font_large, fill=(107, 114, 128))
    
    img.save(f'deal-{i}.jpg', quality=90)
    print(f'Created deal-{i}.jpg')

# Create category images
categories = ['Men', 'Women', 'Kids', 'Beauty', 'Home', 'Sports']
for i, category in enumerate(categories, 1):
    img = Image.new('RGB', (300, 300), (147, 51, 234))
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype('arial.ttf', 32)
    except:
        font = ImageFont.load_default()
    
    text = category.upper()
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (300 - text_width) // 2
    y = (300 - text_height) // 2
    
    draw.text((x, y), text, font=font, fill=(255, 255, 255))
    
    img.save(f'category-{i}.jpg', quality=90)
    print(f'Created category-{i}.jpg')

print('All missing images created successfully!')
