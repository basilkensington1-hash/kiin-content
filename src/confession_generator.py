#!/usr/bin/env python3
"""
Caregiver Confessions Generator
Creates intimate, vulnerable video content for caregivers who need validation.

Features:
- Soft gradient backgrounds
- Word-by-word text animation
- Gentle TTS voice synthesis
- 9:16 vertical format (1080x1920)
- 15-25 second duration
"""

import json
import random
import os
import subprocess
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import asyncio
import edge_tts
import textwrap
import re
import math

class ConfessionGenerator:
    def __init__(self, config_path=None, output_dir=None):
        """Initialize the confession generator"""
        self.base_dir = Path(__file__).parent.parent
        self.config_path = config_path or self.base_dir / "config" / "confessions.json"
        self.output_dir = Path(output_dir or self.base_dir / "output")
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Video specifications
        self.width = 1080
        self.height = 1920
        self.fps = 24
        
        # Load confessions
        self.confessions = self.load_confessions()
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def load_confessions(self):
        """Load confessions from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)
                return data['confessions']
        except FileNotFoundError:
            raise FileNotFoundError(f"Confessions file not found at {self.config_path}")
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON in confessions file")
    
    def create_gradient_background(self, color_scheme="warm"):
        """Create a soft gradient background"""
        # Color schemes for different moods
        schemes = {
            "warm": {
                "start": (251, 236, 220),  # Warm cream
                "middle": (247, 220, 196), # Soft peach
                "end": (243, 204, 172)     # Light terracotta
            },
            "cool": {
                "start": (230, 238, 246),  # Soft blue
                "middle": (220, 230, 240), # Light blue-grey
                "end": (210, 222, 234)     # Muted blue
            },
            "neutral": {
                "start": (248, 246, 244),  # Off white
                "middle": (240, 236, 232), # Warm grey
                "end": (232, 226, 218)     # Soft beige
            }
        }
        
        colors = schemes.get(color_scheme, schemes["warm"])
        
        # Create image with gradient
        image = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(image)
        
        # Create vertical gradient
        for y in range(self.height):
            # Calculate position (0 to 1) along gradient
            pos = y / self.height
            
            # Smooth gradient with multiple transition points
            if pos < 0.5:
                # Transition from start to middle
                t = pos * 2
                r = int(colors["start"][0] + (colors["middle"][0] - colors["start"][0]) * t)
                g = int(colors["start"][1] + (colors["middle"][1] - colors["start"][1]) * t)
                b = int(colors["start"][2] + (colors["middle"][2] - colors["start"][2]) * t)
            else:
                # Transition from middle to end
                t = (pos - 0.5) * 2
                r = int(colors["middle"][0] + (colors["end"][0] - colors["middle"][0]) * t)
                g = int(colors["middle"][1] + (colors["end"][1] - colors["middle"][1]) * t)
                b = int(colors["middle"][2] + (colors["end"][2] - colors["middle"][2]) * t)
            
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))
        
        # Add subtle texture overlay
        self.add_subtle_texture(image)
        
        return image
    
    def add_subtle_texture(self, image):
        """Add very subtle texture to prevent flat background"""
        overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Add very faint noise pattern
        for i in range(0, self.width, 40):
            for j in range(0, self.height, 40):
                if random.random() > 0.95:  # Very sparse
                    opacity = random.randint(3, 8)  # Very subtle
                    size = random.randint(1, 2)
                    draw.ellipse([i, j, i+size, j+size], 
                               fill=(255, 255, 255, opacity))
        
        # Blend with original
        image.paste(Image.alpha_composite(image.convert('RGBA'), overlay).convert('RGB'))
    
    def get_font(self, size=60):
        """Get font for text rendering"""
        # Try to find a good font, fall back to default
        font_paths = [
            "/System/Library/Fonts/Helvetica.ttc",  # macOS
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
            "C:/Windows/Fonts/arial.ttf",  # Windows
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, size)
                except:
                    pass
        
        # Fall back to default
        try:
            return ImageFont.truetype("arial.ttf", size)
        except:
            return ImageFont.load_default()
    
    def wrap_text(self, text, font, max_width):
        """Wrap text to fit within specified width"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = current_line + [word]
            bbox = font.getbbox(" ".join(test_line))
            width = bbox[2] - bbox[0]
            
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                else:
                    # Word is too long, force it
                    lines.append(word)
        
        if current_line:
            lines.append(" ".join(current_line))
        
        return lines
    
    def create_text_frames(self, confession, total_duration):
        """Create frames with animated text appearance"""
        hook = confession['hook']
        content = confession['confession']
        validation = confession['validation']
        
        total_frames = int(total_duration * self.fps)
        frames = []
        
        # Text styling
        hook_font = self.get_font(55)
        content_font = self.get_font(48)
        validation_font = self.get_font(40)
        
        # Text positioning
        margin = 80
        max_width = self.width - (2 * margin)
        
        # Wrap all text sections
        hook_lines = self.wrap_text(hook, hook_font, max_width)
        content_lines = self.wrap_text(content, content_font, max_width)
        validation_lines = self.wrap_text(validation, validation_font, max_width)
        
        # Calculate timing (hook: 20%, content: 65%, validation: 15%)
        hook_frames = int(total_frames * 0.20)
        content_frames = int(total_frames * 0.65)
        validation_frames = total_frames - hook_frames - content_frames
        
        # Timing for word-by-word animation
        hook_words = hook.split()
        content_words = content.split()
        validation_words = validation.split()
        
        # Create frames
        for frame_num in range(total_frames):
            bg = self.create_gradient_background()
            draw = ImageDraw.Draw(bg)
            
            current_y = 400  # Start position
            
            if frame_num < hook_frames:
                # Hook phase - animate word by word
                words_to_show = int((frame_num / hook_frames) * len(hook_words)) + 1
                visible_hook = " ".join(hook_words[:words_to_show])
                visible_hook_lines = self.wrap_text(visible_hook, hook_font, max_width)
                
                for line in visible_hook_lines:
                    bbox = hook_font.getbbox(line)
                    x = (self.width - (bbox[2] - bbox[0])) // 2
                    draw.text((x, current_y), line, fill=(80, 60, 60), font=hook_font)
                    current_y += bbox[3] - bbox[1] + 20
            
            elif frame_num < hook_frames + content_frames:
                # Content phase
                content_frame = frame_num - hook_frames
                
                # Show full hook (faded)
                for line in hook_lines:
                    bbox = hook_font.getbbox(line)
                    x = (self.width - (bbox[2] - bbox[0])) // 2
                    draw.text((x, current_y), line, fill=(120, 100, 100), font=hook_font)
                    current_y += bbox[3] - bbox[1] + 20
                
                current_y += 40  # Space between sections
                
                # Animate content words
                words_to_show = int((content_frame / content_frames) * len(content_words)) + 1
                visible_content = " ".join(content_words[:words_to_show])
                visible_content_lines = self.wrap_text(visible_content, content_font, max_width)
                
                for line in visible_content_lines:
                    bbox = content_font.getbbox(line)
                    x = (self.width - (bbox[2] - bbox[0])) // 2
                    draw.text((x, current_y), line, fill=(60, 60, 60), font=content_font)
                    current_y += bbox[3] - bbox[1] + 25
            
            else:
                # Validation phase
                validation_frame = frame_num - hook_frames - content_frames
                
                # Show full hook and content (more faded)
                for line in hook_lines:
                    bbox = hook_font.getbbox(line)
                    x = (self.width - (bbox[2] - bbox[0])) // 2
                    draw.text((x, current_y), line, fill=(150, 130, 130), font=hook_font)
                    current_y += bbox[3] - bbox[1] + 20
                
                current_y += 30
                
                for line in content_lines:
                    bbox = content_font.getbbox(line)
                    x = (self.width - (bbox[2] - bbox[0])) // 2
                    draw.text((x, current_y), line, fill=(120, 120, 120), font=content_font)
                    current_y += bbox[3] - bbox[1] + 25
                
                current_y += 60
                
                # Animate validation
                words_to_show = int((validation_frame / validation_frames) * len(validation_words)) + 1
                visible_validation = " ".join(validation_words[:words_to_show])
                visible_validation_lines = self.wrap_text(visible_validation, validation_font, max_width)
                
                for line in visible_validation_lines:
                    bbox = validation_font.getbbox(line)
                    x = (self.width - (bbox[2] - bbox[0])) // 2
                    draw.text((x, current_y), line, fill=(100, 80, 60), font=validation_font)
                    current_y += bbox[3] - bbox[1] + 20
            
            frames.append(bg)
        
        return frames
    
    async def create_audio(self, confession, duration):
        """Create audio using edge-tts"""
        # Combine all text
        full_text = f"{confession['hook']} {confession['confession']} {confession['validation']}"
        
        # Use a soft, intimate voice
        voice = "en-US-AriaNeural"  # Soft, warm female voice
        
        output_path = self.temp_dir / "audio.wav"
        
        communicate = edge_tts.Communicate(full_text, voice)
        communicate.rate = "-20%"  # Slower for intimate feeling
        communicate.pitch = "-5Hz"  # Slightly lower pitch
        
        await communicate.save(str(output_path))
        
        return output_path
    
    def save_frames_as_video(self, frames, output_path, audio_path=None):
        """Save frames as video using FFmpeg"""
        # Save frames as temporary images
        frame_pattern = self.temp_dir / "frame_%05d.png"
        
        for i, frame in enumerate(frames):
            frame.save(self.temp_dir / f"frame_{i:05d}.png")
        
        # Build FFmpeg command - use macOS hardware encoder
        cmd = [
            "ffmpeg", "-y",  # Overwrite output
            "-framerate", str(self.fps),
            "-i", str(self.temp_dir / "frame_%05d.png"),
        ]
        
        # Add audio if provided
        if audio_path and os.path.exists(audio_path):
            cmd.extend([
                "-i", str(audio_path),
                "-c:v", "h264_videotoolbox",  # Use macOS hardware encoder
                "-b:v", "2M",  # 2Mbps bitrate
                "-c:a", "aac",
                "-b:a", "128k",
                "-shortest"  # Match video duration
            ])
        else:
            cmd.extend([
                "-c:v", "h264_videotoolbox",  # Use macOS hardware encoder
                "-b:v", "2M",  # 2Mbps bitrate
            ])
        
        cmd.extend(["-pix_fmt", "yuv420p", str(output_path)])
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Video saved: {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"❌ FFmpeg error: {e}")
            print(f"stdout: {e.stdout.decode()}")
            print(f"stderr: {e.stderr.decode()}")
            raise
    
    def cleanup(self):
        """Clean up temporary files"""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    async def generate_video(self, confession_id=None, output_name="confession_example.mp4"):
        """Generate a complete confession video"""
        try:
            # Select confession
            if confession_id is None:
                confession = random.choice(self.confessions)
            else:
                confession = next((c for c in self.confessions if c['id'] == confession_id), None)
                if not confession:
                    raise ValueError(f"Confession ID {confession_id} not found")
            
            print(f"🎬 Generating confession video: '{confession['hook'][:50]}...'")
            
            # Use target duration or default
            duration = confession.get('duration_target', 20)
            
            # Create text animation frames
            print("📝 Creating text animation frames...")
            frames = self.create_text_frames(confession, duration)
            
            # Create audio
            print("🎵 Generating TTS audio...")
            audio_path = await self.create_audio(confession, duration)
            
            # Save final video
            output_path = self.output_dir / output_name
            print("🎥 Rendering final video...")
            self.save_frames_as_video(frames, output_path, audio_path)
            
            print(f"\n✅ Video generated successfully!")
            print(f"📍 Location: {output_path}")
            print(f"📏 Dimensions: {self.width}x{self.height} (9:16)")
            print(f"⏱️  Duration: ~{duration} seconds")
            print(f"💬 Confession: {confession['id']}")
            
            return output_path
            
        except Exception as e:
            print(f"❌ Error generating video: {e}")
            raise
        finally:
            self.cleanup()

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate caregiver confession videos")
    parser.add_argument("--confession-id", type=int, help="Specific confession ID to use")
    parser.add_argument("--output", "-o", default="confession_example.mp4", help="Output filename")
    parser.add_argument("--config", help="Path to confessions JSON file")
    parser.add_argument("--output-dir", help="Output directory")
    
    args = parser.parse_args()
    
    # Create generator
    generator = ConfessionGenerator(
        config_path=args.config,
        output_dir=args.output_dir
    )
    
    # Generate video
    asyncio.run(generator.generate_video(
        confession_id=args.confession_id,
        output_name=args.output
    ))

if __name__ == "__main__":
    main()