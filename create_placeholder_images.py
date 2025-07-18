from PIL import Image, ImageDraw, ImageFont
import os

# Create images directory if it doesn't exist
os.makedirs('static/images', exist_ok=True)

# Create logo.png
logo = Image.new('RGB', (150, 40), color='#ff3f6c')
draw = ImageDraw.Draw(logo)
try:
    font = ImageFont.truetype('arial.ttf', 20)
except:
    font = ImageFont.load_default()
draw.text((75, 20), 'NEXUS', fill='white', anchor='mm', font=font)
logo.save('static/images/logo.png')
print('Created logo.png')

# Create favicon.png
favicon = Image.new('RGB', (32, 32), color='#ff3f6c')
draw = ImageDraw.Draw(favicon)
draw.text((16, 16), 'N', fill='white', anchor='mm', font=font)
favicon.save('static/images/favicon.png')
print('Created favicon.png')

# Create hero.jpg
hero = Image.new('RGB', (1920, 600), color='#f8f9fa')
draw = ImageDraw.Draw(hero)
draw.text((960, 300), 'Fashion Store Hero Image', fill='#333333', anchor='mm', font=font)
hero.save('static/images/hero.jpg')
print('Created hero.jpg')

# Create og-image.jpg
og = Image.new('RGB', (1200, 630), color='#ff3f6c')
draw = ImageDraw.Draw(og)
draw.text((600, 315), 'NEXUS Fashion Store', fill='white', anchor='mm', font=font)
og.save('static/images/og-image.jpg')
print('Created og-image.jpg')

print('All images created successfully!')
