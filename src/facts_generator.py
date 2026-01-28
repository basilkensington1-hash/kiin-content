#!/usr/bin/env python3
"""
Kiin "Did You Know" Facts Video Generator
Generates quick educational fact videos about caregiving

Requirements:
- edge-tts: pip install edge-tts
- Pillow: pip install Pillow  
- FFmpeg: brew install ffmpeg (or system package)
"""

import json
import os
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import edge_tts
import subprocess
import random
from brand_utils import KiinBrand

# Video constants
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920

# Timing (in seconds)
INTRO_DURATION = 1.5
FACT_DURATION = 8
DETAIL_DURATION = 4.5
TOTAL_DURATION = INTRO_DURATION + FACT_DURATION + DETAIL_DURATION


class FactsVideoGenerator:
    def __init__(self, config_path: str, output_dir: str):
        self.config_path = Path(config_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Load brand configuration
        self.brand = KiinBrand()
        
        # Load facts from JSON
        with open(self.config_path, 'r') as f:
            self.data = json.load(f)
        
        # TTS voice settings
        self.voice = self.brand.get_voice_config()['tts_voice']
        self.voice_rate = "+10%"  # Slightly faster for facts
        self.voice_pitch = "+0Hz"
    
    def get_font_path(self, size: int = 60, bold: bool = False) -> str:
        """Get system font path based on OS"""
        try:
            font_paths = [
                "/System/Library/Fonts/Helvetica.ttc",  # macOS
                "/System/Library/Fonts/Arial.ttf",       # macOS
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
                "/Windows/Fonts/arial.ttf",              # Windows
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    return font_path
            
            return None
        except:
            return None

    def get_font(self, size: int = 60, bold: bool = False) -> ImageFont.FreeTypeFont:
        """Get font object"""
        font_path = self.get_font_path()
        try:
            if font_path:
                return ImageFont.truetype(font_path, size)
            else:
                return ImageFont.load_default()
        except:
            return ImageFont.load_default()

    def wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = current_line + [word]
            test_text = ' '.join(test_line)
            
            bbox = font.getbbox(test_text)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines

    def create_gradient_background(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> Image.Image:
        """Create a vertical gradient background"""
        image = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), color1)
        
        for y in range(VIDEO_HEIGHT):
            ratio = y / VIDEO_HEIGHT
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            
            for x in range(VIDEO_WIDTH):
                image.putpixel((x, y), (r, g, b))
        
        return image

    def add_decorative_elements(self, image: Image.Image, section: str) -> Image.Image:
        """Add subtle decorative elements to the image"""
        draw = ImageDraw.Draw(image)
        
        if section == "intro":
            # Add lightbulb icon effect (simple circle)
            bulb_color = self.brand.get_color_rgb('accent')
            center_x, center_y = VIDEO_WIDTH // 2, 400
            radius = 40
            draw.ellipse([center_x - radius, center_y - radius, 
                         center_x + radius, center_y + radius], 
                        fill=bulb_color + (100,))  # Semi-transparent
        
        elif section == "fact":
            # Add subtle data visualization elements
            primary_color = self.brand.get_color_rgb('primary')
            # Simple bar chart effect
            for i in range(3):
                bar_height = random.randint(60, 120)
                x = 100 + (i * 60)
                y = VIDEO_HEIGHT - 200 - bar_height
                draw.rectangle([x, y, x + 40, VIDEO_HEIGHT - 200], 
                             fill=primary_color + (80,))
        
        return image

    def create_text_image(self, text: str, bg_colors: Tuple[Tuple[int, int, int], Tuple[int, int, int]], 
                         text_color: Tuple[int, int, int], font_size: int = 60, section: str = "fact") -> Image.Image:
        """Create an image with centered text and gradient background"""
        # Create gradient background
        image = self.create_gradient_background(bg_colors[0], bg_colors[1])
        
        # Add decorative elements
        image = self.add_decorative_elements(image, section)
        
        draw = ImageDraw.Draw(image)
        font = self.get_font(font_size, bold=True)
        
        # Wrap text
        max_width = VIDEO_WIDTH - 120  # 60px margin on each side
        lines = self.wrap_text(text, font, max_width)
        
        # Calculate total text height
        line_height = font_size + 25
        total_height = len(lines) * line_height
        
        # Center vertically, but adjust based on section
        if section == "intro":
            y = VIDEO_HEIGHT // 2 + 100  # Lower for intro
        else:
            y = (VIDEO_HEIGHT - total_height) // 2
        
        for line in lines:
            bbox = font.getbbox(line)
            text_width = bbox[2] - bbox[0]
            x = (VIDEO_WIDTH - text_width) // 2
            
            # Add text shadow for better readability
            shadow_offset = 3
            draw.text((x + shadow_offset, y + shadow_offset), line, fill=(0, 0, 0, 100), font=font)
            draw.text((x, y), line, fill=text_color, font=font)
            y += line_height
        
        return image

    def create_section_image(self, section: str, text: str, fact_data: Dict) -> Image.Image:
        """Create image for a specific section"""
        
        if section == "intro":
            # Bright, attention-grabbing intro
            bg_colors = (self.brand.get_color_rgb('primary'), self.brand.get_color_rgb('secondary'))
            text_color = self.brand.get_color_rgb('text_light')
            full_text = "💡 DID YOU KNOW?"
            font_size = 70
            
        elif section == "fact":
            # Clean, data-focused main fact
            bg_colors = (self.brand.get_color_rgb('background_warm'), self.brand.get_color_rgb('background_cool'))
            text_color = self.brand.get_color_rgb('text_dark')
            full_text = fact_data['fact']
            font_size = 58
            
        else:  # detail
            # Softer background for additional context
            bg_colors = (self.brand.get_color_rgb('secondary'), self.brand.get_color_rgb('accent'))
            text_color = self.brand.get_color_rgb('text_light')
            full_text = f"🔍 {fact_data['detail']}"
            font_size = 50
        
        return self.create_text_image(full_text, bg_colors, text_color, font_size, section)

    async def generate_audio(self, text: str, output_path: str):
        """Generate TTS audio for given text"""
        communicate = edge_tts.Communicate(text, self.voice, rate=self.voice_rate, pitch=self.voice_pitch)
        await communicate.save(output_path)

    def create_video_from_sections(self, sections: List[Tuple[str, str, float]], 
                                 audio_path: str, output_path: str, fact_data: Dict):
        """Create video from section images and audio using FFmpeg"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save section images
            image_paths = []
            
            for i, (section_name, text, duration) in enumerate(sections):
                image_path = os.path.join(temp_dir, f"section_{i:02d}.png")
                image = self.create_section_image(section_name, text, fact_data)
                image.save(image_path)
                image_paths.append(image_path)
            
            # Build FFmpeg command for smooth transitions
            cmd = [
                'ffmpeg', '-y'  # Overwrite output file
            ]
            
            # Add input images with specific durations
            for i, (image_path, duration) in enumerate(zip(image_paths, [s[2] for s in sections])):
                cmd.extend(['-loop', '1', '-t', str(duration), '-i', image_path])
            
            # Add audio
            cmd.extend(['-i', audio_path])
            
            # Create filter complex for crossfade transitions
            filter_parts = []
            concat_inputs = ""
            
            for i in range(len(sections)):
                if i == 0:
                    filter_parts.append(f"[{i}:v]fade=in:st=0:d=0.5[v{i}]")
                else:
                    filter_parts.append(f"[{i}:v]fade=in:st=0:d=0.5,fade=out:st={(sections[i][2]-0.5)}:d=0.5[v{i}]")
                concat_inputs += f"[v{i}]"
            
            filter_parts.append(f"{concat_inputs}concat=n={len(sections)}:v=1:a=0[outv]")
            filter_complex = ";".join(filter_parts)
            
            cmd.extend([
                '-filter_complex', filter_complex,
                '-map', '[outv]',
                '-map', f'{len(image_paths)}:a',
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-shortest',
                '-r', '30',
                '-pix_fmt', 'yuv420p',
                output_path
            ])
            
            # Execute FFmpeg
            print(f"Executing: {' '.join(cmd[:10])}...")  # Truncated for readability
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"FFmpeg Error: {result.stderr}")
                raise Exception(f"FFmpeg failed: {result.stderr}")

    async def generate_fact_video(self, fact: Dict, output_filename: str = None) -> str:
        """Generate a complete fact video"""
        if not output_filename:
            # Create safe filename from fact
            safe_title = "".join(c for c in fact['category'] if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_title = safe_title.replace(' ', '_')[:30]
            output_filename = f"fact_{fact['id']:02d}_{safe_title}.mp4"
        
        output_path = self.output_dir / output_filename
        
        print(f"Generating fact video {fact['id']}: {fact['fact'][:50]}...")
        
        # Prepare sections
        sections = [
            ("intro", "Did you know?", INTRO_DURATION),
            ("fact", fact['fact'], FACT_DURATION),
            ("detail", fact['detail'], DETAIL_DURATION)
        ]
        
        # Create audio script - make it engaging and natural
        audio_script = f"Did you know? {fact['fact']} {fact['detail']}"
        
        # Generate audio
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio:
            await self.generate_audio(audio_script, temp_audio.name)
            
            try:
                # Create video
                self.create_video_from_sections(sections, temp_audio.name, str(output_path), fact)
                print(f"✅ Video generated: {output_path}")
                return str(output_path)
                
            finally:
                # Cleanup temp audio
                os.unlink(temp_audio.name)

    async def generate_example_video(self) -> str:
        """Generate one example video using the first fact"""
        if not self.data['facts']:
            raise ValueError("No facts found in configuration")
        
        first_fact = self.data['facts'][0]
        return await self.generate_fact_video(first_fact, "facts_example.mp4")

    def list_facts(self) -> List[Dict]:
        """List all available facts"""
        return self.data['facts']

    def get_facts_by_category(self, category: str) -> List[Dict]:
        """Get facts filtered by category"""
        return [fact for fact in self.data['facts'] if fact['category'] == category]

    async def generate_random_fact_video(self) -> str:
        """Generate a video from a random fact"""
        if not self.data['facts']:
            raise ValueError("No facts found in configuration")
        
        random_fact = random.choice(self.data['facts'])
        return await self.generate_fact_video(random_fact)


async def main():
    """Main function to generate example video"""
    # Setup paths
    config_path = "/Users/nick/clawd/kiin-content/config/caregiver_facts.json"
    output_dir = "/Users/nick/clawd/kiin-content/output"
    
    # Create generator
    generator = FactsVideoGenerator(config_path, output_dir)
    
    print("💡 Kiin 'Did You Know?' Facts Video Generator")
    print("=" * 60)
    
    # Generate example video
    try:
        video_path = await generator.generate_example_video()
        print(f"\n🎉 Success! Example fact video generated at: {video_path}")
        
        # Show video info
        if os.path.exists(video_path):
            file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
            print(f"📁 File size: {file_size:.2f} MB")
            print(f"📐 Resolution: {VIDEO_WIDTH}x{VIDEO_HEIGHT} (9:16)")
            print(f"⏱️  Duration: ~{TOTAL_DURATION} seconds")
    
    except Exception as e:
        print(f"❌ Error generating video: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())