#!/usr/bin/env python3
"""
Instagram Carousel Generator for Caregiver Content
Professional slide generator with multiple templates and consistent branding.
"""

import json
import os
import argparse
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import textwrap
from typing import Dict, List, Tuple, Any
import sys

class CarouselGenerator:
    def __init__(self, content_file: str = None):
        """Initialize the carousel generator with content database."""
        if content_file is None:
            # Default to relative path from script location
            script_dir = Path(__file__).parent
            content_file = script_dir.parent / "config" / "carousel_content.json"
        
        self.content_file = Path(content_file)
        self.content = self._load_content()
        self.size = (1080, 1080)  # Instagram square format
        
        # Brand colors from config
        self.colors = self.content['brand']['colors']
        
        # Try to load system fonts, fallback to default
        self.fonts = self._load_fonts()
        
    def _load_content(self) -> Dict:
        """Load content database from JSON file."""
        if not self.content_file.exists():
            raise FileNotFoundError(f"Content file not found: {self.content_file}")
        
        with open(self.content_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_fonts(self) -> Dict[str, ImageFont.FreeTypeFont]:
        """Load system fonts with fallbacks."""
        fonts = {}
        
        # Common font locations across systems
        font_paths = [
            "/System/Library/Fonts/",  # macOS
            "/usr/share/fonts/",       # Linux
            "C:/Windows/Fonts/",       # Windows
        ]
        
        # Font mappings (system font -> fallback)
        font_map = {
            'header': ['Arial-Bold.ttf', 'arial.ttf', 'DejaVuSans-Bold.ttf'],
            'body': ['Arial.ttf', 'arial.ttf', 'DejaVuSans.ttf'],
            'accent': ['Arial-Italic.ttf', 'arial.ttf', 'DejaVuSans-Oblique.ttf']
        }
        
        for font_type, font_files in font_map.items():
            font_loaded = False
            for font_file in font_files:
                for path in font_paths:
                    font_path = os.path.join(path, font_file)
                    if os.path.exists(font_path):
                        try:
                            fonts[f'{font_type}_large'] = ImageFont.truetype(font_path, 48)
                            fonts[f'{font_type}_medium'] = ImageFont.truetype(font_path, 36)
                            fonts[f'{font_type}_small'] = ImageFont.truetype(font_path, 24)
                            font_loaded = True
                            break
                        except:
                            continue
                if font_loaded:
                    break
            
            # Fallback to default font if system font not found
            if not font_loaded:
                fonts[f'{font_type}_large'] = ImageFont.load_default()
                fonts[f'{font_type}_medium'] = ImageFont.load_default()
                fonts[f'{font_type}_small'] = ImageFont.load_default()
        
        return fonts
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _draw_progress_dots(self, draw: ImageDraw.Draw, slide_num: int, total_slides: int):
        """Draw progress indicator dots at bottom of slide."""
        dot_radius = 8
        dot_spacing = 20
        total_width = (total_slides - 1) * dot_spacing
        start_x = (self.size[0] - total_width) // 2
        y = self.size[1] - 50
        
        for i in range(total_slides):
            x = start_x + i * dot_spacing
            if i == slide_num:
                # Current slide - filled dot
                draw.ellipse([x-dot_radius, y-dot_radius, x+dot_radius, y+dot_radius], 
                           fill=self._hex_to_rgb(self.colors['primary']))
            else:
                # Other slides - outline dot
                draw.ellipse([x-dot_radius, y-dot_radius, x+dot_radius, y+dot_radius], 
                           outline=self._hex_to_rgb(self.colors['secondary']), width=2)
    
    def _draw_swipe_hint(self, draw: ImageDraw.Draw):
        """Draw swipe hint on the right side."""
        # Draw swipe arrow
        x = self.size[0] - 30
        y = self.size[1] // 2
        
        # Arrow pointing right
        arrow_points = [
            (x-15, y-10),
            (x-5, y),
            (x-15, y+10)
        ]
        draw.polygon(arrow_points, fill=self._hex_to_rgb(self.colors['secondary']))
        
        # Add "SWIPE" text vertically
        swipe_text = "SWIPE"
        for i, char in enumerate(swipe_text):
            char_y = y - 50 + i * 20
            draw.text((x-25, char_y), char, fill=self._hex_to_rgb(self.colors['secondary']), 
                     font=self.fonts['body_small'])
    
    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        """Wrap text to fit within specified width."""
        lines = []
        
        # Split by existing line breaks first
        paragraphs = text.split('\n')
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                lines.append('')
                continue
                
            words = paragraph.split()
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                bbox = font.getbbox(test_line)
                text_width = bbox[2] - bbox[0]
                
                if text_width <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        # Word is too long, force break
                        lines.append(word)
            
            if current_line:
                lines.append(' '.join(current_line))
        
        return lines
    
    def _create_cover_slide(self, topic_data: Dict, template_data: Dict) -> Image.Image:
        """Create the cover slide for a carousel."""
        img = Image.new('RGB', self.size, self._hex_to_rgb(self.colors['background']))
        draw = ImageDraw.Draw(img)
        
        # Background gradient effect
        for y in range(self.size[1] // 3):
            alpha = y / (self.size[1] // 3)
            color = self._hex_to_rgb(self.colors['primary'])
            gradient_color = tuple(int(c * alpha) for c in color)
            draw.rectangle([0, y*3, self.size[0], (y+1)*3], fill=gradient_color)
        
        # Title
        title_text = template_data['cover_format'].format(topic=topic_data['title'])
        title_lines = self._wrap_text(title_text, self.fonts['header_large'], self.size[0] - 80)
        
        y_offset = 100
        for line in title_lines:
            bbox = self.fonts['header_large'].getbbox(line)
            text_width = bbox[2] - bbox[0]
            x = (self.size[0] - text_width) // 2
            draw.text((x, y_offset), line, fill=self._hex_to_rgb(self.colors['text_light']), 
                     font=self.fonts['header_large'])
            y_offset += 60
        
        # Hook/subtitle
        hook_lines = self._wrap_text(topic_data['hook'], self.fonts['body_medium'], self.size[0] - 100)
        y_offset += 50
        
        for line in hook_lines:
            bbox = self.fonts['body_medium'].getbbox(line)
            text_width = bbox[2] - bbox[0]
            x = (self.size[0] - text_width) // 2
            draw.text((x, y_offset), line, fill=self._hex_to_rgb(self.colors['text_light']), 
                     font=self.fonts['body_medium'])
            y_offset += 40
        
        # Decorative element
        center_x = self.size[0] // 2
        draw.rectangle([center_x - 100, y_offset + 30, center_x + 100, y_offset + 35], 
                      fill=self._hex_to_rgb(self.colors['accent']))
        
        return img
    
    def _create_tips_slide(self, slide_data: Dict, slide_num: int, total_slides: int) -> Image.Image:
        """Create a tip slide."""
        img = Image.new('RGB', self.size, self._hex_to_rgb(self.colors['background']))
        draw = ImageDraw.Draw(img)
        
        # Header background
        draw.rectangle([0, 0, self.size[0], 150], fill=self._hex_to_rgb(self.colors['primary']))
        
        # Tip number and emoji
        tip_text = f"TIP {slide_num} {slide_data.get('visual_hint', '💡')}"
        bbox = self.fonts['header_medium'].getbbox(tip_text)
        text_width = bbox[2] - bbox[0]
        x = (self.size[0] - text_width) // 2
        draw.text((x, 30), tip_text, fill=self._hex_to_rgb(self.colors['text_light']), 
                 font=self.fonts['header_medium'])
        
        # Title
        title_lines = self._wrap_text(slide_data['title'], self.fonts['header_medium'], self.size[0] - 80)
        y_offset = 90
        for line in title_lines:
            bbox = self.fonts['header_medium'].getbbox(line)
            text_width = bbox[2] - bbox[0]
            x = (self.size[0] - text_width) // 2
            draw.text((x, y_offset), line, fill=self._hex_to_rgb(self.colors['text_light']), 
                     font=self.fonts['header_medium'])
            y_offset += 35
        
        # Content
        content_lines = self._wrap_text(slide_data['content'], self.fonts['body_medium'], self.size[0] - 80)
        y_offset = 200
        
        for line in content_lines:
            draw.text((40, y_offset), line, fill=self._hex_to_rgb(self.colors['text_dark']), 
                     font=self.fonts['body_medium'])
            y_offset += 45
        
        # Progress dots and swipe hint
        self._draw_progress_dots(draw, slide_num, total_slides)
        if slide_num < total_slides - 1:
            self._draw_swipe_hint(draw)
        
        return img
    
    def _create_signs_slide(self, slide_data: Dict, slide_num: int, total_slides: int) -> Image.Image:
        """Create a signs slide."""
        img = Image.new('RGB', self.size, self._hex_to_rgb(self.colors['background']))
        draw = ImageDraw.Draw(img)
        
        # Header with warning color
        draw.rectangle([0, 0, self.size[0], 120], fill=self._hex_to_rgb(self.colors['accent']))
        
        # Sign number and emoji
        sign_text = f"SIGN {slide_num} {slide_data.get('visual_hint', '⚠️')}"
        bbox = self.fonts['header_medium'].getbbox(sign_text)
        text_width = bbox[2] - bbox[0]
        x = (self.size[0] - text_width) // 2
        draw.text((x, 40), sign_text, fill=self._hex_to_rgb(self.colors['text_dark']), 
                 font=self.fonts['header_medium'])
        
        # Title
        title_lines = self._wrap_text(slide_data['title'], self.fonts['header_medium'], self.size[0] - 60)
        y_offset = 160
        for line in title_lines:
            draw.text((30, y_offset), line, fill=self._hex_to_rgb(self.colors['primary']), 
                     font=self.fonts['header_medium'])
            y_offset += 45
        
        # Content
        content_lines = self._wrap_text(slide_data['content'], self.fonts['body_medium'], self.size[0] - 60)
        y_offset += 30
        
        for line in content_lines:
            draw.text((30, y_offset), line, fill=self._hex_to_rgb(self.colors['text_dark']), 
                     font=self.fonts['body_medium'])
            y_offset += 40
        
        # Progress dots and swipe hint
        self._draw_progress_dots(draw, slide_num, total_slides)
        if slide_num < total_slides - 1:
            self._draw_swipe_hint(draw)
        
        return img
    
    def _create_communication_slide(self, slide_data: Dict, slide_num: int, total_slides: int) -> Image.Image:
        """Create a communication slide."""
        img = Image.new('RGB', self.size, self._hex_to_rgb(self.colors['background']))
        draw = ImageDraw.Draw(img)
        
        # Split design - red and green sections
        mid_y = self.size[1] // 2
        
        # "Instead of" section (light red background)
        draw.rectangle([0, 0, self.size[0], mid_y], fill=(255, 240, 240))
        draw.text((30, 30), "❌ INSTEAD OF SAYING:", fill=(180, 0, 0), font=self.fonts['body_medium'])
        
        instead_lines = self._wrap_text(slide_data['instead_of'], self.fonts['header_medium'], self.size[0] - 60)
        y_offset = 80
        for line in instead_lines:
            draw.text((30, y_offset), line, fill=(120, 0, 0), font=self.fonts['header_medium'])
            y_offset += 40
        
        # "Say this" section (light green background)
        draw.rectangle([0, mid_y, self.size[0], self.size[1] - 80], fill=(240, 255, 240))
        draw.text((30, mid_y + 30), "✅ SAY THIS INSTEAD:", fill=(0, 120, 0), font=self.fonts['body_medium'])
        
        say_lines = self._wrap_text(slide_data['say_this'], self.fonts['header_medium'], self.size[0] - 60)
        y_offset = mid_y + 80
        for line in say_lines:
            draw.text((30, y_offset), line, fill=(0, 100, 0), font=self.fonts['header_medium'])
            y_offset += 40
        
        # Why it matters
        if 'why' in slide_data:
            why_text = f"💡 {slide_data['why']}"
            draw.text((30, self.size[1] - 150), why_text, fill=self._hex_to_rgb(self.colors['text_dark']), 
                     font=self.fonts['body_small'])
        
        # Progress dots and swipe hint
        self._draw_progress_dots(draw, slide_num, total_slides)
        if slide_num < total_slides - 1:
            self._draw_swipe_hint(draw)
        
        return img
    
    def _create_truth_slide(self, slide_data: Dict, slide_num: int, total_slides: int) -> Image.Image:
        """Create a myth vs reality slide."""
        img = Image.new('RGB', self.size, self._hex_to_rgb(self.colors['background']))
        draw = ImageDraw.Draw(img)
        
        # Header
        draw.rectangle([0, 0, self.size[0], 100], fill=self._hex_to_rgb(self.colors['primary']))
        draw.text((30, 35), "MYTH vs REALITY", fill=self._hex_to_rgb(self.colors['text_light']), 
                 font=self.fonts['header_medium'])
        
        # Myth section
        draw.text((30, 130), "🚫 MYTH:", fill=(180, 0, 0), font=self.fonts['body_medium'])
        myth_lines = self._wrap_text(slide_data['myth'], self.fonts['body_medium'], self.size[0] - 60)
        y_offset = 170
        for line in myth_lines:
            draw.text((30, y_offset), line, fill=self._hex_to_rgb(self.colors['text_dark']), 
                     font=self.fonts['body_medium'])
            y_offset += 35
        
        # Reality section
        y_offset += 30
        draw.text((30, y_offset), "✅ REALITY:", fill=(0, 120, 0), font=self.fonts['body_medium'])
        y_offset += 40
        
        reality_lines = self._wrap_text(slide_data['reality'], self.fonts['body_medium'], self.size[0] - 60)
        for line in reality_lines:
            draw.text((30, y_offset), line, fill=self._hex_to_rgb(self.colors['text_dark']), 
                     font=self.fonts['body_medium'])
            y_offset += 35
        
        # Impact
        if 'impact' in slide_data:
            y_offset += 20
            impact_text = f"⚠️ Impact: {slide_data['impact']}"
            impact_lines = self._wrap_text(impact_text, self.fonts['body_small'], self.size[0] - 60)
            for line in impact_lines:
                draw.text((30, y_offset), line, fill=self._hex_to_rgb(self.colors['accent']), 
                         font=self.fonts['body_small'])
                y_offset += 30
        
        # Progress dots and swipe hint
        self._draw_progress_dots(draw, slide_num, total_slides)
        if slide_num < total_slides - 1:
            self._draw_swipe_hint(draw)
        
        return img
    
    def _create_story_slide(self, slide_data: Dict, slide_num: int, total_slides: int) -> Image.Image:
        """Create a story slide."""
        img = Image.new('RGB', self.size, self._hex_to_rgb(self.colors['background']))
        draw = ImageDraw.Draw(img)
        
        # Gradient background based on emotion
        emotion_colors = {
            'overwhelm': (180, 100, 100),
            'realization': (200, 150, 100),
            'relief': (100, 180, 150),
            'connection': (120, 150, 200),
            'hope': (150, 200, 120)
        }
        
        emotion = slide_data.get('emotion', 'hope')
        color = emotion_colors.get(emotion, emotion_colors['hope'])
        
        # Subtle gradient
        for y in range(self.size[1] // 4):
            alpha = 0.1 * (y / (self.size[1] // 4))
            gradient_color = tuple(int(255 - (255 - c) * alpha) for c in color)
            draw.rectangle([0, y*4, self.size[0], (y+1)*4], fill=gradient_color)
        
        # Chapter header
        chapter_text = f"CHAPTER {slide_num}"
        draw.text((30, 30), chapter_text, fill=self._hex_to_rgb(self.colors['primary']), 
                 font=self.fonts['accent_medium'])
        
        # Title
        title_lines = self._wrap_text(slide_data['title'], self.fonts['header_large'], self.size[0] - 60)
        y_offset = 80
        for line in title_lines:
            draw.text((30, y_offset), line, fill=self._hex_to_rgb(self.colors['text_dark']), 
                     font=self.fonts['header_large'])
            y_offset += 50
        
        # Content
        content_lines = self._wrap_text(slide_data['content'], self.fonts['body_medium'], self.size[0] - 60)
        y_offset += 30
        
        for line in content_lines:
            draw.text((30, y_offset), line, fill=self._hex_to_rgb(self.colors['text_dark']), 
                     font=self.fonts['body_medium'])
            y_offset += 40
        
        # Progress dots and swipe hint
        self._draw_progress_dots(draw, slide_num, total_slides)
        if slide_num < total_slides - 1:
            self._draw_swipe_hint(draw)
        
        return img
    
    def _create_cta_slide(self, template_data: Dict) -> Image.Image:
        """Create the call-to-action slide."""
        img = Image.new('RGB', self.size, self._hex_to_rgb(self.colors['primary']))
        draw = ImageDraw.Draw(img)
        
        # Background pattern
        for i in range(0, self.size[0], 100):
            for j in range(0, self.size[1], 100):
                if (i // 100 + j // 100) % 2:
                    draw.rectangle([i, j, i+50, j+50], 
                                 fill=self._hex_to_rgb(self.colors['secondary']))
        
        # Main CTA text
        cta_lines = self._wrap_text(template_data['cta_message'], self.fonts['header_large'], self.size[0] - 80)
        y_offset = 200
        
        for line in cta_lines:
            bbox = self.fonts['header_large'].getbbox(line)
            text_width = bbox[2] - bbox[0]
            x = (self.size[0] - text_width) // 2
            draw.text((x, y_offset), line, fill=self._hex_to_rgb(self.colors['text_light']), 
                     font=self.fonts['header_large'])
            y_offset += 60
        
        # Action buttons design
        button_y = y_offset + 100
        button_width = 200
        button_height = 60
        
        actions = ["❤️ FOLLOW", "💾 SAVE", "↗️ SHARE"]
        total_width = len(actions) * button_width + (len(actions) - 1) * 40
        start_x = (self.size[0] - total_width) // 2
        
        for i, action in enumerate(actions):
            x = start_x + i * (button_width + 40)
            # Button background
            draw.rectangle([x, button_y, x + button_width, button_y + button_height], 
                          fill=self._hex_to_rgb(self.colors['accent']))
            
            # Button text
            bbox = self.fonts['body_medium'].getbbox(action)
            text_width = bbox[2] - bbox[0]
            text_x = x + (button_width - text_width) // 2
            text_y = button_y + (button_height - 30) // 2
            draw.text((text_x, text_y), action, fill=self._hex_to_rgb(self.colors['text_dark']), 
                     font=self.fonts['body_medium'])
        
        return img
    
    def generate_carousel(self, topic_key: str, output_dir: str = "./carousels/") -> List[str]:
        """Generate a complete carousel for the given topic."""
        if topic_key not in self.content['topics']:
            raise ValueError(f"Topic '{topic_key}' not found in content database")
        
        topic_data = self.content['topics'][topic_key]
        template_key = topic_data['template']
        template_data = self.content['templates'][template_key]
        
        # Create output directory
        output_path = Path(output_dir) / topic_key
        output_path.mkdir(parents=True, exist_ok=True)
        
        slides = []
        
        # 1. Cover slide
        cover_img = self._create_cover_slide(topic_data, template_data)
        cover_path = output_path / "01_cover.png"
        cover_img.save(cover_path)
        slides.append(str(cover_path))
        
        # 2. Content slides
        content_slides = topic_data['slides']
        total_slides = len(content_slides) + 2  # +2 for cover and CTA
        
        for i, slide_data in enumerate(content_slides, 1):
            if template_key == 'tips':
                slide_img = self._create_tips_slide(slide_data, i, total_slides)
            elif template_key == 'signs':
                slide_img = self._create_signs_slide(slide_data, i, total_slides)
            elif template_key == 'communication':
                slide_img = self._create_communication_slide(slide_data, i, total_slides)
            elif template_key == 'truth':
                slide_img = self._create_truth_slide(slide_data, i, total_slides)
            elif template_key == 'story':
                slide_img = self._create_story_slide(slide_data, i, total_slides)
            else:
                # Fallback to tips format
                slide_img = self._create_tips_slide(slide_data, i, total_slides)
            
            slide_path = output_path / f"{i+1:02d}_slide_{i}.png"
            slide_img.save(slide_path)
            slides.append(str(slide_path))
        
        # 3. CTA slide
        cta_img = self._create_cta_slide(template_data)
        cta_path = output_path / f"{len(content_slides)+2:02d}_cta.png"
        cta_img.save(cta_path)
        slides.append(str(cta_path))
        
        return slides
    
    def list_topics(self) -> List[str]:
        """List all available topics."""
        return list(self.content['topics'].keys())
    
    def get_topic_info(self, topic_key: str) -> Dict:
        """Get information about a specific topic."""
        if topic_key not in self.content['topics']:
            return None
        
        topic_data = self.content['topics'][topic_key]
        return {
            'title': topic_data['title'],
            'template': topic_data['template'],
            'slide_count': len(topic_data['slides']) + 2,  # +2 for cover and CTA
            'hook': topic_data.get('hook', '')
        }

def main():
    parser = argparse.ArgumentParser(description='Generate Instagram carousels for caregiver content')
    parser.add_argument('--topic', type=str, help='Topic to generate carousel for')
    parser.add_argument('--output-dir', type=str, default='./carousels/', 
                       help='Output directory for generated images')
    parser.add_argument('--list', action='store_true', help='List available topics')
    parser.add_argument('--info', type=str, help='Get information about a specific topic')
    parser.add_argument('--content-file', type=str, help='Path to content JSON file')
    
    args = parser.parse_args()
    
    try:
        generator = CarouselGenerator(args.content_file)
        
        if args.list:
            print("Available topics:")
            for topic in generator.list_topics():
                info = generator.get_topic_info(topic)
                print(f"  {topic}: {info['title']} ({info['slide_count']} slides)")
            return
        
        if args.info:
            info = generator.get_topic_info(args.info)
            if info:
                print(f"Topic: {args.info}")
                print(f"Title: {info['title']}")
                print(f"Template: {info['template']}")
                print(f"Slides: {info['slide_count']}")
                print(f"Hook: {info['hook']}")
            else:
                print(f"Topic '{args.info}' not found")
            return
        
        if not args.topic:
            print("Error: Please specify a topic with --topic or use --list to see available topics")
            return
        
        print(f"Generating carousel for topic: {args.topic}")
        slides = generator.generate_carousel(args.topic, args.output_dir)
        
        print(f"✅ Generated {len(slides)} slides:")
        for slide in slides:
            print(f"  {slide}")
        
        print(f"\nCarousel saved to: {Path(args.output_dir) / args.topic}")
        print("Ready to upload to Instagram! 🚀")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()