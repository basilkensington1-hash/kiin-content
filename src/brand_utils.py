#!/usr/bin/env python3
"""
Kiin Brand Utilities - Shared branding functions for content generators
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class KiinBrand:
    """Centralized access to Kiin brand assets and configuration"""
    
    def __init__(self):
        self.brand_dir = Path(__file__).parent.parent / 'brand'
        self._config = None
        self._colors = None
        self._fonts = None
    
    @property
    def config(self) -> Dict[str, Any]:
        """Load and cache brand configuration"""
        if self._config is None:
            config_file = self.brand_dir / 'brand_config.json'
            with open(config_file, 'r') as f:
                self._config = json.load(f)
        return self._config
    
    @property
    def colors(self) -> Dict[str, str]:
        """Get brand colors as hex values"""
        if self._colors is None:
            colors_file = self.brand_dir / 'colors.json'
            with open(colors_file, 'r') as f:
                color_data = json.load(f)
            self._colors = color_data['hex_values']
        return self._colors
    
    @property
    def fonts(self) -> Dict[str, Any]:
        """Get font configuration"""
        if self._fonts is None:
            fonts_file = self.brand_dir / 'fonts.json'
            with open(fonts_file, 'r') as f:
                self._fonts = json.load(f)
        return self._fonts
    
    def get_color_rgb(self, color_name: str) -> tuple:
        """Convert hex color to RGB tuple"""
        hex_color = self.colors[color_name]
        return tuple(int(hex_color[1:][i:i+2], 16) for i in (0, 2, 4))
    
    def get_color_rgba(self, color_name: str, alpha: float = 1.0) -> tuple:
        """Convert hex color to RGBA tuple"""
        rgb = self.get_color_rgb(color_name)
        return rgb + (int(alpha * 255),)
    
    def get_logo_path(self) -> Path:
        """Get path to main logo"""
        return self.brand_dir / 'logo.png'
    
    def get_watermark_path(self) -> Path:
        """Get path to watermark"""
        return self.brand_dir / 'watermark.png'
    
    def get_voice_config(self) -> Dict[str, Any]:
        """Get TTS voice configuration"""
        return self.config['voice']
    
    def get_css_variables(self) -> str:
        """Generate CSS custom properties for brand colors"""
        css_vars = [":root {"]
        
        for name, value in self.colors.items():
            css_name = name.replace('_', '-')
            css_vars.append(f"  --kiin-{css_name}: {value};")
        
        css_vars.append("}")
        return "\n".join(css_vars)
    
    def get_font_css(self) -> str:
        """Generate CSS for web fonts"""
        fonts = self.fonts
        
        css = []
        css.append("/* Kiin Brand Fonts */")
        
        # Add Google Fonts import
        if 'web_imports' in fonts and 'google_fonts' in fonts['web_imports']:
            css.append(f"@import url('{fonts['web_imports']['google_fonts']}');")
        
        css.append("")
        
        # Add font family definitions
        for font_type, font_config in fonts['font_stack'].items():
            family_name = f"kiin-{font_type}"
            font_stack = f"'{font_config['primary']}', " + ", ".join(font_config['fallbacks'])
            css.append(f".{family_name} {{ font-family: {font_stack}; }}")
        
        return "\n".join(css)
    
    def apply_brand_to_html(self, html_content: str) -> str:
        """Apply brand styling to HTML content"""
        # Add brand CSS to head
        brand_css = f"""
<style>
{self.get_css_variables()}

{self.get_font_css()}

body {{
    font-family: '{self.fonts['font_stack']['body']['primary']}', sans-serif;
    color: var(--kiin-text-dark);
    background-color: var(--kiin-background-warm);
    line-height: 1.6;
}}

h1, h2, h3, h4, h5, h6 {{
    font-family: '{self.fonts['font_stack']['heading']['primary']}', sans-serif;
    color: var(--kiin-primary);
}}

.kiin-primary {{ color: var(--kiin-primary); }}
.kiin-secondary {{ color: var(--kiin-secondary); }}
.kiin-accent {{ color: var(--kiin-accent); }}

.kiin-bg-warm {{ background-color: var(--kiin-background-warm); }}
.kiin-bg-cool {{ background-color: var(--kiin-background-cool); }}
</style>
"""
        
        # Insert CSS before closing head tag
        if '</head>' in html_content:
            return html_content.replace('</head>', brand_css + '\n</head>')
        else:
            # If no head tag, add at the beginning
            return brand_css + '\n' + html_content

def get_brand_prompt_context() -> str:
    """Get brand context for AI prompts"""
    brand = KiinBrand()
    
    return f"""
Brand Context for Kiin:
- Mission: {brand.config['mission']}
- Voice: {brand.config['voice']['tone']}
- Personality: {', '.join(brand.config['voice']['personality_traits'])}
- Key Messages: {', '.join(brand.config['content_guidelines']['key_messages'])}
- Avoid: {', '.join(brand.config['voice']['avoid'])}

Visual Style: {brand.config['visual_style']['mood']}
Primary Color: {brand.colors['primary']} (warm, trustworthy blue)
Secondary Color: {brand.colors['secondary']} (gentle sage green)
"""

def create_branded_thumbnail(title: str, subtitle: str = "", size: tuple = (1920, 1080)) -> Optional[Path]:
    """Create a branded thumbnail image (requires PIL)"""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("PIL (Pillow) not available for thumbnail generation")
        return None
    
    brand = KiinBrand()
    
    # Create image with brand background
    img = Image.new('RGB', size, brand.get_color_rgb('background_warm'))
    draw = ImageDraw.Draw(img)
    
    # Load fonts (with fallbacks)
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 72)
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    # Draw title
    title_color = brand.get_color_rgb('primary')
    
    # Simple text positioning (can be enhanced)
    title_y = size[1] // 3
    draw.text((50, title_y), title, fill=title_color, font=title_font)
    
    if subtitle:
        subtitle_color = brand.get_color_rgb('secondary')
        subtitle_y = title_y + 100
        draw.text((50, subtitle_y), subtitle, fill=subtitle_color, font=subtitle_font)
    
    # Save thumbnail
    output_path = Path("branded_thumbnail.png")
    img.save(output_path)
    return output_path

# Convenience functions for easy imports
def get_brand_colors() -> Dict[str, str]:
    """Quick access to brand colors"""
    return KiinBrand().colors

def get_primary_color() -> str:
    """Get primary brand color"""
    return KiinBrand().colors['primary']

def get_brand_voice() -> str:
    """Get brand voice for TTS"""
    return KiinBrand().get_voice_config()['tts_voice']

def get_brand_tone() -> str:
    """Get brand tone description"""
    return KiinBrand().get_voice_config()['tone']

# Example integration functions
def integrate_with_podcast_generator():
    """Example: How to integrate branding with podcast generator"""
    print("To integrate with podcast generator:")
    print("1. Import: from brand_utils import KiinBrand, get_brand_voice")
    print("2. Use brand voice: tts_voice = get_brand_voice()")
    print("3. Apply colors to thumbnails using create_branded_thumbnail()")
    print("4. Include brand context in AI prompts using get_brand_prompt_context()")

def integrate_with_video_generator():
    """Example: How to integrate branding with video generator"""
    print("To integrate with video generator:")
    print("1. Import: from brand_utils import KiinBrand")
    print("2. Get watermark: brand.get_watermark_path()")
    print("3. Use apply_branding.py script to add watermarks automatically")
    print("4. Include brand colors in any generated graphics")

if __name__ == "__main__":
    # Demo the brand utilities
    brand = KiinBrand()
    print("Kiin Brand Utilities Demo")
    print("=" * 40)
    print(f"Brand Name: {brand.config['name']}")
    print(f"Tagline: {brand.config['tagline']}")
    print(f"Primary Color: {brand.colors['primary']}")
    print(f"TTS Voice: {brand.get_voice_config()['tts_voice']}")
    print(f"Logo Path: {brand.get_logo_path()}")
    print("\nBrand Prompt Context:")
    print(get_brand_prompt_context())