#!/usr/bin/env python3
"""
Kiin Video Assembler
Combine intro, main content, and outro clips into final videos
"""

import argparse
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from brand_utils import KiinBrand
from effects import VideoEffects
from intro_generator import IntroGenerator
from outro_generator import OutroGenerator

class VideoAssembler:
    """Assemble complete videos from intro, main content, and outro clips"""
    
    def __init__(self):
        self.brand = KiinBrand()
        self.effects = VideoEffects()
        self.intro_gen = IntroGenerator()
        self.outro_gen = OutroGenerator()
        
        # Default settings
        self.defaults = {
            'intro_style': 'minimal',
            'outro_style': 'standard',
            'outro_cta': 'follow',
            'social_handle': '@kiinapp',
            'add_transitions': True,
            'normalize_audio': True,
            'output_quality': 'high'
        }
    
    def assemble_video(self, main_video: str, output_file: str = 'final.mp4',
                      intro_video: Optional[str] = None, outro_video: Optional[str] = None,
                      add_intro: bool = False, add_outro: bool = False,
                      intro_style: str = 'minimal', outro_style: str = 'standard',
                      outro_cta: str = 'follow', social_handle: str = '@kiinapp',
                      add_transitions: bool = True, normalize_audio: bool = True) -> bool:
        """Assemble final video from components"""
        
        if not os.path.exists(main_video):
            print(f"Main video file not found: {main_video}")
            return False
        
        print(f"Assembling video with main content: {main_video}")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            segments = []
            
            # Get main video dimensions for consistency
            main_info = self.effects.get_video_info(main_video)
            video_width = int(main_info.get('width', 1080))
            video_height = int(main_info.get('height', 1920))
            
            print(f"Video dimensions: {video_width}x{video_height}")
            
            # Step 1: Handle intro
            if intro_video or add_intro:
                if add_intro and not intro_video:
                    # Generate intro automatically
                    intro_file = os.path.join(temp_dir, 'generated_intro.mp4')
                    print(f"Generating {intro_style} intro...")
                    if self.intro_gen.generate_intro(
                        style=intro_style, 
                        output_file=intro_file,
                        width=video_width,
                        height=video_height
                    ):
                        intro_video = intro_file
                    else:
                        print("Failed to generate intro, continuing without it")
                        intro_video = None
                
                if intro_video and os.path.exists(intro_video):
                    # Ensure intro matches main video dimensions
                    resized_intro = os.path.join(temp_dir, 'intro_resized.mp4')
                    if self._resize_video(intro_video, resized_intro, video_width, video_height):
                        segments.append(resized_intro)
                        print(f"✓ Added intro: {intro_video}")
                    else:
                        print(f"Failed to resize intro: {intro_video}")
            
            # Step 2: Add main video
            segments.append(main_video)
            print(f"✓ Added main content: {main_video}")
            
            # Step 3: Handle outro
            if outro_video or add_outro:
                if add_outro and not outro_video:
                    # Generate outro automatically
                    outro_file = os.path.join(temp_dir, 'generated_outro.mp4')
                    print(f"Generating {outro_style} outro with CTA: {outro_cta}...")
                    if self.outro_gen.generate_outro(
                        cta=outro_cta,
                        style=outro_style,
                        output_file=outro_file,
                        width=video_width,
                        height=video_height,
                        social_handle=social_handle
                    ):
                        outro_video = outro_file
                    else:
                        print("Failed to generate outro, continuing without it")
                        outro_video = None
                
                if outro_video and os.path.exists(outro_video):
                    # Ensure outro matches main video dimensions
                    resized_outro = os.path.join(temp_dir, 'outro_resized.mp4')
                    if self._resize_video(outro_video, resized_outro, video_width, video_height):
                        segments.append(resized_outro)
                        print(f"✓ Added outro: {outro_video}")
                    else:
                        print(f"Failed to resize outro: {outro_video}")
            
            # Step 4: Combine all segments
            if len(segments) == 1:
                # Only main video, just copy it
                import shutil
                shutil.copy2(main_video, output_file)
                print(f"✓ Video saved (no additional segments): {output_file}")
                return True
            
            combined_file = os.path.join(temp_dir, 'combined.mp4')
            if not self._combine_videos(segments, combined_file, add_transitions):
                print("Failed to combine video segments")
                return False
            
            # Step 5: Post-processing
            processed_file = os.path.join(temp_dir, 'processed.mp4')
            if not self._post_process_video(combined_file, processed_file, 
                                          normalize_audio=normalize_audio):
                print("Failed to post-process video")
                return False
            
            # Step 6: Final output
            try:
                import shutil
                shutil.copy2(processed_file, output_file)
                print(f"✓ Final video saved: {output_file}")
                
                # Print video info
                final_info = self.effects.get_video_info(output_file)
                duration = float(final_info.get('duration', 0))
                print(f"  Duration: {duration:.1f}s")
                print(f"  Dimensions: {final_info.get('width')}x{final_info.get('height')}")
                
                return True
                
            except Exception as e:
                print(f"Failed to save final output: {e}")
                return False
    
    def _resize_video(self, input_file: str, output_file: str, 
                     width: int, height: int) -> bool:
        """Resize video to match target dimensions"""
        cmd = [
            'ffmpeg', '-y',
            '-i', input_file,
            '-vf', f'scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black',
            '-c:v', 'libx264', '-preset', 'fast',
            '-c:a', 'aac',
            output_file
        ]
        return self.effects._run_ffmpeg(cmd)
    
    def _combine_videos(self, segments: List[str], output_file: str, 
                       add_transitions: bool = True) -> bool:
        """Combine multiple video segments"""
        
        if len(segments) <= 1:
            print("Need at least 2 segments to combine")
            return False
        
        # Create concat file
        concat_file = os.path.join(os.path.dirname(output_file), 'concat_list.txt')
        
        try:
            with open(concat_file, 'w') as f:
                for segment in segments:
                    f.write(f"file '{segment}'\n")
            
            if add_transitions and len(segments) > 1:
                # Use complex filter for smooth transitions
                return self._combine_with_transitions(segments, output_file)
            else:
                # Simple concatenation
                cmd = [
                    'ffmpeg', '-y',
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', concat_file,
                    '-c', 'copy',
                    output_file
                ]
                return self.effects._run_ffmpeg(cmd)
                
        except Exception as e:
            print(f"Failed to create concat file: {e}")
            return False
        finally:
            if os.path.exists(concat_file):
                os.remove(concat_file)
    
    def _combine_with_transitions(self, segments: List[str], output_file: str) -> bool:
        """Combine videos with smooth transitions between segments"""
        
        if len(segments) == 2:
            # Simple crossfade between two videos
            return self._crossfade_two_videos(segments[0], segments[1], output_file)
        
        # For more than 2 videos, use a more complex approach
        temp_dir = os.path.dirname(output_file)
        
        # Start with first two videos
        current_combined = os.path.join(temp_dir, 'temp_combined_1.mp4')
        if not self._crossfade_two_videos(segments[0], segments[1], current_combined):
            return False
        
        # Add remaining videos one by one
        for i, segment in enumerate(segments[2:], start=2):
            next_combined = os.path.join(temp_dir, f'temp_combined_{i}.mp4')
            if not self._crossfade_two_videos(current_combined, segment, next_combined):
                return False
            current_combined = next_combined
        
        # Move final result to output
        import shutil
        shutil.copy2(current_combined, output_file)
        return True
    
    def _crossfade_two_videos(self, video1: str, video2: str, output_file: str,
                             transition_duration: float = 0.5) -> bool:
        """Create crossfade transition between two videos"""
        
        # Get video durations and check for audio
        info1 = self.effects.get_video_info(video1)
        info2 = self.effects.get_video_info(video2)
        
        duration1 = float(info1.get('duration', 0))
        duration2 = float(info2.get('duration', 0))
        
        # Check if videos have audio streams
        has_audio1 = self._has_audio_stream(video1)
        has_audio2 = self._has_audio_stream(video2)
        has_audio = has_audio1 and has_audio2
        
        if duration1 < transition_duration or duration2 < transition_duration:
            # If videos are too short for crossfade, just concatenate
            if has_audio:
                filter_complex = '[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[outv][outa]'
                map_args = ['-map', '[outv]', '-map', '[outa]', '-c:a', 'aac']
            else:
                filter_complex = '[0:v][1:v]concat=n=2:v=1[outv]'
                map_args = ['-map', '[outv]']
            
            cmd = [
                'ffmpeg', '-y',
                '-i', video1,
                '-i', video2,
                '-filter_complex', filter_complex
            ] + map_args + [
                '-c:v', 'libx264', '-preset', 'fast',
                output_file
            ]
        else:
            # Create crossfade
            offset = duration1 - transition_duration
            
            if has_audio:
                filter_complex = (
                    f'[0:v][1:v]xfade=transition=fade:duration={transition_duration}:offset={offset}[v];'
                    f'[0:a][1:a]acrossfade=d={transition_duration}[a]'
                )
                map_args = ['-map', '[v]', '-map', '[a]', '-c:a', 'aac']
            else:
                filter_complex = f'[0:v][1:v]xfade=transition=fade:duration={transition_duration}:offset={offset}[v]'
                map_args = ['-map', '[v]']
            
            cmd = [
                'ffmpeg', '-y',
                '-i', video1,
                '-i', video2,
                '-filter_complex', filter_complex
            ] + map_args + [
                '-c:v', 'libx264', '-preset', 'fast',
                output_file
            ]
        
        return self.effects._run_ffmpeg(cmd)
    
    def _has_audio_stream(self, video_file: str) -> bool:
        """Check if video has audio stream"""
        cmd = [
            'ffprobe', '-v', 'quiet',
            '-select_streams', 'a',
            '-show_entries', 'stream=codec_type',
            '-of', 'csv=p=0',
            video_file
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return bool(result.stdout.strip())
        except subprocess.CalledProcessError:
            return False
    
    def _post_process_video(self, input_file: str, output_file: str,
                           normalize_audio: bool = True, quality: str = 'high') -> bool:
        """Apply post-processing to final video"""
        
        filters = []
        audio_filters = []
        
        # Video filters
        if quality == 'high':
            # Enhance video quality
            filters.append('unsharp=5:5:1.0:5:5:0.5')  # Slight sharpening
        
        # Audio filters
        if normalize_audio:
            audio_filters.append('loudnorm=I=-16:TP=-1.5:LRA=11')  # Normalize audio
        
        # Build filter strings
        video_filter = ','.join(filters) if filters else None
        audio_filter = ','.join(audio_filters) if audio_filters else None
        
        cmd = ['ffmpeg', '-y', '-i', input_file]
        
        if video_filter:
            cmd.extend(['-vf', video_filter])
        
        if audio_filter:
            cmd.extend(['-af', audio_filter])
        
        # Quality settings
        if quality == 'high':
            cmd.extend(['-c:v', 'libx264', '-preset', 'slow', '-crf', '18'])
        else:
            cmd.extend(['-c:v', 'libx264', '-preset', 'fast', '-crf', '23'])
        
        cmd.extend(['-c:a', 'aac', '-b:a', '128k', output_file])
        
        return self.effects._run_ffmpeg(cmd)
    
    def create_video_from_template(self, template_name: str, main_video: str,
                                  output_file: str, **kwargs) -> bool:
        """Create video using a predefined template"""
        
        templates = {
            'social_post': {
                'add_intro': True,
                'add_outro': True,
                'intro_style': 'minimal',
                'outro_style': 'standard',
                'outro_cta': 'follow',
                'add_transitions': True
            },
            'tutorial': {
                'add_intro': True,
                'add_outro': True,
                'intro_style': 'professional',
                'outro_style': 'standard',
                'outro_cta': 'save',
                'add_transitions': False
            },
            'story': {
                'add_intro': False,
                'add_outro': True,
                'outro_style': 'warm',
                'outro_cta': 'more',
                'add_transitions': True
            },
            'quick_tip': {
                'add_intro': True,
                'add_outro': True,
                'intro_style': 'minimal',
                'outro_style': 'minimal',
                'outro_cta': 'save',
                'add_transitions': False
            }
        }
        
        if template_name not in templates:
            print(f"Unknown template: {template_name}")
            print(f"Available templates: {list(templates.keys())}")
            return False
        
        template_config = templates[template_name]
        
        # Merge template config with provided kwargs
        config = {**template_config, **kwargs}
        
        print(f"Using template: {template_name}")
        
        return self.assemble_video(main_video, output_file, **config)
    
    def batch_process(self, input_dir: str, output_dir: str, template: str = 'social_post') -> int:
        """Batch process multiple videos"""
        
        if not os.path.exists(input_dir):
            print(f"Input directory not found: {input_dir}")
            return 0
        
        os.makedirs(output_dir, exist_ok=True)
        
        video_extensions = ['.mp4', '.mov', '.avi', '.mkv']
        input_files = []
        
        for file in os.listdir(input_dir):
            if any(file.lower().endswith(ext) for ext in video_extensions):
                input_files.append(os.path.join(input_dir, file))
        
        if not input_files:
            print(f"No video files found in {input_dir}")
            return 0
        
        print(f"Found {len(input_files)} video files to process")
        
        success_count = 0
        
        for i, input_file in enumerate(input_files, 1):
            print(f"\n[{i}/{len(input_files)}] Processing: {os.path.basename(input_file)}")
            
            # Generate output filename
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            output_file = os.path.join(output_dir, f"{base_name}_final.mp4")
            
            if self.create_video_from_template(template, input_file, output_file):
                success_count += 1
                print(f"✓ Completed: {output_file}")
            else:
                print(f"✗ Failed: {input_file}")
        
        print(f"\nBatch processing complete: {success_count}/{len(input_files)} successful")
        return success_count

def main():
    parser = argparse.ArgumentParser(description='Assemble Kiin videos from components')
    
    # Required arguments
    parser.add_argument('--main', required=True, help='Main video file')
    parser.add_argument('--output', default='final.mp4', help='Output file path')
    
    # Optional video components
    parser.add_argument('--intro', help='Intro video file')
    parser.add_argument('--outro', help='Outro video file')
    
    # Auto-generation flags
    parser.add_argument('--add-intro', action='store_true', 
                       help='Generate intro automatically')
    parser.add_argument('--add-outro', action='store_true',
                       help='Generate outro automatically')
    
    # Style options
    parser.add_argument('--intro-style', default='minimal',
                       choices=['minimal', 'warm', 'professional'],
                       help='Intro style (if auto-generating)')
    parser.add_argument('--outro-style', default='standard',
                       choices=['standard', 'warm', 'minimal', 'gradient'],
                       help='Outro style (if auto-generating)')
    parser.add_argument('--outro-cta', default='follow',
                       help='Outro call-to-action text')
    parser.add_argument('--social-handle', default='@kiinapp',
                       help='Social media handle')
    
    # Processing options
    parser.add_argument('--no-transitions', action='store_true',
                       help='Disable smooth transitions')
    parser.add_argument('--no-audio-normalize', action='store_true',
                       help='Skip audio normalization')
    
    # Template and batch options
    parser.add_argument('--template', 
                       choices=['social_post', 'tutorial', 'story', 'quick_tip'],
                       help='Use predefined template')
    parser.add_argument('--batch-input-dir', help='Batch process directory')
    parser.add_argument('--batch-output-dir', help='Batch output directory')
    
    args = parser.parse_args()
    
    assembler = VideoAssembler()
    
    # Batch processing mode
    if args.batch_input_dir:
        output_dir = args.batch_output_dir or 'batch_output'
        template = args.template or 'social_post'
        count = assembler.batch_process(args.batch_input_dir, output_dir, template)
        print(f"Processed {count} videos")
        return 0 if count > 0 else 1
    
    # Template mode
    if args.template:
        success = assembler.create_video_from_template(
            args.template, args.main, args.output,
            social_handle=args.social_handle,
            outro_cta=args.outro_cta
        )
    else:
        # Manual assembly
        success = assembler.assemble_video(
            main_video=args.main,
            output_file=args.output,
            intro_video=args.intro,
            outro_video=args.outro,
            add_intro=args.add_intro,
            add_outro=args.add_outro,
            intro_style=args.intro_style,
            outro_style=args.outro_style,
            outro_cta=args.outro_cta,
            social_handle=args.social_handle,
            add_transitions=not args.no_transitions,
            normalize_audio=not args.no_audio_normalize
        )
    
    if success:
        print("✓ Video assembly completed successfully!")
        return 0
    else:
        print("✗ Video assembly failed!")
        return 1

if __name__ == '__main__':
    exit(main())