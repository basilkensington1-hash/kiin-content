#!/usr/bin/env python3
"""
Kiin Video Effects Library
Reusable video effects using FFmpeg
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from brand_utils import KiinBrand

class VideoEffects:
    """Reusable video effects using FFmpeg"""
    
    def __init__(self):
        self.brand = KiinBrand()
        self.temp_dir = tempfile.mkdtemp()
    
    def fade_in(self, input_file: str, output_file: str, duration: float = 0.5) -> bool:
        """Apply fade in effect"""
        cmd = [
            'ffmpeg', '-y',
            '-i', input_file,
            '-vf', f'fade=t=in:st=0:d={duration}',
            '-af', f'afade=t=in:st=0:d={duration}',
            '-c:v', 'libx264', '-preset', 'fast',
            output_file
        ]
        return self._run_ffmpeg(cmd)
    
    def fade_out(self, input_file: str, output_file: str, duration: float = 0.5, 
                 start_time: Optional[float] = None) -> bool:
        """Apply fade out effect"""
        if start_time is None:
            # Get video duration to calculate fade start
            video_info = self.get_video_info(input_file)
            start_time = float(video_info['duration']) - duration
        
        cmd = [
            'ffmpeg', '-y',
            '-i', input_file,
            '-vf', f'fade=t=out:st={start_time}:d={duration}',
            '-af', f'afade=t=out:st={start_time}:d={duration}',
            '-c:v', 'libx264', '-preset', 'fast',
            output_file
        ]
        return self._run_ffmpeg(cmd)
    
    def ken_burns_effect(self, input_file: str, output_file: str, 
                        zoom_start: float = 1.0, zoom_end: float = 1.1,
                        duration: Optional[float] = None) -> bool:
        """Apply Ken Burns effect (subtle zoom/pan)"""
        video_info = self.get_video_info(input_file)
        if duration is None:
            duration = float(video_info['duration'])
        
        # Create subtle zoom with slight pan
        scale_filter = (
            f"scale=2*iw:2*ih,"
            f"crop=iw/2:ih/2:"
            f"'(iw-ow)/2+((iw-ow)/2)*sin(t*2*PI/{duration})':"
            f"'(ih-oh)/2+((ih-oh)/2)*cos(t*2*PI/{duration})'"
        )
        
        cmd = [
            'ffmpeg', '-y',
            '-i', input_file,
            '-vf', scale_filter,
            '-c:v', 'libx264', '-preset', 'fast',
            '-t', str(duration),
            output_file
        ]
        return self._run_ffmpeg(cmd)
    
    def text_typewriter(self, text: str, duration: float, font_size: int = 48,
                       font_color: str = 'white', background: str = 'transparent',
                       width: int = 1080, height: int = 1920) -> str:
        """Create typewriter text animation - simplified for FFmpeg compatibility"""
        # Return empty string as drawtext filter not available
        print("Text effects not available - drawtext filter missing from FFmpeg build")
        return ""
    
    def text_fade_in(self, text: str, duration: float, font_size: int = 48,
                    font_color: str = 'white', width: int = 1080, height: int = 1920) -> str:
        """Create fade-in text animation - simplified for FFmpeg compatibility"""
        # Return empty string as drawtext filter not available
        print("Text effects not available - drawtext filter missing from FFmpeg build")
        return ""
    
    def color_grade_warm(self, input_file: str, output_file: str) -> bool:
        """Apply warm color grading preset"""
        # Simplified warm color grading using only basic eq filter
        color_filter = "eq=brightness=0.05:saturation=1.2:gamma=0.95"
        
        cmd = [
            'ffmpeg', '-y',
            '-i', input_file,
            '-vf', color_filter,
            '-c:v', 'libx264', '-preset', 'fast',
            output_file
        ]
        return self._run_ffmpeg(cmd)
    
    def color_grade_cool(self, input_file: str, output_file: str) -> bool:
        """Apply cool color grading preset"""
        # Simplified cool color grading using only basic eq filter
        color_filter = "eq=brightness=-0.02:saturation=1.1:contrast=1.05:gamma=1.05"
        
        cmd = [
            'ffmpeg', '-y',
            '-i', input_file,
            '-vf', color_filter,
            '-c:v', 'libx264', '-preset', 'fast',
            output_file
        ]
        return self._run_ffmpeg(cmd)
    
    def color_grade_professional(self, input_file: str, output_file: str) -> bool:
        """Apply professional color grading preset"""
        # Professional look with basic eq filter only
        color_filter = "eq=brightness=0.02:saturation=0.95:contrast=1.1:gamma=0.95"
        
        cmd = [
            'ffmpeg', '-y',
            '-i', input_file,
            '-vf', color_filter,
            '-c:v', 'libx264', '-preset', 'fast',
            output_file
        ]
        return self._run_ffmpeg(cmd)
    
    def add_watermark(self, input_file: str, output_file: str, 
                     watermark_path: Optional[str] = None, 
                     position: str = 'bottom_right', opacity: float = 0.7) -> bool:
        """Add watermark to video"""
        if watermark_path is None:
            watermark_path = self.brand.brand_dir / 'watermark.png'
        
        # Position mapping
        positions = {
            'top_left': '10:10',
            'top_right': 'W-w-10:10',
            'bottom_left': '10:H-h-10',
            'bottom_right': 'W-w-10:H-h-10',
            'center': '(W-w)/2:(H-h)/2'
        }
        
        overlay_pos = positions.get(position, positions['bottom_right'])
        
        cmd = [
            'ffmpeg', '-y',
            '-i', input_file,
            '-i', str(watermark_path),
            '-filter_complex', f'[1][0]scale2ref=oh*mdar:ih/8[logo][video];[video][logo]overlay={overlay_pos}:format=auto,format=yuv420p',
            '-c:v', 'libx264', '-preset', 'fast',
            output_file
        ]
        return self._run_ffmpeg(cmd)
    
    def create_color_background(self, color: str, duration: float, 
                              width: int = 1080, height: int = 1920) -> str:
        """Create solid color background video"""
        output_file = os.path.join(self.temp_dir, f'bg_{color.replace("#", "")}_{duration}.mp4')
        
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', f'color=c={color}:size={width}x{height}:d={duration}',
            '-c:v', 'libx264', '-preset', 'fast',
            '-pix_fmt', 'yuv420p',
            output_file
        ]
        
        if self._run_ffmpeg(cmd):
            return output_file
        return ""
    
    def get_video_info(self, video_file: str) -> Dict[str, str]:
        """Get video information using ffprobe"""
        cmd = [
            'ffprobe', '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            video_file
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            import json
            info = json.loads(result.stdout)
            
            # Extract useful information
            format_info = info.get('format', {})
            video_stream = next((s for s in info.get('streams', []) if s.get('codec_type') == 'video'), {})
            
            return {
                'duration': format_info.get('duration', '0'),
                'width': video_stream.get('width', 0),
                'height': video_stream.get('height', 0),
                'fps': video_stream.get('r_frame_rate', '30/1'),
                'codec': video_stream.get('codec_name', 'unknown')
            }
        except subprocess.CalledProcessError:
            return {'duration': '0', 'width': 0, 'height': 0, 'fps': '30/1', 'codec': 'unknown'}
    
    def _run_ffmpeg(self, cmd: List[str]) -> bool:
        """Run ffmpeg command and return success status"""
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg error: {e.stderr.decode()}")
            return False
    
    def cleanup(self):
        """Clean up temporary files"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)