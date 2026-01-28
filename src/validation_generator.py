#!/usr/bin/env python3
"""
Validation Video Generator for Caregivers
Creates short, powerful validation videos with calming visuals and gentle audio.
"""

import argparse
import json
import os
import random
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import asyncio
import edge_tts
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np


class ValidationVideoGenerator:
    """Generate validation videos for caregivers with calming visuals and audio."""
    
    def __init__(self, config_path: str = None):
        """Initialize the generator with configuration."""
        self.width = 1080
        self.height = 1920
        self.fps = 24  # Reduced for faster generation
        
        # Paths
        if config_path is None:
            script_dir = Path(__file__).parent
            config_path = script_dir.parent / "config" / "validation_messages.json"
        
        self.config_path = Path(config_path)
        self.messages = self._load_messages()
        
        # TTS settings
        self.tts_voice = "en-US-AriaNeural"  # Gentle female voice
        self.speech_rate = "+0%"
        
        # Colors and styling
        self.gradient_colors = [
            [(135, 206, 250), (221, 160, 221)],  # Sky blue to plum
            [(255, 182, 193), (221, 160, 221)],  # Light pink to plum
            [(175, 238, 238), (255, 182, 193)],  # Pale turquoise to light pink
            [(230, 230, 250), (255, 192, 203)],  # Lavender to pink
            [(240, 248, 255), (230, 230, 250)],  # Alice blue to lavender
            [(255, 240, 245), (221, 160, 221)],  # Lavender blush to plum
        ]
        
    def _load_messages(self) -> Dict:
        """Load validation messages from JSON config."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")
    
    def get_random_message(self, category: str = None) -> Dict:
        """Get a random message from the specified category or all categories."""
        if category and category in self.messages:
            messages = self.messages[category]
        else:
            # Get all messages from all categories
            messages = []
            for cat_messages in self.messages.values():
                messages.extend(cat_messages)
        
        if not messages:
            raise ValueError(f"No messages found in category: {category}")
        
        return random.choice(messages)
    
    def create_gradient_background(self, colors: Tuple[Tuple[int, int, int], Tuple[int, int, int]]) -> Image.Image:
        """Create a smooth gradient background."""
        # Create base gradient
        base = Image.new('RGB', (self.width, self.height))
        
        # Create gradient array
        color1, color2 = colors
        gradient = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        for y in range(self.height):
            ratio = y / self.height
            for c in range(3):
                gradient[y, :, c] = int(color1[c] * (1 - ratio) + color2[c] * ratio)
        
        # Convert to PIL Image
        gradient_img = Image.fromarray(gradient)
        
        # Add subtle texture/noise for warmth
        noise = Image.new('RGB', (self.width, self.height), (255, 255, 255))
        noise_pixels = []
        for _ in range(self.width * self.height):
            val = random.randint(240, 255)
            noise_pixels.append((val, val, val))
        noise.putdata(noise_pixels)
        
        # Blend gradient with subtle noise
        base = Image.blend(gradient_img, noise, 0.05)
        
        # Apply slight blur for softness
        base = base.filter(ImageFilter.GaussianBlur(radius=1))
        
        return base
    
    def get_font_for_text(self, text: str, max_width: int, max_height: int) -> Tuple[ImageFont.FreeTypeFont, int]:
        """Get the best font size for the given text constraints."""
        # Try to find system fonts (fallback to default if not found)
        font_paths = [
            "/System/Library/Fonts/Helvetica.ttc",  # macOS
            "/System/Library/Fonts/Geneva.ttf",     # macOS alternative
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",  # Linux
            "/Windows/Fonts/arial.ttf",             # Windows
        ]
        
        font_path = None
        for path in font_paths:
            if os.path.exists(path):
                font_path = path
                break
        
        # Start with a reasonable font size and adjust
        for font_size in range(60, 25, -5):
            try:
                if font_path:
                    font = ImageFont.truetype(font_path, font_size)
                else:
                    font = ImageFont.load_default()
                    break
                
                # Test if text fits
                dummy_img = Image.new('RGB', (max_width, max_height))
                dummy_draw = ImageDraw.Draw(dummy_img)
                
                # Wrap text
                lines = textwrap.wrap(text, width=30)  # Rough character estimate
                total_height = 0
                max_line_width = 0
                
                for line in lines:
                    bbox = dummy_draw.textbbox((0, 0), line, font=font)
                    line_width = bbox[2] - bbox[0]
                    line_height = bbox[3] - bbox[1]
                    total_height += line_height
                    max_line_width = max(max_line_width, line_width)
                
                if max_line_width <= max_width and total_height <= max_height:
                    return font, font_size
                    
            except (OSError, IOError):
                continue
        
        # Fallback to default font
        return ImageFont.load_default(), 30
    
    def add_text_to_image(self, image: Image.Image, text: str, y_position_ratio: float = 0.5) -> Image.Image:
        """Add text overlay to image with proper wrapping and positioning."""
        draw = ImageDraw.Draw(image)
        
        # Define text area (with padding)
        padding = 80
        text_width = self.width - (padding * 2)
        text_height = self.height // 3
        
        # Get appropriate font
        font, font_size = self.get_font_for_text(text, text_width, text_height)
        
        # Wrap text
        lines = []
        words = text.split()
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            line_width = bbox[2] - bbox[0]
            
            if line_width <= text_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # Calculate total text height
        line_height = font_size + 10  # Add some line spacing
        total_height = len(lines) * line_height
        
        # Position text vertically
        start_y = int((self.height * y_position_ratio) - (total_height / 2))
        
        # Add subtle shadow for better readability
        shadow_offset = 2
        shadow_color = (100, 100, 100, 180)  # Semi-transparent dark gray
        text_color = (40, 40, 40)  # Dark gray, not pure black for warmth
        
        for i, line in enumerate(lines):
            # Calculate line position
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            x = (self.width - line_width) // 2
            y = start_y + (i * line_height)
            
            # Draw shadow
            if hasattr(Image, 'LANCZOS'):
                # Create shadow on separate layer for better quality
                shadow_img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
                shadow_draw = ImageDraw.Draw(shadow_img)
                shadow_draw.text((x + shadow_offset, y + shadow_offset), line, 
                               font=font, fill=shadow_color)
                image = Image.alpha_composite(image.convert('RGBA'), shadow_img).convert('RGB')
                draw = ImageDraw.Draw(image)
            
            # Draw main text
            draw.text((x, y), line, font=font, fill=text_color)
        
        return image
    
    async def generate_tts_audio(self, text: str, output_path: str) -> float:
        """Generate TTS audio and return duration in seconds."""
        try:
            # Clean text for TTS (remove emojis and special characters that might cause issues)
            clean_text = ''.join(char for char in text if ord(char) < 0x1F600 or ord(char) > 0x1F64F)
            clean_text = clean_text.replace('💙', '').replace('🤗', '').replace('🌟', '').replace('💚', '').replace('✨', '')
            clean_text = clean_text.replace('🌈', '').replace('💪', '').replace('🤍', '').replace('🔋', '').replace('💤', '')
            clean_text = clean_text.replace('👁️', '').replace('🌊', '').replace('😴', '').replace('💫', '')
            clean_text = clean_text.strip()
            
            # Create TTS
            communicate = edge_tts.Communicate(clean_text, self.tts_voice, rate=self.speech_rate)
            await communicate.save(output_path)
            
            # Get audio duration using ffprobe
            try:
                result = subprocess.run([
                    'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                    '-of', 'csv=p=0', output_path
                ], capture_output=True, text=True, check=True)
                duration = float(result.stdout.strip())
                return duration
            except (subprocess.CalledProcessError, ValueError):
                # Fallback: estimate duration (rough approximation)
                words = len(clean_text.split())
                return max(8.0, words * 0.4)  # Minimum 8 seconds
                
        except Exception as e:
            raise RuntimeError(f"Failed to generate TTS audio: {e}")
    
    def create_video_frames(self, text: str, duration: float, temp_dir: str) -> List[str]:
        """Create video frames with text animation."""
        total_frames = int(duration * self.fps)
        frame_paths = []
        
        # Choose random gradient and create background once
        gradient_colors = random.choice(self.gradient_colors)
        base_bg = self.create_gradient_background(gradient_colors)
        
        # Animation phases
        fade_in_frames = min(24, total_frames // 4)  # 1 second or 1/4 of video
        stable_frames = max(24, total_frames - (fade_in_frames * 2))
        fade_out_frames = total_frames - fade_in_frames - stable_frames
        
        for frame_num in range(total_frames):
            # Show progress every 24 frames (every second)
            if frame_num % 24 == 0:
                print(f"  Generating frame {frame_num + 1}/{total_frames} ({(frame_num + 1) / total_frames * 100:.1f}%)")
                
            # Copy background (much faster than recreating)
            bg = base_bg.copy()
            
            # Determine animation state
            if frame_num < fade_in_frames:
                # Fade in
                alpha = frame_num / fade_in_frames
                text_alpha = int(255 * alpha)
            elif frame_num < fade_in_frames + stable_frames:
                # Stable
                text_alpha = 255
            else:
                # Fade out
                fade_progress = (frame_num - fade_in_frames - stable_frames) / fade_out_frames
                text_alpha = int(255 * (1 - fade_progress))
            
            # Add text with animation
            if text_alpha > 0:
                # Create text layer
                text_layer = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
                text_with_overlay = self.add_text_to_image(text_layer.convert('RGB'), text)
                text_layer = text_with_overlay.convert('RGBA')
                
                # Apply alpha
                if text_alpha < 255:
                    alpha_layer = Image.new('RGBA', (self.width, self.height), (255, 255, 255, text_alpha))
                    text_layer = Image.composite(text_layer, Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0)), alpha_layer)
                
                # Composite with background
                bg = bg.convert('RGBA')
                bg = Image.alpha_composite(bg, text_layer)
                bg = bg.convert('RGB')
            
            # Save frame
            frame_path = os.path.join(temp_dir, f"frame_{frame_num:06d}.png")
            bg.save(frame_path, "PNG")
            frame_paths.append(frame_path)
        
        return frame_paths
    
    def combine_audio_video(self, frame_pattern: str, audio_path: str, output_path: str, duration: float):
        """Combine frames and audio into final video using FFmpeg."""
        try:
            # FFmpeg command to create video
            cmd = [
                'ffmpeg', '-y',  # Overwrite output file
                '-framerate', str(self.fps),
                '-i', frame_pattern,
                '-i', audio_path,
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-pix_fmt', 'yuv420p',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-shortest',  # End when shortest input ends
                '-t', str(duration),  # Ensure exact duration
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"FFmpeg failed: {e.stderr}")
    
    async def generate_video(self, message_text: str = None, output_path: str = None, 
                           category: str = None) -> str:
        """Generate a complete validation video."""
        # Get message
        if message_text:
            message_data = {"text": message_text, "duration": 15}  # Default duration
        else:
            message_data = self.get_random_message(category)
        
        text = message_data["text"]
        target_duration = message_data.get("duration", 15)
        
        # Set up output path
        if not output_path:
            output_path = f"validation_video_{random.randint(1000, 9999)}.mp4"
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                print(f"Generating validation video...")
                print(f"Message: {text}")
                
                # Generate audio
                audio_path = os.path.join(temp_dir, "audio.wav")
                print("Generating TTS audio...")
                audio_duration = await self.generate_tts_audio(text, audio_path)
                
                # Use the longer of target duration or audio duration
                video_duration = max(target_duration, audio_duration + 1)  # Add 1 second buffer
                
                print(f"Creating {int(video_duration * self.fps)} video frames...")
                # Create video frames
                frame_paths = self.create_video_frames(text, video_duration, temp_dir)
                
                # Combine into video
                print("Combining audio and video...")
                frame_pattern = os.path.join(temp_dir, "frame_%06d.png")
                self.combine_audio_video(frame_pattern, audio_path, output_path, video_duration)
                
                print(f"✅ Video generated successfully: {output_path}")
                return output_path
                
            except Exception as e:
                raise RuntimeError(f"Failed to generate video: {e}")


async def main():
    """Main function to handle command line interface."""
    parser = argparse.ArgumentParser(description="Generate validation videos for caregivers")
    parser.add_argument("--message", type=str, help="Custom message to use")
    parser.add_argument("--output", type=str, help="Output video path")
    parser.add_argument("--category", type=str, 
                       choices=["permission_statements", "guilt_relief", "burnout_acknowledgment", "caregiver_identity"],
                       help="Category of validation message")
    parser.add_argument("--config", type=str, help="Path to validation messages config JSON")
    
    args = parser.parse_args()
    
    try:
        # Check dependencies
        required_commands = ['ffmpeg', 'ffprobe']
        for cmd in required_commands:
            try:
                subprocess.run([cmd, '-version'], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                print(f"❌ Required command '{cmd}' not found. Please install FFmpeg.")
                sys.exit(1)
        
        # Initialize generator
        generator = ValidationVideoGenerator(args.config)
        
        # Generate video
        output_path = await generator.generate_video(
            message_text=args.message,
            output_path=args.output,
            category=args.category
        )
        
        print(f"\n🎉 Validation video created: {output_path}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())