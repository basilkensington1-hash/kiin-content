#!/usr/bin/env python3
"""
Kiin "Myth vs Reality" Video Generator
Generates myth-busting videos about caregiving misconceptions

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
INTRO_DURATION = 2
MYTH_DURATION = 8
TRANSITION_DURATION = 2
REALITY_DURATION = 8
TOTAL_DURATION = INTRO_DURATION + MYTH_DURATION + TRANSITION_DURATION + REALITY_DURATION


class MythBusterVideoGenerator:
    def __init__(self, config_path: str, output_dir: str):
        self.config_path = Path(config_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Load brand configuration
        self.brand = KiinBrand()
        
        # Load myths from JSON
        with open(self.config_path, 'r') as f:
            self.data = json.load(f)
        
        # TTS voice settings
        self.voice = self.brand.get_voice_config()['tts_voice']
        self.voice_rate = "+5%"  # Slightly faster for clarity
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

    def create_split_background(self, left_color: Tuple[int, int, int], 
                               right_color: Tuple[int, int, int]) -> Image.Image:
        """Create a split-screen background"""
        image = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), (0, 0, 0))
        
        # Create left half
        left_half = Image.new('RGB', (VIDEO_WIDTH // 2, VIDEO_HEIGHT), left_color)
        image.paste(left_half, (0, 0))
        
        # Create right half  
        right_half = Image.new('RGB', (VIDEO_WIDTH // 2, VIDEO_HEIGHT), right_color)
        image.paste(right_half, (VIDEO_WIDTH // 2, 0))
        
        # Add subtle gradient in the middle for smooth transition
        draw = ImageDraw.Draw(image)
        center_x = VIDEO_WIDTH // 2
        
        for i in range(-10, 10):
            alpha = max(0, 255 - abs(i) * 25)
            line_color = (255, 255, 255, alpha)
            draw.line([(center_x + i, 0), (center_x + i, VIDEO_HEIGHT)], fill=line_color, width=1)
        
        return image

    def create_myth_vs_reality_image(self, myth_text: str, reality_text: str) -> Image.Image:
        """Create split-screen myth vs reality image"""
        # Colors for myth (red-ish) and reality (green-ish)
        myth_color = (180, 60, 60)  # Darker red
        reality_color = (60, 140, 80)  # Darker green
        
        # Create split background
        image = self.create_split_background(myth_color, reality_color)
        draw = ImageDraw.Draw(image)
        
        # Font settings
        header_font = self.get_font(50, bold=True)
        text_font = self.get_font(40, bold=False)
        
        # Add headers
        myth_header = "MYTH"
        reality_header = "REALITY"
        
        # Calculate header positions
        myth_header_bbox = header_font.getbbox(myth_header)
        reality_header_bbox = header_font.getbbox(reality_header)
        
        myth_header_x = (VIDEO_WIDTH // 4) - (myth_header_bbox[2] - myth_header_bbox[0]) // 2
        reality_header_x = (3 * VIDEO_WIDTH // 4) - (reality_header_bbox[2] - reality_header_bbox[0]) // 2
        header_y = 150
        
        # Draw headers with shadow
        shadow_offset = 3
        draw.text((myth_header_x + shadow_offset, header_y + shadow_offset), 
                 myth_header, fill=(0, 0, 0, 150), font=header_font)
        draw.text((myth_header_x, header_y), myth_header, fill=(255, 255, 255), font=header_font)
        
        draw.text((reality_header_x + shadow_offset, header_y + shadow_offset), 
                 reality_header, fill=(0, 0, 0, 150), font=header_font)
        draw.text((reality_header_x, header_y), reality_header, fill=(255, 255, 255), font=header_font)
        
        # Add text content
        left_margin = 50
        right_margin = VIDEO_WIDTH // 2 + 50
        text_width = VIDEO_WIDTH // 2 - 100
        text_y = 300
        
        # Wrap and draw myth text
        myth_lines = self.wrap_text(myth_text, text_font, text_width)
        current_y = text_y
        for line in myth_lines:
            line_bbox = text_font.getbbox(line)
            line_width = line_bbox[2] - line_bbox[0]
            line_x = left_margin + (text_width - line_width) // 2
            
            # Text shadow
            draw.text((line_x + shadow_offset, current_y + shadow_offset), 
                     line, fill=(0, 0, 0, 150), font=text_font)
            draw.text((line_x, current_y), line, fill=(255, 255, 255), font=text_font)
            current_y += 55
        
        # Wrap and draw reality text
        reality_lines = self.wrap_text(reality_text, text_font, text_width)
        current_y = text_y
        for line in reality_lines:
            line_bbox = text_font.getbbox(line)
            line_width = line_bbox[2] - line_bbox[0]
            line_x = right_margin + (text_width - line_width) // 2
            
            # Text shadow
            draw.text((line_x + shadow_offset, current_y + shadow_offset), 
                     line, fill=(0, 0, 0, 150), font=text_font)
            draw.text((line_x, current_y), line, fill=(255, 255, 255), font=text_font)
            current_y += 55
        
        # Add icons
        # Add X for myth side
        x_size = 60
        x_x = myth_header_x + 20
        x_y = header_y - 80
        draw.line([(x_x, x_y), (x_x + x_size, x_y + x_size)], fill=(255, 255, 255), width=8)
        draw.line([(x_x + x_size, x_y), (x_x, x_y + x_size)], fill=(255, 255, 255), width=8)
        
        # Add checkmark for reality side
        check_x = reality_header_x + 20
        check_y = header_y - 80
        check_size = 60
        draw.line([(check_x, check_y + check_size // 2), 
                  (check_x + check_size // 3, check_y + check_size)], fill=(255, 255, 255), width=8)
        draw.line([(check_x + check_size // 3, check_y + check_size), 
                  (check_x + check_size, check_y)], fill=(255, 255, 255), width=8)
        
        return image

    def create_solid_color_image(self, text: str, bg_color: Tuple[int, int, int], 
                                text_color: Tuple[int, int, int], font_size: int = 60) -> Image.Image:
        """Create a solid color background with centered text"""
        image = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), bg_color)
        draw = ImageDraw.Draw(image)
        
        font = self.get_font(font_size, bold=True)
        
        # Wrap text
        max_width = VIDEO_WIDTH - 120
        lines = self.wrap_text(text, font, max_width)
        
        # Calculate total text height
        line_height = font_size + 25
        total_height = len(lines) * line_height
        
        # Center vertically
        y = (VIDEO_HEIGHT - total_height) // 2
        
        for line in lines:
            bbox = font.getbbox(line)
            text_width = bbox[2] - bbox[0]
            x = (VIDEO_WIDTH - text_width) // 2
            
            # Add shadow for readability
            shadow_offset = 3
            draw.text((x + shadow_offset, y + shadow_offset), line, fill=(0, 0, 0, 100), font=font)
            draw.text((x, y), line, fill=text_color, font=font)
            y += line_height
        
        return image

    def create_section_image(self, section: str, myth_data: Dict) -> Image.Image:
        """Create image for a specific section"""
        
        if section == "intro":
            # Attention-grabbing intro
            bg_color = self.brand.get_color_rgb('primary')
            text_color = self.brand.get_color_rgb('text_light')
            text = "🔍 MYTH BUSTED!"
            return self.create_solid_color_image(text, bg_color, text_color, font_size=65)
            
        elif section == "myth":
            # Show just the myth first
            bg_color = (180, 60, 60)  # Red for myth
            text_color = self.brand.get_color_rgb('text_light')
            text = f"MYTH: {myth_data['myth']}"
            return self.create_solid_color_image(text, bg_color, text_color, font_size=50)
            
        elif section == "transition":
            # Transition "BUT ACTUALLY..."
            bg_color = self.brand.get_color_rgb('accent')
            text_color = self.brand.get_color_rgb('text_dark')
            text = "BUT ACTUALLY..."
            return self.create_solid_color_image(text, bg_color, text_color, font_size=60)
            
        else:  # reality
            # Show the reality
            bg_color = (60, 140, 80)  # Green for reality
            text_color = self.brand.get_color_rgb('text_light')
            text = f"REALITY: {myth_data['reality']}"
            return self.create_solid_color_image(text, bg_color, text_color, font_size=50)

    async def generate_audio(self, text: str, output_path: str):
        """Generate TTS audio for given text"""
        communicate = edge_tts.Communicate(text, self.voice, rate=self.voice_rate, pitch=self.voice_pitch)
        await communicate.save(output_path)

    def create_video_from_sections(self, sections: List[Tuple[str, str, float]], 
                                 audio_path: str, output_path: str, myth_data: Dict):
        """Create video from section images and audio using FFmpeg"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save section images
            image_paths = []
            
            for i, (section_name, text, duration) in enumerate(sections):
                image_path = os.path.join(temp_dir, f"section_{i:02d}.png")
                image = self.create_section_image(section_name, myth_data)
                image.save(image_path)
                image_paths.append(image_path)
            
            # Build FFmpeg command
            cmd = [
                'ffmpeg', '-y'  # Overwrite output file
            ]
            
            # Add input images with specific durations
            for i, (image_path, duration) in enumerate(zip(image_paths, [s[2] for s in sections])):
                cmd.extend(['-loop', '1', '-t', str(duration), '-i', image_path])
            
            # Add audio
            cmd.extend(['-i', audio_path])
            
            # Create filter complex for dramatic transitions
            filter_parts = []
            concat_inputs = ""
            
            for i in range(len(sections)):
                if i == 0:
                    filter_parts.append(f"[{i}:v]fade=in:st=0:d=0.5[v{i}]")
                elif sections[i][0] == "transition":
                    # Quick cut for dramatic effect
                    filter_parts.append(f"[{i}:v]fade=in:st=0:d=0.2[v{i}]")
                else:
                    filter_parts.append(f"[{i}:v]fade=in:st=0:d=0.3[v{i}]")
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
            print(f"Executing: {' '.join(cmd[:10])}...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"FFmpeg Error: {result.stderr}")
                raise Exception(f"FFmpeg failed: {result.stderr}")

    async def generate_myth_video(self, myth: Dict, output_filename: str = None) -> str:
        """Generate a complete myth-busting video"""
        if not output_filename:
            # Create safe filename
            safe_title = "".join(c for c in myth['category'] if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_title = safe_title.replace(' ', '_')[:30]
            output_filename = f"myth_{myth['id']:02d}_{safe_title}.mp4"
        
        output_path = self.output_dir / output_filename
        
        print(f"Generating myth-buster video {myth['id']}: {myth['myth'][:50]}...")
        
        # Prepare sections
        sections = [
            ("intro", "Myth Busted!", INTRO_DURATION),
            ("myth", myth['myth'], MYTH_DURATION),
            ("transition", "But actually...", TRANSITION_DURATION),
            ("reality", myth['reality'], REALITY_DURATION)
        ]
        
        # Create engaging audio script
        audio_script = f"Myth busted! Many people believe {myth['myth']} But actually, {myth['reality']} {myth.get('explanation', '')}"
        
        # Generate audio
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio:
            await self.generate_audio(audio_script, temp_audio.name)
            
            try:
                # Create video
                self.create_video_from_sections(sections, temp_audio.name, str(output_path), myth)
                print(f"✅ Video generated: {output_path}")
                return str(output_path)
                
            finally:
                # Cleanup temp audio
                os.unlink(temp_audio.name)

    async def generate_example_video(self) -> str:
        """Generate one example video using the first myth"""
        if not self.data['myths']:
            raise ValueError("No myths found in configuration")
        
        first_myth = self.data['myths'][0]
        return await self.generate_myth_video(first_myth, "mythbuster_example.mp4")

    def list_myths(self) -> List[Dict]:
        """List all available myths"""
        return self.data['myths']

    def get_myths_by_category(self, category: str) -> List[Dict]:
        """Get myths filtered by category"""
        return [myth for myth in self.data['myths'] if myth['category'] == category]

    async def generate_random_myth_video(self) -> str:
        """Generate a video from a random myth"""
        if not self.data['myths']:
            raise ValueError("No myths found in configuration")
        
        random_myth = random.choice(self.data['myths'])
        return await self.generate_myth_video(random_myth)


async def main():
    """Main function to generate example video"""
    # Setup paths
    config_path = "/Users/nick/clawd/kiin-content/config/caregiver_myths.json"
    output_dir = "/Users/nick/clawd/kiin-content/output"
    
    # Create generator
    generator = MythBusterVideoGenerator(config_path, output_dir)
    
    print("🔍 Kiin 'Myth vs Reality' Video Generator")
    print("=" * 60)
    
    # Generate example video
    try:
        video_path = await generator.generate_example_video()
        print(f"\n🎉 Success! Example myth-buster video generated at: {video_path}")
        
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