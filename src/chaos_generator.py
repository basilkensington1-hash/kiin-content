#!/usr/bin/env python3
"""
Coordination Chaos Content Generator

Creates before/after videos showing care coordination problems and solutions.
Directly demonstrates Kiin's value proposition.

Usage:
    python chaos_generator.py [scenario_id]
"""

import os
import sys
import json
import asyncio
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple
import edge_tts
from PIL import Image, ImageDraw, ImageFont
import textwrap

# Video configuration
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30

# Timing configuration (in seconds)
HOOK_DURATION = 5
CHAOS_DURATION = 15
TURNING_POINT_DURATION = 5
CALM_DURATION = 15
CTA_DURATION = 5

# Color schemes
CHAOS_COLORS = {
    'background': '#2D1B1B',  # Dark red
    'primary': '#FF4444',     # Bright red
    'secondary': '#FF8888',   # Light red
    'text': '#FFFFFF'         # White
}

CALM_COLORS = {
    'background': '#1B2D2D',  # Dark blue-green
    'primary': '#4488FF',     # Bright blue
    'secondary': '#88CCFF',   # Light blue
    'text': '#FFFFFF'         # White
}

class ChaosGenerator:
    def __init__(self, config_path: str, output_dir: str):
        self.config_path = Path(config_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Load scenarios
        with open(self.config_path, 'r') as f:
            self.data = json.load(f)
        
        # Create temp directory for assets
        self.temp_dir = Path(tempfile.mkdtemp(prefix='chaos_gen_'))
        
    def get_font(self, size: int = 40) -> ImageFont.FreeTypeFont:
        """Get font for text rendering"""
        # Try to find system fonts, fallback to default
        font_paths = [
            '/System/Library/Fonts/Arial.ttf',
            '/System/Library/Fonts/Helvetica.ttc',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, size)
                except:
                    continue
        
        # Fallback to default font
        return ImageFont.load_default()
    
    def wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
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
                    # Word is too long, force it
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def create_text_image(self, text: str, colors: Dict[str, str], 
                         font_size: int = 50, subtitle: str = None) -> str:
        """Create an image with text overlay"""
        img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), colors['background'])
        draw = ImageDraw.Draw(img)
        
        # Main text font
        font = self.get_font(font_size)
        subtitle_font = self.get_font(int(font_size * 0.6)) if subtitle else None
        
        # Wrap main text
        max_text_width = VIDEO_WIDTH - 120  # Padding
        lines = self.wrap_text(text, font, max_text_width)
        
        # Calculate total text height
        line_height = font_size + 10
        total_height = len(lines) * line_height
        if subtitle:
            total_height += int(font_size * 0.8) + 30
        
        # Start position (center vertically)
        y_start = (VIDEO_HEIGHT - total_height) // 2
        
        # Draw main text
        for i, line in enumerate(lines):
            bbox = font.getbbox(line)
            text_width = bbox[2] - bbox[0]
            x = (VIDEO_WIDTH - text_width) // 2
            y = y_start + (i * line_height)
            
            # Draw text with shadow for readability
            draw.text((x+2, y+2), line, font=font, fill='#000000')  # Shadow
            draw.text((x, y), line, font=font, fill=colors['text'])
        
        # Draw subtitle if provided
        if subtitle and subtitle_font:
            sub_lines = self.wrap_text(subtitle, subtitle_font, max_text_width)
            sub_y_start = y_start + total_height - (len(sub_lines) * (int(font_size * 0.6) + 5))
            
            for i, line in enumerate(sub_lines):
                bbox = subtitle_font.getbbox(line)
                text_width = bbox[2] - bbox[0]
                x = (VIDEO_WIDTH - text_width) // 2
                y = sub_y_start + (i * (int(font_size * 0.6) + 5))
                
                draw.text((x+1, y+1), line, font=subtitle_font, fill='#000000')  # Shadow
                draw.text((x, y), line, font=subtitle_font, fill=colors['secondary'])
        
        # Add visual elements
        self._add_visual_elements(draw, colors)
        
        # Save image
        output_path = self.temp_dir / f'text_{len(list(self.temp_dir.glob("text_*.png")))}.png'
        img.save(output_path)
        return str(output_path)
    
    def _add_visual_elements(self, draw: ImageDraw.Draw, colors: Dict[str, str]):
        """Add decorative visual elements to images"""
        # Add corner accents
        accent_size = 60
        
        # Top corners
        draw.rectangle([0, 0, accent_size, 10], fill=colors['primary'])
        draw.rectangle([VIDEO_WIDTH-accent_size, 0, VIDEO_WIDTH, 10], fill=colors['primary'])
        
        # Bottom corners  
        draw.rectangle([0, VIDEO_HEIGHT-10, accent_size, VIDEO_HEIGHT], fill=colors['primary'])
        draw.rectangle([VIDEO_WIDTH-accent_size, VIDEO_HEIGHT-10, VIDEO_WIDTH, VIDEO_HEIGHT], fill=colors['primary'])
        
        # Side accents for chaos (jagged) vs calm (smooth)
        if colors == CHAOS_COLORS:
            # Jagged lines for chaos
            for i in range(5):
                y1 = 200 + (i * 300)
                y2 = y1 + 50
                draw.polygon([
                    (20, y1), (40, y1+25), (20, y2), (0, y1+25)
                ], fill=colors['secondary'])
                draw.polygon([
                    (VIDEO_WIDTH-20, y1), (VIDEO_WIDTH, y1+25), 
                    (VIDEO_WIDTH-20, y2), (VIDEO_WIDTH-40, y1+25)
                ], fill=colors['secondary'])
        else:
            # Smooth curves for calm
            for i in range(3):
                y = 300 + (i * 400)
                draw.ellipse([0, y, 40, y+40], fill=colors['secondary'])
                draw.ellipse([VIDEO_WIDTH-40, y, VIDEO_WIDTH, y+40], fill=colors['secondary'])
    
    def create_transition_frame(self, progress: float) -> str:
        """Create transition frame between chaos and calm"""
        img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), '#1B1B2D')
        draw = ImageDraw.Draw(img)
        
        # Create a gradient effect
        chaos_alpha = int(255 * (1 - progress))
        calm_alpha = int(255 * progress)
        
        # Add transition text
        font = self.get_font(60)
        text = "Everything changed when..."
        bbox = font.getbbox(text)
        text_width = bbox[2] - bbox[0]
        x = (VIDEO_WIDTH - text_width) // 2
        y = VIDEO_HEIGHT // 2 - 30
        
        draw.text((x+2, y+2), text, font=font, fill='#000000')  # Shadow
        draw.text((x, y), text, font=font, fill='#FFFFFF')
        
        # Add animated elements
        circle_radius = int(50 + (progress * 100))
        draw.ellipse([
            VIDEO_WIDTH//2 - circle_radius, 
            VIDEO_HEIGHT//2 + 100 - circle_radius,
            VIDEO_WIDTH//2 + circle_radius,
            VIDEO_HEIGHT//2 + 100 + circle_radius
        ], outline='#4488FF', width=3)
        
        output_path = self.temp_dir / f'transition_{int(progress*100):03d}.png'
        img.save(output_path)
        return str(output_path)
    
    async def generate_audio(self, script: Dict[str, str]) -> Dict[str, str]:
        """Generate TTS audio for all parts"""
        voice = "en-US-AriaNeural"  # Clear, professional voice
        audio_files = {}
        
        for section, text in script.items():
            if not text.strip():
                continue
                
            # Create TTS
            communicate = edge_tts.Communicate(text, voice)
            audio_path = self.temp_dir / f'audio_{section}.wav'
            await communicate.save(str(audio_path))
            audio_files[section] = str(audio_path)
        
        return audio_files
    
    def create_video_segment(self, image_path: str, audio_path: str, 
                           duration: float, output_path: str):
        """Create video segment from image and audio"""
        cmd = [
            'ffmpeg', '-y',
            '-loop', '1',
            '-i', image_path,
            '-i', audio_path,
            '-c:v', 'libx264',
            '-t', str(duration),
            '-pix_fmt', 'yuv420p',
            '-r', str(FPS),
            '-c:a', 'aac',
            '-shortest',
            output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
    
    def create_transition_video(self, duration: float, output_path: str):
        """Create transition video with animated frames"""
        frame_count = int(duration * FPS)
        frame_paths = []
        
        for i in range(frame_count):
            progress = i / frame_count
            frame_path = self.create_transition_frame(progress)
            frame_paths.append(frame_path)
        
        # Create video from frames
        frame_list = self.temp_dir / 'frame_list.txt'
        with open(frame_list, 'w') as f:
            for frame_path in frame_paths:
                f.write(f"file '{frame_path}'\n")
                f.write(f"duration {1/FPS}\n")
        
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(frame_list),
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-r', str(FPS),
            output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
    
    def combine_segments(self, segments: List[str], output_path: str):
        """Combine video segments into final video"""
        # Create concat file
        concat_file = self.temp_dir / 'concat.txt'
        with open(concat_file, 'w') as f:
            for segment in segments:
                f.write(f"file '{segment}'\n")
        
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_file),
            '-c', 'copy',
            output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
    
    async def generate_video(self, scenario_id: str) -> str:
        """Generate complete video for scenario"""
        # Find scenario
        scenario = None
        for s in self.data['scenarios']:
            if s['id'] == scenario_id:
                scenario = s
                break
        
        if not scenario:
            raise ValueError(f"Scenario '{scenario_id}' not found")
        
        print(f"Generating video for scenario: {scenario_id}")
        
        # Create script
        script = {
            'hook': scenario['hook'],
            'chaos': '. '.join(scenario['chaos']),
            'turning_point': scenario['turning_point'],
            'calm': '. '.join(scenario['calm']),
            'cta': scenario['cta']
        }
        
        # Generate audio
        print("Generating audio...")
        audio_files = await self.generate_audio(script)
        
        # Create images
        print("Creating visuals...")
        images = {}
        images['hook'] = self.create_text_image(
            script['hook'], CHAOS_COLORS, 55
        )
        images['chaos'] = self.create_text_image(
            script['chaos'], CHAOS_COLORS, 38, "The Problem"
        )
        images['turning_point'] = self.create_text_image(
            script['turning_point'], {'background': '#2D2D1B', 'primary': '#FFAA44', 
                                    'secondary': '#FFCC88', 'text': '#FFFFFF'}, 45
        )
        images['calm'] = self.create_text_image(
            script['calm'], CALM_COLORS, 38, "The Solution"
        )
        images['cta'] = self.create_text_image(
            script['cta'], CALM_COLORS, 48
        )
        
        # Create video segments
        print("Creating video segments...")
        segments = []
        
        # Hook segment
        hook_segment = self.temp_dir / 'hook.mp4'
        self.create_video_segment(
            images['hook'], audio_files['hook'], 
            HOOK_DURATION, str(hook_segment)
        )
        segments.append(str(hook_segment))
        
        # Chaos segment
        chaos_segment = self.temp_dir / 'chaos.mp4'
        self.create_video_segment(
            images['chaos'], audio_files['chaos'],
            CHAOS_DURATION, str(chaos_segment)
        )
        segments.append(str(chaos_segment))
        
        # Turning point segment
        turning_segment = self.temp_dir / 'turning.mp4'
        self.create_video_segment(
            images['turning_point'], audio_files['turning_point'],
            TURNING_POINT_DURATION, str(turning_segment)
        )
        segments.append(str(turning_segment))
        
        # Calm segment
        calm_segment = self.temp_dir / 'calm.mp4'
        self.create_video_segment(
            images['calm'], audio_files['calm'],
            CALM_DURATION, str(calm_segment)
        )
        segments.append(str(calm_segment))
        
        # CTA segment
        cta_segment = self.temp_dir / 'cta.mp4'
        self.create_video_segment(
            images['cta'], audio_files['cta'],
            CTA_DURATION, str(cta_segment)
        )
        segments.append(str(cta_segment))
        
        # Combine all segments
        print("Combining segments...")
        output_path = self.output_dir / f'{scenario_id}_chaos.mp4'
        self.combine_segments(segments, str(output_path))
        
        print(f"Video created: {output_path}")
        return str(output_path)
    
    def cleanup(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)


async def main():
    script_dir = Path(__file__).parent
    config_path = script_dir.parent / 'config' / 'coordination_scenarios.json'
    output_dir = script_dir.parent / 'output'
    
    generator = ChaosGenerator(config_path, output_dir)
    
    try:
        # Get scenario ID from command line or use first one
        if len(sys.argv) > 1:
            scenario_id = sys.argv[1]
        else:
            scenario_id = generator.data['scenarios'][0]['id']
        
        # Generate video
        output_path = await generator.generate_video(scenario_id)
        print(f"\n✅ Video generated successfully!")
        print(f"📹 Output: {output_path}")
        print(f"📏 Format: 9:16 vertical (1080x1920)")
        print(f"⏱️  Duration: ~{HOOK_DURATION + CHAOS_DURATION + TURNING_POINT_DURATION + CALM_DURATION + CTA_DURATION} seconds")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    finally:
        generator.cleanup()
    
    return 0


if __name__ == '__main__':
    exit(asyncio.run(main()))