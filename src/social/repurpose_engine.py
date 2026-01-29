"""
Repurpose Engine - Adapt content for different social media platforms.
"""

import json
import os
import subprocess
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np

logger = logging.getLogger(__name__)

class RepurposeEngine:
    """Repurpose and adapt content for different social media platforms"""
    
    def __init__(self, config_path: str = "config/platform_specs.json"):
        self.config_path = config_path
        self.specs = self._load_platform_specs()
        self.temp_dir = Path("temp/repurpose")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Platform-specific video specifications
        self.video_specs = {
            'instagram': {
                'aspect_ratios': ['9:16', '1:1', '4:5'],  # Stories, Feed, Reels
                'max_duration': 90,  # seconds
                'min_duration': 3,
                'resolution': {
                    '9:16': (1080, 1920),  # Reels/Stories
                    '1:1': (1080, 1080),   # Square posts
                    '4:5': (1080, 1350)    # Portrait posts
                },
                'bitrate': '3500k',
                'fps': 30,
                'formats': ['mp4'],
                'watermark_position': 'bottom_right',
                'watermark_opacity': 0.7
            },
            'tiktok': {
                'aspect_ratios': ['9:16'],
                'max_duration': 60,
                'min_duration': 15,
                'resolution': {
                    '9:16': (1080, 1920)
                },
                'bitrate': '4000k',
                'fps': 30,
                'formats': ['mp4'],
                'watermark_position': 'bottom_right',
                'watermark_opacity': 0.6
            },
            'youtube': {
                'aspect_ratios': ['9:16', '16:9'],
                'max_duration': 60,  # Shorts
                'min_duration': 15,
                'resolution': {
                    '9:16': (1080, 1920),  # Shorts
                    '16:9': (1920, 1080)   # Regular videos
                },
                'bitrate': '5000k',
                'fps': 30,
                'formats': ['mp4'],
                'watermark_position': 'bottom_left',
                'watermark_opacity': 0.8
            },
            'twitter': {
                'aspect_ratios': ['16:9', '1:1', '9:16'],
                'max_duration': 140,
                'min_duration': 0.5,
                'resolution': {
                    '16:9': (1280, 720),
                    '1:1': (720, 720),
                    '9:16': (720, 1280)
                },
                'bitrate': '2500k',
                'fps': 30,
                'formats': ['mp4'],
                'watermark_position': 'bottom_right',
                'watermark_opacity': 0.5
            },
            'linkedin': {
                'aspect_ratios': ['16:9', '1:1'],
                'max_duration': 600,  # 10 minutes
                'min_duration': 3,
                'resolution': {
                    '16:9': (1920, 1080),
                    '1:1': (1080, 1080)
                },
                'bitrate': '4000k',
                'fps': 30,
                'formats': ['mp4'],
                'watermark_position': 'bottom_right',
                'watermark_opacity': 0.9
            },
            'pinterest': {
                'aspect_ratios': ['2:3', '1:1', '9:16'],
                'max_duration': 60,
                'min_duration': 4,
                'resolution': {
                    '2:3': (1000, 1500),  # Pin aspect ratio
                    '1:1': (1000, 1000),
                    '9:16': (1080, 1920)
                },
                'bitrate': '3000k',
                'fps': 25,
                'formats': ['mp4'],
                'watermark_position': 'bottom_center',
                'watermark_opacity': 0.8
            },
            'facebook': {
                'aspect_ratios': ['9:16', '1:1', '16:9'],
                'max_duration': 90,  # Reels
                'min_duration': 3,
                'resolution': {
                    '9:16': (1080, 1920),  # Reels
                    '1:1': (1080, 1080),   # Square
                    '16:9': (1920, 1080)   # Landscape
                },
                'bitrate': '4000k',
                'fps': 30,
                'formats': ['mp4'],
                'watermark_position': 'bottom_right',
                'watermark_opacity': 0.7
            }
        }
        
        # Brand elements for watermarking
        self.brand_config = {
            'logo_path': 'brand/logo.png',
            'brand_colors': {
                'primary': '#4A90E2',    # Blue
                'secondary': '#F5A623',  # Orange  
                'text': '#2C3E50'       # Dark blue-gray
            },
            'fonts': {
                'primary': 'brand/fonts/primary.ttf',
                'secondary': 'brand/fonts/secondary.ttf'
            },
            'watermark_templates': {
                'simple': '@KiinContent',
                'with_logo': 'logo + @KiinContent',
                'branded': 'Kiin Content Factory'
            }
        }
    
    def _load_platform_specs(self) -> Dict[str, Any]:
        """Load platform specifications"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Platform specs file not found: {self.config_path}")
            return {}
        except Exception as e:
            logger.error(f"Error loading platform specs: {e}")
            return {}
    
    def repurpose_video(self, source_video_path: str, target_platform: str, 
                       aspect_ratio: Optional[str] = None, 
                       watermark_style: str = 'simple') -> Dict[str, Any]:
        """Repurpose video for target platform"""
        
        if not os.path.exists(source_video_path):
            return {"error": f"Source video not found: {source_video_path}"}
        
        platform_spec = self.video_specs.get(target_platform)
        if not platform_spec:
            return {"error": f"Platform not supported: {target_platform}"}
        
        # Choose aspect ratio
        if not aspect_ratio:
            aspect_ratio = platform_spec['aspect_ratios'][0]  # Default to first
        elif aspect_ratio not in platform_spec['aspect_ratios']:
            return {"error": f"Aspect ratio {aspect_ratio} not supported for {target_platform}"}
        
        # Get source video info
        source_info = self._get_video_info(source_video_path)
        if not source_info:
            return {"error": "Could not analyze source video"}
        
        # Generate output filename
        source_name = Path(source_video_path).stem
        output_filename = f"{source_name}_{target_platform}_{aspect_ratio.replace(':', 'x')}.mp4"
        output_path = self.temp_dir / output_filename
        
        try:
            # Process video
            result = self._process_video(
                source_video_path, str(output_path), 
                target_platform, aspect_ratio, watermark_style
            )
            
            if result['success']:
                return {
                    'success': True,
                    'output_path': str(output_path),
                    'platform': target_platform,
                    'aspect_ratio': aspect_ratio,
                    'resolution': platform_spec['resolution'][aspect_ratio],
                    'duration': result.get('duration', source_info['duration']),
                    'file_size_mb': os.path.getsize(output_path) / (1024*1024),
                    'watermark_applied': result.get('watermark_applied', False)
                }
            else:
                return {"error": result.get('error', 'Video processing failed')}
                
        except Exception as e:
            logger.error(f"Error repurposing video: {e}")
            return {"error": str(e)}
    
    def _get_video_info(self, video_path: str) -> Optional[Dict[str, Any]]:
        """Get video information using ffprobe"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"ffprobe failed: {result.stderr}")
                return None
            
            info = json.loads(result.stdout)
            
            # Find video stream
            video_stream = None
            for stream in info['streams']:
                if stream['codec_type'] == 'video':
                    video_stream = stream
                    break
            
            if not video_stream:
                return None
            
            return {
                'width': int(video_stream['width']),
                'height': int(video_stream['height']),
                'duration': float(video_stream.get('duration', 0)),
                'fps': eval(video_stream.get('r_frame_rate', '30/1')),
                'aspect_ratio': f"{video_stream['width']}:{video_stream['height']}",
                'codec': video_stream['codec_name'],
                'bitrate': int(video_stream.get('bit_rate', 0))
            }
            
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return None
    
    def _process_video(self, input_path: str, output_path: str, platform: str,
                      aspect_ratio: str, watermark_style: str) -> Dict[str, Any]:
        """Process video with ffmpeg"""
        
        platform_spec = self.video_specs[platform]
        target_resolution = platform_spec['resolution'][aspect_ratio]
        target_width, target_height = target_resolution
        
        # Build ffmpeg command
        cmd = [
            'ffmpeg', '-i', input_path, '-y',  # -y to overwrite
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-b:v', platform_spec['bitrate'],
            '-r', str(platform_spec['fps']),
            '-pix_fmt', 'yuv420p'
        ]
        
        # Video filters
        filters = []
        
        # Scaling and cropping for aspect ratio
        source_info = self._get_video_info(input_path)
        if source_info:
            source_width = source_info['width']
            source_height = source_info['height']
            
            # Calculate scaling to fit target aspect ratio
            target_aspect = target_width / target_height
            source_aspect = source_width / source_height
            
            if abs(source_aspect - target_aspect) > 0.01:  # Aspect ratios differ
                if source_aspect > target_aspect:
                    # Source is wider, crop width
                    new_width = int(source_height * target_aspect)
                    filters.append(f'crop={new_width}:{source_height}:(iw-{new_width})/2:0')
                else:
                    # Source is taller, crop height  
                    new_height = int(source_width / target_aspect)
                    filters.append(f'crop={source_width}:{new_height}:0:(ih-{new_height})/2')
        
        # Scale to target resolution
        filters.append(f'scale={target_width}:{target_height}')
        
        # Add watermark if specified
        watermark_applied = False
        if watermark_style != 'none':
            watermark_filter = self._create_watermark_filter(platform, watermark_style)
            if watermark_filter:
                filters.append(watermark_filter)
                watermark_applied = True
        
        # Apply filters
        if filters:
            cmd.extend(['-vf', ','.join(filters)])
        
        # Duration limit
        max_duration = platform_spec['max_duration']
        if source_info and source_info['duration'] > max_duration:
            cmd.extend(['-t', str(max_duration)])
        
        # Output path
        cmd.append(output_path)
        
        try:
            logger.info(f"Running ffmpeg: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"ffmpeg failed: {result.stderr}")
                return {
                    'success': False,
                    'error': f"Video processing failed: {result.stderr}"
                }
            
            # Get output video info
            output_info = self._get_video_info(output_path)
            
            return {
                'success': True,
                'duration': output_info['duration'] if output_info else None,
                'watermark_applied': watermark_applied
            }
            
        except Exception as e:
            logger.error(f"Error running ffmpeg: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_watermark_filter(self, platform: str, style: str) -> Optional[str]:
        """Create watermark filter for ffmpeg"""
        
        platform_spec = self.video_specs[platform]
        position = platform_spec.get('watermark_position', 'bottom_right')
        opacity = platform_spec.get('watermark_opacity', 0.7)
        
        # Position mapping
        position_map = {
            'bottom_right': 'W-w-20:H-h-20',
            'bottom_left': '20:H-h-20',
            'bottom_center': '(W-w)/2:H-h-20',
            'top_right': 'W-w-20:20',
            'top_left': '20:20',
            'center': '(W-w)/2:(H-h)/2'
        }
        
        pos = position_map.get(position, position_map['bottom_right'])
        
        # Create text watermark (simple approach)
        if style == 'simple':
            text = self.brand_config['watermark_templates']['simple']
            return f"drawtext=text='{text}':fontsize=24:fontcolor=white@{opacity}:x={pos.split(':')[0]}:y={pos.split(':')[1]}"
        
        # For logo watermarks, would need to overlay image
        # This is a simplified implementation
        return None
    
    def bulk_repurpose(self, source_video_path: str, target_platforms: List[str],
                      watermark_style: str = 'simple') -> Dict[str, Any]:
        """Repurpose video for multiple platforms"""
        
        results = {
            'source_video': source_video_path,
            'total_platforms': len(target_platforms),
            'successful': [],
            'failed': [],
            'outputs': {}
        }
        
        for platform in target_platforms:
            try:
                result = self.repurpose_video(
                    source_video_path, platform, 
                    watermark_style=watermark_style
                )
                
                if result.get('success'):
                    results['successful'].append(platform)
                    results['outputs'][platform] = result
                else:
                    results['failed'].append({
                        'platform': platform,
                        'error': result.get('error', 'Unknown error')
                    })
                    
            except Exception as e:
                logger.error(f"Error repurposing for {platform}: {e}")
                results['failed'].append({
                    'platform': platform,
                    'error': str(e)
                })
        
        results['success_rate'] = len(results['successful']) / len(target_platforms)
        
        logger.info(f"Bulk repurpose complete: {len(results['successful'])}/{len(target_platforms)} successful")
        return results
    
    def create_platform_thumbnails(self, source_video_path: str, 
                                  platforms: List[str]) -> Dict[str, Any]:
        """Create platform-specific thumbnails from video"""
        
        thumbnails = {}
        
        # Extract frame at 2 seconds (or 25% through video)
        source_info = self._get_video_info(source_video_path)
        if not source_info:
            return {"error": "Could not analyze source video"}
        
        duration = source_info['duration']
        timestamp = min(2.0, duration * 0.25)  # 2 seconds or 25% through
        
        for platform in platforms:
            try:
                platform_spec = self.video_specs.get(platform)
                if not platform_spec:
                    continue
                
                # Use first aspect ratio for thumbnail
                aspect_ratio = platform_spec['aspect_ratios'][0]
                resolution = platform_spec['resolution'][aspect_ratio]
                
                # Create thumbnail filename
                source_name = Path(source_video_path).stem
                thumbnail_filename = f"{source_name}_{platform}_thumbnail.jpg"
                thumbnail_path = self.temp_dir / thumbnail_filename
                
                # Extract frame with ffmpeg
                cmd = [
                    'ffmpeg', '-i', source_video_path, '-y',
                    '-ss', str(timestamp),
                    '-vframes', '1',
                    '-vf', f'scale={resolution[0]}:{resolution[1]}',
                    '-q:v', '2',  # High quality
                    str(thumbnail_path)
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    thumbnails[platform] = {
                        'path': str(thumbnail_path),
                        'resolution': resolution,
                        'aspect_ratio': aspect_ratio
                    }
                else:
                    logger.error(f"Thumbnail creation failed for {platform}: {result.stderr}")
                    
            except Exception as e:
                logger.error(f"Error creating thumbnail for {platform}: {e}")
        
        return {
            'thumbnails': thumbnails,
            'timestamp_used': timestamp,
            'total_created': len(thumbnails)
        }
    
    def optimize_for_mobile(self, video_path: str) -> str:
        """Optimize video specifically for mobile viewing"""
        
        source_name = Path(video_path).stem
        output_path = self.temp_dir / f"{source_name}_mobile_optimized.mp4"
        
        cmd = [
            'ffmpeg', '-i', video_path, '-y',
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '28',  # Slightly lower quality for smaller size
            '-profile:v', 'baseline',  # Better mobile compatibility
            '-level', '3.0',
            '-movflags', '+faststart',  # Progressive download
            '-b:v', '2000k',  # Lower bitrate for mobile
            '-maxrate', '2500k',
            '-bufsize', '5000k',
            '-vf', 'scale=720:-2',  # Max width 720px
            str(output_path)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                original_size = os.path.getsize(video_path)
                optimized_size = os.path.getsize(output_path)
                compression_ratio = (original_size - optimized_size) / original_size
                
                logger.info(f"Mobile optimization complete. Size reduction: {compression_ratio:.1%}")
                return str(output_path)
            else:
                logger.error(f"Mobile optimization failed: {result.stderr}")
                return video_path
                
        except Exception as e:
            logger.error(f"Error optimizing for mobile: {e}")
            return video_path
    
    def create_preview_collage(self, repurposed_videos: Dict[str, str]) -> str:
        """Create a preview collage showing all platform versions"""
        
        if not repurposed_videos:
            return ""
        
        try:
            # Extract first frame from each video
            frames = {}
            for platform, video_path in repurposed_videos.items():
                if os.path.exists(video_path):
                    cap = cv2.VideoCapture(video_path)
                    ret, frame = cap.read()
                    if ret:
                        frames[platform] = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    cap.release()
            
            if not frames:
                return ""
            
            # Create collage
            collage = self._create_frame_collage(frames)
            
            # Save collage
            collage_path = self.temp_dir / "platform_preview_collage.jpg"
            Image.fromarray(collage).save(collage_path, quality=90)
            
            return str(collage_path)
            
        except Exception as e:
            logger.error(f"Error creating preview collage: {e}")
            return ""
    
    def _create_frame_collage(self, frames: Dict[str, np.ndarray]) -> np.ndarray:
        """Create a collage from video frames"""
        
        # Resize all frames to same height for consistent display
        target_height = 300
        resized_frames = {}
        
        for platform, frame in frames.items():
            h, w = frame.shape[:2]
            new_width = int(w * target_height / h)
            resized = cv2.resize(frame, (new_width, target_height))
            resized_frames[platform] = resized
        
        # Calculate collage dimensions
        total_width = sum(frame.shape[1] for frame in resized_frames.values())
        max_height = max(frame.shape[0] for frame in resized_frames.values())
        
        # Create collage
        collage = np.zeros((max_height + 60, total_width, 3), dtype=np.uint8)  # +60 for labels
        collage.fill(255)  # White background
        
        x_offset = 0
        for platform, frame in resized_frames.items():
            h, w = frame.shape[:2]
            
            # Place frame
            collage[30:30+h, x_offset:x_offset+w] = frame
            
            # Add platform label
            cv2.putText(collage, platform.upper(), 
                       (x_offset + 10, 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            
            x_offset += w
        
        return collage
    
    def get_platform_recommendations(self, source_video_path: str) -> Dict[str, Any]:
        """Get recommendations for which platforms to target based on content"""
        
        source_info = self._get_video_info(source_video_path)
        if not source_info:
            return {"error": "Could not analyze source video"}
        
        recommendations = {
            'primary_platforms': [],
            'secondary_platforms': [],
            'not_recommended': [],
            'modifications_needed': {}
        }
        
        duration = source_info['duration']
        aspect_ratio = source_info['width'] / source_info['height']
        
        for platform, spec in self.video_specs.items():
            score = 0
            issues = []
            
            # Duration check
            if duration <= spec['max_duration']:
                score += 30
            else:
                issues.append(f"Video too long (max {spec['max_duration']}s)")
            
            if duration >= spec['min_duration']:
                score += 20
            else:
                issues.append(f"Video too short (min {spec['min_duration']}s)")
            
            # Aspect ratio compatibility
            compatible_ratios = []
            for ratio_str in spec['aspect_ratios']:
                ratio_parts = ratio_str.split(':')
                platform_ratio = float(ratio_parts[0]) / float(ratio_parts[1])
                if abs(aspect_ratio - platform_ratio) < 0.2:  # Close enough
                    compatible_ratios.append(ratio_str)
                    score += 25
            
            if not compatible_ratios:
                issues.append("Aspect ratio needs adjustment")
                score += 10  # Still possible with cropping
            
            # Platform-specific bonuses
            if platform == 'instagram' and duration <= 30:
                score += 10  # Short content performs well
            elif platform == 'tiktok' and 15 <= duration <= 30:
                score += 15  # Sweet spot for TikTok
            elif platform == 'youtube' and duration >= 30:
                score += 10  # Longer content for YouTube
            elif platform == 'linkedin' and duration <= 60:
                score += 10  # Professional platforms prefer shorter
            
            # Categorize platforms
            if score >= 70:
                recommendations['primary_platforms'].append({
                    'platform': platform,
                    'score': score,
                    'compatible_ratios': compatible_ratios or spec['aspect_ratios'][:1]
                })
            elif score >= 40:
                recommendations['secondary_platforms'].append({
                    'platform': platform,
                    'score': score,
                    'issues': issues
                })
            else:
                recommendations['not_recommended'].append({
                    'platform': platform,
                    'score': score,
                    'issues': issues
                })
            
            if issues:
                recommendations['modifications_needed'][platform] = issues
        
        # Sort by score
        recommendations['primary_platforms'].sort(key=lambda x: x['score'], reverse=True)
        recommendations['secondary_platforms'].sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations
    
    def cleanup_temp_files(self, keep_recent_hours: int = 24):
        """Clean up temporary files older than specified hours"""
        
        cutoff_time = os.time() - (keep_recent_hours * 3600)
        cleaned_count = 0
        
        try:
            for file_path in self.temp_dir.glob("*"):
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    cleaned_count += 1
            
            logger.info(f"Cleaned up {cleaned_count} temporary files")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error cleaning temp files: {e}")
            return 0