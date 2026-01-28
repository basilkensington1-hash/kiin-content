#!/usr/bin/env python3
"""Simple debug test for validation generator v2"""

import sys
import os
sys.path.append('/Users/nick/clawd/kiin-content/src')

try:
    print("Testing imports...")
    from voice_manager import VoiceManager
    print("✅ VoiceManager imported")
    
    from music_mixer import MusicMixer
    print("✅ MusicMixer imported")
    
    from brand_utils import KiinBrand
    print("✅ KiinBrand imported")
    
    from validation_generator_v2 import EnhancedValidationGenerator
    print("✅ EnhancedValidationGenerator imported")
    
    print("\nCreating generator...")
    generator = EnhancedValidationGenerator()
    print("✅ Generator created successfully")
    
    print(f"\nTotal messages: {generator._count_total_messages(generator.messages)}")
    
    print("\nGetting random message...")
    message = generator.get_random_message("permission_statements")
    print(f"✅ Got message: {message['text'][:50]}...")
    
    print("\nBasic setup complete!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()