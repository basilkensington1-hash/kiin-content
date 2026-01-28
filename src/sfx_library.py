#!/usr/bin/env python3
"""
Sound Effects Library for Kiin Content - Professional SFX Management
Curated sound effects library for emotional accent and content enhancement
"""

import json
import os
import random
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Try to import audio generation libraries
try:
    import numpy as np
    from scipy.io import wavfile
    import scipy.signal as signal
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    print("scipy not available - procedural sound generation disabled")

try:
    from pydub import AudioSegment
    from pydub.generators import Sine, Square, Sawtooth, Triangle
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    print("pydub not available - sound synthesis disabled")


class SoundEffect:
    """Represents a sound effect with metadata and usage context"""
    
    def __init__(self, name: str, file_path: str = None, metadata: Dict = None):
        self.name = name
        self.file_path = Path(file_path) if file_path else None
        self.metadata = metadata or {}
        
        # Basic properties
        self.category = self.metadata.get('category', 'misc')
        self.duration = self.metadata.get('duration', 0.0)
        self.emotional_impact = self.metadata.get('emotional_impact', 'neutral')
        self.usage_context = self.metadata.get('usage_context', [])
        self.volume_level = self.metadata.get('volume_level', 0.7)
        
        # Quality and format info
        self.sample_rate = self.metadata.get('sample_rate', 44100)
        self.format = self.metadata.get('format', 'wav')
        self.channels = self.metadata.get('channels', 1)  # Mono by default for SFX
    
    def is_suitable_for_context(self, context: str, emotional_tone: str = None) -> bool:
        """Check if this SFX is suitable for a given context and emotional tone"""
        # Check usage context
        if context not in self.usage_context and 'general' not in self.usage_context:
            return False
        
        # Check emotional compatibility if specified
        if emotional_tone:
            compatible_emotions = {
                'notification': ['neutral', 'informative', 'attention'],
                'transition': ['smooth', 'neutral', 'flowing'],
                'emotional_accent': ['emotional', 'dramatic', 'touching'],
                'text_reveal': ['informative', 'neutral', 'engaging'],
                'ambient': ['calm', 'peaceful', 'background']
            }
            
            category_emotions = compatible_emotions.get(self.category, ['neutral'])
            if emotional_tone not in category_emotions and self.emotional_impact != emotional_tone:
                return False
        
        return True


class SFXGenerator:
    """Generate procedural sound effects when pre-made ones aren't available"""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
    
    def generate_notification_sound(self, style: str = 'gentle', duration: float = 0.5) -> Optional[str]:
        """Generate a notification sound"""
        if not PYDUB_AVAILABLE:
            return None
        
        try:
            if style == 'gentle':
                # Soft bell-like notification
                tone1 = Sine(800).to_audio_segment(duration=int(duration * 500))
                tone2 = Sine(1200).to_audio_segment(duration=int(duration * 300))
                
                # Apply envelope
                tone1 = tone1.fade_in(50).fade_out(200)
                tone2 = tone2.fade_in(100).fade_out(150)
                
                # Combine with slight delay
                notification = tone1.overlay(tone2, position=100)
                
            elif style == 'urgent':
                # More attention-getting notification
                tone1 = Square(600).to_audio_segment(duration=int(duration * 200))
                tone2 = Square(900).to_audio_segment(duration=int(duration * 200))
                tone3 = Square(600).to_audio_segment(duration=int(duration * 200))
                
                notification = tone1 + tone2 + tone3
                notification = notification.fade_in(20).fade_out(50)
                
            elif style == 'subtle':
                # Very subtle notification
                tone = Sine(1000).to_audio_segment(duration=int(duration * 1000))
                notification = tone.fade_in(100).fade_out(300)
                notification = notification - 20  # Reduce volume
                
            else:
                return None
            
            # Normalize and export
            notification = notification.normalize()
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            notification.export(temp_file.name, format='wav')
            
            return temp_file.name
            
        except Exception as e:
            print(f"Error generating notification sound: {e}")
            return None
    
    def generate_transition_whoosh(self, direction: str = 'forward', intensity: float = 0.5) -> Optional[str]:
        """Generate a transition whoosh sound"""
        if not (SCIPY_AVAILABLE and PYDUB_AVAILABLE):
            return None
        
        try:
            duration = 1.0  # 1 second whoosh
            t = np.linspace(0, duration, int(self.sample_rate * duration))
            
            # Create noise base
            noise = np.random.normal(0, 0.1, len(t))
            
            # Apply frequency sweep (whoosh effect)
            if direction == 'forward':
                freq_sweep = np.linspace(2000, 200, len(t)) * intensity
            elif direction == 'reverse':
                freq_sweep = np.linspace(200, 2000, len(t)) * intensity
            else:  # 'neutral'
                freq_sweep = np.ones(len(t)) * 800 * intensity
            
            # Apply sweep to noise
            whoosh = np.zeros_like(t)
            for i in range(len(t)):
                whoosh[i] = noise[i] * np.sin(2 * np.pi * freq_sweep[i] * t[i])
            
            # Apply envelope
            envelope = signal.windows.hann(len(t))
            whoosh *= envelope
            
            # Normalize
            whoosh = whoosh / np.max(np.abs(whoosh))
            
            # Convert to audio segment
            audio_data = (whoosh * 32767).astype(np.int16)
            audio_segment = AudioSegment(
                audio_data.tobytes(),
                frame_rate=self.sample_rate,
                sample_width=2,
                channels=1
            )
            
            # Export
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            audio_segment.export(temp_file.name, format='wav')
            
            return temp_file.name
            
        except Exception as e:
            print(f"Error generating whoosh: {e}")
            return None
    
    def generate_text_reveal_sound(self, style: str = 'typewriter') -> Optional[str]:
        """Generate text reveal sound effects"""
        if not PYDUB_AVAILABLE:
            return None
        
        try:
            if style == 'typewriter':
                # Short click sounds
                base_freq = 800
                duration_ms = 30
                
                clicks = []
                for i in range(5):  # 5 quick clicks
                    freq = base_freq + random.randint(-100, 100)
                    click = Square(freq).to_audio_segment(duration=duration_ms)
                    click = click.fade_in(5).fade_out(10)
                    clicks.append(click)
                
                # Combine with small gaps
                result = AudioSegment.empty()
                for i, click in enumerate(clicks):
                    if i > 0:
                        result += AudioSegment.silent(duration=10)
                    result += click
                
            elif style == 'digital':
                # Digital beep sequence
                freqs = [600, 800, 1000]
                result = AudioSegment.empty()
                
                for freq in freqs:
                    beep = Sine(freq).to_audio_segment(duration=50)
                    beep = beep.fade_in(10).fade_out(10)
                    result += beep + AudioSegment.silent(duration=20)
                
            elif style == 'gentle_chime':
                # Soft chime
                tone1 = Sine(880).to_audio_segment(duration=200)
                tone2 = Sine(1320).to_audio_segment(duration=150)
                
                result = tone1.overlay(tone2, position=50)
                result = result.fade_in(30).fade_out(80)
                
            else:
                return None
            
            # Normalize and export
            result = result.normalize()
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            result.export(temp_file.name, format='wav')
            
            return temp_file.name
            
        except Exception as e:
            print(f"Error generating text reveal sound: {e}")
            return None
    
    def generate_emotional_accent(self, emotion: str = 'touching') -> Optional[str]:
        """Generate emotional accent sounds"""
        if not PYDUB_AVAILABLE:
            return None
        
        try:
            if emotion == 'touching':
                # Soft, warm tone
                fundamental = 220  # A3
                harmonics = [1, 0.5, 0.3, 0.2]  # Harmonic series weights
                
                result = AudioSegment.empty()
                for i, weight in enumerate(harmonics):
                    freq = fundamental * (i + 1)
                    tone = Sine(freq).to_audio_segment(duration=800)
                    tone = tone - (20 - int(weight * 20))  # Adjust volume by harmonic weight
                    
                    if i == 0:
                        result = tone
                    else:
                        result = result.overlay(tone)
                
                result = result.fade_in(200).fade_out(300)
                
            elif emotion == 'hopeful':
                # Rising tones
                freqs = [330, 440, 550, 660]  # Rising progression
                result = AudioSegment.empty()
                
                for i, freq in enumerate(freqs):
                    tone = Sine(freq).to_audio_segment(duration=150)
                    tone = tone.fade_in(20).fade_out(50)
                    
                    if i == 0:
                        result = tone
                    else:
                        result += tone
                
            elif emotion == 'calming':
                # Low, warm drone
                base = Sine(110).to_audio_segment(duration=1000)  # Low A
                fifth = Sine(165).to_audio_segment(duration=1000)  # Perfect fifth
                
                result = base.overlay(fifth - 6)  # Fifth slightly quieter
                result = result.fade_in(300).fade_out(400)
                
            else:
                return None
            
            # Normalize and export
            result = result.normalize() - 10  # Keep emotional accents subtle
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            result.export(temp_file.name, format='wav')
            
            return temp_file.name
            
        except Exception as e:
            print(f"Error generating emotional accent: {e}")
            return None
    
    def generate_ambient_background(self, ambience: str = 'room_tone', duration: float = 10.0) -> Optional[str]:
        """Generate ambient background sounds"""
        if not (SCIPY_AVAILABLE and PYDUB_AVAILABLE):
            return None
        
        try:
            t = np.linspace(0, duration, int(self.sample_rate * duration))
            
            if ambience == 'room_tone':
                # Very subtle room tone
                noise = np.random.normal(0, 0.01, len(t))
                
                # Filter to remove harsh frequencies
                from scipy.signal import butter, filtfilt
                b, a = butter(4, 2000 / (self.sample_rate / 2), 'low')
                filtered_noise = filtfilt(b, a, noise)
                
                audio = filtered_noise
                
            elif ambience == 'nature_soft':
                # Soft nature ambience
                base_noise = np.random.normal(0, 0.02, len(t))
                
                # Add occasional soft bird-like tones
                for _ in range(int(duration / 3)):  # Every 3 seconds on average
                    start_idx = random.randint(0, len(t) - self.sample_rate)
                    freq = random.randint(800, 2000)
                    tone_duration = random.uniform(0.1, 0.5)
                    tone_samples = int(tone_duration * self.sample_rate)
                    
                    if start_idx + tone_samples < len(t):
                        tone = 0.005 * np.sin(2 * np.pi * freq * 
                                            np.linspace(0, tone_duration, tone_samples))
                        envelope = signal.windows.hann(len(tone))
                        tone *= envelope
                        
                        end_idx = start_idx + len(tone)
                        base_noise[start_idx:end_idx] += tone
                
                audio = base_noise
                
            else:
                return None
            
            # Normalize
            audio = audio / np.max(np.abs(audio)) * 0.3  # Keep ambient very quiet
            
            # Convert to audio segment
            audio_data = (audio * 32767).astype(np.int16)
            audio_segment = AudioSegment(
                audio_data.tobytes(),
                frame_rate=self.sample_rate,
                sample_width=2,
                channels=1
            )
            
            # Export
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            audio_segment.export(temp_file.name, format='wav')
            
            return temp_file.name
            
        except Exception as e:
            print(f"Error generating ambient background: {e}")
            return None


class SFXLibrary:
    """Sound effects library manager"""
    
    def __init__(self, library_path: str = None):
        if not library_path:
            library_path = Path(__file__).parent.parent / "assets" / "sfx"
        
        self.library_path = Path(library_path)
        self.config_path = Path(__file__).parent.parent / "config" / "sfx_catalog.json"
        self.generator = SFXGenerator()
        
        # Sound effect collections organized by category
        self.sfx_by_category = {}
        self.all_sfx = []
        
        # Initialize library
        self._load_config()
        self._scan_library()
    
    def _load_config(self):
        """Load SFX catalog configuration"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                self.config = json.load(f)
        else:
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default SFX catalog configuration"""
        default_config = {
            "version": "1.0",
            "description": "Sound Effects Catalog for Kiin Content Factory",
            "updated": datetime.now().isoformat(),
            
            "categories": {
                "notification": {
                    "description": "Sound effects for notifications and alerts in chaos content",
                    "usage_contexts": ["chaos_stories", "urgent_moments", "attention_grabbing"],
                    "characteristics": ["brief", "clear", "non-startling"],
                    "examples": [
                        "gentle_chime.wav",
                        "soft_bell.wav", 
                        "notification_pop.wav",
                        "subtle_ding.wav"
                    ],
                    "volume_range": [0.4, 0.7],
                    "duration_range": [0.2, 1.0]
                },
                
                "transition": {
                    "description": "Smooth transition sounds between content segments",
                    "usage_contexts": ["section_changes", "topic_shifts", "scene_transitions"],
                    "characteristics": ["smooth", "flowing", "non-jarring"],
                    "examples": [
                        "whoosh_soft.wav",
                        "swoosh_gentle.wav",
                        "wind_transition.wav",
                        "page_turn.wav"
                    ],
                    "volume_range": [0.3, 0.6],
                    "duration_range": [0.5, 2.0]
                },
                
                "emotional_accent": {
                    "description": "Subtle sounds to enhance emotional moments",
                    "usage_contexts": ["touching_moments", "realizations", "emotional_peaks"],
                    "characteristics": ["subtle", "emotional", "enhancing"],
                    "examples": [
                        "heart_warm.wav",
                        "touching_chord.wav",
                        "gentle_swell.wav",
                        "emotional_rise.wav"
                    ],
                    "volume_range": [0.2, 0.5],
                    "duration_range": [0.5, 3.0]
                },
                
                "text_reveal": {
                    "description": "Sounds for text appearing on screen",
                    "usage_contexts": ["text_animation", "quote_reveals", "tip_presentation"],
                    "characteristics": ["crisp", "informative", "engaging"],
                    "examples": [
                        "typewriter_click.wav",
                        "text_pop.wav",
                        "digital_beep.wav",
                        "key_tap.wav"
                    ],
                    "volume_range": [0.3, 0.6],
                    "duration_range": [0.1, 0.5]
                },
                
                "ambient": {
                    "description": "Background ambience and room tone",
                    "usage_contexts": ["background_fill", "atmosphere", "continuity"],
                    "characteristics": ["subtle", "continuous", "non-distracting"],
                    "examples": [
                        "room_tone_warm.wav",
                        "gentle_ambience.wav",
                        "soft_background.wav",
                        "peaceful_atmosphere.wav"
                    ],
                    "volume_range": [0.1, 0.3],
                    "duration_range": [10.0, 60.0]
                }
            },
            
            "content_type_mappings": {
                "validation": {
                    "preferred_categories": ["emotional_accent", "ambient"],
                    "avoid_categories": ["notification"],
                    "emotional_tone": "touching"
                },
                "confessions": {
                    "preferred_categories": ["emotional_accent", "ambient", "transition"],
                    "avoid_categories": ["notification"],
                    "emotional_tone": "intimate"
                },
                "tips": {
                    "preferred_categories": ["text_reveal", "transition", "ambient"],
                    "avoid_categories": ["emotional_accent"],
                    "emotional_tone": "informative"
                },
                "sandwich_gen": {
                    "preferred_categories": ["text_reveal", "transition", "notification"],
                    "avoid_categories": [],
                    "emotional_tone": "energetic"
                },
                "chaos": {
                    "preferred_categories": ["notification", "transition", "text_reveal"],
                    "avoid_categories": [],
                    "emotional_tone": "dramatic"
                }
            },
            
            "usage_guidelines": {
                "frequency": {
                    "notification": "Sparingly - only for important moments",
                    "transition": "Between major sections",
                    "emotional_accent": "At peak emotional moments",
                    "text_reveal": "For important text/quotes",
                    "ambient": "Throughout, very subtle"
                },
                
                "volume_mixing": {
                    "notification": "Clear but not overpowering",
                    "transition": "Subtle, supporting the flow",
                    "emotional_accent": "Barely audible, felt more than heard",
                    "text_reveal": "Clear but brief",
                    "ambient": "Almost inaudible, just filling silence"
                },
                
                "timing": {
                    "notification": "Sync with visual elements",
                    "transition": "Bridge content segments smoothly",
                    "emotional_accent": "At emotional peak, not before",
                    "text_reveal": "Sync with text animation",
                    "ambient": "Continuous, seamless loops"
                }
            },
            
            "quality_standards": {
                "format": "WAV preferred, MP3 acceptable",
                "sample_rate": "44100 Hz minimum",
                "bit_depth": "16-bit minimum",
                "channels": "Mono preferred for SFX",
                "normalization": "Normalized but not over-compressed",
                "fade_requirements": {
                    "notification": "Quick fade-in, natural decay",
                    "transition": "Smooth fade-in and fade-out",
                    "emotional_accent": "Gradual fade-in, long fade-out",
                    "text_reveal": "Quick fade-in, quick fade-out",
                    "ambient": "Seamless loops, no audible breaks"
                }
            }
        }
        
        # Save default configuration
        self.config_path.parent.mkdir(exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        self.config = default_config
    
    def _scan_library(self):
        """Scan library directory for sound effects"""
        if not self.library_path.exists():
            return
        
        audio_extensions = ['.wav', '.mp3', '.aac', '.m4a', '.ogg']
        
        # Scan category directories
        categories = list(self.config.get('categories', {}).keys())
        
        for category in categories:
            category_path = self.library_path / category
            if category_path.exists():
                sfx_files = []
                for ext in audio_extensions:
                    sfx_files.extend(category_path.glob(f'*{ext}'))
                
                category_sfx = []
                for sfx_file in sfx_files:
                    # Create SoundEffect object with basic metadata
                    metadata = {
                        'category': category,
                        'format': sfx_file.suffix[1:],
                        'usage_context': self.config['categories'][category].get('usage_contexts', [])
                    }
                    
                    sfx = SoundEffect(sfx_file.stem, str(sfx_file), metadata)
                    category_sfx.append(sfx)
                    self.all_sfx.append(sfx)
                
                self.sfx_by_category[category] = category_sfx
        
        print(f"Scanned SFX library: {len(self.all_sfx)} effects across {len(self.sfx_by_category)} categories")
    
    def get_sfx(self, category: str, context: str = None, emotional_tone: str = None) -> Optional[SoundEffect]:
        """Get a sound effect for specific category and context"""
        
        # Check if we have files for this category
        if category in self.sfx_by_category and self.sfx_by_category[category]:
            suitable_sfx = []
            for sfx in self.sfx_by_category[category]:
                if sfx.is_suitable_for_context(context or 'general', emotional_tone):
                    suitable_sfx.append(sfx)
            
            if suitable_sfx:
                return random.choice(suitable_sfx)
        
        # If no suitable file found, try to generate one procedurally
        return self._generate_fallback_sfx(category, context, emotional_tone)
    
    def _generate_fallback_sfx(self, category: str, context: str = None, 
                              emotional_tone: str = None) -> Optional[SoundEffect]:
        """Generate a fallback sound effect when no file is available"""
        
        generated_file = None
        
        if category == 'notification':
            style = 'gentle' if emotional_tone in ['touching', 'calm'] else 'subtle'
            generated_file = self.generator.generate_notification_sound(style)
            
        elif category == 'transition':
            direction = 'neutral'
            if context and 'forward' in context:
                direction = 'forward'
            elif context and 'back' in context:
                direction = 'reverse'
            generated_file = self.generator.generate_transition_whoosh(direction)
            
        elif category == 'text_reveal':
            style = 'gentle_chime' if emotional_tone == 'touching' else 'digital'
            generated_file = self.generator.generate_text_reveal_sound(style)
            
        elif category == 'emotional_accent':
            emotion = emotional_tone or 'touching'
            generated_file = self.generator.generate_emotional_accent(emotion)
            
        elif category == 'ambient':
            ambience = 'room_tone'
            generated_file = self.generator.generate_ambient_background(ambience)
        
        if generated_file:
            # Create SoundEffect object for generated file
            metadata = {
                'category': category,
                'generated': True,
                'format': 'wav',
                'usage_context': [context or 'general'],
                'emotional_impact': emotional_tone or 'neutral'
            }
            
            return SoundEffect(f"generated_{category}", generated_file, metadata)
        
        return None
    
    def get_sfx_for_content_type(self, content_type: str, sfx_type: str, 
                                context: str = None) -> Optional[SoundEffect]:
        """Get sound effect optimized for specific content type"""
        
        content_config = self.config.get('content_type_mappings', {}).get(content_type, {})
        
        # Check if this SFX type is preferred for this content type
        preferred = content_config.get('preferred_categories', [])
        avoided = content_config.get('avoid_categories', [])
        
        if sfx_type in avoided:
            return None
        
        emotional_tone = content_config.get('emotional_tone', 'neutral')
        
        return self.get_sfx(sfx_type, context, emotional_tone)
    
    def create_sfx_timing_map(self, content_duration: float, content_type: str) -> List[Dict]:
        """Create a timing map for when to use different sound effects"""
        
        timing_map = []
        content_config = self.config.get('content_type_mappings', {}).get(content_type, {})
        preferred_categories = content_config.get('preferred_categories', [])
        
        # Add ambient background for full duration if preferred
        if 'ambient' in preferred_categories:
            ambient_sfx = self.get_sfx('ambient', content_type)
            if ambient_sfx:
                timing_map.append({
                    'time': 0.0,
                    'sfx': ambient_sfx,
                    'volume': 0.15,
                    'fade_in': 2.0,
                    'fade_out': 2.0
                })
        
        # Add transition sounds at strategic points
        if 'transition' in preferred_categories and content_duration > 15:
            # Add transitions at 25%, 50%, 75% marks for longer content
            for percent in [0.25, 0.5, 0.75]:
                time_point = content_duration * percent
                transition_sfx = self.get_sfx('transition', 'section_change')
                if transition_sfx:
                    timing_map.append({
                        'time': time_point,
                        'sfx': transition_sfx,
                        'volume': 0.4,
                        'fade_in': 0.2,
                        'fade_out': 0.5
                    })
        
        # Add emotional accents for appropriate content
        if 'emotional_accent' in preferred_categories:
            # Place emotional accent at 60-70% through content (emotional peak)
            accent_time = content_duration * random.uniform(0.6, 0.7)
            accent_sfx = self.get_sfx('emotional_accent', 'touching_moment')
            if accent_sfx:
                timing_map.append({
                    'time': accent_time,
                    'sfx': accent_sfx,
                    'volume': 0.25,
                    'fade_in': 1.0,
                    'fade_out': 2.0
                })
        
        return timing_map
    
    def create_library_structure(self):
        """Create the directory structure for the SFX library"""
        categories = list(self.config.get('categories', {}).keys())
        
        for category in categories:
            category_dir = self.library_path / category
            category_dir.mkdir(parents=True, exist_ok=True)
            
            # Create README for each category
            readme_path = category_dir / "README.md"
            category_config = self.config['categories'][category]
            
            readme_content = f"""# {category.replace('_', ' ').title()} Sound Effects

{category_config.get('description', '')}

## Characteristics
{', '.join(category_config.get('characteristics', []))}

## Usage Contexts
{', '.join(category_config.get('usage_contexts', []))}

## Examples
{chr(10).join(f'- {example}' for example in category_config.get('examples', []))}

## Technical Requirements
- Volume Range: {category_config.get('volume_range', [0.3, 0.7])}
- Duration Range: {category_config.get('duration_range', [0.5, 2.0])} seconds
- Format: WAV preferred, 44.1kHz, 16-bit, mono
- Normalization: Yes, but preserve dynamics

## Usage Guidelines
{self.config.get('usage_guidelines', {}).get('frequency', {}).get(category, '')}

Volume: {self.config.get('usage_guidelines', {}).get('volume_mixing', {}).get(category, '')}

Timing: {self.config.get('usage_guidelines', {}).get('timing', {}).get(category, '')}
"""
            
            readme_path.write_text(readme_content)
        
        print(f"✓ Created SFX library structure at {self.library_path}")
    
    def validate_sfx_file(self, file_path: str, category: str) -> Dict:
        """Validate an SFX file for library inclusion"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {"valid": False, "error": "File not found"}
        
        # Check file format
        valid_formats = ['.wav', '.mp3', '.aac', '.m4a', '.ogg']
        if file_path.suffix.lower() not in valid_formats:
            return {"valid": False, "error": f"Invalid format. Use: {', '.join(valid_formats)}"}
        
        # Check category
        if category not in self.config.get('categories', {}):
            return {"valid": False, "error": f"Invalid category. Use: {', '.join(self.config.get('categories', {}).keys())}"}
        
        category_config = self.config['categories'][category]
        
        # Basic file validation
        try:
            if PYDUB_AVAILABLE:
                audio = AudioSegment.from_file(str(file_path))
                duration = len(audio) / 1000.0
                
                # Check duration range
                duration_range = category_config.get('duration_range', [0.1, 10.0])
                if not (duration_range[0] <= duration <= duration_range[1]):
                    return {
                        "valid": False, 
                        "error": f"Duration {duration:.1f}s outside range {duration_range[0]}-{duration_range[1]}s"
                    }
                
                return {
                    "valid": True,
                    "duration": duration,
                    "format": file_path.suffix,
                    "category": category,
                    "recommendations": [
                        f"Use volume range: {category_config.get('volume_range', [0.3, 0.7])}",
                        f"Usage contexts: {', '.join(category_config.get('usage_contexts', []))}",
                        "Normalize audio but preserve dynamics",
                        "Add appropriate fades as needed"
                    ]
                }
            else:
                return {"valid": True, "warning": "Could not analyze audio - pydub not available"}
                
        except Exception as e:
            return {"valid": False, "error": f"Audio analysis failed: {e}"}


# CLI interface
def main():
    """Main CLI interface for SFX Library"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sound Effects Library - Professional SFX Management")
    parser.add_argument('--category', type=str,
                       help='SFX category (notification, transition, emotional_accent, text_reveal, ambient)')
    parser.add_argument('--context', type=str,
                       help='Usage context')
    parser.add_argument('--emotional-tone', type=str,
                       help='Emotional tone')
    parser.add_argument('--content-type', type=str,
                       help='Content type (validation, tips, confessions, etc.)')
    parser.add_argument('--generate', type=str,
                       help='Generate SFX for category')
    parser.add_argument('--timing-map', type=float,
                       help='Create timing map for duration (seconds)')
    parser.add_argument('--validate', type=str,
                       help='Validate SFX file')
    parser.add_argument('--create-structure', action='store_true',
                       help='Create SFX library directory structure')
    parser.add_argument('--scan-library', action='store_true',
                       help='Scan and update SFX library')
    parser.add_argument('--library-path', type=str,
                       help='Path to SFX library')
    
    args = parser.parse_args()
    
    sfx_library = SFXLibrary(args.library_path)
    
    if args.create_structure:
        sfx_library.create_library_structure()
    
    elif args.scan_library:
        sfx_library._scan_library()
        print("✓ SFX library scanned and updated")
    
    elif args.validate:
        if not args.category:
            print("Category required for validation")
            return
        
        result = sfx_library.validate_sfx_file(args.validate, args.category)
        if result['valid']:
            print(f"✓ Valid SFX file: {args.validate}")
            print(f"  Duration: {result.get('duration', 'unknown')}")
            print(f"  Category: {result.get('category')}")
            print("  Recommendations:")
            for rec in result.get('recommendations', []):
                print(f"    • {rec}")
        else:
            print(f"✗ Invalid SFX file: {result['error']}")
    
    elif args.generate:
        sfx = sfx_library._generate_fallback_sfx(
            args.generate, args.context, args.emotional_tone
        )
        if sfx:
            print(f"✓ Generated SFX: {sfx.file_path}")
            print(f"  Category: {sfx.category}")
            print(f"  Emotional Impact: {sfx.emotional_impact}")
        else:
            print(f"✗ Could not generate SFX for category: {args.generate}")
    
    elif args.timing_map and args.content_type:
        timing_map = sfx_library.create_sfx_timing_map(args.timing_map, args.content_type)
        
        print(f"SFX Timing Map for {args.content_type} ({args.timing_map:.1f}s):")
        for event in timing_map:
            sfx_name = event['sfx'].name if event['sfx'] else 'None'
            print(f"  {event['time']:5.1f}s: {sfx_name} (vol: {event['volume']:.2f})")
    
    elif args.category:
        sfx = None
        if args.content_type:
            sfx = sfx_library.get_sfx_for_content_type(
                args.content_type, args.category, args.context
            )
        else:
            sfx = sfx_library.get_sfx(args.category, args.context, args.emotional_tone)
        
        if sfx:
            print(f"Selected SFX: {sfx.name}")
            print(f"Category: {sfx.category}")
            if sfx.file_path:
                print(f"File: {sfx.file_path}")
            print(f"Usage Context: {', '.join(sfx.usage_context)}")
        else:
            print(f"No suitable SFX found for category: {args.category}")
    
    else:
        parser.print_help()
        print("\nAvailable categories:", ", ".join(sfx_library.config.get('categories', {}).keys()))


if __name__ == "__main__":
    main()