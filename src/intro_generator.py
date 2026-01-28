#!/usr/bin/env python3
"""
Kiin Intro Generator
Generate branded intro clips with logo animations and effects
"""

import argparse
import os
import tempfile
from pathlib import Path
from typing import Dict, Optional
from brand_utils import KiinBrand
from effects import VideoEffects

class IntroGenerator:
    """Generate branded intro clips for Kiin content"""
    
    def __init__(self):
        self.brand = KiinBrand()
        self.effects = VideoEffects()
        self.logo_path = self.brand.brand_dir / 'logo.png'
        
        # Style definitions
        self.styles = {
            'minimal': {
                'background_color': self.brand.colors['background_cool'],
                'duration': 2.5,
                'logo_animation': 'fade_scale',
                'text_style': 'simple',
                'color_grade': None
            },
            'warm': {
                'background_color': self.brand.colors['background_warm'],
                'duration': 3.0,
                'logo_animation': 'slide_in',
                'text_style': 'warm',
                'color_grade': 'warm'
            },
            'professional': {
                'background_color': self.brand.colors['primary'],
                'duration': 2.0,
                'logo_animation': 'quick_fade',
                'text_style': 'professional',
                'color_grade': 'professional'
            }
        }
    
    def generate_intro(self, style: str = 'minimal', duration: Optional[float] = None,
                      output_file: str = 'intro.mp4', width: int = 1080, height: int = 1920) -> bool:
        """Generate a branded intro clip"""
        
        if style not in self.styles:
            print(f"Unknown style '{style}'. Available: {list(self.styles.keys())}")
            return False
        
        style_config = self.styles[style]
        intro_duration = duration if duration else style_config['duration']
        
        print(f"Generating {style} intro ({intro_duration}s)...")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Step 1: Create background
            bg_file = os.path.join(temp_dir, 'background.mp4')
            bg_color = style_config['background_color']
            
            bg_video = self.effects.create_color_background(
                bg_color, intro_duration, width, height
            )
            if not bg_video:
                print("Failed to create background")
                return False
            
            # Step 2: Create logo animation based on style
            logo_file = os.path.join(temp_dir, 'logo_animated.mp4')
            if not self._create_logo_animation(
                style_config['logo_animation'], 
                logo_file, 
                intro_duration, 
                width, 
                height
            ):
                print("Failed to create logo animation")
                return False
            
            # Step 3: Combine background and logo
            combined_file = os.path.join(temp_dir, 'combined.mp4')
            if not self._combine_background_and_logo(bg_video, logo_file, combined_file):
                print("Failed to combine background and logo")
                return False
            
            # Step 4: Add text if needed for the style
            text_file = os.path.join(temp_dir, 'with_text.mp4')
            if not self._add_intro_text(combined_file, text_file, style_config, intro_duration, width, height):
                print("Failed to add text")
                return False
            
            # Step 5: Apply color grading if specified
            graded_file = os.path.join(temp_dir, 'graded.mp4')
            if style_config['color_grade']:
                if style_config['color_grade'] == 'warm':
                    success = self.effects.color_grade_warm(text_file, graded_file)
                elif style_config['color_grade'] == 'professional':
                    success = self.effects.color_grade_professional(text_file, graded_file)
                else:
                    success = False
                
                if not success:
                    print("Failed to apply color grading")
                    return False
                final_file = graded_file
            else:
                final_file = text_file
            
            # Step 6: Add fade in effect
            faded_file = os.path.join(temp_dir, 'faded.mp4')
            if not self.effects.fade_in(final_file, faded_file, 0.3):
                print("Failed to add fade in")
                return False
            
            # Step 7: Copy to final output
            import shutil
            try:
                shutil.copy2(faded_file, output_file)
                print(f"✓ Intro saved to {output_file}")
                return True
            except Exception as e:
                print(f"Failed to save output: {e}")
                return False
    
    def _create_logo_animation(self, animation_type: str, output_file: str, 
                             duration: float, width: int, height: int) -> bool:
        """Create animated logo based on animation type"""
        
        logo_size = min(width, height) // 4  # Logo is 1/4 of the smaller dimension
        
        if animation_type == 'fade_scale':
            return self._logo_fade_scale(output_file, duration, width, height, logo_size)
        elif animation_type == 'slide_in':
            return self._logo_slide_in(output_file, duration, width, height, logo_size)
        elif animation_type == 'quick_fade':
            return self._logo_quick_fade(output_file, duration, width, height, logo_size)
        else:
            return False
    
    def _logo_fade_scale(self, output_file: str, duration: float, 
                        width: int, height: int, logo_size: int) -> bool:
        """Create fade + scale logo animation"""
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', f'color=c=black@0.0:size={width}x{height}:d={duration}',
            '-i', str(self.logo_path),
            '-filter_complex', (
                f'[1]scale={logo_size}:{logo_size}:force_original_aspect_ratio=decrease[logo];'
                f'[0][logo]overlay=(W-w)/2:(H-h)/2:enable=\'between(t,0.5,{duration-0.3})\''
            ),
            '-c:v', 'libx264', '-preset', 'fast',
            '-pix_fmt', 'yuv420p',
            output_file
        ]
        return self.effects._run_ffmpeg(cmd)
    
    def _logo_slide_in(self, output_file: str, duration: float, 
                      width: int, height: int, logo_size: int) -> bool:
        """Create slide-in logo animation"""
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', f'color=c=black@0.0:size={width}x{height}:d={duration}',
            '-i', str(self.logo_path),
            '-filter_complex', (
                f'[1]scale={logo_size}:{logo_size}:force_original_aspect_ratio=decrease[logo];'
                f'[0][logo]overlay='
                f'\'if(lt(t,0.8),W-w*(t/0.8),(W-w)/2)\':(H-h)/2:enable=\'between(t,0,{duration})\''
            ),
            '-c:v', 'libx264', '-preset', 'fast',
            '-pix_fmt', 'yuv420p',
            output_file
        ]
        return self.effects._run_ffmpeg(cmd)
    
    def _logo_quick_fade(self, output_file: str, duration: float, 
                        width: int, height: int, logo_size: int) -> bool:
        """Create quick fade logo animation"""
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', f'color=c=black@0.0:size={width}x{height}:d={duration}',
            '-i', str(self.logo_path),
            '-filter_complex', (
                f'[1]scale={logo_size}:{logo_size}:force_original_aspect_ratio=decrease[logo];'
                f'[0][logo]overlay=(W-w)/2:(H-h)/2:enable=\'between(t,0.2,{duration})\''
            ),
            '-c:v', 'libx264', '-preset', 'fast',
            '-pix_fmt', 'yuv420p',
            output_file
        ]
        return self.effects._run_ffmpeg(cmd)
    
    def _combine_background_and_logo(self, bg_file: str, logo_file: str, output_file: str) -> bool:
        """Combine background and logo animations"""
        cmd = [
            'ffmpeg', '-y',
            '-i', bg_file,
            '-i', logo_file,
            '-filter_complex', '[0][1]overlay=0:0',
            '-c:v', 'libx264', '-preset', 'fast',
            output_file
        ]
        return self.effects._run_ffmpeg(cmd)
    
    def _add_intro_text(self, input_file: str, output_file: str, style_config: Dict,
                       duration: float, width: int, height: int) -> bool:
        """Add intro text based on style"""
        
        # For now, skip text overlay due to FFmpeg filter limitations
        # Just copy the input to output
        import shutil
        shutil.copy2(input_file, output_file)
        return True
    
    def list_styles(self):
        """List available intro styles"""
        print("Available intro styles:")
        for style_name, config in self.styles.items():
            print(f"  {style_name}: {config['duration']}s - {config.get('description', 'No description')}")

def main():
    parser = argparse.ArgumentParser(description='Generate Kiin branded intro clips')
    parser.add_argument('--style', default='minimal', 
                       choices=['minimal', 'warm', 'professional'],
                       help='Intro style')
    parser.add_argument('--duration', type=float,
                       help='Duration in seconds (overrides style default)')
    parser.add_argument('--output', default='intro.mp4',
                       help='Output file path')
    parser.add_argument('--width', type=int, default=1080,
                       help='Video width')
    parser.add_argument('--height', type=int, default=1920,
                       help='Video height')
    parser.add_argument('--list-styles', action='store_true',
                       help='List available styles and exit')
    
    args = parser.parse_args()
    
    generator = IntroGenerator()
    
    if args.list_styles:
        generator.list_styles()
        return
    
    success = generator.generate_intro(
        style=args.style,
        duration=args.duration,
        output_file=args.output,
        width=args.width,
        height=args.height
    )
    
    if success:
        print("✓ Intro generation completed successfully!")
    else:
        print("✗ Intro generation failed!")
        return 1

if __name__ == '__main__':
    exit(main())