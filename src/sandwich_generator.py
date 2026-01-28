#!/usr/bin/env python3
"""
Sandwich Generation Diaries - POV Content Generator
Creates relatable POV-style videos for the sandwich generation audience.
"""

import json
import os
import random
import asyncio
import subprocess
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import edge_tts
import uuid
from typing import Dict, List, Tuple

class SandwichGenerator:
    def __init__(self, config_dir: str = None, output_dir: str = None):
        """Initialize the generator with config and output directories."""
        self.script_dir = Path(__file__).parent
        self.project_dir = self.script_dir.parent
        
        self.config_dir = Path(config_dir) if config_dir else self.project_dir / "config"
        self.output_dir = Path(output_dir) if output_dir else self.project_dir / "output"
        self.temp_dir = Path(tempfile.mkdtemp(prefix="sandwich_gen_"))
        
        # Video settings
        self.video_width = 1080
        self.video_height = 1920
        self.fps = 30
        
        # Timing settings (in seconds)
        self.hook_duration = 5
        self.chaos_duration = 20
        self.punchline_duration = 10
        self.total_duration = self.hook_duration + self.chaos_duration + self.punchline_duration
        
        # Visual settings
        self.background_colors = [
            "#1a1a2e",  # Dark blue-purple
            "#16213e",  # Navy
            "#0f3460",  # Dark blue
            "#533483",  # Purple
            "#2d1b69",  # Deep purple
        ]
        
        # TTS settings
        self.voice = "en-US-AriaNeural"  # Warm, relatable female voice
        self.speech_rate = "+10%"
        
        # Load scenarios
        self.scenarios = self._load_scenarios()
    
    def _load_scenarios(self) -> List[Dict]:
        """Load scenarios from JSON file."""
        scenarios_file = self.config_dir / "sandwich_scenarios.json"
        with open(scenarios_file, 'r') as f:
            data = json.load(f)
        return data['scenarios']
    
    def _get_font(self, size: int) -> ImageFont.FreeTypeFont:
        """Get font for text rendering, with fallbacks."""
        font_paths = [
            "/System/Library/Fonts/Helvetica.ttc",  # macOS
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",  # Linux
            "arial.ttf",  # Windows
        ]
        
        for font_path in font_paths:
            try:
                return ImageFont.truetype(font_path, size)
            except (OSError, IOError):
                continue
        
        # Fallback to default font
        return ImageFont.load_default()
    
    async def _generate_tts(self, text: str, output_path: str) -> float:
        """Generate TTS audio and return duration in seconds."""
        print(f"Generating TTS for: {text[:50]}...")
        
        # Clean text for TTS
        clean_text = text.replace("POV:", "").replace("—", " - ").strip()
        
        communicate = edge_tts.Communicate(clean_text, self.voice, rate=self.speech_rate)
        await communicate.save(output_path)
        
        # Get duration using ffprobe
        cmd = [
            "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
            "-of", "csv=p=0", str(output_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        duration = float(result.stdout.strip()) if result.stdout.strip() else 2.0
        
        return duration
    
    def _create_text_image(self, text: str, width: int, height: int, 
                          bg_color: str, text_color: str = "white", 
                          font_size: int = 60, is_timestamp: bool = False) -> Image.Image:
        """Create an image with text overlay."""
        img = Image.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(img)
        
        # Adjust font size for timestamps
        if is_timestamp:
            font_size = 45
            text_color = "#ffd700"  # Gold for timestamps
        
        font = self._get_font(font_size)
        
        # Handle multi-line text
        max_width = width - 120  # Padding
        lines = []
        words = text.split()
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Calculate total text height
        line_height = font_size + 20
        total_text_height = len(lines) * line_height
        start_y = (height - total_text_height) // 2
        
        # Draw each line
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2]
            x = (width - text_width) // 2
            y = start_y + (i * line_height)
            
            # Add subtle shadow for readability
            draw.text((x + 2, y + 2), line, fill="black", font=font)
            draw.text((x, y), line, fill=text_color, font=font)
        
        return img
    
    def _create_video_segment(self, images: List[str], audio_path: str, 
                            output_path: str, duration: float) -> None:
        """Create a video segment from images and audio."""
        print(f"Creating video segment: {output_path}")
        
        # Create video from images
        if len(images) == 1:
            # Single image - just display for duration
            cmd = [
                "ffmpeg", "-y", "-loop", "1", "-i", images[0],
                "-t", str(duration), "-pix_fmt", "yuv420p",
                "-vf", f"scale={self.video_width}:{self.video_height}",
                str(self.temp_dir / "temp_video.mp4")
            ]
        else:
            # Multiple images - create slideshow
            segment_duration = duration / len(images)
            inputs = []
            filter_complex = []
            
            for i, img in enumerate(images):
                inputs.extend(["-loop", "1", "-t", str(segment_duration), "-i", img])
                filter_complex.append(f"[{i}:v]scale={self.video_width}:{self.video_height}[v{i}];")
            
            # Concatenate videos
            filter_complex.append("".join([f"[v{i}]" for i in range(len(images))]) + 
                                f"concat=n={len(images)}:v=1[outv]")
            
            cmd = ["ffmpeg", "-y"] + inputs + [
                "-filter_complex", "".join(filter_complex),
                "-map", "[outv]", "-pix_fmt", "yuv420p",
                str(self.temp_dir / "temp_video.mp4")
            ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        
        # Add audio
        cmd = [
            "ffmpeg", "-y",
            "-i", str(self.temp_dir / "temp_video.mp4"),
            "-i", audio_path,
            "-c:v", "copy", "-c:a", "aac",
            "-shortest",
            output_path
        ]
        subprocess.run(cmd, check=True, capture_output=True)
    
    async def generate_video(self, scenario_index: int = None, output_filename: str = None) -> str:
        """Generate a complete POV video from a scenario."""
        # Select scenario
        if scenario_index is None:
            scenario = random.choice(self.scenarios)
            scenario_index = self.scenarios.index(scenario)
        else:
            scenario = self.scenarios[scenario_index]
        
        print(f"Generating video for scenario {scenario_index}: {scenario['hook'][:50]}...")
        
        # Create output filename
        if not output_filename:
            output_filename = f"sandwich_pov_{scenario_index}_{uuid.uuid4().hex[:8]}.mp4"
        
        output_path = self.output_dir / output_filename
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Choose background color
        bg_color = random.choice(self.background_colors)
        
        # Generate TTS for each segment
        hook_audio = self.temp_dir / "hook.wav"
        punchline_audio = self.temp_dir / "punchline.wav"
        
        await self._generate_tts(scenario['hook'], str(hook_audio))
        await self._generate_tts(scenario['punchline'], str(punchline_audio))
        
        # Create images for hook
        hook_img = self._create_text_image(
            scenario['hook'], self.video_width, self.video_height, bg_color
        )
        hook_img_path = self.temp_dir / "hook.png"
        hook_img.save(hook_img_path)
        
        # Create images for chaos montage
        chaos_images = []
        for i, moment in enumerate(scenario['chaos_moments']):
            # Alternate between timestamp and regular text styling
            is_timestamp = any(time_indicator in moment for time_indicator in ['am', 'pm', ':'])
            
            img = self._create_text_image(
                moment, self.video_width, self.video_height, bg_color,
                is_timestamp=is_timestamp
            )
            img_path = self.temp_dir / f"chaos_{i}.png"
            img.save(img_path)
            chaos_images.append(str(img_path))
        
        # Create punchline image
        punchline_img = self._create_text_image(
            scenario['punchline'], self.video_width, self.video_height, bg_color,
            text_color="#ff6b6b", font_size=65  # Slightly larger, pink text for punchline
        )
        punchline_img_path = self.temp_dir / "punchline.png"
        punchline_img.save(punchline_img_path)
        
        # Create video segments
        hook_video = self.temp_dir / "hook_segment.mp4"
        chaos_video = self.temp_dir / "chaos_segment.mp4"
        punchline_video = self.temp_dir / "punchline_segment.mp4"
        
        # Hook segment
        self._create_video_segment([str(hook_img_path)], str(hook_audio), 
                                 str(hook_video), self.hook_duration)
        
        # Chaos montage (quick cuts)
        # Create silent audio for chaos segment
        chaos_audio = self.temp_dir / "chaos_silent.wav"
        cmd = [
            "ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo",
            "-t", str(self.chaos_duration), str(chaos_audio)
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        
        self._create_video_segment(chaos_images, str(chaos_audio), 
                                 str(chaos_video), self.chaos_duration)
        
        # Punchline segment
        self._create_video_segment([str(punchline_img_path)], str(punchline_audio),
                                 str(punchline_video), self.punchline_duration)
        
        # Concatenate all segments
        concat_file = self.temp_dir / "concat.txt"
        with open(concat_file, 'w') as f:
            f.write(f"file '{hook_video}'\n")
            f.write(f"file '{chaos_video}'\n")
            f.write(f"file '{punchline_video}'\n")
        
        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
            "-c", "copy", str(output_path)
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        
        print(f"Video generated successfully: {output_path}")
        return str(output_path)
    
    def cleanup(self):
        """Clean up temporary files."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

async def main():
    """Main function to generate example video."""
    print("🥪 Sandwich Generation Diaries - Content Generator")
    print("=" * 50)
    
    generator = SandwichGenerator()
    
    try:
        # Generate example video
        output_path = await generator.generate_video(
            scenario_index=0,  # Use first scenario
            output_filename="sandwich_example.mp4"
        )
        
        print(f"\n✅ Example video generated: {output_path}")
        print(f"📐 Dimensions: {generator.video_width}x{generator.video_height} (9:16)")
        print(f"⏱️  Duration: ~{generator.total_duration} seconds")
        print(f"🎭 Voice: {generator.voice}")
        
    except Exception as e:
        print(f"❌ Error generating video: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        generator.cleanup()

if __name__ == "__main__":
    asyncio.run(main())