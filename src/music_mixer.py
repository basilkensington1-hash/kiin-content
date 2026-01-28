#!/usr/bin/env python3
"""
Music Mixer for Kiin Content - Professional Background Music Integration
Adds mood-appropriate background music to videos with intelligent audio ducking
"""

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import cv2


class MusicMixer:
    """Professional music mixing for video content"""
    
    def __init__(self):
        self.config_path = Path(__file__).parent.parent / "config" / "audio_config.json"
        self.assets_path = Path(__file__).parent.parent / "assets"
        
        # Mood-based music recommendations
        self.mood_mappings = {
            "calm": {
                "description": "Peaceful, relaxing ambient sounds",
                "suggested_tracks": [
                    "ambient_peaceful.mp3", "piano_soft.mp3", "nature_birds.mp3",
                    "strings_gentle.mp3", "acoustic_warm.mp3"
                ],
                "volume_level": 0.15,
                "duck_ratio": 0.3,
                "characteristics": ["peaceful", "non-intrusive", "flowing"]
            },
            "warm": {
                "description": "Warm, nurturing background music",
                "suggested_tracks": [
                    "acoustic_guitar_warm.mp3", "piano_emotional.mp3", "strings_hopeful.mp3",
                    "ambient_caring.mp3", "folk_gentle.mp3"
                ],
                "volume_level": 0.18,
                "duck_ratio": 0.25,
                "characteristics": ["emotional", "supportive", "human"]
            },
            "uplifting": {
                "description": "Positive, encouraging background music",
                "suggested_tracks": [
                    "acoustic_upbeat.mp3", "piano_inspiring.mp3", "strings_hopeful.mp3",
                    "folk_positive.mp3", "ambient_bright.mp3"
                ],
                "volume_level": 0.20,
                "duck_ratio": 0.35,
                "characteristics": ["inspiring", "energetic", "hopeful"]
            },
            "intimate": {
                "description": "Subtle, intimate background for personal content",
                "suggested_tracks": [
                    "ambient_minimal.mp3", "piano_solo_soft.mp3", "strings_subtle.mp3",
                    "acoustic_fingerpicking.mp3"
                ],
                "volume_level": 0.12,
                "duck_ratio": 0.2,
                "characteristics": ["minimal", "personal", "unobtrusive"]
            },
            "professional": {
                "description": "Clean, professional background for tips and advice",
                "suggested_tracks": [
                    "corporate_soft.mp3", "piano_clean.mp3", "ambient_professional.mp3",
                    "strings_modern.mp3", "acoustic_clear.mp3"
                ],
                "volume_level": 0.16,
                "duck_ratio": 0.4,
                "characteristics": ["clear", "modern", "confident"]
            },
            "energetic": {
                "description": "Energetic but appropriate for family content",
                "suggested_tracks": [
                    "acoustic_rhythmic.mp3", "piano_lively.mp3", "folk_upbeat.mp3",
                    "ambient_flowing.mp3", "strings_dynamic.mp3"
                ],
                "volume_level": 0.22,
                "duck_ratio": 0.45,
                "characteristics": ["rhythmic", "engaging", "balanced"]
            }
        }
        
        # Content type to mood mapping
        self.content_mood_map = {
            "validation": "warm",
            "confessions": "intimate", 
            "tips": "professional",
            "sandwich_gen": "energetic",
            "general": "calm"
        }
    
    def check_ffmpeg(self) -> bool:
        """Check if FFmpeg is available"""
        try:
            subprocess.run(['ffmpeg', '-version'], 
                         capture_output=True, check=True, timeout=5)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def get_video_info(self, video_path: str) -> Dict:
        """Get video information using OpenCV and FFprobe"""
        info = {}
        
        try:
            # Get basic video info with OpenCV
            cap = cv2.VideoCapture(video_path)
            if cap.isOpened():
                info['width'] = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                info['height'] = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                info['fps'] = cap.get(cv2.CAP_PROP_FPS)
                info['frame_count'] = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                info['duration'] = info['frame_count'] / info['fps'] if info['fps'] > 0 else 0
                cap.release()
            
            # Get audio info with FFprobe if available
            if self.check_ffmpeg():
                try:
                    result = subprocess.run([
                        'ffprobe', '-v', 'quiet', '-print_format', 'json',
                        '-show_streams', video_path
                    ], capture_output=True, text=True, timeout=10)
                    
                    if result.returncode == 0:
                        probe_data = json.loads(result.stdout)
                        for stream in probe_data.get('streams', []):
                            if stream.get('codec_type') == 'audio':
                                info['has_audio'] = True
                                info['audio_codec'] = stream.get('codec_name', 'unknown')
                                break
                        else:
                            info['has_audio'] = False
                except Exception:
                    info['has_audio'] = True  # Assume audio exists if probe fails
            else:
                info['has_audio'] = True  # Assume audio exists without FFmpeg
                
        except Exception as e:
            print(f"Warning: Could not get complete video info: {e}")
            info = {'duration': 0, 'has_audio': True}
        
        return info
    
    def calculate_ducking_params(self, mood: str, video_info: Dict) -> Dict:
        """Calculate audio ducking parameters based on mood and video"""
        if mood not in self.mood_mappings:
            mood = "calm"
        
        mood_config = self.mood_mappings[mood]
        base_volume = mood_config['volume_level']
        duck_ratio = mood_config['duck_ratio']
        
        # Adjust based on video length
        duration = video_info.get('duration', 0)
        if duration > 300:  # 5+ minutes, reduce volume slightly
            base_volume *= 0.9
        elif duration < 60:  # Short videos, can be slightly louder
            base_volume *= 1.1
        
        return {
            "music_volume": max(0.05, min(0.3, base_volume)),
            "duck_volume": max(0.02, base_volume * duck_ratio),
            "fade_in_duration": 3.0,
            "fade_out_duration": 3.0,
            "duck_threshold": -25,  # dB threshold for ducking
            "duck_ratio": duck_ratio
        }
    
    def create_audio_filter_complex(self, music_duration: float, video_duration: float, 
                                   params: Dict, has_speech: bool = True) -> str:
        """Create FFmpeg filter complex for audio mixing with ducking"""
        music_vol = params['music_volume']
        duck_vol = params['duck_volume'] 
        fade_in = params['fade_in_duration']
        fade_out = params['fade_out_duration']
        
        # Ensure music doesn't exceed video duration
        music_end = min(music_duration, video_duration)
        fade_out_start = max(0, music_end - fade_out)
        
        if has_speech:
            # Advanced ducking filter
            filter_complex = f"""
            [1:a]aloop=loop=-1:size=2e+09,volume={music_vol},
            afade=t=in:st=0:d={fade_in},
            afade=t=out:st={fade_out_start}:d={fade_out}[music];
            [0:a]compand=attacks=0.1:decays=0.3:points=-80/-80|-30/-15|-10/-5|0/-3[compressed_speech];
            [compressed_speech][music]sidechaincompress=threshold=0.003:ratio=3:attack=5:release=50:makeup=1:knee=2[mixed]
            """
        else:
            # Simple mixing without ducking
            filter_complex = f"""
            [1:a]aloop=loop=-1:size=2e+09,volume={music_vol},
            afade=t=in:st=0:d={fade_in},
            afade=t=out:st={fade_out_start}:d={fade_out}[music];
            [0:a][music]amix=inputs=2:duration=shortest[mixed]
            """
        
        return filter_complex.strip()
    
    def mix_video_with_music(self, video_path: str, music_path: str, 
                            output_path: str, mood: str = "calm",
                            custom_params: Dict = None) -> bool:
        """Mix video with background music using intelligent ducking"""
        
        if not self.check_ffmpeg():
            print("✗ Error: FFmpeg not found. Please install FFmpeg to use music mixing.")
            return False
        
        if not os.path.exists(video_path):
            print(f"✗ Error: Video file not found: {video_path}")
            return False
        
        if not os.path.exists(music_path):
            print(f"✗ Error: Music file not found: {music_path}")
            return False
        
        # Get video information
        video_info = self.get_video_info(video_path)
        print(f"📹 Video: {video_info.get('duration', 0):.1f}s, Audio: {video_info.get('has_audio', True)}")
        
        # Calculate mixing parameters
        if custom_params:
            params = custom_params
        else:
            params = self.calculate_ducking_params(mood, video_info)
        
        print(f"🎵 Mixing with '{mood}' mood (vol: {params['music_volume']:.2f}, duck: {params['duck_volume']:.2f})")
        
        try:
            # Create filter complex
            music_info = self.get_audio_duration(music_path)
            music_duration = music_info if music_info > 0 else video_info.get('duration', 0)
            
            filter_complex = self.create_audio_filter_complex(
                music_duration, 
                video_info.get('duration', 0),
                params,
                video_info.get('has_audio', True)
            )
            
            # Build FFmpeg command
            cmd = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-i', music_path,
                '-filter_complex', filter_complex,
                '-map', '0:v',
                '-map', '[mixed]',
                '-c:v', 'copy',  # Copy video stream without re-encoding
                '-c:a', 'aac',   # Encode audio as AAC
                '-b:a', '128k',  # Audio bitrate
                '-shortest',     # End when shortest input ends
                output_path
            ]
            
            # Run FFmpeg
            print("🔄 Processing video with background music...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✓ Successfully created: {output_path}")
                return True
            else:
                print(f"✗ FFmpeg error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"✗ Error during mixing: {e}")
            return False
    
    def get_audio_duration(self, audio_path: str) -> float:
        """Get duration of audio file"""
        try:
            if self.check_ffmpeg():
                result = subprocess.run([
                    'ffprobe', '-v', 'quiet', '-show_entries',
                    'format=duration', '-of', 'csv=p=0', audio_path
                ], capture_output=True, text=True)
                return float(result.stdout.strip())
        except:
            pass
        return 0
    
    def suggest_music_for_mood(self, mood: str) -> Dict:
        """Get music suggestions for a specific mood"""
        if mood not in self.mood_mappings:
            print(f"Unknown mood: {mood}")
            print(f"Available moods: {', '.join(self.mood_mappings.keys())}")
            return {}
        
        return self.mood_mappings[mood]
    
    def suggest_music_for_content_type(self, content_type: str) -> Dict:
        """Get music suggestions for content type"""
        mood = self.content_mood_map.get(content_type, "calm")
        return self.suggest_music_for_mood(mood)
    
    def list_moods(self) -> None:
        """List all available moods with descriptions"""
        print("🎵 Available Moods for Background Music:")
        print("=" * 50)
        
        for mood, config in self.mood_mappings.items():
            print(f"\n{mood.upper()}:")
            print(f"  Description: {config['description']}")
            print(f"  Characteristics: {', '.join(config['characteristics'])}")
            print(f"  Volume Level: {config['volume_level']:.2f}")
            print(f"  Suggested tracks:")
            for track in config['suggested_tracks']:
                print(f"    • {track}")
    
    def create_sample_music_library(self, output_dir: str) -> None:
        """Create a sample music library structure with README"""
        library_path = Path(output_dir)
        library_path.mkdir(parents=True, exist_ok=True)
        
        # Create mood directories
        for mood in self.mood_mappings.keys():
            mood_dir = library_path / mood
            mood_dir.mkdir(exist_ok=True)
            
            # Create README for each mood
            readme_path = mood_dir / "README.md"
            config = self.mood_mappings[mood]
            
            readme_content = f"""# {mood.title()} Music Collection

{config['description']}

## Characteristics
{', '.join(config['characteristics'])}

## Recommended Tracks
{chr(10).join(f'- {track}' for track in config['suggested_tracks'])}

## Usage Parameters
- Volume Level: {config['volume_level']:.2f}
- Duck Ratio: {config['duck_ratio']:.2f}

## File Requirements
- Format: MP3, WAV, or AAC
- Quality: 128kbps or higher
- Length: 3-10 minutes (will loop automatically)
- No vocals or prominent percussion
- Consistent volume throughout

## Free Music Sources
See MUSIC_SOURCES.md in the assets folder for royalty-free music sources.
"""
            readme_path.write_text(readme_content)
        
        print(f"✓ Sample music library structure created at: {library_path}")
        print(f"  Created {len(self.mood_mappings)} mood directories with documentation")
    
    def validate_music_file(self, music_path: str) -> Dict:
        """Validate music file for use in mixing"""
        if not os.path.exists(music_path):
            return {"valid": False, "error": "File not found"}
        
        # Check file extension
        valid_extensions = ['.mp3', '.wav', '.aac', '.m4a', '.ogg']
        if not any(music_path.lower().endswith(ext) for ext in valid_extensions):
            return {"valid": False, "error": f"Unsupported format. Use: {', '.join(valid_extensions)}"}
        
        # Get duration and basic info
        duration = self.get_audio_duration(music_path)
        if duration == 0:
            return {"valid": False, "error": "Could not read audio file or zero duration"}
        
        # Check duration
        if duration < 30:
            return {"valid": False, "error": "Music too short (minimum 30 seconds)"}
        elif duration > 600:  # 10 minutes
            return {"valid": False, "warning": "Music very long (>10 min), consider shorter loops"}
        
        return {
            "valid": True,
            "duration": duration,
            "format": Path(music_path).suffix,
            "recommendations": [
                "Ensure consistent volume throughout",
                "Avoid tracks with prominent vocals", 
                "Instrumental music works best for background",
                "3-5 minute loops are optimal"
            ]
        }


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Music Mixer for Kiin Content - Professional Background Music Integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python music_mixer.py --video input.mp4 --music ambient.mp3 --output mixed.mp4
  python music_mixer.py --video input.mp4 --mood calm --output mixed.mp4
  python music_mixer.py --list-moods
  python music_mixer.py --suggest-content tips
  python music_mixer.py --validate-music ambient.mp3
  python music_mixer.py --create-library ./music_library
        """
    )
    
    parser.add_argument('--video', type=str, help='Input video file')
    parser.add_argument('--music', type=str, help='Background music file')
    parser.add_argument('--output', type=str, help='Output video file')
    parser.add_argument('--mood', type=str, choices=list(MusicMixer().mood_mappings.keys()),
                       help='Music mood (alternative to --music)')
    parser.add_argument('--content-type', type=str, 
                       choices=['validation', 'confessions', 'tips', 'sandwich_gen', 'general'],
                       help='Content type (will auto-select mood)')
    parser.add_argument('--volume', type=float, help='Custom music volume (0.0-1.0)')
    parser.add_argument('--duck-ratio', type=float, help='Custom ducking ratio (0.0-1.0)')
    parser.add_argument('--list-moods', action='store_true', help='List available moods')
    parser.add_argument('--suggest-mood', type=str, help='Get suggestions for specific mood')
    parser.add_argument('--suggest-content', type=str, help='Get suggestions for content type')
    parser.add_argument('--validate-music', type=str, help='Validate music file for mixing')
    parser.add_argument('--create-library', type=str, help='Create sample music library structure')
    parser.add_argument('--info', type=str, help='Get information about video file')
    
    args = parser.parse_args()
    
    mixer = MusicMixer()
    
    if args.list_moods:
        mixer.list_moods()
    
    elif args.suggest_mood:
        suggestion = mixer.suggest_music_for_mood(args.suggest_mood)
        if suggestion:
            print(f"\n🎵 Music suggestions for '{args.suggest_mood}' mood:")
            print(f"Description: {suggestion['description']}")
            print(f"Characteristics: {', '.join(suggestion['characteristics'])}")
            print("Suggested tracks:")
            for track in suggestion['suggested_tracks']:
                print(f"  • {track}")
    
    elif args.suggest_content:
        suggestion = mixer.suggest_music_for_content_type(args.suggest_content)
        if suggestion:
            mood = mixer.content_mood_map.get(args.suggest_content, "calm")
            print(f"\n🎯 Music suggestions for '{args.suggest_content}' content:")
            print(f"Recommended mood: {mood}")
            print(f"Description: {suggestion['description']}")
            print("Suggested tracks:")
            for track in suggestion['suggested_tracks']:
                print(f"  • {track}")
    
    elif args.validate_music:
        validation = mixer.validate_music_file(args.validate_music)
        if validation['valid']:
            print(f"✓ Valid music file: {args.validate_music}")
            print(f"  Duration: {validation['duration']:.1f} seconds")
            print(f"  Format: {validation['format']}")
            print("  Recommendations:")
            for rec in validation['recommendations']:
                print(f"    • {rec}")
        else:
            print(f"✗ Invalid music file: {validation['error']}")
    
    elif args.create_library:
        mixer.create_sample_music_library(args.create_library)
    
    elif args.info:
        info = mixer.get_video_info(args.info)
        print(f"\n📹 Video Information: {args.info}")
        print(f"  Duration: {info.get('duration', 0):.1f} seconds")
        print(f"  Resolution: {info.get('width', '?')}x{info.get('height', '?')}")
        print(f"  FPS: {info.get('fps', '?')}")
        print(f"  Has Audio: {info.get('has_audio', '?')}")
        if 'audio_codec' in info:
            print(f"  Audio Codec: {info['audio_codec']}")
    
    elif args.video and args.output:
        if not (args.music or args.mood or args.content_type):
            print("Error: Must specify either --music, --mood, or --content-type")
            return
        
        # Determine music file and mood
        music_file = args.music
        mood = args.mood
        
        if args.content_type:
            mood = mixer.content_mood_map.get(args.content_type, "calm")
            print(f"Using mood '{mood}' for content type '{args.content_type}'")
        
        if not music_file and mood:
            # Look for suitable music file in assets
            mood_suggestions = mixer.mood_mappings[mood]['suggested_tracks']
            for track in mood_suggestions:
                potential_path = mixer.assets_path / "music" / mood / track
                if potential_path.exists():
                    music_file = str(potential_path)
                    print(f"Using music: {track}")
                    break
            
            if not music_file:
                print(f"✗ No music file found for mood '{mood}'")
                print(f"Create music library with: --create-library ./music")
                print(f"Or specify music file with: --music path/to/file.mp3")
                return
        
        # Custom parameters
        custom_params = None
        if args.volume or args.duck_ratio:
            video_info = mixer.get_video_info(args.video)
            custom_params = mixer.calculate_ducking_params(mood or "calm", video_info)
            if args.volume:
                custom_params['music_volume'] = max(0.0, min(1.0, args.volume))
            if args.duck_ratio:
                custom_params['duck_ratio'] = max(0.0, min(1.0, args.duck_ratio))
                custom_params['duck_volume'] = custom_params['music_volume'] * args.duck_ratio
        
        # Mix the video
        success = mixer.mix_video_with_music(
            args.video, music_file, args.output, 
            mood or "calm", custom_params
        )
        
        if success:
            print(f"🎉 Success! Mixed video created: {args.output}")
        else:
            print("❌ Failed to create mixed video")
    
    else:
        parser.print_help()
        print(f"\nAvailable moods: {', '.join(mixer.mood_mappings.keys())}")


if __name__ == "__main__":
    main()