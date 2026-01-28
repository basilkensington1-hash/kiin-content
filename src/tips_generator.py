#!/usr/bin/env python3
"""
Caregiver Tips Video Generator
Generates educational "Stop Doing This" format videos for caregivers

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
from PIL import Image, ImageDraw, ImageFont
import edge_tts
import subprocess

# Constants
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FONT_COLOR_WHITE = (255, 255, 255)
FONT_COLOR_BLACK = (40, 40, 40)
RED_COLOR = (220, 53, 69)      # Bootstrap danger red
GREEN_COLOR = (25, 135, 84)    # Bootstrap success green
BLUE_COLOR = (13, 110, 253)    # Bootstrap primary blue
BACKGROUND_GRAY = (248, 249, 250)

# Video timing (in seconds)
HOOK_DURATION = 3
WRONG_DURATION = 8  
RIGHT_DURATION = 12
ENCOURAGEMENT_DURATION = 5
TOTAL_DURATION = HOOK_DURATION + WRONG_DURATION + RIGHT_DURATION + ENCOURAGEMENT_DURATION


class CaregiverTipVideoGenerator:
    def __init__(self, config_path: str, output_dir: str):
        self.config_path = Path(config_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Load tips from JSON
        with open(self.config_path, 'r') as f:
            self.data = json.load(f)
        
        # TTS voice settings
        self.voice = "en-US-AriaNeural"  # Warm, clear female voice
        self.voice_rate = "+0%"
        self.voice_pitch = "+0Hz"
    
    def get_font_path(self, size: int = 60, bold: bool = False) -> str:
        """Get system font path based on OS"""
        try:
            # Try to find a good system font
            font_paths = [
                "/System/Library/Fonts/Helvetica.ttc",  # macOS
                "/System/Library/Fonts/Arial.ttf",       # macOS
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
                "/Windows/Fonts/arial.ttf",              # Windows
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    return font_path
            
            # Fallback to default
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
                    # Single word too long, add it anyway
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines

    def create_text_image(self, text: str, bg_color: Tuple[int, int, int], 
                         text_color: Tuple[int, int, int], font_size: int = 60) -> Image.Image:
        """Create an image with centered text"""
        image = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), bg_color)
        draw = ImageDraw.Draw(image)
        
        font = self.get_font(font_size, bold=True)
        
        # Wrap text
        max_width = VIDEO_WIDTH - 120  # 60px margin on each side
        lines = self.wrap_text(text, font, max_width)
        
        # Calculate total text height
        line_height = font_size + 20
        total_height = len(lines) * line_height
        
        # Center vertically
        y = (VIDEO_HEIGHT - total_height) // 2
        
        for line in lines:
            bbox = font.getbbox(line)
            text_width = bbox[2] - bbox[0]
            x = (VIDEO_WIDTH - text_width) // 2
            
            draw.text((x, y), line, fill=text_color, font=font)
            y += line_height
        
        return image

    def create_section_image(self, section: str, text: str, section_number: int, total_sections: int) -> Image.Image:
        """Create image for a specific section with appropriate styling"""
        
        if section == "hook":
            bg_color = BLUE_COLOR
            text_color = FONT_COLOR_WHITE
            prefix = "STOP! "
        elif section == "wrong":
            bg_color = RED_COLOR
            text_color = FONT_COLOR_WHITE
            prefix = "❌ DON'T: "
        elif section == "right":
            bg_color = GREEN_COLOR
            text_color = FONT_COLOR_WHITE
            prefix = "✅ DO: "
        else:  # encouragement
            bg_color = BACKGROUND_GRAY
            text_color = FONT_COLOR_BLACK
            prefix = "💙 "
        
        full_text = prefix + text
        return self.create_text_image(full_text, bg_color, text_color, font_size=55)

    async def generate_audio(self, text: str, output_path: str):
        """Generate TTS audio for given text"""
        communicate = edge_tts.Communicate(text, self.voice, rate=self.voice_rate, pitch=self.voice_pitch)
        await communicate.save(output_path)

    def create_video_from_sections(self, sections: List[Tuple[str, str, float]], 
                                 audio_path: str, output_path: str):
        """Create video from section images and audio using FFmpeg"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save section images
            image_paths = []
            filter_complex_parts = []
            
            for i, (section_name, text, duration) in enumerate(sections):
                image_path = os.path.join(temp_dir, f"section_{i:02d}.png")
                image = self.create_section_image(section_name, text, i, len(sections))
                image.save(image_path)
                image_paths.append(image_path)
            
            # Create FFmpeg filter complex for transitions
            filter_parts = []
            current_time = 0
            
            for i, (_, _, duration) in enumerate(sections):
                if i == 0:
                    filter_parts.append(f"[{i}:v]loop=loop=-1:size=1:start=0,setpts=PTS-STARTPTS[v{i}]")
                else:
                    filter_parts.append(f"[{i}:v]loop=loop=-1:size=1:start=0,setpts=PTS-STARTPTS+{current_time}/TB[v{i}]")
                current_time += duration
            
            # Concatenate video parts
            concat_inputs = "".join(f"[v{i}]" for i in range(len(sections)))
            filter_parts.append(f"{concat_inputs}concat=n={len(sections)}:v=1:a=0[outv]")
            
            filter_complex = ";".join(filter_parts)
            
            # Build FFmpeg command
            cmd = [
                'ffmpeg', '-y'  # Overwrite output file
            ]
            
            # Add input images
            for image_path in image_paths:
                cmd.extend(['-loop', '1', '-t', str(TOTAL_DURATION), '-i', image_path])
            
            # Add audio
            cmd.extend(['-i', audio_path])
            
            # Add filter and output options
            cmd.extend([
                '-filter_complex', filter_complex,
                '-map', '[outv]',
                '-map', f'{len(image_paths)}:a',
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-shortest',
                '-r', '30',  # 30 fps
                '-pix_fmt', 'yuv420p',
                output_path
            ])
            
            # Execute FFmpeg
            print(f"Executing: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"FFmpeg Error: {result.stderr}")
                raise Exception(f"FFmpeg failed: {result.stderr}")

    async def generate_tip_video(self, tip: Dict, output_filename: str = None) -> str:
        """Generate a complete tip video"""
        if not output_filename:
            output_filename = f"tip_{tip['id']:02d}_{tip['category']}.mp4"
        
        output_path = self.output_dir / output_filename
        
        print(f"Generating video for tip {tip['id']}: {tip['hook'][:50]}...")
        
        # Prepare sections
        sections = [
            ("hook", tip['hook'], HOOK_DURATION),
            ("wrong", tip['wrong'], WRONG_DURATION),
            ("right", tip['right'], RIGHT_DURATION), 
            ("encouragement", tip['encouragement'], ENCOURAGEMENT_DURATION)
        ]
        
        # Create combined audio script
        audio_script = f"{tip['hook']}. {tip['wrong']}. Instead, {tip['right']}. {tip['encouragement']}"
        
        # Generate audio
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio:
            await self.generate_audio(audio_script, temp_audio.name)
            
            try:
                # Create video
                self.create_video_from_sections(sections, temp_audio.name, str(output_path))
                print(f"✅ Video generated: {output_path}")
                return str(output_path)
                
            finally:
                # Cleanup temp audio
                os.unlink(temp_audio.name)

    async def generate_example_video(self) -> str:
        """Generate one example video using the first tip"""
        if not self.data['tips']:
            raise ValueError("No tips found in configuration")
        
        first_tip = self.data['tips'][0]
        return await self.generate_tip_video(first_tip, "tips_example.mp4")

    def list_tips(self) -> List[Dict]:
        """List all available tips"""
        return self.data['tips']

    def get_tips_by_category(self, category: str) -> List[Dict]:
        """Get tips filtered by category"""
        return [tip for tip in self.data['tips'] if tip['category'] == category]


async def main():
    """Main function to generate example video"""
    # Setup paths
    config_path = "/Users/nick/clawd/kiin-content/config/caregiver_tips.json"
    output_dir = "/Users/nick/clawd/kiin-content/output"
    
    # Create generator
    generator = CaregiverTipVideoGenerator(config_path, output_dir)
    
    print("🎬 Caregiver Tips Video Generator")
    print("=" * 50)
    
    # Generate example video
    try:
        video_path = await generator.generate_example_video()
        print(f"\n🎉 Success! Example video generated at: {video_path}")
        
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