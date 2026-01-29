#!/usr/bin/env python3
"""
Audio Mixer V2 for Kiin Content - Professional Multi-Track Audio Engine
Advanced audio mixing with compression, EQ, multi-track support and export options
"""

import json
import os
import subprocess
import tempfile
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime

# Try to import audio processing libraries
try:
    from pydub import AudioSegment, effects
    from pydub.utils import make_chunks
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    print("pydub not available - advanced audio processing disabled")

try:
    import numpy as np
    from scipy.signal import butter, filtfilt, resample
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    print("scipy not available - advanced signal processing disabled")


class AudioTrack:
    """Represents an audio track with processing parameters"""
    
    def __init__(self, file_path: str, track_type: str = 'unknown', metadata: Dict = None):
        self.file_path = Path(file_path)
        self.track_type = track_type  # 'speech', 'music', 'sfx', 'ambient'
        self.metadata = metadata or {}
        
        # Audio properties
        self.audio_segment = None
        self.duration = 0.0
        self.sample_rate = 44100
        self.channels = 2
        
        # Processing parameters
        self.volume = 1.0
        self.start_time = 0.0
        self.fade_in = 0.0
        self.fade_out = 0.0
        self.eq_settings = {}
        self.compression = {}
        self.automation = []
        
        # Load audio
        self._load_audio()
    
    def _load_audio(self):
        """Load audio file and extract properties"""
        if not self.file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {self.file_path}")
        
        if PYDUB_AVAILABLE:
            try:
                self.audio_segment = AudioSegment.from_file(str(self.file_path))
                self.duration = len(self.audio_segment) / 1000.0  # Convert to seconds
                self.sample_rate = self.audio_segment.frame_rate
                self.channels = self.audio_segment.channels
                
            except Exception as e:
                raise Exception(f"Could not load audio file {self.file_path}: {e}")
        else:
            raise Exception("pydub required for audio loading")
    
    def apply_volume(self, volume: float):
        """Apply volume change to the track"""
        if self.audio_segment:
            self.volume = volume
            db_change = 20 * np.log10(volume) if volume > 0 else -60
            self.audio_segment = self.audio_segment + db_change
    
    def apply_fade(self, fade_in: float = 0.0, fade_out: float = 0.0):
        """Apply fade in/out to the track"""
        if self.audio_segment:
            self.fade_in = fade_in
            self.fade_out = fade_out
            
            if fade_in > 0:
                fade_in_ms = int(fade_in * 1000)
                self.audio_segment = self.audio_segment.fade_in(fade_in_ms)
            
            if fade_out > 0:
                fade_out_ms = int(fade_out * 1000)
                self.audio_segment = self.audio_segment.fade_out(fade_out_ms)
    
    def apply_eq(self, eq_settings: Dict):
        """Apply EQ to the track using pydub effects"""
        if not self.audio_segment or not PYDUB_AVAILABLE:
            return
        
        self.eq_settings = eq_settings
        
        # Apply high-pass filter if specified
        if 'low_cut' in eq_settings:
            # Simulate high-pass with low-shelf reduction
            self.audio_segment = effects.low_pass_filter(
                self.audio_segment, eq_settings['low_cut'] * 8
            )
        
        # Apply low-pass filter if specified
        if 'high_cut' in eq_settings:
            self.audio_segment = effects.low_pass_filter(
                self.audio_segment, eq_settings['high_cut']
            )
        
        # Apply bass and treble adjustments
        if 'bass_gain' in eq_settings:
            # Boost/cut bass frequencies
            bass_gain = eq_settings['bass_gain']
            if bass_gain != 0:
                self.audio_segment = self.audio_segment + bass_gain
        
        if 'treble_gain' in eq_settings:
            # Boost/cut treble frequencies
            treble_gain = eq_settings['treble_gain']
            if treble_gain != 0:
                # Simple treble adjustment (not true EQ, but better than nothing)
                self.audio_segment = effects.low_pass_filter(
                    self.audio_segment, 8000
                ) + treble_gain
    
    def apply_compression(self, compression: Dict):
        """Apply dynamic range compression"""
        if not self.audio_segment or not PYDUB_AVAILABLE:
            return
        
        self.compression = compression
        
        # pydub has basic normalization and compression
        if compression.get('normalize', False):
            self.audio_segment = effects.normalize(self.audio_segment)
        
        # Simple compression simulation using dynamic range reduction
        threshold = compression.get('threshold', -20)  # dB
        ratio = compression.get('ratio', 3.0)
        
        # This is a simplified compression - real compression requires more advanced processing
        if threshold > -60:  # Only apply if threshold is reasonable
            compressed = effects.compress_dynamic_range(
                self.audio_segment, threshold=threshold, ratio=ratio
            )
            self.audio_segment = compressed
    
    def get_processed_audio(self) -> AudioSegment:
        """Get the fully processed audio segment"""
        return self.audio_segment


class AudioMixerV2:
    """Professional multi-track audio mixer"""
    
    def __init__(self):
        self.tracks = []
        self.config_path = Path(__file__).parent.parent / "config" / "audio_presets.json"
        self.sample_rate = 44100
        self.channels = 2
        self.master_volume = 1.0
        
        # Load mixing presets
        self._load_presets()
        
        # Master bus effects
        self.master_eq = {}
        self.master_compression = {}
        self.master_limiter = {}
        
        # Mixing state
        self.mixed_audio = None
        self.mix_duration = 0.0
    
    def _load_presets(self):
        """Load audio mixing presets"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                self.presets = json.load(f)
        else:
            self._create_default_presets()
    
    def _create_default_presets(self):
        """Create default audio mixing presets"""
        default_presets = {
            "version": "2.0",
            "description": "Audio mixing presets for Kiin Content Factory",
            "updated": datetime.now().isoformat(),
            
            "content_presets": {
                "podcast_standard": {
                    "description": "Standard podcast mixing for voice-heavy content",
                    "target_lufs": -16,
                    "peak_limit": -1,
                    "sample_rate": 44100,
                    "channels": 2,
                    
                    "track_settings": {
                        "speech": {
                            "volume": 1.0,
                            "compression": {
                                "threshold": -18,
                                "ratio": 3.0,
                                "attack": 10,
                                "release": 100,
                                "normalize": True
                            },
                            "eq": {
                                "low_cut": 80,
                                "high_cut": 8000,
                                "presence_boost": 2  # 3kHz area
                            }
                        },
                        "music": {
                            "volume": 0.15,
                            "compression": {
                                "threshold": -24,
                                "ratio": 2.0,
                                "attack": 20,
                                "release": 200,
                                "normalize": False
                            },
                            "eq": {
                                "low_cut": 60,
                                "high_cut": 10000,
                                "mid_cut": -3  # Reduce mids to make space for voice
                            },
                            "ducking": {
                                "enabled": True,
                                "threshold": -30,
                                "ratio": 4.0,
                                "attack": 5,
                                "release": 50
                            }
                        },
                        "sfx": {
                            "volume": 0.4,
                            "compression": {
                                "threshold": -20,
                                "ratio": 2.5,
                                "attack": 1,
                                "release": 50,
                                "normalize": False
                            },
                            "eq": {
                                "low_cut": 100,
                                "high_cut": 6000
                            }
                        }
                    },
                    
                    "master_bus": {
                        "eq": {
                            "low_cut": 40,
                            "high_cut": 15000,
                            "warmth_boost": 1  # Slight low-mid warmth
                        },
                        "compression": {
                            "threshold": -12,
                            "ratio": 2.0,
                            "attack": 30,
                            "release": 300,
                            "makeup_gain": 2
                        },
                        "limiter": {
                            "threshold": -1,
                            "release": 50
                        }
                    }
                },
                
                "documentary_style": {
                    "description": "Cinematic documentary mixing with emotional music",
                    "target_lufs": -14,
                    "peak_limit": -0.5,
                    
                    "track_settings": {
                        "speech": {
                            "volume": 1.0,
                            "compression": {
                                "threshold": -16,
                                "ratio": 2.5,
                                "attack": 15,
                                "release": 150
                            },
                            "eq": {
                                "low_cut": 70,
                                "high_cut": 10000,
                                "presence_boost": 3
                            }
                        },
                        "music": {
                            "volume": 0.25,
                            "compression": {
                                "threshold": -20,
                                "ratio": 1.8,
                                "attack": 50,
                                "release": 300
                            },
                            "eq": {
                                "low_cut": 50,
                                "bass_warmth": 2,
                                "mid_cut": -2
                            },
                            "ducking": {
                                "enabled": True,
                                "threshold": -25,
                                "ratio": 3.0,
                                "attack": 10,
                                "release": 100
                            }
                        }
                    }
                },
                
                "social_media_punchy": {
                    "description": "Punchy mix for social media with strong presence",
                    "target_lufs": -12,
                    "peak_limit": -0.1,
                    
                    "track_settings": {
                        "speech": {
                            "volume": 1.0,
                            "compression": {
                                "threshold": -14,
                                "ratio": 4.0,
                                "attack": 5,
                                "release": 80
                            },
                            "eq": {
                                "low_cut": 100,
                                "presence_boost": 4,
                                "brightness": 2
                            }
                        },
                        "music": {
                            "volume": 0.3,
                            "compression": {
                                "threshold": -16,
                                "ratio": 3.0,
                                "attack": 10,
                                "release": 100
                            },
                            "eq": {
                                "bass_boost": 2,
                                "mid_cut": -4
                            }
                        }
                    }
                },
                
                "audiobook_clear": {
                    "description": "Clear, focused mixing for speech-only content",
                    "target_lufs": -18,
                    "peak_limit": -2,
                    
                    "track_settings": {
                        "speech": {
                            "volume": 1.0,
                            "compression": {
                                "threshold": -20,
                                "ratio": 2.0,
                                "attack": 20,
                                "release": 200
                            },
                            "eq": {
                                "low_cut": 80,
                                "high_cut": 8000,
                                "clarity_boost": 2
                            }
                        },
                        "ambient": {
                            "volume": 0.1,
                            "eq": {
                                "low_cut": 200,
                                "high_cut": 4000
                            }
                        }
                    }
                }
            },
            
            "export_formats": {
                "podcast_mp3": {
                    "format": "mp3",
                    "bitrate": "128k",
                    "sample_rate": 44100,
                    "channels": 2,
                    "quality": "standard"
                },
                "youtube_aac": {
                    "format": "aac",
                    "bitrate": "192k",
                    "sample_rate": 48000,
                    "channels": 2,
                    "quality": "high"
                },
                "instagram_mp3": {
                    "format": "mp3",
                    "bitrate": "128k",
                    "sample_rate": 44100,
                    "channels": 2,
                    "loudness": -12  # LUFS
                },
                "high_quality_wav": {
                    "format": "wav",
                    "sample_rate": 48000,
                    "channels": 2,
                    "bit_depth": 24
                }
            },
            
            "quality_standards": {
                "speech_intelligibility": {
                    "frequency_range": [300, 3400],  # Phone quality range
                    "snr_minimum": 20,  # Signal to noise ratio in dB
                    "dynamic_range_target": [6, 12]  # dB range
                },
                "music_quality": {
                    "frequency_range": [20, 20000],
                    "dynamic_range_target": [8, 16],
                    "stereo_imaging": "centered_mono_compatible"
                },
                "master_output": {
                    "peak_limit": -0.1,  # True peak limit
                    "lufs_range": [-18, -12],  # Acceptable LUFS range
                    "phase_coherence": "mono_compatible"
                }
            },
            
            "automation_templates": {
                "speech_ducking": {
                    "description": "Automatic music ducking during speech",
                    "detection_threshold": -40,  # dB
                    "duck_amount": 0.3,  # Multiply music by this when speech detected
                    "attack_time": 0.1,  # seconds
                    "release_time": 0.5   # seconds
                },
                "fade_transitions": {
                    "default_fade_in": 1.0,
                    "default_fade_out": 2.0,
                    "crossfade_duration": 3.0
                }
            }
        }
        
        # Save default presets
        self.config_path.parent.mkdir(exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(default_presets, f, indent=2)
        
        self.presets = default_presets
    
    def add_track(self, file_path: str, track_type: str, start_time: float = 0.0, 
                  metadata: Dict = None) -> AudioTrack:
        """Add a track to the mix"""
        track = AudioTrack(file_path, track_type, metadata)
        track.start_time = start_time
        self.tracks.append(track)
        return track
    
    def apply_preset(self, preset_name: str):
        """Apply a mixing preset to all tracks"""
        if preset_name not in self.presets.get('content_presets', {}):
            raise ValueError(f"Unknown preset: {preset_name}")
        
        preset = self.presets['content_presets'][preset_name]
        
        # Apply track-specific settings
        for track in self.tracks:
            track_type = track.track_type
            if track_type in preset.get('track_settings', {}):
                track_settings = preset['track_settings'][track_type]
                
                # Apply volume
                if 'volume' in track_settings:
                    track.apply_volume(track_settings['volume'])
                
                # Apply EQ
                if 'eq' in track_settings:
                    track.apply_eq(track_settings['eq'])
                
                # Apply compression
                if 'compression' in track_settings:
                    track.apply_compression(track_settings['compression'])
        
        # Set master bus settings
        if 'master_bus' in preset:
            master_bus = preset['master_bus']
            self.master_eq = master_bus.get('eq', {})
            self.master_compression = master_bus.get('compression', {})
            self.master_limiter = master_bus.get('limiter', {})
    
    def create_speech_automation(self, speech_track: AudioTrack, 
                                music_tracks: List[AudioTrack]) -> List[Dict]:
        """Create automation for ducking music during speech"""
        if not PYDUB_AVAILABLE or not SCIPY_AVAILABLE:
            return []
        
        automation_events = []
        
        # Analyze speech track for silent vs speaking sections
        speech_audio = speech_track.get_processed_audio()
        
        # Convert to numpy array for analysis
        samples = np.array(speech_audio.get_array_of_samples())
        if speech_audio.channels == 2:
            samples = samples.reshape((-1, 2))
            samples = samples.mean(axis=1)  # Convert to mono
        
        # Detect speech activity using simple energy-based VAD
        frame_size = int(self.sample_rate * 0.1)  # 100ms frames
        hop_size = int(frame_size / 2)  # 50% overlap
        
        speech_segments = []
        for i in range(0, len(samples) - frame_size, hop_size):
            frame = samples[i:i + frame_size]
            energy = np.sum(frame ** 2)
            
            # Simple threshold-based speech detection
            threshold = np.max(samples ** 2) * 0.01  # 1% of peak energy
            
            time_start = i / self.sample_rate
            time_end = (i + frame_size) / self.sample_rate
            
            if energy > threshold:
                speech_segments.append((time_start, time_end, 'speech'))
            else:
                speech_segments.append((time_start, time_end, 'silence'))
        
        # Create ducking automation based on speech segments
        automation_template = self.presets.get('automation_templates', {}).get('speech_ducking', {})
        duck_amount = automation_template.get('duck_amount', 0.3)
        attack_time = automation_template.get('attack_time', 0.1)
        release_time = automation_template.get('release_time', 0.5)
        
        current_state = 'silence'
        for start_time, end_time, activity in speech_segments:
            if activity != current_state:
                if activity == 'speech':
                    # Duck music down
                    automation_events.append({
                        'time': start_time,
                        'action': 'duck_down',
                        'target_tracks': [track for track in music_tracks],
                        'target_volume': duck_amount,
                        'fade_duration': attack_time
                    })
                else:
                    # Bring music back up
                    automation_events.append({
                        'time': start_time,
                        'action': 'duck_up', 
                        'target_tracks': [track for track in music_tracks],
                        'target_volume': 1.0,
                        'fade_duration': release_time
                    })
                
                current_state = activity
        
        return automation_events
    
    def mix_tracks(self, total_duration: float = None) -> AudioSegment:
        """Mix all tracks together"""
        if not self.tracks:
            raise ValueError("No tracks to mix")
        
        if not PYDUB_AVAILABLE:
            raise Exception("pydub required for mixing")
        
        # Determine mix duration
        if total_duration is None:
            max_end_time = 0
            for track in self.tracks:
                track_end = track.start_time + track.duration
                max_end_time = max(max_end_time, track_end)
            total_duration = max_end_time
        
        self.mix_duration = total_duration
        
        # Create silent base track
        mix_duration_ms = int(total_duration * 1000)
        mixed = AudioSegment.silent(duration=mix_duration_ms, frame_rate=self.sample_rate)
        
        # Mix each track
        for track in self.tracks:
            processed_audio = track.get_processed_audio()
            
            # Position track at correct time
            start_ms = int(track.start_time * 1000)
            
            # Overlay the track
            mixed = mixed.overlay(processed_audio, position=start_ms)
        
        # Apply master bus processing
        self._apply_master_bus_processing(mixed)
        
        self.mixed_audio = mixed
        return mixed
    
    def _apply_master_bus_processing(self, audio: AudioSegment):
        """Apply master bus EQ, compression, and limiting"""
        if not PYDUB_AVAILABLE:
            return audio
        
        # Apply master EQ
        if self.master_eq:
            if 'low_cut' in self.master_eq:
                # High-pass filter
                cutoff = self.master_eq['low_cut']
                if cutoff > 20:
                    audio = effects.high_pass_filter(audio, cutoff)
            
            if 'high_cut' in self.master_eq:
                # Low-pass filter
                cutoff = self.master_eq['high_cut']
                if cutoff < 20000:
                    audio = effects.low_pass_filter(audio, cutoff)
        
        # Apply master compression
        if self.master_compression:
            threshold = self.master_compression.get('threshold', -12)
            ratio = self.master_compression.get('ratio', 2.0)
            makeup_gain = self.master_compression.get('makeup_gain', 0)
            
            audio = effects.compress_dynamic_range(audio, threshold=threshold, ratio=ratio)
            
            if makeup_gain != 0:
                audio = audio + makeup_gain
        
        # Apply master limiter (basic peak limiting)
        if self.master_limiter:
            threshold_db = self.master_limiter.get('threshold', -1)
            audio = effects.normalize(audio, headroom=abs(threshold_db))
        
        return audio
    
    def analyze_mix_quality(self) -> Dict:
        """Analyze the quality metrics of the mixed audio"""
        if not self.mixed_audio:
            raise ValueError("No mixed audio to analyze")
        
        if not SCIPY_AVAILABLE:
            return {"error": "scipy required for audio analysis"}
        
        # Convert to numpy array
        samples = np.array(self.mixed_audio.get_array_of_samples())
        if self.mixed_audio.channels == 2:
            samples = samples.reshape((-1, 2))
            # Use left channel for analysis
            samples = samples[:, 0]
        
        # Calculate metrics
        peak_level = np.max(np.abs(samples)) / 32768.0  # Normalize to -1 to 1
        peak_db = 20 * np.log10(peak_level) if peak_level > 0 else -96
        
        # RMS level calculation
        rms = np.sqrt(np.mean(samples ** 2)) / 32768.0
        rms_db = 20 * np.log10(rms) if rms > 0 else -96
        
        # Dynamic range (simplified)
        window_size = int(self.sample_rate * 0.1)  # 100ms windows
        window_rms = []
        for i in range(0, len(samples) - window_size, window_size):
            window = samples[i:i + window_size]
            window_rms.append(np.sqrt(np.mean(window ** 2)))
        
        if window_rms:
            dynamic_range = 20 * np.log10(np.max(window_rms) / np.mean(window_rms)) if np.mean(window_rms) > 0 else 0
        else:
            dynamic_range = 0
        
        # Estimate LUFS (simplified - not true ITU-R BS.1770)
        estimated_lufs = rms_db + 3  # Rough approximation
        
        return {
            "peak_level_db": peak_db,
            "rms_level_db": rms_db,
            "estimated_lufs": estimated_lufs,
            "dynamic_range_db": dynamic_range,
            "duration_seconds": self.mix_duration,
            "sample_rate": self.sample_rate,
            "channels": self.mixed_audio.channels,
            "quality_assessment": self._assess_quality(peak_db, estimated_lufs, dynamic_range)
        }
    
    def _assess_quality(self, peak_db: float, lufs: float, dynamic_range: float) -> Dict:
        """Assess the quality of the mix based on standards"""
        assessment = {
            "overall": "good",
            "issues": [],
            "recommendations": []
        }
        
        # Check peak levels
        if peak_db > -0.1:
            assessment["issues"].append("Peak level too high - risk of clipping")
            assessment["recommendations"].append("Apply limiting or reduce master volume")
            assessment["overall"] = "poor"
        elif peak_db > -1:
            assessment["issues"].append("Peak level close to maximum")
            assessment["recommendations"].append("Consider reducing peak level for safety")
            if assessment["overall"] == "good":
                assessment["overall"] = "fair"
        
        # Check LUFS for different platforms
        if lufs > -12:
            assessment["issues"].append("Very loud mix - may be limited by streaming platforms")
            assessment["recommendations"].append("Consider reducing overall level")
            if assessment["overall"] in ["good", "fair"]:
                assessment["overall"] = "fair"
        elif lufs < -20:
            assessment["issues"].append("Very quiet mix - may lack impact")
            assessment["recommendations"].append("Consider increasing overall level")
            if assessment["overall"] == "good":
                assessment["overall"] = "fair"
        
        # Check dynamic range
        if dynamic_range < 3:
            assessment["issues"].append("Very compressed - lack of dynamics")
            assessment["recommendations"].append("Reduce compression ratio or threshold")
            if assessment["overall"] in ["good", "fair"]:
                assessment["overall"] = "fair"
        elif dynamic_range > 20:
            assessment["issues"].append("Very wide dynamic range - may not translate well")
            assessment["recommendations"].append("Consider gentle compression")
        
        return assessment
    
    def export_mix(self, output_path: str, export_format: str = "podcast_mp3") -> bool:
        """Export the mixed audio in specified format"""
        if not self.mixed_audio:
            raise ValueError("No mixed audio to export")
        
        if export_format not in self.presets.get('export_formats', {}):
            raise ValueError(f"Unknown export format: {export_format}")
        
        format_settings = self.presets['export_formats'][export_format]
        
        try:
            # Apply format-specific processing
            export_audio = self.mixed_audio
            
            # Resample if needed
            target_sr = format_settings.get('sample_rate', 44100)
            if target_sr != export_audio.frame_rate:
                export_audio = export_audio.set_frame_rate(target_sr)
            
            # Convert channels if needed
            target_channels = format_settings.get('channels', 2)
            if target_channels == 1 and export_audio.channels == 2:
                export_audio = export_audio.set_channels(1)
            elif target_channels == 2 and export_audio.channels == 1:
                export_audio = export_audio.set_channels(2)
            
            # Apply loudness normalization if specified
            if 'loudness' in format_settings:
                target_lufs = format_settings['loudness']
                current_analysis = self.analyze_mix_quality()
                current_lufs = current_analysis.get('estimated_lufs', -16)
                
                # Adjust gain to match target LUFS (simplified)
                lufs_difference = target_lufs - current_lufs
                export_audio = export_audio + lufs_difference
            
            # Export based on format
            audio_format = format_settings.get('format', 'mp3')
            bitrate = format_settings.get('bitrate', '128k')
            
            if audio_format == 'mp3':
                export_audio.export(
                    output_path,
                    format="mp3",
                    bitrate=bitrate
                )
            elif audio_format == 'aac':
                export_audio.export(
                    output_path,
                    format="mp4",
                    codec="aac",
                    bitrate=bitrate
                )
            elif audio_format == 'wav':
                export_audio.export(
                    output_path,
                    format="wav"
                )
            else:
                raise ValueError(f"Unsupported export format: {audio_format}")
            
            return True
            
        except Exception as e:
            print(f"Export error: {e}")
            return False
    
    def create_stems(self, output_dir: str) -> List[str]:
        """Export individual tracks as stems for external mixing"""
        if not self.tracks:
            raise ValueError("No tracks to export as stems")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        exported_files = []
        
        for i, track in enumerate(self.tracks):
            # Create filename
            stem_name = f"stem_{i:02d}_{track.track_type}_{track.file_path.stem}.wav"
            stem_path = output_path / stem_name
            
            # Export processed track
            processed_audio = track.get_processed_audio()
            
            # Pad with silence to match mix duration
            if self.mix_duration > 0:
                mix_duration_ms = int(self.mix_duration * 1000)
                start_ms = int(track.start_time * 1000)
                
                # Create full-length track with silence padding
                full_track = AudioSegment.silent(duration=mix_duration_ms, frame_rate=self.sample_rate)
                full_track = full_track.overlay(processed_audio, position=start_ms)
                
                full_track.export(str(stem_path), format="wav")
            else:
                processed_audio.export(str(stem_path), format="wav")
            
            exported_files.append(str(stem_path))
        
        return exported_files
    
    def get_mixing_report(self) -> Dict:
        """Generate a comprehensive mixing report"""
        report = {
            "mix_info": {
                "total_tracks": len(self.tracks),
                "mix_duration": self.mix_duration,
                "sample_rate": self.sample_rate,
                "channels": self.channels
            },
            "track_breakdown": [],
            "quality_analysis": {},
            "recommendations": []
        }
        
        # Track breakdown
        for i, track in enumerate(self.tracks):
            track_info = {
                "track_number": i + 1,
                "type": track.track_type,
                "file_name": track.file_path.name,
                "duration": track.duration,
                "start_time": track.start_time,
                "volume": track.volume,
                "processing": {
                    "eq_applied": bool(track.eq_settings),
                    "compression_applied": bool(track.compression),
                    "fade_in": track.fade_in,
                    "fade_out": track.fade_out
                }
            }
            report["track_breakdown"].append(track_info)
        
        # Quality analysis
        if self.mixed_audio:
            report["quality_analysis"] = self.analyze_mix_quality()
        
        # General recommendations
        speech_tracks = [t for t in self.tracks if t.track_type == 'speech']
        music_tracks = [t for t in self.tracks if t.track_type == 'music']
        
        if len(speech_tracks) > 1:
            report["recommendations"].append("Multiple speech tracks detected - ensure proper timing")
        
        if len(music_tracks) > 1:
            report["recommendations"].append("Multiple music tracks - consider volume balance")
        
        if not music_tracks and len(self.tracks) == 1:
            report["recommendations"].append("Consider adding subtle background music")
        
        return report


# CLI interface
def main():
    """Main CLI interface for Audio Mixer V2"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Audio Mixer V2 - Professional Multi-Track Mixer")
    parser.add_argument('--speech', type=str, help='Speech/voice audio file')
    parser.add_argument('--music', type=str, help='Background music file')
    parser.add_argument('--sfx', type=str, nargs='+', help='Sound effects files')
    parser.add_argument('--preset', type=str, default='podcast_standard',
                       help='Mixing preset to apply')
    parser.add_argument('--output', type=str, help='Output file path')
    parser.add_argument('--format', type=str, default='podcast_mp3',
                       help='Export format')
    parser.add_argument('--duration', type=float,
                       help='Total mix duration (seconds)')
    parser.add_argument('--analyze', action='store_true',
                       help='Analyze mix quality only')
    parser.add_argument('--stems', type=str,
                       help='Export stems to directory')
    parser.add_argument('--report', action='store_true',
                       help='Generate mixing report')
    parser.add_argument('--list-presets', action='store_true',
                       help='List available presets')
    
    args = parser.parse_args()
    
    mixer = AudioMixerV2()
    
    if args.list_presets:
        print("Available mixing presets:")
        for preset_name, preset_data in mixer.presets.get('content_presets', {}).items():
            print(f"  • {preset_name}: {preset_data.get('description', '')}")
        
        print("\nAvailable export formats:")
        for format_name, format_data in mixer.presets.get('export_formats', {}).items():
            print(f"  • {format_name}: {format_data.get('format', 'unknown')} at {format_data.get('bitrate', 'unknown')}")
        return
    
    # Add tracks
    if args.speech:
        mixer.add_track(args.speech, 'speech', 0.0)
        print(f"Added speech track: {args.speech}")
    
    if args.music:
        mixer.add_track(args.music, 'music', 0.0)
        print(f"Added music track: {args.music}")
    
    if args.sfx:
        for i, sfx_file in enumerate(args.sfx):
            # For demo purposes, space SFX tracks every 5 seconds
            start_time = i * 5.0
            mixer.add_track(sfx_file, 'sfx', start_time)
            print(f"Added SFX track: {sfx_file} at {start_time}s")
    
    if not mixer.tracks:
        print("No tracks added. Use --speech, --music, or --sfx")
        return
    
    # Apply preset
    if args.preset:
        try:
            mixer.apply_preset(args.preset)
            print(f"Applied preset: {args.preset}")
        except ValueError as e:
            print(f"Preset error: {e}")
            return
    
    # Mix tracks
    try:
        mixed_audio = mixer.mix_tracks(args.duration)
        print(f"Mixed {len(mixer.tracks)} tracks (duration: {mixer.mix_duration:.1f}s)")
    except Exception as e:
        print(f"Mixing error: {e}")
        return
    
    # Analysis
    if args.analyze or args.report:
        quality = mixer.analyze_mix_quality()
        print(f"\nQuality Analysis:")
        print(f"  Peak Level: {quality['peak_level_db']:.1f} dB")
        print(f"  RMS Level: {quality['rms_level_db']:.1f} dB")
        print(f"  Estimated LUFS: {quality['estimated_lufs']:.1f}")
        print(f"  Dynamic Range: {quality['dynamic_range_db']:.1f} dB")
        
        assessment = quality['quality_assessment']
        print(f"  Overall Quality: {assessment['overall']}")
        
        if assessment['issues']:
            print("  Issues:")
            for issue in assessment['issues']:
                print(f"    • {issue}")
        
        if assessment['recommendations']:
            print("  Recommendations:")
            for rec in assessment['recommendations']:
                print(f"    • {rec}")
    
    # Generate full report
    if args.report:
        report = mixer.get_mixing_report()
        
        print(f"\nMixing Report:")
        print(f"Total Tracks: {report['mix_info']['total_tracks']}")
        print(f"Mix Duration: {report['mix_info']['mix_duration']:.1f}s")
        
        print(f"\nTrack Breakdown:")
        for track_info in report['track_breakdown']:
            print(f"  Track {track_info['track_number']}: {track_info['type']} - {track_info['file_name']}")
            print(f"    Duration: {track_info['duration']:.1f}s, Start: {track_info['start_time']:.1f}s")
            print(f"    Volume: {track_info['volume']:.2f}, Processing: {track_info['processing']}")
        
        if report['recommendations']:
            print(f"\nGeneral Recommendations:")
            for rec in report['recommendations']:
                print(f"  • {rec}")
    
    # Export stems
    if args.stems:
        try:
            stem_files = mixer.create_stems(args.stems)
            print(f"\nExported {len(stem_files)} stems to {args.stems}/")
            for stem in stem_files:
                print(f"  • {Path(stem).name}")
        except Exception as e:
            print(f"Stem export error: {e}")
    
    # Export final mix
    if args.output:
        try:
            success = mixer.export_mix(args.output, args.format)
            if success:
                print(f"\n✓ Exported mix: {args.output}")
                print(f"  Format: {args.format}")
            else:
                print(f"✗ Export failed")
        except Exception as e:
            print(f"Export error: {e}")


if __name__ == "__main__":
    main()