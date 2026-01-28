#!/usr/bin/env python3
"""
Kiin Content Quote Card Generator

Generate beautiful, shareable quote cards for Instagram and Pinterest with
elegant typography, gradient backgrounds, and Kiin branding.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from PIL.ImageColor import getrgb
import textwrap
import random
import math

# Kiin brand colors
KIIN_COLORS = {
    "primary": "#4A90B8",
    "secondary": "#6BB3A0", 
    "accent": "#F4A460",
    "background_warm": "#FDF9F5",
    "background_cool": "#F8FAFB",
    "text_light": "#FFFFFF",
    "text_dark": "#2C3E50"
}

class QuoteCardGenerator:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.brand_dir = self.base_dir / "brand"
        self.config_dir = self.base_dir / "config"
        self.load_brand_assets()
        self.load_templates()
        self.load_confessions()
    
    def load_brand_assets(self):
        """Load Kiin logo and watermark"""
        try:
            self.logo = Image.open(self.brand_dir / "logo.png").convert("RGBA")
            self.watermark = Image.open(self.brand_dir / "watermark.png").convert("RGBA")
        except FileNotFoundError:
            print("Warning: Brand assets not found. Continuing without logo/watermark.")
            self.logo = None
            self.watermark = None
    
    def load_templates(self):
        """Load quote card templates"""
        template_path = self.config_dir / "quote_templates.json"
        try:
            with open(template_path, 'r') as f:
                self.templates = json.load(f)
        except FileNotFoundError:
            print(f"Templates file not found: {template_path}")
            print("Using default templates")
            self.templates = self.get_default_templates()
    
    def load_confessions(self):
        """Load confessions for quote extraction"""
        confessions_path = self.config_dir / "confessions.json"
        try:
            with open(confessions_path, 'r') as f:
                data = json.load(f)
                # Handle both old and new formats
                if isinstance(data, list):
                    self.confessions = data
                elif "confessions" in data:
                    self.confessions = data["confessions"]
                else:
                    self.confessions = []
        except FileNotFoundError:
            print("Warning: Confessions file not found. --from-confession won't work.")
            self.confessions = []
    
    def get_default_templates(self):
        """Default templates if file doesn't exist"""
        return {
            "minimal": {
                "name": "Minimal",
                "description": "Clean, centered text on gradient background",
                "background_type": "gradient",
                "gradient_colors": ["#F8FAFB", "#E8F4FD"],
                "gradient_direction": "diagonal",
                "text_position": "center",
                "font_size": "large",
                "font_weight": "normal",
                "text_color": "#2C3E50",
                "accent_color": "#4A90B8",
                "decorative_elements": ["subtle_border"],
                "branding_position": "bottom-right",
                "branding_opacity": 0.7
            },
            "warm": {
                "name": "Warm & Caring",
                "description": "Warm colors with soft decorative elements",
                "background_type": "gradient",
                "gradient_colors": ["#FDF9F5", "#F4A460"],
                "gradient_direction": "radial",
                "text_position": "center",
                "font_size": "medium",
                "font_weight": "bold",
                "text_color": "#2C3E50",
                "accent_color": "#F4A460",
                "decorative_elements": ["soft_frame", "quote_marks"],
                "branding_position": "bottom-left",
                "branding_opacity": 0.6
            },
            "supportive": {
                "name": "Supportive",
                "description": "Green-toned with supportive visual elements",
                "background_type": "gradient",
                "gradient_colors": ["#F0FFF0", "#6BB3A0"],
                "gradient_direction": "vertical",
                "text_position": "center",
                "font_size": "large",
                "font_weight": "bold",
                "text_color": "#FFFFFF",
                "accent_color": "#6BB3A0",
                "decorative_elements": ["heart_accent", "soft_shadow"],
                "branding_position": "bottom-center",
                "branding_opacity": 0.8
            },
            "elegant": {
                "name": "Elegant",
                "description": "Sophisticated design with serif typography",
                "background_type": "gradient",
                "gradient_colors": ["#4A90B8", "#2C3E50"],
                "gradient_direction": "diagonal",
                "text_position": "center",
                "font_size": "xlarge",
                "font_weight": "light",
                "text_color": "#FFFFFF",
                "accent_color": "#F4A460",
                "decorative_elements": ["elegant_border", "flourish"],
                "branding_position": "top-right",
                "branding_opacity": 0.9
            },
            "modern": {
                "name": "Modern",
                "description": "Contemporary design with bold typography",
                "background_type": "solid",
                "gradient_colors": ["#2C3E50"],
                "gradient_direction": "none",
                "text_position": "offset",
                "font_size": "xlarge",
                "font_weight": "bold",
                "text_color": "#FFFFFF",
                "accent_color": "#4A90B8",
                "decorative_elements": ["geometric_accent", "bold_line"],
                "branding_position": "bottom-right",
                "branding_opacity": 1.0
            },
            "dreamy": {
                "name": "Dreamy",
                "description": "Soft, ethereal design with light colors",
                "background_type": "gradient",
                "gradient_colors": ["#E8F4FD", "#F0F8FF", "#FFFFFF"],
                "gradient_direction": "radial",
                "text_position": "center",
                "font_size": "medium",
                "font_weight": "normal",
                "text_color": "#4A90B8",
                "accent_color": "#6BB3A0",
                "decorative_elements": ["cloud_texture", "soft_glow"],
                "branding_position": "bottom-right",
                "branding_opacity": 0.5
            }
        }
    
    def get_font(self, size=72, weight="normal"):
        """Get appropriate font with fallbacks"""
        font_options = {
            "light": [
                "/System/Library/Fonts/Helvetica-Light.ttc",
                "/System/Library/Fonts/Helvetica.ttc",
            ],
            "normal": [
                "/System/Library/Fonts/Helvetica.ttc",
                "/System/Library/Fonts/Arial.ttf",
                "/Library/Fonts/Arial.ttf",
            ],
            "bold": [
                "/System/Library/Fonts/Helvetica-Bold.ttc",
                "/System/Library/Fonts/Arial-Bold.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
            ]
        }
        
        for font_path in font_options.get(weight, font_options["normal"]):
            try:
                return ImageFont.truetype(font_path, size)
            except (OSError, IOError):
                continue
        
        # Fallback to default font
        return ImageFont.load_default()
    
    def create_gradient_background(self, width, height, colors, direction="vertical"):
        """Create various types of gradient backgrounds"""
        img = Image.new("RGB", (width, height))
        
        if len(colors) < 2:
            colors = [colors[0], colors[0]]
        
        if direction == "vertical":
            for y in range(height):
                ratio = y / height
                color = self.interpolate_colors(colors, ratio)
                for x in range(width):
                    img.putpixel((x, y), color)
        
        elif direction == "horizontal":
            for x in range(width):
                ratio = x / width
                color = self.interpolate_colors(colors, ratio)
                for y in range(height):
                    img.putpixel((x, y), color)
        
        elif direction == "diagonal":
            for x in range(width):
                for y in range(height):
                    ratio = (x + y) / (width + height)
                    color = self.interpolate_colors(colors, ratio)
                    img.putpixel((x, y), color)
        
        elif direction == "radial":
            center_x, center_y = width // 2, height // 2
            max_distance = math.sqrt(center_x**2 + center_y**2)
            
            for x in range(width):
                for y in range(height):
                    distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                    ratio = min(distance / max_distance, 1.0)
                    color = self.interpolate_colors(colors, ratio)
                    img.putpixel((x, y), color)
        
        return img
    
    def interpolate_colors(self, colors, ratio):
        """Interpolate between multiple colors"""
        if len(colors) == 1:
            return getrgb(colors[0])
        
        # Clamp ratio
        ratio = max(0, min(1, ratio))
        
        # Handle multiple colors
        if len(colors) > 2:
            segment_size = 1.0 / (len(colors) - 1)
            segment = int(ratio / segment_size)
            segment = min(segment, len(colors) - 2)
            local_ratio = (ratio - segment * segment_size) / segment_size
            color1 = getrgb(colors[segment])
            color2 = getrgb(colors[segment + 1])
        else:
            color1 = getrgb(colors[0])
            color2 = getrgb(colors[1])
            local_ratio = ratio
        
        # Linear interpolation
        r = int(color1[0] * (1 - local_ratio) + color2[0] * local_ratio)
        g = int(color1[1] * (1 - local_ratio) + color2[1] * local_ratio)
        b = int(color1[2] * (1 - local_ratio) + color2[2] * local_ratio)
        
        return (r, g, b)
    
    def add_decorative_elements(self, img, elements, accent_color):
        """Add decorative elements to the quote card"""
        draw = ImageDraw.Draw(img, 'RGBA')
        width, height = img.size
        
        for element in elements:
            if element == "subtle_border":
                # Thin border around the card
                border_width = 4
                draw.rectangle([border_width//2, border_width//2, 
                               width-border_width//2, height-border_width//2],
                              outline=getrgb(accent_color) + (100,),
                              width=border_width)
            
            elif element == "soft_frame":
                # Rounded corner frame
                margin = 40
                corner_radius = 20
                frame_color = getrgb(accent_color) + (80,)
                
                # Draw frame with rounded corners (simplified)
                draw.rectangle([margin, margin, width-margin, height-margin],
                              outline=frame_color, width=6)
            
            elif element == "quote_marks":
                # Large decorative quote marks
                font_size = min(width, height) // 8
                font = self.get_font(font_size, "bold")
                
                # Opening quote
                draw.text((50, 80), '"', fill=getrgb(accent_color) + (120,), font=font)
                
                # Closing quote (bottom right)
                bbox = draw.textbbox((0, 0), '"', font=font)
                quote_width = bbox[2] - bbox[0]
                quote_height = bbox[3] - bbox[1]
                draw.text((width - quote_width - 50, height - quote_height - 80), 
                         '"', fill=getrgb(accent_color) + (120,), font=font)
            
            elif element == "heart_accent":
                # Small heart symbol
                heart_size = 30
                heart_x = width // 2
                heart_y = height - 100
                
                # Simple heart shape using circles and triangle
                self.draw_heart(draw, heart_x, heart_y, heart_size, accent_color)
            
            elif element == "geometric_accent":
                # Modern geometric accent
                accent_width = 100
                accent_height = 8
                x = 50
                y = height // 2 - 50
                
                draw.rectangle([x, y, x + accent_width, y + accent_height],
                              fill=getrgb(accent_color))
            
            elif element == "elegant_border":
                # Elegant decorative border
                margin = 60
                draw.rectangle([margin, margin, width-margin, height-margin],
                              outline=getrgb(accent_color) + (150,), width=2)
                
                # Corner decorations
                corner_size = 20
                for corner in [(margin, margin), (width-margin, margin), 
                              (margin, height-margin), (width-margin, height-margin)]:
                    x, y = corner
                    draw.ellipse([x-corner_size//2, y-corner_size//2,
                                 x+corner_size//2, y+corner_size//2],
                                fill=getrgb(accent_color) + (100,))
    
    def draw_heart(self, draw, x, y, size, color):
        """Draw a simple heart shape"""
        # Create heart using two circles and a triangle
        radius = size // 4
        
        # Left circle
        draw.ellipse([x - radius - radius//2, y - radius//2, 
                     x - radius//2, y + radius//2], 
                    fill=getrgb(color) + (120,))
        
        # Right circle  
        draw.ellipse([x + radius//2, y - radius//2,
                     x + radius + radius//2, y + radius//2],
                    fill=getrgb(color) + (120,))
        
        # Bottom triangle
        points = [(x - radius, y), (x + radius, y), (x, y + size//2)]
        draw.polygon(points, fill=getrgb(color) + (120,))
    
    def add_text_with_layout(self, img, quote, template, author=None):
        """Add text with sophisticated typography and layout"""
        draw = ImageDraw.Draw(img, 'RGBA')
        width, height = img.size
        
        # Get font size based on template
        font_sizes = {
            "small": min(width, height) // 25,
            "medium": min(width, height) // 20,
            "large": min(width, height) // 15,
            "xlarge": min(width, height) // 12
        }
        
        font_size = font_sizes.get(template.get("font_size", "medium"), font_sizes["medium"])
        font = self.get_font(font_size, template.get("font_weight", "normal"))
        
        # Prepare quote text
        quote_text = f'"{quote}"' if not quote.startswith('"') else quote
        
        # Text wrapping
        margin = 80
        max_width = width - 2 * margin
        
        # Wrap text
        lines = self.wrap_text(quote_text, font, max_width, draw)
        
        # Calculate text positioning
        line_height = font_size * 1.4
        total_text_height = len(lines) * line_height
        
        if template.get("text_position") == "center":
            start_y = (height - total_text_height) // 2
        elif template.get("text_position") == "offset":
            start_y = height // 3
        else:
            start_y = (height - total_text_height) // 2
        
        # Draw text with shadow if needed
        text_color = template.get("text_color", "#2C3E50")
        
        for i, line in enumerate(lines):
            # Center each line
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            x = (width - line_width) // 2
            y = start_y + i * line_height
            
            # Add subtle text shadow for better readability
            if template.get("text_color") == "#FFFFFF":
                draw.text((x + 2, y + 2), line, fill=(0, 0, 0, 60), font=font)
            
            # Main text
            draw.text((x, y), line, fill=text_color, font=font)
        
        # Add author attribution if provided
        if author:
            author_font_size = font_size // 2
            author_font = self.get_font(author_font_size, "normal")
            author_text = f"— {author}"
            
            bbox = draw.textbbox((0, 0), author_text, font=author_font)
            author_width = bbox[2] - bbox[0]
            author_x = (width - author_width) // 2
            author_y = start_y + len(lines) * line_height + 40
            
            accent_color = template.get("accent_color", KIIN_COLORS["accent"])
            draw.text((author_x, author_y), author_text, fill=accent_color, font=author_font)
    
    def wrap_text(self, text, font, max_width, draw):
        """Intelligently wrap text to fit within specified width"""
        lines = []
        words = text.split()
        current_line = ""
        
        for word in words:
            test_line = f"{current_line} {word}" if current_line else word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            test_width = bbox[2] - bbox[0]
            
            if test_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    # Word is too long, break it
                    lines.append(word)
                    current_line = ""
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def add_branding(self, img, position="bottom-right", opacity=0.7):
        """Add Kiin branding to the quote card"""
        if self.watermark is None:
            return img
        
        width, height = img.size
        watermark_size = min(width, height) // 20
        watermark = self.watermark.resize((watermark_size, watermark_size), 
                                        Image.Resampling.LANCZOS)
        
        # Adjust opacity
        if opacity < 1.0:
            alpha = watermark.split()[-1]
            alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
            watermark.putalpha(alpha)
        
        # Position watermark
        margin = 30
        if position == "bottom-right":
            x = width - watermark_size - margin
            y = height - watermark_size - margin
        elif position == "bottom-left":
            x = margin
            y = height - watermark_size - margin
        elif position == "bottom-center":
            x = (width - watermark_size) // 2
            y = height - watermark_size - margin
        elif position == "top-right":
            x = width - watermark_size - margin
            y = margin
        else:  # top-left
            x = margin
            y = margin
        
        img.paste(watermark, (x, y), watermark)
        return img
    
    def generate_quote_card(self, quote, template_name="minimal", author=None, 
                           size="instagram", output_path=None):
        """Generate a complete quote card"""
        
        # Platform sizes
        sizes = {
            "instagram": (1080, 1080),
            "instagram_story": (1080, 1920),
            "pinterest": (1000, 1500),
            "square": (1000, 1000),
            "wide": (1200, 630)
        }
        
        width, height = sizes.get(size, sizes["instagram"])
        template = self.templates.get(template_name, list(self.templates.values())[0])
        
        # Create background
        if template.get("background_type") == "gradient":
            colors = template.get("gradient_colors", [KIIN_COLORS["background_cool"]])
            direction = template.get("gradient_direction", "vertical")
            img = self.create_gradient_background(width, height, colors, direction)
        else:
            # Solid background
            color = template.get("gradient_colors", [KIIN_COLORS["background_cool"]])[0]
            img = Image.new("RGB", (width, height), color)
        
        # Convert to RGBA for compositing
        img = img.convert("RGBA")
        
        # Add decorative elements
        decorative_elements = template.get("decorative_elements", [])
        accent_color = template.get("accent_color", KIIN_COLORS["accent"])
        if decorative_elements:
            self.add_decorative_elements(img, decorative_elements, accent_color)
        
        # Add quote text
        self.add_text_with_layout(img, quote, template, author)
        
        # Add branding
        branding_position = template.get("branding_position", "bottom-right")
        branding_opacity = template.get("branding_opacity", 0.7)
        img = self.add_branding(img, branding_position, branding_opacity)
        
        # Convert back to RGB for saving
        final_img = Image.new("RGB", img.size, (255, 255, 255))
        final_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        
        # Save or return
        if output_path:
            final_img.save(output_path, "PNG", quality=95, optimize=True)
            print(f"Quote card saved: {output_path}")
        
        return final_img
    
    def extract_confession_quote(self, confession_id):
        """Extract a quote from a confession"""
        try:
            confession_id = int(confession_id)
            if 0 <= confession_id < len(self.confessions):
                confession = self.confessions[confession_id]
                # Use the confession text, hook, or validation as the quote
                quote_text = (confession.get("confession") or 
                             confession.get("hook") or 
                             confession.get("validation") or 
                             confession.get("text", ""))
                return quote_text, confession.get("author", None)
            else:
                print(f"Confession ID {confession_id} not found (available: 0-{len(self.confessions)-1})")
                return None, None
        except ValueError:
            print(f"Invalid confession ID: {confession_id}")
            return None, None

def main():
    parser = argparse.ArgumentParser(description="Generate Kiin quote cards")
    parser.add_argument("--quote", help="Quote text to use")
    parser.add_argument("--from-confession", type=int, 
                       help="Extract quote from confession ID")
    parser.add_argument("--template", default="minimal",
                       help="Template to use (see templates.json)")
    parser.add_argument("--author", help="Quote author/attribution")
    parser.add_argument("--size", default="instagram",
                       choices=["instagram", "instagram_story", "pinterest", "square", "wide"],
                       help="Output size/platform")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--list-templates", action="store_true",
                       help="List available templates")
    
    args = parser.parse_args()
    
    generator = QuoteCardGenerator()
    
    if args.list_templates:
        print("Available templates:")
        for name, template in generator.templates.items():
            print(f"  {name}: {template.get('description', 'No description')}")
        return
    
    # Get quote text
    quote_text = None
    author = args.author
    
    if args.quote:
        quote_text = args.quote
    elif args.from_confession is not None:
        quote_text, confession_author = generator.extract_confession_quote(args.from_confession)
        if not author and confession_author:
            author = confession_author
    else:
        print("Error: Must provide either --quote or --from-confession")
        sys.exit(1)
    
    if not quote_text:
        print("Error: Could not get quote text")
        sys.exit(1)
    
    # Generate output filename if not provided
    if not args.output:
        safe_text = "".join(c for c in quote_text[:30] if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_text = safe_text.replace(' ', '_')
        args.output = f"quote_{safe_text}_{args.template}_{args.size}.png"
    
    # Validate template
    if args.template not in generator.templates:
        print(f"Warning: Template '{args.template}' not found. Using 'minimal'")
        args.template = "minimal"
    
    # Generate quote card
    generator.generate_quote_card(
        quote=quote_text,
        template_name=args.template,
        author=author,
        size=args.size,
        output_path=args.output
    )

if __name__ == "__main__":
    main()