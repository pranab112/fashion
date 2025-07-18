from PIL import Image, ImageDraw, ImageFont
import os

# Create icons directory if it doesn't exist
os.makedirs('static/images/icons', exist_ok=True)

# Icon sizes needed
sizes = [72, 96, 128, 144, 152, 192, 384, 512]

# Create icons for each size
for size in sizes:
    icon = Image.new('RGB', (size, size), color='#ff3f6c')
    draw = ImageDraw.Draw(icon)
    try:
        # Calculate font size based on icon size
        font_size = int(size * 0.5)  # 50% of icon size
        font = ImageFont.truetype('arial.ttf', font_size)
    except:
        font = ImageFont.load_default()
    
    # Draw 'N' in the center
    draw.text((size/2, size/2), 'N', fill='white', anchor='mm', font=font)
    
    # Save the icon
    icon.save(f'static/images/icons/icon-{size}x{size}.png')
    print(f'Created icon-{size}x{size}.png')

print('All icons created successfully!')
