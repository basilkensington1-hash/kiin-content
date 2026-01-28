#!/usr/bin/env python3
"""
Test simplified generators to identify working patterns
"""

import asyncio
import math
import os
import sys
import traceback
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_video_file(path: str) -> bool:
    """Check if video file exists and is valid"""
    if not os.path.exists(path):
        return False
    
    try:
        import subprocess
        result = subprocess.run([
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', path
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            import json
            data = json.loads(result.stdout)
            streams = data.get('streams', [])
            has_video = any(s.get('codec_type') == 'video' for s in streams)
            return has_video
        return False
    except Exception:
        return False

async def test_simplified_confession():
    """Test the simplified confession generator"""
    print("🧪 Testing Simplified Confession Generator...")
    
    try:
        from confession_generator_v2_simplified import ConfessionGeneratorV2Simplified
        generator = ConfessionGeneratorV2Simplified()
        print("✅ Simplified confession generator initialized")
        
        # Create output directory
        output_dir = Path("output/simplified_tests")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Test video generation
        output_path = str(output_dir / "confession_simplified_test.mp4")
        
        print("🎬 Generating confession video...")
        result_path = await generator.generate_confession_v2(
            output_name="confession_simplified_test.mp4"
        )
        
        if check_video_file(result_path):
            size = os.path.getsize(result_path)
            print(f"✅ Simplified confession video created successfully!")
            print(f"📁 File: {result_path}")
            print(f"📏 Size: {size} bytes")
            return True
        else:
            print("❌ Video file invalid or missing")
            return False
            
    except Exception as e:
        print(f"❌ Simplified confession test failed: {e}")
        traceback.print_exc()
        return False

def test_basic_validation_manual():
    """Test validation generator with manual approach"""
    print("\n🧪 Testing Manual Validation Generation...")
    
    try:
        # Let's try to manually create a basic validation video
        # to understand what's failing in the full generator
        
        from PIL import Image, ImageDraw, ImageFont
        import subprocess
        
        # Create output directory
        output_dir = Path("output/manual_tests")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create basic frames manually
        frames_dir = output_dir / "frames"
        frames_dir.mkdir(exist_ok=True)
        
        width, height = 1080, 1920
        frame_count = 120  # 5 seconds at 24fps
        
        print("🎨 Creating frames manually...")
        
        for i in range(frame_count):
            # Create frame
            frame = Image.new('RGB', (width, height), color=(40, 40, 60))
            draw = ImageDraw.Draw(frame)
            
            # Add simple text
            try:
                # Try to load a font
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 60)
            except:
                font = ImageFont.load_default()
            
            text = "You are enough, exactly as you are."
            
            # Get text bounding box
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Center text
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
            # Add simple breathing effect
            alpha = 200 + int(50 * math.sin(i * 0.1))
            color = (255, 255, 255, min(255, max(0, alpha)))
            
            draw.text((x, y), text, font=font, fill=(255, 255, 255))
            
            # Save frame
            frame.save(frames_dir / f"frame_{i:04d}.png")
        
        print(f"✅ Created {frame_count} frames")
        
        # Convert to video using FFmpeg
        output_video = str(output_dir / "manual_validation_test.mp4")
        
        print("🎬 Converting frames to video...")
        cmd = [
            'ffmpeg', '-y', '-r', '24',
            '-i', str(frames_dir / 'frame_%04d.png'),
            '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
            '-crf', '23', output_video
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and check_video_file(output_video):
            size = os.path.getsize(output_video)
            print(f"✅ Manual validation video created successfully!")
            print(f"📁 File: {output_video}")
            print(f"📏 Size: {size} bytes")
            
            # Cleanup frames
            import shutil
            shutil.rmtree(frames_dir)
            print("🧹 Cleaned up temporary frames")
            
            return True
        else:
            print("❌ FFmpeg conversion failed")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Manual validation test failed: {e}")
        traceback.print_exc()
        return False

async def main():
    """Run tests"""
    print("🚀 Testing simplified and manual approaches...\n")
    
    # Test simplified confession generator
    result1 = await test_simplified_confession()
    
    # Test manual validation creation
    result2 = test_basic_validation_manual()
    
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    
    status1 = "✅ PASS" if result1 else "❌ FAIL"
    status2 = "✅ PASS" if result2 else "❌ FAIL"
    
    print(f"{status1} Simplified Confession Generator")
    print(f"{status2} Manual Validation Creation")
    
    if result1 and result2:
        print("\n🎉 Both tests passed! Basic video generation works.")
        print("The issue is likely in the complex V2 logic.")
    elif result1:
        print("\n⚠️ Simplified generator works, but manual approach failed.")
        print("Check FFmpeg configuration.")
    elif result2:
        print("\n⚠️ Manual approach works, but simplified generator failed.")
        print("Check simplified generator dependencies.")
    else:
        print("\n❌ Both tests failed. Check basic video pipeline.")

if __name__ == "__main__":
    asyncio.run(main())