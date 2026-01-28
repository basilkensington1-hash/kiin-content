#!/usr/bin/env python3
"""
Test script to verify Kiin brand kit is working correctly
"""

import json
import sys
from pathlib import Path

def test_brand_assets():
    """Test that all brand assets are present and valid"""
    
    brand_dir = Path(__file__).parent
    src_dir = brand_dir.parent / 'src'
    
    tests = []
    
    # Test 1: Brand config exists and is valid JSON
    try:
        config_file = brand_dir / 'brand_config.json'
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        required_keys = ['name', 'tagline', 'colors', 'fonts', 'voice']
        missing_keys = [key for key in required_keys if key not in config]
        
        if missing_keys:
            tests.append(f"❌ Brand config missing keys: {missing_keys}")
        else:
            tests.append(f"✅ Brand config valid with all required keys")
            tests.append(f"   Brand: {config['name']} - {config['tagline']}")
    
    except Exception as e:
        tests.append(f"❌ Brand config error: {e}")
    
    # Test 2: Colors file exists and is valid
    try:
        colors_file = brand_dir / 'colors.json'
        with open(colors_file, 'r') as f:
            colors = json.load(f)
        
        if 'hex_values' in colors and len(colors['hex_values']) >= 7:
            tests.append(f"✅ Colors file valid with {len(colors['hex_values'])} colors")
            tests.append(f"   Primary: {colors['hex_values'].get('primary', 'N/A')}")
        else:
            tests.append("❌ Colors file missing hex_values or insufficient colors")
    
    except Exception as e:
        tests.append(f"❌ Colors file error: {e}")
    
    # Test 3: Fonts file exists
    try:
        fonts_file = brand_dir / 'fonts.json'
        with open(fonts_file, 'r') as f:
            fonts = json.load(f)
        
        if 'font_stack' in fonts:
            font_count = len(fonts['font_stack'])
            tests.append(f"✅ Fonts file valid with {font_count} font definitions")
        else:
            tests.append("❌ Fonts file missing font_stack")
    
    except Exception as e:
        tests.append(f"❌ Fonts file error: {e}")
    
    # Test 4: Logo assets exist
    logo_file = brand_dir / 'logo.png'
    watermark_file = brand_dir / 'watermark.png'
    
    if logo_file.exists():
        tests.append(f"✅ Logo file exists ({logo_file.stat().st_size} bytes)")
    else:
        tests.append("❌ Logo file missing")
    
    if watermark_file.exists():
        tests.append(f"✅ Watermark file exists ({watermark_file.stat().st_size} bytes)")
    else:
        tests.append("❌ Watermark file missing")
    
    # Test 5: Brand utilities module
    try:
        sys.path.insert(0, str(src_dir))
        import brand_utils
        
        brand = brand_utils.KiinBrand()
        colors = brand.colors
        voice_config = brand.get_voice_config()
        
        tests.append("✅ Brand utilities module imports successfully")
        tests.append(f"   Primary color: {colors.get('primary', 'N/A')}")
        tests.append(f"   TTS voice: {voice_config.get('tts_voice', 'N/A')}")
    
    except Exception as e:
        tests.append(f"❌ Brand utilities error: {e}")
    
    # Test 6: Branding script exists
    branding_script = src_dir / 'apply_branding.py'
    if branding_script.exists() and branding_script.stat().st_mode & 0o111:
        tests.append(f"✅ Branding script exists and is executable")
    elif branding_script.exists():
        tests.append(f"⚠️  Branding script exists but may not be executable")
    else:
        tests.append("❌ Branding script missing")
    
    # Test 7: Documentation exists
    guidelines = brand_dir / 'BRAND_GUIDELINES.md'
    integration = brand_dir / 'INTEGRATION_GUIDE.md'
    
    if guidelines.exists():
        tests.append(f"✅ Brand guidelines documentation exists")
    else:
        tests.append("❌ Brand guidelines missing")
    
    if integration.exists():
        tests.append(f"✅ Integration guide exists")
    else:
        tests.append("❌ Integration guide missing")
    
    return tests

def main():
    print("🎨 Kiin Brand Kit Test")
    print("=" * 50)
    
    tests = test_brand_assets()
    
    for test in tests:
        print(test)
    
    # Summary
    passed = len([t for t in tests if t.startswith('✅')])
    warnings = len([t for t in tests if t.startswith('⚠️')])
    failed = len([t for t in tests if t.startswith('❌')])
    
    print("\n" + "=" * 50)
    print(f"Test Summary: {passed} passed, {warnings} warnings, {failed} failed")
    
    if failed == 0:
        print("🎉 Brand kit is ready to use!")
        print("\nQuick start:")
        print("1. python src/brand_utils.py  # Demo brand utilities")
        print("2. python src/apply_branding.py --help  # Video branding help")
        print("3. Read brand/BRAND_GUIDELINES.md for usage guidelines")
    else:
        print("❌ Some tests failed. Check the errors above.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)