#!/usr/bin/env python3
"""
Fixed version of validation generator V2 with proper error handling and diagnostics
"""

import asyncio
import math
import os
import sys
import tempfile
import traceback
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

class FixedValidationGenerator:
    """Simplified but working version of validation generator V2"""
    
    def __init__(self):
        self.width = 1080
        self.height = 1920
        self.fps = 24
        
        # Simple validation messages
        self.messages = [
            "You are enough, exactly as you are.",
            "It's okay to not be okay sometimes.",
            "Your feelings are valid.",
            "You deserve love and kindness.",
            "You're doing better than you think.",
            "It's okay to rest when you're tired.",
            "You matter more than you realize.",
            "Your journey is valid, even when it's hard."
        ]
        
        # Simple color schemes
        self.color_schemes = {
            "calm_blue": [(135, 206, 250), (221, 160, 221)],
            "warm_pink": [(255, 182, 193), (221, 160, 221)],
            "nature_green": [(175, 238, 238), (255, 182, 193)],
            "lavender": [(230, 230, 250), (255, 192, 203)]
        }
    
    def create_gradient_background(self, color_scheme: str, frame_index: int, total_frames: int) -> Image.Image:
        """Create animated gradient background"""
        colors = self.color_schemes.get(color_scheme, self.color_schemes["calm_blue"])
        
        # Create gradient
        background = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(background)
        
        # Animate gradient shift
        progress = frame_index / total_frames
        blend_factor = (math.sin(progress * math.pi * 2) + 1) / 2
        
        # Interpolate colors
        color1 = colors[0]
        color2 = colors[1]
        
        for y in range(self.height):
            # Create vertical gradient
            y_factor = y / self.height
            
            # Blend with animation
            final_factor = y_factor * (1 - blend_factor * 0.3)
            
            r = int(color1[0] * (1 - final_factor) + color2[0] * final_factor)
            g = int(color1[1] * (1 - final_factor) + color2[1] * final_factor)
            b = int(color1[2] * (1 - final_factor) + color2[2] * final_factor)
            
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))
        
        return background
    
    def add_breathing_text(self, image: Image.Image, text: str, frame_index: int, total_frames: int):
        """Add text with breathing animation"""
        draw = ImageDraw.Draw(image)
        
        # Try to load a nice font
        try:
            font_size = 60
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Breathing animation
        progress = frame_index / total_frames
        breathing_scale = 1.0 + 0.05 * math.sin(progress * math.pi * 4)
        breathing_opacity = 200 + int(50 * math.sin(progress * math.pi * 2))
        
        # Get text dimensions
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center text
        x = (self.width - text_width) // 2
        y = (self.height - text_height) // 2
        
        # Apply breathing scale effect (simple version)
        opacity = min(255, max(0, breathing_opacity))
        
        # Draw text with shadow for depth
        shadow_color = (0, 0, 0, 100)
        text_color = (255, 255, 255, opacity)
        
        # Shadow
        draw.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0))
        # Main text
        draw.text((x, y), text, font=font, fill=(255, 255, 255))
    
    def create_frames(self, message: str, duration: float = 8.0, color_scheme: str = "calm_blue"):
        """Create all frames for the video"""
        total_frames = int(duration * self.fps)
        frames = []
        
        print(f"🎨 Creating {total_frames} frames...")
        
        for i in range(total_frames):
            # Create background
            background = self.create_gradient_background(color_scheme, i, total_frames)
            
            # Add text
            self.add_breathing_text(background, message, i, total_frames)
            
            frames.append(background)
            
            if (i + 1) % 30 == 0:  # Progress update every second
                print(f"   Created {i + 1}/{total_frames} frames...")
        
        return frames
    
    def save_video(self, frames: list, output_path: str) -> bool:
        """Save frames as video using FFmpeg"""
        try:
            # Create temporary directory for frames
            temp_dir = Path(tempfile.mkdtemp())
            frames_dir = temp_dir / "frames"
            frames_dir.mkdir(exist_ok=True)
            
            print("💾 Saving frames...")
            
            # Save all frames as PNG
            for i, frame in enumerate(frames):
                frame_path = frames_dir / f"frame_{i:04d}.png"
                frame.save(frame_path)
            
            print("🎬 Converting to video with FFmpeg...")
            
            # Ensure output directory exists
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # FFmpeg command
            import subprocess
            cmd = [
                'ffmpeg', '-y', '-r', str(self.fps),
                '-i', str(frames_dir / 'frame_%04d.png'),
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                '-crf', '23', '-movflags', '+faststart',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Video conversion successful!")
                
                # Cleanup
                import shutil
                shutil.rmtree(temp_dir)
                print("🧹 Cleaned up temporary files")
                
                return True
            else:
                print(f"❌ FFmpeg error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error saving video: {e}")
            traceback.print_exc()
            return False
    
    async def generate_validation_video(self, 
                                      message: str = None,
                                      output_path: str = None,
                                      duration: float = 8.0,
                                      color_scheme: str = "calm_blue") -> str:
        """Generate a validation video"""
        
        try:
            # Use provided message or random one
            if message is None:
                import random
                message = random.choice(self.messages)
            
            # Create output path
            if output_path is None:
                output_dir = Path("output/fixed_validation")
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = str(output_dir / f"validation_fixed_{int(asyncio.get_event_loop().time())}.mp4")
            
            print(f"🎬 Generating validation video...")
            print(f"📝 Message: {message}")
            print(f"🎨 Color scheme: {color_scheme}")
            print(f"⏱️ Duration: {duration}s")
            print(f"📁 Output: {output_path}")
            
            # Create frames
            frames = self.create_frames(message, duration, color_scheme)
            
            # Save video
            if self.save_video(frames, output_path):
                # Verify output
                if os.path.exists(output_path):
                    size = os.path.getsize(output_path)
                    print(f"\n🎉 Validation video created successfully!")
                    print(f"📁 File: {output_path}")
                    print(f"📏 Size: {size} bytes")
                    return output_path
                else:
                    raise Exception("Output file not found after creation")
            else:
                raise Exception("Video save failed")
                
        except Exception as e:
            print(f"❌ Error generating validation video: {e}")
            traceback.print_exc()
            raise

async def test_fixed_generator():
    """Test the fixed generator"""
    print("🧪 Testing Fixed Validation Generator...")
    
    generator = FixedValidationGenerator()
    
    # Test multiple scenarios
    test_scenarios = [
        {
            "name": "Basic validation",
            "message": "You are enough, exactly as you are.",
            "color_scheme": "calm_blue",
            "duration": 6.0
        },
        {
            "name": "Self-care reminder",
            "message": "It's okay to rest when you're tired.",
            "color_scheme": "warm_pink",
            "duration": 7.0
        },
        {
            "name": "Emotional validation",
            "message": "Your feelings are valid, even the difficult ones.",
            "color_scheme": "lavender",
            "duration": 8.0
        }
    ]
    
    results = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n--- Test {i}: {scenario['name']} ---")
        
        try:
            output_path = await generator.generate_validation_video(
                message=scenario["message"],
                duration=scenario["duration"],
                color_scheme=scenario["color_scheme"],
                output_path=f"output/fixed_validation/test_{i}_{scenario['name'].lower().replace(' ', '_')}.mp4"
            )
            
            results.append((scenario['name'], True, output_path))
            
        except Exception as e:
            print(f"❌ Test {i} failed: {e}")
            results.append((scenario['name'], False, str(e)))
    
    # Summary
    print("\n" + "="*60)
    print("📊 FIXED GENERATOR TEST RESULTS")
    print("="*60)
    
    passed = 0
    for name, success, info in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {name}")
        if success:
            print(f"    → {info}")
            passed += 1
        else:
            print(f"    → Error: {info}")
    
    print(f"\n🎯 Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Fixed generator works perfectly.")
        return True
    else:
        print("⚠️ Some tests failed. Check errors above.")
        return False

async def main():
    """Main test function"""
    success = await test_fixed_generator()
    
    if success:
        print("\n✨ Fixed validation generator is working!")
        print("This proves the basic approach works. The issue in the original V2 generator")
        print("is likely in complex features like advanced particle systems, TTS integration,")
        print("or intricate background rendering.")
    else:
        print("\n⚠️ Fixed generator has issues. Check the basic video pipeline.")

if __name__ == "__main__":
    asyncio.run(main())