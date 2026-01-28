#!/usr/bin/env python3
"""
Generate Kiin brand logos and watermarks
"""

from PIL import Image, ImageDraw, ImageFont
import json
import os

def load_brand_colors():
    """Load brand colors from colors.json"""
    with open('colors.json', 'r') as f:
        colors = json.load(f)
    return colors['hex_values']

def create_logo(width=800, height=200):
    """Create the main Kiin logo"""
    colors = load_brand_colors()
    
    # Create image with transparent background
    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Try to use a nice font, fall back to default
    try:
        # Try different font sizes to find what fits
        font_size = int(height * 0.6)
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except:
        try:
            font_size = int(height * 0.6)  
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
    
    # Text to draw
    text = "Kiin"
    
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center the text
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Draw text in primary brand color
    primary_color = colors['primary']
    # Convert hex to RGB
    primary_rgb = tuple(int(primary_color[1:][i:i+2], 16) for i in (0, 2, 4))
    
    draw.text((x, y), text, fill=primary_rgb + (255,), font=font)
    
    # Add tagline below
    tagline = "Care coordination made easier"
    tagline_size = int(height * 0.15)
    
    try:
        tagline_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", tagline_size)
    except:
        try:
            tagline_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", tagline_size)
        except:
            tagline_font = ImageFont.load_default()
    
    # Get tagline bounding box
    tagline_bbox = draw.textbbox((0, 0), tagline, font=tagline_font)
    tagline_width = tagline_bbox[2] - tagline_bbox[0]
    tagline_height = tagline_bbox[3] - tagline_bbox[1]
    
    # Position tagline
    tagline_x = (width - tagline_width) // 2
    tagline_y = y + text_height + 10
    
    # Use secondary color for tagline
    secondary_color = colors['secondary']
    secondary_rgb = tuple(int(secondary_color[1:][i:i+2], 16) for i in (0, 2, 4))
    
    draw.text((tagline_x, tagline_y), tagline, fill=secondary_rgb + (255,), font=tagline_font)
    
    return img

def create_watermark(size=200):
    """Create a subtle watermark version"""
    colors = load_brand_colors()
    
    # Create square image with transparent background
    img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Use smaller font for watermark
    try:
        font_size = int(size * 0.3)
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
    
    text = "Kiin"
    
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center the text
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    # Use primary color but with reduced opacity for watermark
    primary_color = colors['primary']
    primary_rgb = tuple(int(primary_color[1:][i:i+2], 16) for i in (0, 2, 4))
    
    # Draw with 60% opacity for watermark
    draw.text((x, y), text, fill=primary_rgb + (153,), font=font)  # 153 = 60% of 255
    
    return img

def main():
    """Generate all logo assets"""
    print("Generating Kiin brand assets...")
    
    # Change to the brand directory
    os.chdir('/Users/nick/clawd/kiin-content/brand/')
    
    # Generate main logo
    print("Creating logo.png...")
    logo = create_logo()
    logo.save('logo.png', 'PNG')
    
    # Generate watermark
    print("Creating watermark.png...")
    watermark = create_watermark()
    watermark.save('watermark.png', 'PNG')
    
    print("Brand assets generated successfully!")
    print("- logo.png: Main Kiin wordmark with tagline")
    print("- watermark.png: Subtle watermark for videos")

if __name__ == "__main__":
    main()