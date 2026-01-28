#!/usr/bin/env python3
"""
Kiin Content Thumbnail Generator

Generate eye-catching thumbnails for various social media platforms with
Kiin branding, emotional color schemes, and professional typography.
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
import subprocess
import tempfile

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

# Emotional color schemes for different content types
EMOTIONAL_SCHEMES = {
    "validation": {
        "background": ["#E8F4FD", "#F0F8FF", "#E6F3FF"],
        "overlay": "#4A90B8",
        "text": "#2C3E50",
        "accent": "#6BB3A0"
    },
    "support": {
        "background": ["#F0FFF0", "#E8F5E8", "#F5FFF5"],
        "overlay": "#6BB3A0",
        "text": "#2C3E50", 
        "accent": "#4A90B8"
    },
    "energy": {
        "background": ["#FFF8DC", "#FFEAA7", "#FDCB6E"],
        "overlay": "#F4A460",
        "text": "#2C3E50",
        "accent": "#4A90B8"
    },
    "calm": {
        "background": ["#F8FAFB", "#E8F0FE", "#F0F8FF"],
        "overlay": "#4A90B8",
        "text": "#2C3E50",
        "accent": "#6BB3A0"
    },
    "warm": {
        "background": ["#FDF9F5", "#FFF5EE", "#FFFAF0"],
        "overlay": "#F4A460",
        "text": "#2C3E50",
        "accent": "#4A90B8"
    }
}

# Platform-specific dimensions
PLATFORM_SIZES = {
    "youtube": (1280, 720),
    "instagram_feed": (1080, 1080),
    "instagram_story": (1080, 1920),
    "twitter": (1200, 675),
    "facebook": (1200, 630),
    "linkedin": (1200, 627),
    "pinterest": (1000, 1500),
    "tiktok": (1080, 1920),
    "default": (1280, 720)
}

class ThumbnailGenerator:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.brand_dir = self.base_dir / "brand"
        self.load_brand_assets()
    
    def load_brand_assets(self):
        """Load Kiin logo and watermark"""
        try:
            self.logo = Image.open(self.brand_dir / "logo.png").convert("RGBA")
            self.watermark = Image.open(self.brand_dir / "watermark.png").convert("RGBA")
        except FileNotFoundError:
            print("Warning: Brand assets not found. Continuing without logo/watermark.")
            self.logo = None
            self.watermark = None
    
    def get_font(self, size=72, bold=False):
        """Get appropriate font with fallbacks"""
        font_options = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Arial.ttf",
            "/Library/Fonts/Arial.ttf",
            "arial.ttf",
            "helvetica.ttc"
        ]
        
        for font_path in font_options:
            try:
                return ImageFont.truetype(font_path, size)
            except (OSError, IOError):
                continue
        
        # Fallback to default font
        try:
            return ImageFont.load_default()
        except:
            return ImageFont.load_default()
    
    def extract_video_frame(self, video_path, timestamp="00:00:01"):
        """Extract a frame from video using ffmpeg"""
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Use ffmpeg to extract frame
            cmd = [
                "ffmpeg", "-i", video_path, "-ss", timestamp,
                "-vframes", "1", "-f", "image2", "-y", temp_path
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            
            frame = Image.open(temp_path).convert("RGB")
            os.unlink(temp_path)
            return frame
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fallback: create placeholder if ffmpeg not available
            print("Warning: ffmpeg not available. Creating placeholder frame.")
            os.unlink(temp_path)
            return self.create_placeholder_frame()
    
    def create_placeholder_frame(self):
        """Create a placeholder frame when video processing fails"""
        img = Image.new("RGB", (1920, 1080), color=KIIN_COLORS["background_warm"])
        draw = ImageDraw.Draw(img)
        
        font = self.get_font(72)
        text = "Video Frame Placeholder"
        
        # Center the text
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (img.width - text_width) // 2
        y = (img.height - text_height) // 2
        
        draw.text((x, y), text, fill=KIIN_COLORS["text_dark"], font=font)
        return img
    
    def create_gradient_background(self, width, height, colors, direction="vertical"):
        """Create a gradient background"""
        if len(colors) < 2:
            colors = [colors[0], colors[0]]
        
        # Create base image
        img = Image.new("RGB", (width, height))
        
        # Create gradient
        if direction == "vertical":
            for y in range(height):
                ratio = y / height
                r = int(getrgb(colors[0])[0] * (1 - ratio) + getrgb(colors[1])[0] * ratio)
                g = int(getrgb(colors[0])[1] * (1 - ratio) + getrgb(colors[1])[1] * ratio)
                b = int(getrgb(colors[0])[2] * (1 - ratio) + getrgb(colors[1])[2] * ratio)
                
                for x in range(width):
                    img.putpixel((x, y), (r, g, b))
        else:  # horizontal
            for x in range(width):
                ratio = x / width
                r = int(getrgb(colors[0])[0] * (1 - ratio) + getrgb(colors[1])[0] * ratio)
                g = int(getrgb(colors[0])[1] * (1 - ratio) + getrgb(colors[1])[1] * ratio)
                b = int(getrgb(colors[0])[2] * (1 - ratio) + getrgb(colors[1])[2] * ratio)
                
                for y in range(height):
                    img.putpixel((x, y), (r, g, b))
        
        return img
    
    def add_face_placeholder_zones(self, img, num_faces=1):
        """Add subtle face placeholder zones"""
        draw = ImageDraw.Draw(img, 'RGBA')
        width, height = img.size
        
        # Define face zones (oval shapes)
        face_size = min(width, height) // 6
        
        for i in range(num_faces):
            # Position faces naturally (avoid center, prefer rule of thirds)
            if i == 0:
                x = width // 3
                y = height // 3
            else:
                x = random.randint(face_size, width - face_size)
                y = random.randint(face_size, height - face_size)
            
            # Draw subtle oval
            left = x - face_size // 2
            top = y - face_size // 2
            right = x + face_size // 2
            bottom = y + face_size // 2
            
            # Very subtle circle/oval for face placement
            draw.ellipse([left, top, right, bottom], 
                        outline=getrgb(KIIN_COLORS["accent"]) + (50,),
                        width=3)
    
    def add_text_overlay(self, img, text, scheme_name="validation", position="center"):
        """Add text overlay with professional typography"""
        draw = ImageDraw.Draw(img, 'RGBA')
        width, height = img.size
        scheme = EMOTIONAL_SCHEMES.get(scheme_name, EMOTIONAL_SCHEMES["validation"])
        
        # Add semi-transparent overlay for better text readability
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # Create text shadow/backdrop
        if position in ["center", "bottom"]:
            overlay_height = height // 3
            overlay_y = height - overlay_height if position == "bottom" else height // 3
            
            overlay_draw.rectangle([0, overlay_y, width, overlay_y + overlay_height], 
                                 fill=getrgb(scheme["overlay"]) + (180,))
        
        img = Image.alpha_composite(img.convert('RGBA'), overlay)
        draw = ImageDraw.Draw(img)
        
        # Wrap text for better readability
        font_size = min(width // 15, 80)
        font = self.get_font(font_size, bold=True)
        
        # Calculate text wrapping
        max_width = width - 100  # 50px margin on each side
        lines = []
        
        words = text.split()
        current_line = ""
        
        for word in words:
            test_line = f"{current_line} {word}" if current_line else word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # Position text
        total_height = len(lines) * font_size * 1.2
        
        if position == "center":
            start_y = (height - total_height) // 2
        elif position == "bottom":
            start_y = height - total_height - 50
        else:  # top
            start_y = 50
        
        # Draw text with shadow for better readability
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            x = (width - line_width) // 2
            y = start_y + i * font_size * 1.2
            
            # Text shadow
            draw.text((x + 2, y + 2), line, fill=(0, 0, 0, 128), font=font)
            # Main text
            draw.text((x, y), line, fill=scheme["text"], font=font)
    
    def add_branding(self, img, position="bottom-right", opacity=0.6):
        """Add Kiin branding to the thumbnail"""
        if self.watermark is None:
            return img
        
        width, height = img.size
        watermark_size = min(width, height) // 15
        watermark = self.watermark.resize((watermark_size, watermark_size), Image.Resampling.LANCZOS)
        
        # Adjust opacity
        if opacity < 1.0:
            alpha = watermark.split()[-1]
            alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
            watermark.putalpha(alpha)
        
        # Position watermark
        margin = 20
        if position == "bottom-right":
            x = width - watermark_size - margin
            y = height - watermark_size - margin
        elif position == "bottom-left":
            x = margin
            y = height - watermark_size - margin
        elif position == "top-right":
            x = width - watermark_size - margin
            y = margin
        else:  # top-left
            x = margin
            y = margin
        
        img.paste(watermark, (x, y), watermark)
        return img
    
    def generate_thumbnail(self, text=None, video_path=None, content_type="validation", 
                          platform="youtube", output_path=None, face_zones=0):
        """Generate a complete thumbnail"""
        
        # Get platform dimensions
        width, height = PLATFORM_SIZES.get(platform, PLATFORM_SIZES["default"])
        
        # Create base image
        if video_path:
            # Extract frame from video
            base_img = self.extract_video_frame(video_path)
            base_img = base_img.resize((width, height), Image.Resampling.LANCZOS)
        else:
            # Create gradient background
            scheme = EMOTIONAL_SCHEMES.get(content_type, EMOTIONAL_SCHEMES["validation"])
            colors = scheme["background"]
            if len(colors) >= 2:
                base_img = self.create_gradient_background(width, height, colors[:2])
            else:
                base_img = Image.new("RGB", (width, height), colors[0])
        
        # Convert to RGBA for compositing
        base_img = base_img.convert("RGBA")
        
        # Add face placeholder zones if requested
        if face_zones > 0:
            self.add_face_placeholder_zones(base_img, face_zones)
        
        # Add text overlay if provided
        if text:
            self.add_text_overlay(base_img, text, content_type)
        
        # Add Kiin branding
        base_img = self.add_branding(base_img)
        
        # Convert back to RGB for saving
        final_img = Image.new("RGB", base_img.size, (255, 255, 255))
        final_img.paste(base_img, mask=base_img.split()[-1] if base_img.mode == 'RGBA' else None)
        
        # Save or return
        if output_path:
            final_img.save(output_path, "PNG", quality=95, optimize=True)
            print(f"Thumbnail saved: {output_path}")
        
        return final_img

def main():
    parser = argparse.ArgumentParser(description="Generate Kiin content thumbnails")
    parser.add_argument("--text", help="Text overlay for thumbnail")
    parser.add_argument("--video", help="Video file to extract frame from")
    parser.add_argument("--type", default="validation", 
                       choices=list(EMOTIONAL_SCHEMES.keys()),
                       help="Content type for emotional color scheme")
    parser.add_argument("--platform", default="youtube",
                       choices=list(PLATFORM_SIZES.keys()),
                       help="Target platform")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--faces", type=int, default=0,
                       help="Number of face placeholder zones to add")
    
    args = parser.parse_args()
    
    if not args.text and not args.video:
        print("Error: Must provide either --text or --video")
        sys.exit(1)
    
    # Generate output filename if not provided
    if not args.output:
        if args.video:
            base_name = Path(args.video).stem
            args.output = f"{base_name}_thumb_{args.platform}.png"
        else:
            safe_text = "".join(c for c in args.text[:30] if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_text = safe_text.replace(' ', '_')
            args.output = f"{safe_text}_{args.platform}.png"
    
    # Generate thumbnail
    generator = ThumbnailGenerator()
    generator.generate_thumbnail(
        text=args.text,
        video_path=args.video,
        content_type=args.type,
        platform=args.platform,
        output_path=args.output,
        face_zones=args.faces
    )

if __name__ == "__main__":
    main()