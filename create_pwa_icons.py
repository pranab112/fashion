from PIL import Image, ImageDraw, ImageFont
import os

# Create icons directory if it doesn't exist
os.makedirs('static/images/icons', exist_ok=True)

# Create icon-144x144.png
icon = Image.new('RGB', (144, 144), color='#ff3f6c')
draw = ImageDraw.Draw(icon)
try:
    font = ImageFont.truetype('arial.ttf', 72)
except:
    font = ImageFont.load_default()
draw.text((72, 72), 'N', fill='white', anchor='mm', font=font)
icon.save('static/images/icons/icon-144x144.png')
print('Created icon-144x144.png')
