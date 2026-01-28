#!/usr/bin/env python3
"""
Kiin Brand Applicator - Add watermarks and branding to videos
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

def load_brand_config():
    """Load the brand configuration"""
    brand_dir = Path(__file__).parent.parent / 'brand'
    config_file = brand_dir / 'brand_config.json'
    
    if not config_file.exists():
        raise FileNotFoundError(f"Brand config not found at {config_file}")
    
    with open(config_file, 'r') as f:
        return json.load(f)

def check_ffmpeg():
    """Check if ffmpeg is available"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def apply_watermark(input_file, output_file, watermark_path, position='bottom-right', opacity=0.6, size_percent=5):
    """Apply watermark to video using ffmpeg"""
    
    # Calculate position filter based on position argument
    if position == 'bottom-right':
        overlay_filter = f"overlay=W-w-20:H-h-20"
    elif position == 'bottom-left':
        overlay_filter = f"overlay=20:H-h-20"
    elif position == 'top-right':
        overlay_filter = f"overlay=W-w-20:20"
    elif position == 'top-left':
        overlay_filter = f"overlay=20:20"
    else:
        overlay_filter = f"overlay=W-w-20:H-h-20"  # default to bottom-right
    
    # Build ffmpeg command
    cmd = [
        'ffmpeg',
        '-i', input_file,
        '-i', watermark_path,
        '-filter_complex', 
        f"[1:v]scale=iw*{size_percent/100}:ih*{size_percent/100},format=rgba,colorchannelmixer=aa={opacity}[watermark]; [0:v][watermark]{overlay_filter}",
        '-codec:a', 'copy',
        '-y',  # overwrite output file
        output_file
    ]
    
    print(f"Applying watermark to {input_file}...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✓ Watermark applied successfully: {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error applying watermark: {e}")
        print(f"FFmpeg output: {e.stderr}")
        return False

def create_intro_outro(brand_config, duration=3):
    """Create intro/outro video clips (placeholder implementation)"""
    print("Note: Intro/outro generation requires additional video assets.")
    print("For now, this is a placeholder. You can:")
    print("1. Create intro/outro video files manually")
    print("2. Use the brand colors and fonts as guidance")
    print("3. Place them in the brand/ directory as intro.mp4 and outro.mp4")
    
    return None

def add_intro_outro(input_file, output_file, brand_dir):
    """Add intro and outro to video (if available)"""
    intro_file = brand_dir / 'intro.mp4'
    outro_file = brand_dir / 'outro.mp4'
    
    has_intro = intro_file.exists()
    has_outro = outro_file.exists()
    
    if not has_intro and not has_outro:
        print("No intro.mp4 or outro.mp4 found in brand directory")
        return False
    
    # Build concat filter
    inputs = []
    filter_parts = []
    
    if has_intro:
        inputs.extend(['-i', str(intro_file)])
        filter_parts.append('[0:v][0:a]')
    
    inputs.extend(['-i', input_file])
    main_index = 1 if has_intro else 0
    filter_parts.append(f'[{main_index}:v][{main_index}:a]')
    
    if has_outro:
        outro_index = main_index + 1
        inputs.extend(['-i', str(outro_file)])
        filter_parts.append(f'[{outro_index}:v][{outro_index}:a]')
    
    concat_filter = ''.join(filter_parts) + f'concat=n={len(filter_parts)}:v=1:a=1[outv][outa]'
    
    cmd = [
        'ffmpeg',
        *inputs,
        '-filter_complex', concat_filter,
        '-map', '[outv]',
        '-map', '[outa]',
        '-y',
        output_file
    ]
    
    print(f"Adding intro/outro to {input_file}...")
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✓ Intro/outro added successfully: {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error adding intro/outro: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Apply Kiin branding to videos')
    parser.add_argument('--input', required=True, help='Input video file')
    parser.add_argument('--output', help='Output video file (default: input_branded.mp4)')
    parser.add_argument('--add-watermark', action='store_true', default=True, help='Add watermark (default: True)')
    parser.add_argument('--no-watermark', action='store_true', help='Skip watermark')
    parser.add_argument('--add-intro', action='store_true', help='Add intro video')
    parser.add_argument('--add-outro', action='store_true', help='Add outro video')
    parser.add_argument('--position', default='bottom-right', 
                      choices=['bottom-right', 'bottom-left', 'top-right', 'top-left'],
                      help='Watermark position')
    parser.add_argument('--opacity', type=float, default=0.6, help='Watermark opacity (0.0-1.0)')
    parser.add_argument('--size', type=int, default=5, help='Watermark size as % of video width')
    
    args = parser.parse_args()
    
    # Check if ffmpeg is available
    if not check_ffmpeg():
        print("✗ Error: ffmpeg not found. Please install ffmpeg first:")
        print("  brew install ffmpeg")
        return 1
    
    # Load brand configuration
    try:
        brand_config = load_brand_config()
    except FileNotFoundError as e:
        print(f"✗ Error: {e}")
        return 1
    
    # Determine output file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"✗ Error: Input file not found: {args.input}")
        return 1
    
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_stem(input_path.stem + '_branded')
    
    brand_dir = Path(__file__).parent.parent / 'brand'
    watermark_path = brand_dir / 'watermark.png'
    
    current_file = str(input_path)
    
    # Apply intro/outro first if requested
    if args.add_intro or args.add_outro:
        temp_file = str(input_path.with_stem(input_path.stem + '_temp'))
        if add_intro_outro(current_file, temp_file, brand_dir):
            current_file = temp_file
        else:
            print("Continuing without intro/outro...")
    
    # Apply watermark (unless explicitly disabled)
    if args.add_watermark and not args.no_watermark:
        if not watermark_path.exists():
            print(f"✗ Error: Watermark not found at {watermark_path}")
            return 1
        
        success = apply_watermark(
            current_file, 
            str(output_path),
            str(watermark_path),
            args.position,
            args.opacity,
            args.size
        )
        
        if not success:
            return 1
    else:
        # Just copy the file if no watermark
        import shutil
        shutil.copy2(current_file, output_path)
        print(f"✓ File copied without watermark: {output_path}")
    
    # Clean up temp file if created
    if current_file != str(input_path):
        try:
            os.remove(current_file)
        except OSError:
            pass
    
    print(f"\n✓ Branding applied successfully!")
    print(f"Input:  {args.input}")
    print(f"Output: {output_path}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())