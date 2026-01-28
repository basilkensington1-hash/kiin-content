#!/usr/bin/env python3
"""
Debug individual modules to find hang source
"""

import os
import sys
import traceback

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_voice_manager():
    """Test VoiceManager initialization"""
    print("🔍 Testing VoiceManager...")
    try:
        from voice_manager import VoiceManager
        print("✅ VoiceManager import successful")
        
        vm = VoiceManager()
        print("✅ VoiceManager initialization successful")
        return True
    except Exception as e:
        print(f"❌ VoiceManager failed: {e}")
        traceback.print_exc()
        return False

def test_music_mixer():
    """Test MusicMixer initialization"""
    print("🔍 Testing MusicMixer...")
    try:
        from music_mixer import MusicMixer
        print("✅ MusicMixer import successful")
        
        mm = MusicMixer()
        print("✅ MusicMixer initialization successful")
        return True
    except Exception as e:
        print(f"❌ MusicMixer failed: {e}")
        traceback.print_exc()
        return False

def test_brand_utils():
    """Test KiinBrand initialization"""
    print("🔍 Testing KiinBrand...")
    try:
        from brand_utils import KiinBrand
        print("✅ KiinBrand import successful")
        
        brand = KiinBrand()
        print("✅ KiinBrand initialization successful")
        return True
    except Exception as e:
        print(f"❌ KiinBrand failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Test all modules"""
    print("🚀 Testing individual modules...\n")
    
    results = []
    
    # Test each module
    results.append(("VoiceManager", test_voice_manager()))
    print()
    
    results.append(("MusicMixer", test_music_mixer()))
    print()
    
    results.append(("KiinBrand", test_brand_utils()))
    print()
    
    # Summary
    print("=" * 50)
    print("📊 MODULE TEST RESULTS")
    print("=" * 50)
    
    for module, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {module}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All modules initialized successfully!")
        print("The hang might be in the video generation logic itself.")
    else:
        print("\n⚠️ Some modules failed to initialize!")
        print("This explains the hang in the main generator.")

if __name__ == "__main__":
    main()