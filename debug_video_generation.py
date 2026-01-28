#!/usr/bin/env python3
"""
Debug video generation step by step
"""

import asyncio
import os
import sys
import traceback
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_video_generation():
    """Test video generation step by step"""
    
    print("🔍 Testing validation generator video creation...")
    
    try:
        from validation_generator_v2 import EnhancedValidationGenerator
        
        generator = EnhancedValidationGenerator()
        print("✅ Generator initialized")
        
        # Create output directory
        output_dir = Path("output/debug_tests")
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Output directory created: {output_dir}")
        
        # Test message retrieval first
        print("🔍 Testing message retrieval...")
        try:
            message = generator.get_random_message("guilt_relief")
            print(f"✅ Message retrieved: {message['text'][:50]}...")
        except Exception as e:
            print(f"❌ Message retrieval failed: {e}")
            # Try with a custom message instead
            message = {"text": "You are enough, exactly as you are.", "voice": "en-US-JennyNeural"}
            print("✅ Using custom message instead")
        
        # Check if TTS is available 
        print("🔍 Testing TTS functionality...")
        try:
            # Try basic edge-tts functionality
            import edge_tts
            voices = await edge_tts.list_voices()
            print(f"✅ TTS available, found {len(voices)} voices")
        except Exception as e:
            print(f"❌ TTS test failed: {e}")
            # Continue without TTS for debugging
        
        # Test basic video frame creation
        print("🔍 Testing frame creation...")
        try:
            # Create a test frame
            from PIL import Image, ImageDraw
            test_frame = Image.new('RGB', (1080, 1920), color=(50, 50, 50))
            draw = ImageDraw.Draw(test_frame)
            draw.text((50, 50), "Test Frame", fill=(255, 255, 255))
            
            test_frame_path = output_dir / "test_frame.png"
            test_frame.save(test_frame_path)
            print(f"✅ Basic frame creation successful: {test_frame_path}")
        except Exception as e:
            print(f"❌ Frame creation failed: {e}")
            traceback.print_exc()
            return False
        
        # Test video generation with minimal settings
        print("🔍 Attempting minimal video generation...")
        try:
            output_path = str(output_dir / "validation_minimal_test.mp4")
            
            # Use a very simple approach - disable complex features for debugging
            result = await generator.generate_validation_video(
                message_text="Test message for debugging",
                output_path=output_path,
                style="brand_professional",
                with_music=False  # Disable music
            )
            
            if os.path.exists(result):
                size = os.path.getsize(result)
                print(f"✅ Video generated successfully!")
                print(f"📁 File: {result}")
                print(f"📏 Size: {size} bytes")
                return True
            else:
                print("❌ Video file not found after generation")
                return False
                
        except Exception as e:
            print(f"❌ Video generation failed: {e}")
            print(f"📋 Full traceback:")
            traceback.print_exc()
            
            # Try to check what went wrong
            print("\n🔍 Checking potential issues...")
            
            # Check FFmpeg
            try:
                import subprocess
                result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ FFmpeg is available")
                else:
                    print("❌ FFmpeg not working properly")
            except Exception:
                print("❌ FFmpeg not found")
            
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print(f"📋 Full traceback:")
        traceback.print_exc()
        return False

async def main():
    success = await test_video_generation()
    if success:
        print("\n🎉 Video generation test passed!")
    else:
        print("\n⚠️ Video generation test failed!")

if __name__ == "__main__":
    asyncio.run(main())