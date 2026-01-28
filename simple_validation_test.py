#!/usr/bin/env python3
"""
Simple test for validation generator V2 to debug issues
"""

import asyncio
import os
import sys
import traceback
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_validation_basic():
    """Test basic validation generator functionality"""
    print("🧪 Testing Validation Generator V2 - Basic Import and Instantiation...")
    
    try:
        from validation_generator_v2 import EnhancedValidationGenerator
        print("✅ Import successful")
        
        generator = EnhancedValidationGenerator()
        print("✅ Generator instantiated")
        
        # Test basic message generation
        try:
            message = generator.get_random_message("guilt_relief")
            print(f"✅ Random message generated: {message['text'][:50]}...")
        except Exception as e:
            print(f"❌ Error getting random message: {e}")
        
        # Try to generate a simple video
        output_dir = Path("output/debug_tests")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(output_dir / "validation_debug_test.mp4")
        
        print(f"🎬 Attempting to generate video: {output_path}")
        
        try:
            result = await generator.generate_validation_video(
                message_text="You are enough, exactly as you are.",
                output_path=output_path,
                style="brand_professional",
                with_music=False  # Disable music to avoid TTS issues
            )
            
            if os.path.exists(result):
                print(f"✅ Video generated successfully: {result}")
                # Check file size
                size = os.path.getsize(result)
                print(f"📁 File size: {size} bytes")
                return True
            else:
                print("❌ Video file not found")
                return False
                
        except Exception as e:
            print(f"❌ Error generating video: {e}")
            print(f"📋 Full traceback:")
            traceback.print_exc()
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print(f"📋 Full traceback:")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print(f"📋 Full traceback:")
        traceback.print_exc()
        return False

async def main():
    success = await test_validation_basic()
    if success:
        print("\n🎉 Basic validation test passed!")
    else:
        print("\n⚠️ Basic validation test failed!")

if __name__ == "__main__":
    asyncio.run(main())