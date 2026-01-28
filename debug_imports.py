#!/usr/bin/env python3
"""
Debug imports step by step to find hanging issues
"""

import os
import sys
import traceback

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test imports step by step"""
    
    print("🔍 Testing basic Python imports...")
    try:
        import json
        import math
        import random
        import subprocess
        import tempfile
        import textwrap
        from datetime import datetime
        from pathlib import Path
        from typing import Dict, List, Tuple, Optional, Any
        print("✅ Basic Python imports successful")
    except Exception as e:
        print(f"❌ Basic Python imports failed: {e}")
        return False
    
    print("🔍 Testing asyncio...")
    try:
        import asyncio
        print("✅ asyncio import successful")
    except Exception as e:
        print(f"❌ asyncio import failed: {e}")
        return False
    
    print("🔍 Testing edge_tts...")
    try:
        import edge_tts
        print("✅ edge_tts import successful")
    except Exception as e:
        print(f"❌ edge_tts import failed: {e}")
        return False
    
    print("🔍 Testing PIL...")
    try:
        from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
        print("✅ PIL imports successful")
    except Exception as e:
        print(f"❌ PIL imports failed: {e}")
        return False
    
    print("🔍 Testing numpy...")
    try:
        import numpy as np
        print("✅ numpy import successful")
    except Exception as e:
        print(f"❌ numpy import failed: {e}")
        return False
    
    print("🔍 Testing voice_manager...")
    try:
        from voice_manager import VoiceManager
        print("✅ voice_manager import successful")
    except Exception as e:
        print(f"❌ voice_manager import failed: {e}")
        traceback.print_exc()
        return False
    
    print("🔍 Testing music_mixer...")
    try:
        from music_mixer import MusicMixer
        print("✅ music_mixer import successful")
    except Exception as e:
        print(f"❌ music_mixer import failed: {e}")
        traceback.print_exc()
        return False
    
    print("🔍 Testing brand_utils...")
    try:
        from brand_utils import KiinBrand
        print("✅ brand_utils import successful")
    except Exception as e:
        print(f"❌ brand_utils import failed: {e}")
        traceback.print_exc()
        return False
    
    print("🔍 Testing validation_generator_v2...")
    try:
        from validation_generator_v2 import EnhancedValidationGenerator
        print("✅ validation_generator_v2 import successful")
    except Exception as e:
        print(f"❌ validation_generator_v2 import failed: {e}")
        traceback.print_exc()
        return False
    
    print("🔍 Testing generator instantiation...")
    try:
        generator = EnhancedValidationGenerator()
        print("✅ Generator instantiation successful")
        return True
    except Exception as e:
        print(f"❌ Generator instantiation failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting import debug...")
    success = test_imports()
    if success:
        print("\n🎉 All imports successful!")
    else:
        print("\n⚠️ Import issues found!")