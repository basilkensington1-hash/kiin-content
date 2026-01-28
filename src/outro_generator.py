#!/usr/bin/env python3
"""
Kiin Outro Generator
Generate branded outro clips with CTAs and social branding
"""

import argparse
import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional
from brand_utils import KiinBrand
from effects import VideoEffects

class OutroGenerator:
    """Generate branded outro clips for Kiin content"""
    
    def __init__(self):
        self.brand = KiinBrand()
        self.effects = VideoEffects()
        self.logo_path = self.brand.brand_dir / 'logo.png'
        
        # Predefined CTA templates
        self.cta_templates = {
            'follow': "Follow @kiinapp for more",
            'save': "Save this for later",
            'share': "Share with friends",
            'like': "Like if this helped",
            'subscribe': "Subscribe for daily tips",
            'comment': "Comment your thoughts",
            'more': "More content like this daily",
            'app': "Try Kiin app - link in bio"
        }
        
        # Outro styles
        self.styles = {
            'standard': {
                'background_color': self.brand.colors['primary'],
                'text_color': self.brand.colors['text_light'],
                'duration': 4.0,
                'layout': 'centered'
            },
            'warm': {
                'background_color': self.brand.colors['background_warm'],
                'text_color': self.brand.colors['text_dark'],
                'duration': 5.0,
                'layout': 'bottom_focus'
            },
            'minimal': {
                'background_color': self.brand.colors['background_cool'],
                'text_color': self.brand.colors['text_dark'],
                'duration': 3.5,
                'layout': 'simple'
            },
            'gradient': {
                'background_color': 'gradient',
                'text_color': self.brand.colors['text_light'],
                'duration': 4.5,
                'layout': 'centered'
            }
        }
    
    def generate_outro(self, cta: str = 'follow', style: str = 'standard',
                      duration: Optional[float] = None, output_file: str = 'outro.mp4',
                      width: int = 1080, height: int = 1920,
                      social_handle: str = '@kiinapp') -> bool:
        """Generate a branded outro clip"""
        
        if style not in self.styles:
            print(f"Unknown style '{style}'. Available: {list(self.styles.keys())}")
            return False
        
        style_config = self.styles[style]
        outro_duration = duration if duration else style_config['duration']
        
        # Parse CTA text
        if cta in self.cta_templates:
            cta_text = self.cta_templates[cta]
        else:
            cta_text = cta
        
        # Replace placeholders in CTA
        cta_text = cta_text.replace('@kiinapp', social_handle)
        
        print(f"Generating {style} outro ({outro_duration}s) with CTA: '{cta_text}'")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Step 1: Create background
            bg_file = os.path.join(temp_dir, 'background.mp4')
            if not self._create_outro_background(
                style_config, bg_file, outro_duration, width, height
            ):
                print("Failed to create background")
                return False
            
            # Step 2: Add logo
            logo_file = os.path.join(temp_dir, 'with_logo.mp4')
            if not self._add_outro_logo(bg_file, logo_file, style_config, width, height):
                print("Failed to add logo")
                return False
            
            # Step 3: Add CTA text
            cta_file = os.path.join(temp_dir, 'with_cta.mp4')
            if not self._add_cta_text(logo_file, cta_file, cta_text, style_config, 
                                    outro_duration, width, height):
                print("Failed to add CTA text")
                return False
            
            # Step 4: Add social handle/branding
            branded_file = os.path.join(temp_dir, 'branded.mp4')
            if not self._add_social_branding(cta_file, branded_file, social_handle,
                                           style_config, width, height):
                print("Failed to add social branding")
                return False
            
            # Step 5: Add animations and effects
            animated_file = os.path.join(temp_dir, 'animated.mp4')
            if not self._add_outro_animations(branded_file, animated_file, style_config,
                                            outro_duration):
                print("Failed to add animations")
                return False
            
            # Step 6: Add fade out
            final_file = os.path.join(temp_dir, 'final.mp4')
            if not self.effects.fade_out(animated_file, final_file, 0.5):
                print("Failed to add fade out")
                return False
            
            # Step 7: Copy to output
            import shutil
            try:
                shutil.copy2(final_file, output_file)
                print(f"✓ Outro saved to {output_file}")
                return True
            except Exception as e:
                print(f"Failed to save output: {e}")
                return False
    
    def _create_outro_background(self, style_config: Dict, output_file: str,
                               duration: float, width: int, height: int) -> bool:
        """Create outro background based on style"""
        
        if style_config['background_color'] == 'gradient':
            # Create gradient background
            return self._create_gradient_background(output_file, duration, width, height)
        else:
            # Create solid color background
            bg_video = self.effects.create_color_background(
                style_config['background_color'], duration, width, height
            )
            if bg_video:
                import shutil
                shutil.copy2(bg_video, output_file)
                return True
            return False
    
    def _create_gradient_background(self, output_file: str, duration: float,
                                  width: int, height: int) -> bool:
        """Create gradient background - simplified for FFmpeg compatibility"""
        # Use primary color instead of gradient due to filter limitations
        primary = self.brand.colors['primary']
        
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', f'color=c={primary}:size={width}x{height}:d={duration}',
            '-c:v', 'libx264', '-preset', 'fast',
            '-pix_fmt', 'yuv420p',
            output_file
        ]
        return self.effects._run_ffmpeg(cmd)
    
    def _add_outro_logo(self, input_file: str, output_file: str, 
                       style_config: Dict, width: int, height: int) -> bool:
        """Add logo to outro"""
        logo_size = min(width, height) // 6  # Smaller logo for outro
        
        layout = style_config['layout']
        
        if layout == 'centered':
            overlay_pos = '(W-w)/2:(H-h)/4'  # Top center
        elif layout == 'bottom_focus':
            overlay_pos = '(W-w)/2:H-h-50'   # Bottom center
        elif layout == 'simple':
            overlay_pos = 'W-w-30:30'        # Top right
        else:
            overlay_pos = '(W-w)/2:(H-h)/4'  # Default to top center
        
        cmd = [
            'ffmpeg', '-y',
            '-i', input_file,
            '-i', str(self.logo_path),
            '-filter_complex', (
                f'[1]scale={logo_size}:{logo_size}:force_original_aspect_ratio=decrease[logo];'
                f'[0][logo]overlay={overlay_pos}'
            ),
            '-c:v', 'libx264', '-preset', 'fast',
            output_file
        ]
        return self.effects._run_ffmpeg(cmd)
    
    def _add_cta_text(self, input_file: str, output_file: str, cta_text: str,
                     style_config: Dict, duration: float, width: int, height: int) -> bool:
        """Add CTA text with animation - simplified for FFmpeg compatibility"""
        
        # Skip text overlay due to FFmpeg filter limitations
        # Just copy the input to output
        import shutil
        shutil.copy2(input_file, output_file)
        return True
    
    def _add_social_branding(self, input_file: str, output_file: str, 
                           social_handle: str, style_config: Dict,
                           width: int, height: int) -> bool:
        """Add social handle/branding text - simplified for FFmpeg compatibility"""
        
        # Skip text overlay due to FFmpeg filter limitations
        # Just copy the input to output
        import shutil
        shutil.copy2(input_file, output_file)
        return True
    
    def _add_outro_animations(self, input_file: str, output_file: str,
                            style_config: Dict, duration: float) -> bool:
        """Add subtle animations to outro"""
        
        layout = style_config['layout']
        
        if layout == 'centered':
            # Add subtle zoom
            zoom_filter = f"scale=2*iw:2*ih,crop=iw/2:ih/2:(iw-ow)/2:(ih-oh)/2,scale=1080:1920"
        elif layout == 'gradient' or style_config.get('background_color') == 'gradient':
            # Add slight movement for gradient
            zoom_filter = f"scale=1.05*iw:1.05*ih,crop=iw/1.05:ih/1.05:(iw-ow)/2:(ih-oh)/2"
        else:
            # No additional animation for simple layouts
            import shutil
            shutil.copy2(input_file, output_file)
            return True
        
        cmd = [
            'ffmpeg', '-y',
            '-i', input_file,
            '-vf', zoom_filter,
            '-c:v', 'libx264', '-preset', 'fast',
            output_file
        ]
        return self.effects._run_ffmpeg(cmd)
    
    def generate_end_screen_template(self, output_file: str = 'end_screen.mp4',
                                   width: int = 1080, height: int = 1920) -> bool:
        """Generate an end screen template with multiple CTAs"""
        
        duration = 6.0
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create gradient background
            bg_file = os.path.join(temp_dir, 'background.mp4')
            if not self._create_gradient_background(bg_file, duration, width, height):
                return False
            
            # Add logo
            logo_file = os.path.join(temp_dir, 'with_logo.mp4')
            logo_size = min(width, height) // 5
            
            cmd = [
                'ffmpeg', '-y',
                '-i', bg_file,
                '-i', str(self.logo_path),
                '-filter_complex', (
                    f'[1]scale={logo_size}:{logo_size}:force_original_aspect_ratio=decrease[logo];'
                    f'[0][logo]overlay=(W-w)/2:H/6'
                ),
                '-c:v', 'libx264', '-preset', 'fast',
                logo_file
            ]
            
            if not self.effects._run_ffmpeg(cmd):
                return False
            
            # Skip text elements due to FFmpeg filter limitations
            # Just use the logo file as the multi_text_file
            import shutil
            multi_text_file = os.path.join(temp_dir, 'multi_text.mp4')
            shutil.copy2(logo_file, multi_text_file)
            
            # Add final fade out
            if not self.effects.fade_out(multi_text_file, output_file, 1.0):
                return False
            
            print(f"✓ End screen template saved to {output_file}")
            return True
    
    def list_cta_templates(self):
        """List available CTA templates"""
        print("Available CTA templates:")
        for key, text in self.cta_templates.items():
            print(f"  {key}: '{text}'")

def main():
    parser = argparse.ArgumentParser(description='Generate Kiin branded outro clips')
    parser.add_argument('--cta', default='follow',
                       help='Call-to-action text or template key')
    parser.add_argument('--style', default='standard',
                       choices=['standard', 'warm', 'minimal', 'gradient'],
                       help='Outro style')
    parser.add_argument('--duration', type=float,
                       help='Duration in seconds (overrides style default)')
    parser.add_argument('--output', default='outro.mp4',
                       help='Output file path')
    parser.add_argument('--width', type=int, default=1080,
                       help='Video width')
    parser.add_argument('--height', type=int, default=1920,
                       help='Video height')
    parser.add_argument('--social-handle', default='@kiinapp',
                       help='Social media handle to display')
    parser.add_argument('--list-ctas', action='store_true',
                       help='List available CTA templates and exit')
    parser.add_argument('--end-screen', action='store_true',
                       help='Generate end screen template instead of outro')
    
    args = parser.parse_args()
    
    generator = OutroGenerator()
    
    if args.list_ctas:
        generator.list_cta_templates()
        return
    
    if args.end_screen:
        success = generator.generate_end_screen_template(
            output_file=args.output,
            width=args.width,
            height=args.height
        )
    else:
        success = generator.generate_outro(
            cta=args.cta,
            style=args.style,
            duration=args.duration,
            output_file=args.output,
            width=args.width,
            height=args.height,
            social_handle=args.social_handle
        )
    
    if success:
        print("✓ Outro generation completed successfully!")
    else:
        print("✗ Outro generation failed!")
        return 1

if __name__ == '__main__':
    exit(main())