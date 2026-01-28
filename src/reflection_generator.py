#!/usr/bin/env python3
"""
Kiin Content Factory - Reflection Series Generator

Creates cinematic, nostalgic reflection content based on 2026 TikTok trends.
Focus on transformation stories, before/after caregiving, and emotional journeys.

Trend-aligned features:
- Cinematic storytelling
- Nostalgic/reflective tone
- Transformation narratives
- Therapeutic/calming aesthetic
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import random

# Optional imports with fallbacks
try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL not available. Install with: pip install Pillow")

try:
    import edge_tts
    import asyncio
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    print("Warning: edge-tts not available. Install with: pip install edge-tts")


class ReflectionGenerator:
    """Generate cinematic reflection content for caregivers."""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Cinematic color palettes for different moods
        self.color_palettes = {
            "nostalgic": {
                "background": "#2C1810",  # Deep warm brown
                "gradient_start": "#3D2317",
                "gradient_end": "#1A0F0A",
                "text": "#E8D5C4",  # Warm cream
                "accent": "#C4956A",  # Soft gold
                "highlight": "#E6B98F"
            },
            "transformative": {
                "background": "#0D1B2A",  # Deep navy
                "gradient_start": "#1B263B",
                "gradient_end": "#0D1B2A",
                "text": "#E0E1DD",  # Soft white
                "accent": "#778DA9",  # Steel blue
                "highlight": "#4CC9F0"  # Bright accent
            },
            "hopeful": {
                "background": "#1A1A2E",  # Deep purple-blue
                "gradient_start": "#16213E",
                "gradient_end": "#0F0F1A",
                "text": "#EAEAEA",
                "accent": "#E94560",  # Rose
                "highlight": "#F7B267"  # Warm gold
            },
            "peaceful": {
                "background": "#0B3D0B",  # Deep forest
                "gradient_start": "#1A4A1A",
                "gradient_end": "#0B3D0B",
                "text": "#E8F5E8",  # Soft mint
                "accent": "#7CB342",  # Sage
                "highlight": "#AED581"
            }
        }
        
        # Voice settings for reflective content (warm, intimate)
        self.voice_settings = {
            "narrator": "en-US-JennyNeural",  # Warm, reflective
            "intimate": "en-US-SaraNeural",  # Gentle, personal
            "storyteller": "en-US-AnaNeural",  # Cinematic feel
        }
        
        # Load reflection content
        self.reflections = self._load_reflections()
    
    def _load_reflections(self) -> List[Dict]:
        """Load reflection content from config."""
        config_path = Path(__file__).parent.parent / "config" / "confessions_nostalgia.json"
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                data = json.load(f)
                return data.get('confessions', [])
        
        # Fallback reflections if config not found
        return [
            {
                "id": 1,
                "category": "transformation",
                "emotional_weight": "medium",
                "hook": "I thought caregiving would break me",
                "confession": "Instead, it showed me parts of myself I never knew existed.",
                "validation": "You've discovered strength you didn't know you had.",
                "duration_target": 20,
                "emphasis_words": ["break", "showed", "never knew"]
            }
        ]
    
    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _create_gradient_background(self, size: tuple, palette: Dict) -> Image.Image:
        """Create a cinematic gradient background."""
        if not PIL_AVAILABLE:
            raise ImportError("PIL required for image generation")
        
        width, height = size
        img = Image.new('RGB', (width, height))
        
        start_color = self._hex_to_rgb(palette['gradient_start'])
        end_color = self._hex_to_rgb(palette['gradient_end'])
        
        for y in range(height):
            ratio = y / height
            r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
            g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
            b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
            
            for x in range(width):
                img.putpixel((x, y), (r, g, b))
        
        return img
    
    def _add_film_grain(self, img: Image.Image, intensity: float = 0.03) -> Image.Image:
        """Add subtle film grain for cinematic effect."""
        if not PIL_AVAILABLE:
            return img
        
        import random
        pixels = img.load()
        width, height = img.size
        
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                noise = random.randint(-int(255 * intensity), int(255 * intensity))
                r = max(0, min(255, r + noise))
                g = max(0, min(255, g + noise))
                b = max(0, min(255, b + noise))
                pixels[x, y] = (r, g, b)
        
        return img
    
    def _add_vignette(self, img: Image.Image, intensity: float = 0.4) -> Image.Image:
        """Add cinematic vignette effect."""
        if not PIL_AVAILABLE:
            return img
        
        width, height = img.size
        pixels = img.load()
        center_x, center_y = width // 2, height // 2
        max_dist = ((width/2)**2 + (height/2)**2) ** 0.5
        
        for y in range(height):
            for x in range(width):
                dist = ((x - center_x)**2 + (y - center_y)**2) ** 0.5
                factor = 1 - (dist / max_dist * intensity)
                factor = max(0.3, factor)  # Don't go too dark
                
                r, g, b = pixels[x, y]
                pixels[x, y] = (int(r * factor), int(g * factor), int(b * factor))
        
        return img
    
    def _load_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        """Load a font with fallbacks."""
        font_paths = [
            "/System/Library/Fonts/Supplemental/Georgia.ttf",  # Elegant serif
            "/System/Library/Fonts/NewYork.ttf",
            "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        ]
        
        for path in font_paths:
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, size)
                except:
                    continue
        
        return ImageFont.load_default()
    
    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        """Wrap text to fit within max_width."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            try:
                bbox = font.getbbox(test_line)
                width = bbox[2] - bbox[0]
            except:
                width = len(test_line) * (font.size * 0.6)
            
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def generate_reflection_frame(
        self,
        reflection: Dict,
        frame_type: str = "hook",
        palette_name: str = "nostalgic"
    ) -> Image.Image:
        """Generate a single frame for reflection content."""
        
        if not PIL_AVAILABLE:
            raise ImportError("PIL required")
        
        width, height = 1080, 1920
        palette = self.color_palettes.get(palette_name, self.color_palettes["nostalgic"])
        
        # Create cinematic background
        img = self._create_gradient_background((width, height), palette)
        
        # Add film grain for cinematic feel
        img = self._add_film_grain(img, intensity=0.02)
        
        # Add vignette
        img = self._add_vignette(img, intensity=0.3)
        
        draw = ImageDraw.Draw(img)
        
        # Fonts
        hook_font = self._load_font(72)
        body_font = self._load_font(56)
        validation_font = self._load_font(48)
        
        # Determine content based on frame type
        if frame_type == "hook":
            text = reflection['hook']
            font = hook_font
            y_position = height // 2 - 200
        elif frame_type == "confession":
            text = reflection['confession']
            font = body_font
            y_position = height // 2 - 100
        elif frame_type == "validation":
            text = reflection['validation']
            font = validation_font
            y_position = height // 2
        else:
            text = reflection['hook']
            font = hook_font
            y_position = height // 2 - 200
        
        # Wrap text
        lines = self._wrap_text(text, font, width - 160)
        
        # Calculate total text height
        line_height = font.size + 20
        total_height = len(lines) * line_height
        
        # Center vertically
        start_y = y_position - total_height // 2
        
        # Draw text with shadow for depth
        text_color = self._hex_to_rgb(palette['text'])
        shadow_color = (0, 0, 0)
        
        for i, line in enumerate(lines):
            y = start_y + i * line_height
            
            # Get text width for centering
            try:
                bbox = font.getbbox(line)
                text_width = bbox[2] - bbox[0]
            except:
                text_width = len(line) * (font.size * 0.6)
            
            x = (width - text_width) // 2
            
            # Shadow
            draw.text((x + 3, y + 3), line, fill=shadow_color, font=font)
            # Main text
            draw.text((x, y), line, fill=text_color, font=font)
        
        # Add accent line
        accent_color = self._hex_to_rgb(palette['accent'])
        line_width = 200
        line_y = start_y - 60
        draw.line(
            [(width//2 - line_width//2, line_y), (width//2 + line_width//2, line_y)],
            fill=accent_color,
            width=3
        )
        
        # Add category label
        category = reflection.get('category', 'reflection').upper()
        cat_font = self._load_font(28)
        draw.text((width//2, 200), category, fill=accent_color, font=cat_font, anchor="mm")
        
        # Add Kiin branding
        brand_font = self._load_font(32)
        draw.text((width//2, height - 150), "KIIN", fill=accent_color, font=brand_font, anchor="mm")
        
        return img
    
    async def generate_audio(self, text: str, output_path: str, voice: str = None) -> bool:
        """Generate TTS audio for the reflection."""
        if not EDGE_TTS_AVAILABLE:
            print("Warning: edge-tts not available, skipping audio")
            return False
        
        voice = voice or self.voice_settings['narrator']
        
        try:
            communicate = edge_tts.Communicate(text, voice, rate="-10%", pitch="-5Hz")
            await communicate.save(output_path)
            return True
        except Exception as e:
            print(f"TTS Error: {e}")
            return False
    
    def generate_reflection_video(
        self,
        reflection_id: int = None,
        palette: str = "nostalgic"
    ) -> Optional[str]:
        """Generate complete reflection video."""
        
        # Select reflection
        if reflection_id:
            reflection = next(
                (r for r in self.reflections if r['id'] == reflection_id),
                self.reflections[0] if self.reflections else None
            )
        else:
            reflection = random.choice(self.reflections) if self.reflections else None
        
        if not reflection:
            print("No reflection content available")
            return None
        
        print(f"Generating reflection: {reflection['hook'][:50]}...")
        
        # Create temp directory
        temp_dir = self.output_dir / "temp_reflection"
        temp_dir.mkdir(exist_ok=True)
        
        # Generate frames
        frames = []
        frame_types = ["hook", "confession", "validation"]
        
        for i, frame_type in enumerate(frame_types):
            if PIL_AVAILABLE:
                frame = self.generate_reflection_frame(reflection, frame_type, palette)
                frame_path = temp_dir / f"frame_{i:03d}.png"
                frame.save(frame_path)
                frames.append(frame_path)
        
        if not frames:
            print("Could not generate frames")
            return None
        
        # Generate audio
        full_text = f"{reflection['hook']}... {reflection['confession']}... {reflection['validation']}"
        audio_path = temp_dir / "narration.mp3"
        
        if EDGE_TTS_AVAILABLE:
            asyncio.run(self.generate_audio(full_text, str(audio_path)))
        
        # Create video with FFmpeg
        output_filename = f"reflection_{reflection['category']}_{reflection['id']}.mp4"
        output_path = self.output_dir / output_filename
        
        # Calculate duration per frame
        target_duration = reflection.get('duration_target', 20)
        frame_duration = target_duration / len(frames)
        
        # FFmpeg command
        if audio_path.exists():
            cmd = [
                'ffmpeg', '-y',
                '-framerate', f'1/{frame_duration}',
                '-i', str(temp_dir / 'frame_%03d.png'),
                '-i', str(audio_path),
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-pix_fmt', 'yuv420p',
                '-shortest',
                str(output_path)
            ]
        else:
            # Silent video
            cmd = [
                'ffmpeg', '-y',
                '-framerate', f'1/{frame_duration}',
                '-i', str(temp_dir / 'frame_%03d.png'),
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-pix_fmt', 'yuv420p',
                '-t', str(target_duration),
                str(output_path)
            ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Created: {output_path}")
            
            # Cleanup
            for f in temp_dir.iterdir():
                f.unlink()
            temp_dir.rmdir()
            
            return str(output_path)
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg error: {e}")
            return None


def main():
    """Demo the reflection generator."""
    generator = ReflectionGenerator(output_dir="output")
    
    # Generate a few reflection videos
    palettes = ["nostalgic", "transformative", "hopeful", "peaceful"]
    
    for i, palette in enumerate(palettes[:2]):  # Generate 2 for demo
        print(f"\n--- Generating reflection video {i+1} ({palette}) ---")
        result = generator.generate_reflection_video(palette=palette)
        if result:
            print(f"Success: {result}")
        else:
            print("Failed to generate video")


if __name__ == "__main__":
    main()
