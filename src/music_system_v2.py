#!/usr/bin/env python3
"""
Music Intelligence V2 for Kiin Content - Advanced Music Selection & Beat Analysis
Intelligent mood-based music selection with dynamic mixing capabilities
"""

import json
import os
import tempfile
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import subprocess
import requests
from datetime import datetime
import numpy as np

# Try to import audio analysis libraries
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    print("librosa not available - beat detection and audio analysis disabled")

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    print("pydub not available - advanced audio processing disabled")


class MusicTrack:
    """Represents a music track with metadata and analysis"""
    
    def __init__(self, file_path: str, metadata: Dict = None):
        self.file_path = Path(file_path)
        self.metadata = metadata or {}
        self.analysis = {}
        self.mood_scores = {}
        
        # Basic properties
        self.duration = 0
        self.bpm = None
        self.key = None
        self.energy_level = 0.5
        self.valence = 0.5  # Positivity/negativity
        self.arousal = 0.5  # Calm/energetic
        
        # Load basic info
        self._analyze_basic_properties()
    
    def _analyze_basic_properties(self):
        """Analyze basic audio properties if libraries are available"""
        if not self.file_path.exists():
            return
        
        try:
            if PYDUB_AVAILABLE:
                audio = AudioSegment.from_file(str(self.file_path))
                self.duration = len(audio) / 1000.0  # Convert to seconds
                
            if LIBROSA_AVAILABLE:
                # Load audio for analysis
                y, sr = librosa.load(str(self.file_path))
                self.duration = len(y) / sr
                
                # Tempo and beat tracking
                tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
                self.bpm = tempo
                
                # Spectral features for mood analysis
                spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
                mfccs = librosa.feature.mfcc(y=y, sr=sr)
                chroma = librosa.feature.chroma_stft(y=y, sr=sr)
                
                # Estimate energy and valence from features
                self.energy_level = np.mean(spectral_centroids) / (sr/2)  # Normalize
                self.arousal = min(1.0, tempo / 180.0)  # High tempo = high arousal
                
                # Estimate valence from harmonic features
                chroma_var = np.var(chroma)
                self.valence = min(1.0, chroma_var * 2)  # Harmonic complexity
                
        except Exception as e:
            print(f"Audio analysis warning for {self.file_path.name}: {e}")
    
    def get_mood_compatibility(self, target_mood: str) -> float:
        """Calculate compatibility score with target mood (0-1)"""
        mood_profiles = {
            'supportive_gentle': {
                'energy_range': (0.1, 0.4),
                'valence_range': (0.4, 0.8),
                'arousal_range': (0.1, 0.3),
                'tempo_range': (60, 100)
            },
            'hopeful_uplifting': {
                'energy_range': (0.4, 0.7),
                'valence_range': (0.6, 0.9),
                'arousal_range': (0.3, 0.6),
                'tempo_range': (80, 130)
            },
            'tense_to_calm': {
                'energy_range': (0.2, 0.6),
                'valence_range': (0.3, 0.7),
                'arousal_range': (0.2, 0.8),  # Can start high, end low
                'tempo_range': (70, 120)
            },
            'reflective_emotional': {
                'energy_range': (0.2, 0.5),
                'valence_range': (0.2, 0.6),
                'arousal_range': (0.1, 0.4),
                'tempo_range': (50, 90)
            },
            'energetic_motivating': {
                'energy_range': (0.6, 0.9),
                'valence_range': (0.7, 0.9),
                'arousal_range': (0.6, 0.9),
                'tempo_range': (110, 160)
            }
        }
        
        if target_mood not in mood_profiles:
            return 0.5  # Neutral compatibility
        
        profile = mood_profiles[target_mood]
        score = 0.0
        factors = 0
        
        # Energy compatibility
        energy_min, energy_max = profile['energy_range']
        if energy_min <= self.energy_level <= energy_max:
            score += 1.0
        else:
            # Gradual falloff outside range
            if self.energy_level < energy_min:
                score += max(0, 1 - (energy_min - self.energy_level) * 2)
            else:
                score += max(0, 1 - (self.energy_level - energy_max) * 2)
        factors += 1
        
        # Valence compatibility
        valence_min, valence_max = profile['valence_range']
        if valence_min <= self.valence <= valence_max:
            score += 1.0
        else:
            if self.valence < valence_min:
                score += max(0, 1 - (valence_min - self.valence) * 2)
            else:
                score += max(0, 1 - (self.valence - valence_max) * 2)
        factors += 1
        
        # Tempo compatibility (if available)
        if self.bpm:
            tempo_min, tempo_max = profile['tempo_range']
            if tempo_min <= self.bpm <= tempo_max:
                score += 1.0
            else:
                if self.bpm < tempo_min:
                    score += max(0, 1 - (tempo_min - self.bpm) / 50)
                else:
                    score += max(0, 1 - (self.bpm - tempo_max) / 50)
            factors += 1
        
        return score / factors if factors > 0 else 0.5


class MusicLibrary:
    """Manages music library with intelligent organization"""
    
    def __init__(self, library_path: str):
        self.library_path = Path(library_path)
        self.tracks_by_mood = {}
        self.all_tracks = []
        self.royalty_free_sources = {
            'pixabay': 'https://pixabay.com/music/',
            'freemusicarchive': 'https://freemusicarchive.org/',
            'youtube_audio': 'https://studio.youtube.com/channel/UCyour-channel/music',
            'incompetech': 'https://incompetech.com/',
            'zapsplat': 'https://www.zapsplat.com/'
        }
        
        # Initialize library
        self._scan_library()
    
    def _scan_library(self):
        """Scan library directory for music files"""
        if not self.library_path.exists():
            print(f"Music library not found at {self.library_path}")
            return
        
        audio_extensions = ['.mp3', '.wav', '.aac', '.m4a', '.ogg', '.flac']
        
        # Scan mood-based directories
        mood_dirs = ['supportive_gentle', 'hopeful_uplifting', 'tense_to_calm', 
                    'reflective_emotional', 'energetic_motivating']
        
        for mood_dir in mood_dirs:
            mood_path = self.library_path / mood_dir
            if mood_path.exists():
                tracks = []
                for ext in audio_extensions:
                    tracks.extend(mood_path.glob(f'*{ext}'))
                
                self.tracks_by_mood[mood_dir] = [
                    MusicTrack(str(track)) for track in tracks
                ]
                self.all_tracks.extend(self.tracks_by_mood[mood_dir])
        
        print(f"Scanned music library: {len(self.all_tracks)} tracks across {len(self.tracks_by_mood)} moods")
    
    def get_best_track_for_mood(self, mood: str, duration: float = None, 
                               exclude_recent: List[str] = None) -> Optional[MusicTrack]:
        """Get the best track for a specific mood and duration"""
        
        # Get tracks for this mood
        mood_tracks = self.tracks_by_mood.get(mood, [])
        
        if not mood_tracks:
            # Fallback: analyze all tracks for mood compatibility
            mood_tracks = []
            for track in self.all_tracks:
                compatibility = track.get_mood_compatibility(mood)
                if compatibility > 0.6:  # Good compatibility threshold
                    mood_tracks.append((track, compatibility))
            
            # Sort by compatibility
            mood_tracks.sort(key=lambda x: x[1], reverse=True)
            mood_tracks = [track for track, score in mood_tracks[:10]]  # Top 10
        
        if not mood_tracks:
            return None
        
        # Filter by duration if specified
        if duration:
            suitable_tracks = []
            for track in mood_tracks:
                if track.duration == 0:  # Duration unknown, assume suitable
                    suitable_tracks.append(track)
                elif track.duration >= duration * 0.8:  # At least 80% of needed duration
                    suitable_tracks.append(track)
            
            mood_tracks = suitable_tracks if suitable_tracks else mood_tracks
        
        # Exclude recently used tracks
        if exclude_recent:
            excluded_names = [Path(path).name for path in exclude_recent]
            mood_tracks = [track for track in mood_tracks 
                          if track.file_path.name not in excluded_names]
        
        if not mood_tracks:
            return None
        
        # Return best track (for now, just the first one)
        # In the future, could add more sophisticated selection logic
        return mood_tracks[0]
    
    def add_track(self, file_path: str, mood: str, metadata: Dict = None) -> bool:
        """Add a new track to the library"""
        track = MusicTrack(file_path, metadata)
        
        if mood not in self.tracks_by_mood:
            self.tracks_by_mood[mood] = []
        
        self.tracks_by_mood[mood].append(track)
        self.all_tracks.append(track)
        
        return True
    
    def download_royalty_free_music(self, mood: str, count: int = 5) -> List[str]:
        """Download royalty-free music for a specific mood (placeholder)"""
        print(f"Royalty-free music download for '{mood}' mood not implemented yet")
        print("Available sources:")
        for source, url in self.royalty_free_sources.items():
            print(f"  • {source}: {url}")
        
        return []


class MusicSystemV2:
    """Advanced music intelligence system"""
    
    def __init__(self, library_path: str = None):
        if not library_path:
            library_path = Path(__file__).parent.parent / "assets" / "music"
        
        self.library = MusicLibrary(library_path)
        self.config_path = Path(__file__).parent.parent / "config" / "music_library.json"
        self.recent_tracks = []  # Track recently used music to avoid repetition
        self.max_recent_tracks = 20
        
        # Advanced mixing parameters
        self.mixing_presets = {
            'podcast_style': {
                'music_volume': 0.15,
                'duck_ratio': 0.25,
                'crossfade_duration': 3.0,
                'eq_settings': {'low_cut': 80, 'high_cut': 8000},
                'compression': {'ratio': 3.0, 'threshold': -20}
            },
            'documentary_style': {
                'music_volume': 0.20,
                'duck_ratio': 0.30,
                'crossfade_duration': 2.0,
                'eq_settings': {'low_cut': 60, 'high_cut': 10000},
                'compression': {'ratio': 2.5, 'threshold': -18}
            },
            'social_media': {
                'music_volume': 0.25,
                'duck_ratio': 0.40,
                'crossfade_duration': 1.5,
                'eq_settings': {'low_cut': 100, 'high_cut': 6000},
                'compression': {'ratio': 4.0, 'threshold': -16}
            }
        }
        
        # Load configuration
        self._load_config()
    
    def _load_config(self):
        """Load music library configuration"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                self.config = json.load(f)
        else:
            # Create default configuration
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default music library configuration"""
        default_config = {
            "version": "2.0",
            "description": "Music library configuration for Kiin Content Factory",
            "updated": datetime.now().isoformat(),
            
            "moods": {
                "supportive_gentle": {
                    "description": "Gentle, supportive background music for validation content",
                    "characteristics": ["warm", "nurturing", "peaceful", "comforting"],
                    "tempo_range": [60, 100],
                    "energy_level": "low",
                    "emotional_tone": "positive_calm",
                    "instruments": ["soft piano", "gentle strings", "acoustic guitar", "ambient pads"],
                    "avoid": ["percussion", "bass", "dramatic changes", "minor keys"]
                },
                
                "hopeful_uplifting": {
                    "description": "Positive, encouraging music for tips and advice content",
                    "characteristics": ["inspiring", "motivational", "bright", "forward-moving"],
                    "tempo_range": [80, 130],
                    "energy_level": "medium",
                    "emotional_tone": "optimistic",
                    "instruments": ["bright piano", "uplifting strings", "light percussion", "warm pads"],
                    "avoid": ["dark tones", "minor progressions", "sad melodies"]
                },
                
                "tense_to_calm": {
                    "description": "Music that transitions from tension to calm for chaos stories",
                    "characteristics": ["dynamic", "transitional", "resolving", "cathartic"],
                    "tempo_range": [70, 120],
                    "energy_level": "variable",
                    "emotional_tone": "transformative",
                    "instruments": ["building strings", "dynamic piano", "subtle percussion", "resolution pads"],
                    "avoid": ["static mood", "unchanging dynamics", "abrupt changes"]
                },
                
                "reflective_emotional": {
                    "description": "Deep, emotional music for confessions and personal stories",
                    "characteristics": ["intimate", "contemplative", "emotional", "vulnerable"],
                    "tempo_range": [50, 90],
                    "energy_level": "low",
                    "emotional_tone": "contemplative",
                    "instruments": ["solo piano", "intimate strings", "soft pads", "minimal arrangements"],
                    "avoid": ["busy arrangements", "bright tones", "fast rhythms", "complex harmonies"]
                },
                
                "energetic_motivating": {
                    "description": "Energetic, motivating music for sandwich generation content",
                    "characteristics": ["energetic", "driving", "confident", "empowering"],
                    "tempo_range": [110, 160],
                    "energy_level": "high",
                    "emotional_tone": "empowering",
                    "instruments": ["driving piano", "strong strings", "light percussion", "motivational builds"],
                    "avoid": ["slow tempos", "subdued energy", "sad progressions", "overly busy"]
                }
            },
            
            "content_type_mappings": {
                "validation": "supportive_gentle",
                "confessions": "reflective_emotional",
                "tips": "hopeful_uplifting",
                "sandwich_gen": "energetic_motivating",
                "chaos": "tense_to_calm",
                "general": "supportive_gentle"
            },
            
            "royalty_free_sources": {
                "recommended": [
                    {
                        "name": "Pixabay Music",
                        "url": "https://pixabay.com/music/",
                        "license": "Pixabay License (Free)",
                        "quality": "Good",
                        "search_terms": {
                            "supportive_gentle": ["ambient", "peaceful", "calm", "soft"],
                            "hopeful_uplifting": ["inspiring", "uplifting", "positive", "bright"],
                            "tense_to_calm": ["cinematic", "dramatic", "emotional journey"],
                            "reflective_emotional": ["emotional", "contemplative", "sad", "intimate"],
                            "energetic_motivating": ["energetic", "motivational", "upbeat", "driving"]
                        }
                    },
                    {
                        "name": "YouTube Audio Library",
                        "url": "https://studio.youtube.com/channel/music",
                        "license": "Creative Commons / YouTube License",
                        "quality": "High",
                        "search_terms": {
                            "supportive_gentle": ["ambient", "acoustic", "peaceful"],
                            "hopeful_uplifting": ["acoustic", "happy", "upbeat"],
                            "tense_to_calm": ["cinematic", "dramatic"],
                            "reflective_emotional": ["emotional", "sad", "ambient"],
                            "energetic_motivating": ["electronic", "upbeat", "rock"]
                        }
                    }
                ]
            },
            
            "file_organization": {
                "directory_structure": {
                    "supportive_gentle": "assets/music/supportive_gentle/",
                    "hopeful_uplifting": "assets/music/hopeful_uplifting/",
                    "tense_to_calm": "assets/music/tense_to_calm/",
                    "reflective_emotional": "assets/music/reflective_emotional/",
                    "energetic_motivating": "assets/music/energetic_motivating/"
                },
                "naming_convention": "{mood}_{tempo}bpm_{key}_{duration}s_{source}.{ext}",
                "metadata_file": "track_metadata.json"
            },
            
            "quality_standards": {
                "format": ["mp3", "wav", "aac"],
                "minimum_bitrate": "128kbps",
                "sample_rate": "44100Hz",
                "duration_range": [30, 600],  # 30 seconds to 10 minutes
                "volume_consistency": "normalized",
                "fade_requirements": {
                    "fade_in": "2-5 seconds",
                    "fade_out": "3-6 seconds",
                    "loop_ready": "seamless if possible"
                }
            }
        }
        
        # Save default configuration
        self.config_path.parent.mkdir(exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        self.config = default_config
    
    def select_music(self, content_type: str, duration: float = None, 
                    emotional_context: str = None) -> Optional[MusicTrack]:
        """Intelligently select music based on content and context"""
        
        # Map content type to mood
        content_mappings = self.config.get('content_type_mappings', {})
        base_mood = content_mappings.get(content_type, 'supportive_gentle')
        
        # Adjust mood based on emotional context
        if emotional_context:
            mood_adjustments = {
                'urgent': 'energetic_motivating',
                'sad': 'reflective_emotional',
                'hopeful': 'hopeful_uplifting',
                'chaotic': 'tense_to_calm',
                'gentle': 'supportive_gentle'
            }
            base_mood = mood_adjustments.get(emotional_context, base_mood)
        
        # Get best track from library
        track = self.library.get_best_track_for_mood(
            base_mood, duration, self.recent_tracks
        )
        
        if track:
            # Add to recent tracks
            self.recent_tracks.append(str(track.file_path))
            if len(self.recent_tracks) > self.max_recent_tracks:
                self.recent_tracks.pop(0)
        
        return track
    
    def detect_beats(self, track: MusicTrack) -> List[float]:
        """Detect beat positions in a track for sync purposes"""
        if not LIBROSA_AVAILABLE:
            print("Beat detection requires librosa library")
            return []
        
        if not track.file_path.exists():
            return []
        
        try:
            y, sr = librosa.load(str(track.file_path))
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            beat_times = librosa.frames_to_time(beats, sr=sr)
            return beat_times.tolist()
            
        except Exception as e:
            print(f"Beat detection error: {e}")
            return []
    
    def create_dynamic_mix(self, track: MusicTrack, speech_timestamps: List[Tuple[float, float]], 
                          total_duration: float, style: str = 'podcast_style') -> Dict:
        """Create dynamic music mix with intelligent ducking based on speech"""
        
        if style not in self.mixing_presets:
            style = 'podcast_style'
        
        preset = self.mixing_presets[style]
        
        # Calculate ducking segments
        duck_segments = []
        for start_time, end_time in speech_timestamps:
            duck_segments.append({
                'start': max(0, start_time - 0.2),  # Slight pre-duck
                'end': min(total_duration, end_time + 0.1),  # Slight post-duck
                'target_volume': preset['duck_ratio']
            })
        
        # Calculate music volume automation
        volume_automation = []
        current_time = 0.0
        base_volume = preset['music_volume']
        
        # Add fade-in
        volume_automation.append({
            'time': 0.0,
            'volume': 0.0,
            'fade_duration': preset['crossfade_duration']
        })
        
        volume_automation.append({
            'time': preset['crossfade_duration'],
            'volume': base_volume,
            'fade_duration': 0.0
        })
        
        # Add ducking automation
        for segment in duck_segments:
            # Duck down
            volume_automation.append({
                'time': segment['start'],
                'volume': base_volume * segment['target_volume'],
                'fade_duration': 0.1
            })
            
            # Duck up
            volume_automation.append({
                'time': segment['end'],
                'volume': base_volume,
                'fade_duration': 0.2
            })
        
        # Add fade-out
        fade_out_start = total_duration - preset['crossfade_duration']
        volume_automation.append({
            'time': fade_out_start,
            'volume': 0.0,
            'fade_duration': preset['crossfade_duration']
        })
        
        return {
            'track': track,
            'volume_automation': volume_automation,
            'eq_settings': preset.get('eq_settings', {}),
            'compression': preset.get('compression', {}),
            'total_duration': total_duration
        }
    
    def export_music_suggestions(self, content_type: str) -> Dict:
        """Export music suggestions for a content type"""
        mood = self.config['content_type_mappings'].get(content_type, 'supportive_gentle')
        mood_config = self.config['moods'].get(mood, {})
        
        return {
            'content_type': content_type,
            'recommended_mood': mood,
            'mood_config': mood_config,
            'available_tracks': len(self.library.tracks_by_mood.get(mood, [])),
            'royalty_free_sources': self.config.get('royalty_free_sources', {}),
            'search_terms': self._get_search_terms_for_mood(mood)
        }
    
    def _get_search_terms_for_mood(self, mood: str) -> List[str]:
        """Get search terms for finding royalty-free music for a mood"""
        sources = self.config.get('royalty_free_sources', {}).get('recommended', [])
        
        for source in sources:
            search_terms = source.get('search_terms', {})
            if mood in search_terms:
                return search_terms[mood]
        
        # Default search terms
        default_terms = {
            'supportive_gentle': ['ambient', 'peaceful', 'calm', 'soft'],
            'hopeful_uplifting': ['inspiring', 'uplifting', 'positive', 'bright'],
            'tense_to_calm': ['cinematic', 'dramatic', 'emotional'],
            'reflective_emotional': ['emotional', 'contemplative', 'intimate'],
            'energetic_motivating': ['energetic', 'motivational', 'upbeat']
        }
        
        return default_terms.get(mood, ['instrumental', 'background'])


# CLI interface
def main():
    """Main CLI interface for Music System V2"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Music Intelligence V2 - Advanced Music Selection")
    parser.add_argument('--content-type', type=str, 
                       help='Content type (validation, tips, confessions, etc.)')
    parser.add_argument('--mood', type=str,
                       help='Music mood (supportive_gentle, hopeful_uplifting, etc.)')
    parser.add_argument('--duration', type=float,
                       help='Required duration in seconds')
    parser.add_argument('--emotional-context', type=str,
                       help='Emotional context (urgent, sad, hopeful, etc.)')
    parser.add_argument('--suggest', action='store_true',
                       help='Get music suggestions for content type')
    parser.add_argument('--analyze', type=str,
                       help='Analyze a music file')
    parser.add_argument('--scan-library', action='store_true',
                       help='Scan and update music library')
    parser.add_argument('--library-path', type=str,
                       help='Path to music library')
    parser.add_argument('--create-structure', action='store_true',
                       help='Create music library directory structure')
    
    args = parser.parse_args()
    
    music_system = MusicSystemV2(args.library_path)
    
    if args.create_structure:
        # Create directory structure
        base_path = Path(args.library_path) if args.library_path else Path("assets/music")
        moods = ['supportive_gentle', 'hopeful_uplifting', 'tense_to_calm', 
                'reflective_emotional', 'energetic_motivating']
        
        for mood in moods:
            mood_dir = base_path / mood
            mood_dir.mkdir(parents=True, exist_ok=True)
            
            # Create README for each mood
            readme_path = mood_dir / "README.md"
            mood_config = music_system.config['moods'].get(mood, {})
            
            readme_content = f"""# {mood.replace('_', ' ').title()} Music

{mood_config.get('description', '')}

## Characteristics
{', '.join(mood_config.get('characteristics', []))}

## Requirements
- Tempo: {mood_config.get('tempo_range', [60, 120])[0]}-{mood_config.get('tempo_range', [60, 120])[1]} BPM
- Energy Level: {mood_config.get('energy_level', 'medium')}
- Instruments: {', '.join(mood_config.get('instruments', []))}

## Avoid
{', '.join(mood_config.get('avoid', []))}

## File Requirements
- Format: MP3, WAV, or AAC
- Duration: 30 seconds to 10 minutes
- Quality: 128kbps or higher
- Volume: Normalized and consistent
- Fades: 2-5 second fade-in, 3-6 second fade-out
"""
            
            readme_path.write_text(readme_content)
        
        print(f"✓ Created music library structure at {base_path}")
    
    elif args.scan_library:
        music_system.library._scan_library()
        print("✓ Music library scanned and updated")
    
    elif args.analyze:
        track = MusicTrack(args.analyze)
        print(f"Music Track Analysis: {track.file_path.name}")
        print(f"Duration: {track.duration:.1f} seconds")
        print(f"BPM: {track.bpm:.1f}" if track.bpm else "BPM: Unknown")
        print(f"Energy Level: {track.energy_level:.2f}")
        print(f"Valence: {track.valence:.2f}")
        print(f"Arousal: {track.arousal:.2f}")
        
        # Test mood compatibility
        moods = ['supportive_gentle', 'hopeful_uplifting', 'tense_to_calm', 
                'reflective_emotional', 'energetic_motivating']
        print("\nMood Compatibility:")
        for mood in moods:
            compatibility = track.get_mood_compatibility(mood)
            print(f"  {mood}: {compatibility:.2f}")
    
    elif args.suggest:
        if not args.content_type:
            print("Content type required for suggestions")
            return
        
        suggestions = music_system.export_music_suggestions(args.content_type)
        print(f"Music suggestions for '{args.content_type}' content:")
        print(f"Recommended mood: {suggestions['recommended_mood']}")
        print(f"Available tracks: {suggestions['available_tracks']}")
        print(f"Search terms: {', '.join(suggestions['search_terms'])}")
        
        mood_config = suggestions['mood_config']
        print(f"\nMood characteristics: {', '.join(mood_config.get('characteristics', []))}")
        print(f"Tempo range: {mood_config.get('tempo_range', [60, 120])}")
        print(f"Energy level: {mood_config.get('energy_level', 'medium')}")
    
    elif args.content_type or args.mood:
        # Select music
        content_type = args.content_type or 'general'
        
        track = music_system.select_music(
            content_type, args.duration, args.emotional_context
        )
        
        if track:
            print(f"Selected track: {track.file_path.name}")
            print(f"Duration: {track.duration:.1f}s")
            print(f"BPM: {track.bpm:.1f}" if track.bpm else "BPM: Unknown")
            print(f"Path: {track.file_path}")
        else:
            print("No suitable track found")
            suggestions = music_system.export_music_suggestions(content_type)
            print(f"\nTry downloading music for mood: {suggestions['recommended_mood']}")
            print(f"Search terms: {', '.join(suggestions['search_terms'])}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()