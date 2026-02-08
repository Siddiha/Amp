#!/usr/bin/env python3
"""
Generate extension icons for YouTube AI Music Agent
Creates 16x16, 48x48, and 128x128 PNG icons
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_gradient_background(size):
    """Create a purple gradient background."""
    image = Image.new('RGB', (size, size))
    draw = ImageDraw.Draw(image)

    # Purple gradient colors
    color1 = (102, 126, 234)  # #667eea
    color2 = (118, 75, 162)   # #764ba2

    # Draw gradient
    for y in range(size):
        # Interpolate between colors
        ratio = y / size
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        draw.line([(0, y), (size, y)], fill=(r, g, b))

    return image

def draw_music_note(draw, size):
    """Draw a music note on the image."""
    # Scale factor for the note
    scale = size / 128
    center_x = size // 2
    center_y = size // 2

    # Music note circle (bottom)
    note_radius = int(12 * scale)
    circle_x = center_x - int(8 * scale)
    circle_y = center_y + int(15 * scale)
    draw.ellipse(
        [circle_x - note_radius, circle_y - note_radius,
         circle_x + note_radius, circle_y + note_radius],
        fill='white'
    )

    # Music note stem
    stem_width = int(6 * scale)
    stem_height = int(50 * scale)
    stem_x = circle_x + note_radius - stem_width // 2
    stem_y = circle_y - stem_height
    draw.rectangle(
        [stem_x, stem_y, stem_x + stem_width, circle_y],
        fill='white'
    )

    # Music note flag (top curve)
    flag_width = int(20 * scale)
    flag_height = int(15 * scale)
    draw.ellipse(
        [stem_x - flag_width, stem_y - flag_height,
         stem_x + stem_width + flag_width, stem_y + flag_height],
        fill='white'
    )

def create_icon(size, output_path):
    """Create a single icon of specified size."""
    print(f"Creating {size}x{size} icon...")

    # Create gradient background
    image = create_gradient_background(size)
    draw = ImageDraw.Draw(image)

    # Draw music note
    draw_music_note(draw, size)

    # Save
    image.save(output_path, 'PNG')
    print(f"[OK] Saved: {output_path}")

def main():
    """Generate all required icons."""
    print("YouTube AI Music Agent - Icon Generator\n")

    # Create icons directory if it doesn't exist
    icons_dir = os.path.join(os.path.dirname(__file__), 'icons')
    os.makedirs(icons_dir, exist_ok=True)

    # Generate icons
    sizes = [16, 48, 128]
    for size in sizes:
        output_path = os.path.join(icons_dir, f'icon{size}.png')
        create_icon(size, output_path)

    print("\nAll icons generated successfully!")
    print(f"Icons saved in: {icons_dir}")
    print("\nNext steps:")
    print("1. Open Chrome → chrome://extensions/")
    print("2. Enable Developer mode")
    print("3. Click 'Load unpacked'")
    print("4. Select the youtube-extension folder")
    print("5. Configure your API key in the extension popup")

if __name__ == '__main__':
    main()
