#!/usr/bin/env python3
"""
Kiin "Quick Win" Video Generator
Generates ultra-short actionable tip videos for immediate implementation

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
import math
from brand_utils import KiinBrand

# Video constants
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920

# Timing (in seconds) - Keep it snappy!
HOOK_DURATION = 2
TIP_DURATION = 8
ACTION_DURATION = 4
TOTAL_DURATION = HOOK_DURATION + TIP_DURATION + ACTION_DURATION


class QuickWinVideoGenerator:
    def __init__(self, config_path: str, output_dir: str):
        self.config_path = Path(config_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Load brand configuration
        self.brand = KiinBrand()
        
        # Load quick wins from JSON
        with open(self.config_path, 'r') as f:
            self.data = json.load(f)
        
        # TTS voice settings - energetic pace
        self.voice = self.brand.get_voice_config()['tts_voice']
        self.voice_rate = "+15%"  # Faster for energy
        self.voice_pitch = "+5Hz"  # Slightly higher for enthusiasm
    
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

    def create_energetic_background(self, base_color: Tuple[int, int, int], accent_color: Tuple[int, int, int]) -> Image.Image:
        """Create an energetic background with dynamic elements"""
        image = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), base_color)
        draw = ImageDraw.Draw(image)
        
        # Add dynamic circular elements
        for i in range(15):
            # Random circles for energy
            x = random.randint(0, VIDEO_WIDTH)
            y = random.randint(0, VIDEO_HEIGHT)
            radius = random.randint(20, 80)
            alpha = random.randint(30, 100)
            
            # Create semi-transparent circle overlay
            circle_color = accent_color + (alpha,)
            circle_bbox = [x - radius, y - radius, x + radius, y + radius]
            draw.ellipse(circle_bbox, fill=circle_color)
        
        # Add diagonal stripes for movement
        stripe_color = tuple(min(255, c + 20) for c in base_color)
        for i in range(0, VIDEO_WIDTH + VIDEO_HEIGHT, 80):
            points = [
                (i - VIDEO_HEIGHT, 0),
                (i, 0),
                (i - 20, VIDEO_HEIGHT),
                (i - VIDEO_HEIGHT - 20, VIDEO_HEIGHT)
            ]
            draw.polygon(points, fill=stripe_color)
        
        return image

    def add_energy_icons(self, image: Image.Image, section: str) -> Image.Image:
        """Add energetic icons based on section"""
        draw = ImageDraw.Draw(image)
        
        if section == "hook":
            # Lightning bolt effect
            bolt_color = self.brand.get_color_rgb('accent')
            # Simple lightning bolt shape
            points = [
                (VIDEO_WIDTH // 2 - 30, 300),
                (VIDEO_WIDTH // 2 - 10, 350),
                (VIDEO_WIDTH // 2 + 20, 340),
                (VIDEO_WIDTH // 2 + 10, 380),
                (VIDEO_WIDTH // 2 + 30, 370),
                (VIDEO_WIDTH // 2, 400),
                (VIDEO_WIDTH // 2 - 5, 370),
                (VIDEO_WIDTH // 2 - 15, 380),
                (VIDEO_WIDTH // 2 - 10, 350)
            ]
            draw.polygon(points, fill=bolt_color)
            
        elif section == "tip":
            # Target/bullseye for focus
            target_color = self.brand.get_color_rgb('primary')
            center_x, center_y = VIDEO_WIDTH // 2, 400
            for radius in [60, 40, 20]:
                draw.ellipse([center_x - radius, center_y - radius,
                             center_x + radius, center_y + radius],
                            outline=target_color, width=8)
                            
        elif section == "action":
            # Checkmark or arrow for action
            arrow_color = self.brand.get_color_rgb('secondary')
            # Simple arrow pointing right
            arrow_points = [
                (VIDEO_WIDTH // 2 - 40, 350),
                (VIDEO_WIDTH // 2 + 20, 380),
                (VIDEO_WIDTH // 2 - 40, 410),
                (VIDEO_WIDTH // 2 - 20, 380)
            ]
            draw.polygon(arrow_points, fill=arrow_color)
        
        return image

    def create_text_image(self, text: str, bg_color: Tuple[int, int, int], 
                         accent_color: Tuple[int, int, int],
                         text_color: Tuple[int, int, int], 
                         font_size: int = 60, section: str = "tip") -> Image.Image:
        """Create an energetic image with text"""
        # Create energetic background
        image = self.create_energetic_background(bg_color, accent_color)
        
        # Add energy icons
        image = self.add_energy_icons(image, section)
        
        draw = ImageDraw.Draw(image)
        font = self.get_font(font_size, bold=True)
        
        # Wrap text
        max_width = VIDEO_WIDTH - 140  # More padding for energy
        lines = self.wrap_text(text, font, max_width)
        
        # Calculate total text height
        line_height = font_size + 30
        total_height = len(lines) * line_height
        
        # Position text based on section
        if section == "hook":
            y = VIDEO_HEIGHT // 2 + 80  # Below icon
        elif section == "action":
            y = VIDEO_HEIGHT - total_height - 200  # Near bottom
        else:
            y = (VIDEO_HEIGHT - total_height) // 2
        
        for line in lines:
            bbox = font.getbbox(line)
            text_width = bbox[2] - bbox[0]
            x = (VIDEO_WIDTH - text_width) // 2
            
            # Add multiple shadows for depth and energy
            for offset in [5, 3, 1]:
                shadow_alpha = 150 - (offset * 30)
                shadow_color = (0, 0, 0, shadow_alpha)
                draw.text((x + offset, y + offset), line, fill=shadow_color, font=font)
            
            # Main text
            draw.text((x, y), line, fill=text_color, font=font)
            y += line_height
        
        return image

    def create_section_image(self, section: str, quick_win: Dict) -> Image.Image:
        """Create image for a specific section"""
        
        if section == "hook":
            # High-energy hook
            bg_color = self.brand.get_color_rgb('accent')
            accent_color = self.brand.get_color_rgb('primary')
            text_color = self.brand.get_color_rgb('text_dark')
            text = f"⚡ {quick_win['time_to_implement']} TIP!"
            font_size = 65
            
        elif section == "tip":
            # Clear, focused tip
            bg_color = self.brand.get_color_rgb('primary')
            accent_color = self.brand.get_color_rgb('secondary')
            text_color = self.brand.get_color_rgb('text_light')
            text = quick_win['tip']
            font_size = 55
            
        else:  # action
            # Call to action
            bg_color = self.brand.get_color_rgb('secondary')
            accent_color = self.brand.get_color_rgb('accent')
            text_color = self.brand.get_color_rgb('text_light')
            text = f"👆 TRY THIS TODAY: {quick_win['action_step']}"
            font_size = 45
        
        return self.create_text_image(text, bg_color, accent_color, text_color, font_size, section)

    async def generate_audio(self, text: str, output_path: str):
        """Generate TTS audio for given text"""
        communicate = edge_tts.Communicate(text, self.voice, rate=self.voice_rate, pitch=self.voice_pitch)
        await communicate.save(output_path)

    def create_video_from_sections(self, sections: List[Tuple[str, str, float]], 
                                 audio_path: str, output_path: str, quick_win: Dict):
        """Create video from section images and audio using FFmpeg"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save section images
            image_paths = []
            
            for i, (section_name, text, duration) in enumerate(sections):
                image_path = os.path.join(temp_dir, f"section_{i:02d}.png")
                image = self.create_section_image(section_name, quick_win)
                image.save(image_path)
                image_paths.append(image_path)
            
            # Build FFmpeg command with quick cuts
            cmd = [
                'ffmpeg', '-y'  # Overwrite output file
            ]
            
            # Add input images with specific durations
            for i, (image_path, duration) in enumerate(zip(image_paths, [s[2] for s in sections])):
                cmd.extend(['-loop', '1', '-t', str(duration), '-i', image_path])
            
            # Add audio
            cmd.extend(['-i', audio_path])
            
            # Create filter complex for quick, energetic transitions
            filter_parts = []
            concat_inputs = ""
            
            for i in range(len(sections)):
                if i == 0:
                    # Quick fade in
                    filter_parts.append(f"[{i}:v]fade=in:st=0:d=0.2[v{i}]")
                else:
                    # Snap cuts for energy
                    filter_parts.append(f"[{i}:v]fade=in:st=0:d=0.1[v{i}]")
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

    async def generate_quick_win_video(self, quick_win: Dict, output_filename: str = None) -> str:
        """Generate a complete quick win video"""
        if not output_filename:
            # Create safe filename
            safe_title = "".join(c for c in quick_win['category'] if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_title = safe_title.replace(' ', '_')[:30]
            output_filename = f"quickwin_{quick_win['id']:02d}_{safe_title}.mp4"
        
        output_path = self.output_dir / output_filename
        
        print(f"Generating quick win video {quick_win['id']}: {quick_win['tip'][:50]}...")
        
        # Prepare sections
        sections = [
            ("hook", f"{quick_win['time_to_implement']} tip!", HOOK_DURATION),
            ("tip", quick_win['tip'], TIP_DURATION),
            ("action", f"Try this today: {quick_win['action_step']}", ACTION_DURATION)
        ]
        
        # Create energetic audio script
        audio_script = f"Here's a {quick_win['time_to_implement']} tip! {quick_win['tip']} Try this today: {quick_win['action_step']}"
        
        # Generate audio
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio:
            await self.generate_audio(audio_script, temp_audio.name)
            
            try:
                # Create video
                self.create_video_from_sections(sections, temp_audio.name, str(output_path), quick_win)
                print(f"✅ Video generated: {output_path}")
                return str(output_path)
                
            finally:
                # Cleanup temp audio
                os.unlink(temp_audio.name)

    async def generate_example_video(self) -> str:
        """Generate one example video using the first quick win"""
        if not self.data['quick_wins']:
            raise ValueError("No quick wins found in configuration")
        
        first_win = self.data['quick_wins'][0]
        return await self.generate_quick_win_video(first_win, "quickwin_example.mp4")

    def list_quick_wins(self) -> List[Dict]:
        """List all available quick wins"""
        return self.data['quick_wins']

    def get_quick_wins_by_category(self, category: str) -> List[Dict]:
        """Get quick wins filtered by category"""
        return [win for win in self.data['quick_wins'] if win['category'] == category]

    def get_quick_wins_by_time(self, max_minutes: int) -> List[Dict]:
        """Get quick wins that can be implemented within given time"""
        return [win for win in self.data['quick_wins'] 
                if int(win['time_to_implement'].split()[0]) <= max_minutes]

    async def generate_random_quick_win_video(self) -> str:
        """Generate a video from a random quick win"""
        if not self.data['quick_wins']:
            raise ValueError("No quick wins found in configuration")
        
        random_win = random.choice(self.data['quick_wins'])
        return await self.generate_quick_win_video(random_win)


async def main():
    """Main function to generate example video"""
    # Setup paths
    config_path = "/Users/nick/clawd/kiin-content/config/quick_wins.json"
    output_dir = "/Users/nick/clawd/kiin-content/output"
    
    # Create generator
    generator = QuickWinVideoGenerator(config_path, output_dir)
    
    print("⚡ Kiin 'Quick Win' Video Generator")
    print("=" * 50)
    
    # Generate example video
    try:
        video_path = await generator.generate_example_video()
        print(f"\n🎉 Success! Example quick win video generated at: {video_path}")
        
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