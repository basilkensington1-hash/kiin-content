#!/usr/bin/env python3
"""Simple video generation test"""

import sys
import asyncio
import tempfile
import os
sys.path.append('/Users/nick/clawd/kiin-content/src')

from validation_generator_v2 import EnhancedValidationGenerator

async def test_simple_generation():
    """Test simple video generation"""
    try:
        print("Creating generator...")
        generator = EnhancedValidationGenerator()
        print("✅ Generator created")
        
        print("Getting message...")
        message = generator.get_random_message("permission_statements")
        print(f"✅ Message: {message['text'][:50]}...")
        
        print("Testing audio generation...")
        with tempfile.TemporaryDirectory() as temp_dir:
            audio_path = os.path.join(temp_dir, "test_audio.wav")
            try:
                duration = await generator.generate_enhanced_audio(message, audio_path)
                print(f"✅ Audio generated: {duration:.1f} seconds")
            except Exception as e:
                print(f"❌ Audio failed: {e}")
                return False
            
            print("Testing frame generation...")
            try:
                frames = generator.create_enhanced_frames(
                    message, 5.0, temp_dir, "gradient_calm"
                )
                print(f"✅ Generated {len(frames)} frames")
                return True
            except Exception as e:
                print(f"❌ Frame generation failed: {e}")
                import traceback
                traceback.print_exc()
                return False
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_simple_generation())
    print("✅ Test completed!" if success else "❌ Test failed!")