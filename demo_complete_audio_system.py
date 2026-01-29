#!/usr/bin/env python3
"""
Complete Audio System V2 Demo for Kiin Content Factory
Demonstrates the full capabilities of the enhanced audio system

This demo shows:
1. Voice persona selection and speech generation
2. Intelligent music selection based on content type
3. Sound effects placement and timing
4. Professional multi-track mixing
5. Platform-optimized export
"""

import asyncio
import json
import tempfile
from pathlib import Path
from datetime import datetime

# Import our audio system components
from voice_system_v2 import VoiceSystemV2
from music_system_v2 import MusicSystemV2
from sfx_library import SFXLibrary
from audio_mixer_v2 import AudioMixerV2


class AudioSystemDemo:
    """Comprehensive demo of the Audio System V2"""
    
    def __init__(self):
        self.voice_system = VoiceSystemV2()
        self.music_system = MusicSystemV2()
        self.sfx_library = SFXLibrary()
        self.output_dir = Path("demo_output")
        self.output_dir.mkdir(exist_ok=True)
    
    def print_section(self, title: str):
        """Print a formatted section header"""
        print(f"\n{'='*60}")
        print(f" {title}")
        print(f"{'='*60}")
    
    async def demo_voice_personas(self):
        """Demonstrate all voice personas with different emotional tones"""
        self.print_section("VOICE PERSONAS DEMONSTRATION")
        
        # Demo content for each persona
        demo_scripts = {
            "maya": [
                {
                    "text": "You're doing an incredible job caring for your loved one, even when it doesn't feel like it. Your dedication and love make a real difference every single day.",
                    "emotional_tone": "comforting",
                    "content_type": "validation"
                },
                {
                    "text": "I understand how overwhelming it can feel sometimes. You're not alone in this journey, and it's completely normal to have difficult days.",
                    "emotional_tone": "understanding", 
                    "content_type": "confessions"
                }
            ],
            "dr_sarah": [
                {
                    "text": "Here are three essential strategies that can transform your caregiving experience. First, establish consistent routines. Second, prioritize your own self-care. Third, build a strong support network.",
                    "emotional_tone": "instructional",
                    "content_type": "tips"
                },
                {
                    "text": "Remember, taking breaks isn't selfish—it's essential for sustainable caregiving. Your well-being directly impacts your ability to care for others.",
                    "emotional_tone": "encouraging",
                    "content_type": "advice"
                }
            ],
            "alex": [
                {
                    "text": "Okay, real talk—juggling kids and aging parents is absolutely wild. But honestly? You're handling way more than you think you are, and that's something to be proud of.",
                    "emotional_tone": "real_talk",
                    "content_type": "sandwich_gen"
                },
                {
                    "text": "I totally get that feeling when you're running between soccer practice and doctor appointments. It's chaotic, but there are ways to make it work better for everyone.",
                    "emotional_tone": "empathetic",
                    "content_type": "peer_support"
                }
            ],
            "narrator": [
                {
                    "text": "It was supposed to be a simple grocery trip. But when your loved one with dementia suddenly doesn't recognize the familiar store, everything changes in an instant.",
                    "emotional_tone": "dramatic",
                    "content_type": "chaos"
                },
                {
                    "text": "In families across the world, similar stories unfold daily. Moments of chaos that test our patience, our love, and our resilience as caregivers.",
                    "emotional_tone": "reflective",
                    "content_type": "stories"
                }
            ]
        }
        
        generated_files = []
        
        for persona_name, scripts in demo_scripts.items():
            print(f"\n🎤 {persona_name.upper()} PERSONA")
            persona_info = self.voice_system.get_persona_info(persona_name)
            print(f"   Description: {persona_info.get('description', '')}")
            print(f"   Characteristics: {', '.join(persona_info.get('characteristics', []))}")
            
            for i, script in enumerate(scripts):
                print(f"\n   Script {i+1}: {script['emotional_tone']} tone")
                print(f"   Text: {script['text'][:80]}...")
                
                try:
                    output_file = self.output_dir / f"demo_{persona_name}_{script['emotional_tone']}_{i+1}.mp3"
                    
                    speech_file = await self.voice_system.generate_speech(
                        text=script['text'],
                        persona=persona_name,
                        emotional_tone=script['emotional_tone'],
                        content_type=script['content_type'],
                        output_file=str(output_file)
                    )
                    
                    generated_files.append(speech_file)
                    print(f"   ✓ Generated: {Path(speech_file).name}")
                    
                except Exception as e:
                    print(f"   ✗ Error: {e}")
        
        print(f"\n📊 Voice Demo Summary:")
        print(f"   Total personas: {len(demo_scripts)}")
        print(f"   Total variations: {sum(len(scripts) for scripts in demo_scripts.values())}")
        print(f"   Successfully generated: {len(generated_files)}")
        
        return generated_files
    
    def demo_music_intelligence(self):
        """Demonstrate music mood selection and analysis"""
        self.print_section("MUSIC INTELLIGENCE DEMONSTRATION")
        
        content_scenarios = [
            ("validation", "A caregiver is feeling overwhelmed and needs comfort", "gentle"),
            ("tips", "Educational content about medication management", None),
            ("sandwich_gen", "Busy parent managing multiple responsibilities", "urgent"),
            ("chaos", "Story about a medical emergency", "dramatic"),
            ("confessions", "Personal story about caregiver guilt", "vulnerable")
        ]
        
        print("🎵 Content-to-Music Mapping:")
        
        for content_type, description, emotional_context in content_scenarios:
            print(f"\n   Content: {content_type}")
            print(f"   Scenario: {description}")
            print(f"   Emotional Context: {emotional_context or 'default'}")
            
            # Get music recommendation
            music_track = self.music_system.select_music(
                content_type, duration=45.0, emotional_context=emotional_context
            )
            
            if music_track:
                print(f"   → Selected Mood: Based on content analysis")
                print(f"   → Track Properties: {music_track.duration:.1f}s")
                if music_track.bpm:
                    print(f"   → Tempo: {music_track.bpm:.0f} BPM")
                print(f"   → Energy Level: {music_track.energy_level:.2f}")
                print(f"   → Emotional Valence: {music_track.valence:.2f}")
            else:
                # Show what we would recommend
                suggestions = self.music_system.export_music_suggestions(content_type)
                print(f"   → Recommended Mood: {suggestions['recommended_mood']}")
                print(f"   → Search Terms: {', '.join(suggestions['search_terms'])}")
                print(f"   → Note: No tracks in library - would use procedural generation")
        
        # Demonstrate mood analysis
        print(f"\n🎼 Music Mood Categories:")
        for mood, config in self.music_system.config.get('moods', {}).items():
            print(f"   {mood.replace('_', ' ').title()}:")
            print(f"     • {config.get('description', '')}")
            print(f"     • Tempo: {config.get('tempo_range', [60, 120])[0]}-{config.get('tempo_range', [60, 120])[1]} BPM")
            print(f"     • Energy: {config.get('energy_level', 'medium')}")
            print(f"     • Volume: {config.get('recommended_volume', 0.2):.2f}")
    
    def demo_sfx_library(self):
        """Demonstrate sound effects selection and timing"""
        self.print_section("SOUND EFFECTS LIBRARY DEMONSTRATION")
        
        content_demos = [
            ("validation", 30.0, "Gentle emotional support content"),
            ("tips", 45.0, "Educational content with key points"),
            ("chaos", 60.0, "Dramatic story with notifications and transitions"),
            ("confessions", 25.0, "Intimate personal story")
        ]
        
        print("🔊 SFX Category Usage by Content Type:")
        
        for content_type, duration, description in content_demos:
            print(f"\n   Content Type: {content_type}")
            print(f"   Description: {description}")
            print(f"   Duration: {duration}s")
            
            # Create timing map for this content
            timing_map = self.sfx_library.create_sfx_timing_map(duration, content_type)
            
            print(f"   SFX Events Scheduled:")
            if timing_map:
                for event in timing_map:
                    sfx_name = event['sfx'].name if event['sfx'] else 'Generated'
                    print(f"     {event['time']:5.1f}s: {sfx_name} (vol: {event['volume']:.2f})")
            else:
                print("     No SFX recommended for this content type")
            
            # Show category preferences
            content_config = self.sfx_library.config.get('content_type_mappings', {}).get(content_type, {})
            preferred = content_config.get('preferred_categories', [])
            avoided = content_config.get('avoid_categories', [])
            
            if preferred:
                print(f"   Preferred Categories: {', '.join(preferred)}")
            if avoided:
                print(f"   Avoided Categories: {', '.join(avoided)}")
        
        # Demonstrate procedural generation
        print(f"\n🎛️ Procedural SFX Generation Demo:")
        generation_tests = [
            ("notification", "gentle", "Soft attention sound"),
            ("transition", "forward", "Smooth section transition"),
            ("emotional_accent", "touching", "Heart-warming moment"),
            ("text_reveal", "digital", "Modern text appearance")
        ]
        
        for category, style, description in generation_tests:
            print(f"\n   Generating: {category} ({style} style)")
            print(f"   Purpose: {description}")
            
            try:
                sfx = self.sfx_library._generate_fallback_sfx(category, style)
                if sfx:
                    print(f"   ✓ Generated: {sfx.name}")
                    print(f"     Duration: {sfx.duration:.2f}s (estimated)")
                    print(f"     Category: {sfx.category}")
                else:
                    print(f"   ✗ Generation not available for this category")
            except Exception as e:
                print(f"   ✗ Generation error: {e}")
    
    async def demo_complete_audio_mixing(self):
        """Demonstrate complete audio mixing workflow"""
        self.print_section("COMPLETE AUDIO MIXING DEMONSTRATION")
        
        # Create a complete audio piece
        print("🎬 Creating Complete Audio Production:")
        print("   Scenario: Validation content with background music and SFX")
        
        try:
            # 1. Generate speech
            print("\n   Step 1: Generating Speech with Maya Persona")
            validation_text = """
            I want you to know that what you're feeling right now is completely valid. 
            Caregiving is one of life's most challenging journeys, and there are days 
            when it feels overwhelming. But in those quiet moments between the chaos, 
            remember this: your love, your presence, your dedication—they matter more 
            than you can imagine. You're not just caring for someone else; you're 
            embodying the very best of what it means to be human.
            """
            
            speech_file = await self.voice_system.generate_speech(
                text=validation_text.strip(),
                persona="maya",
                emotional_tone="comforting",
                content_type="validation",
                output_file=str(self.output_dir / "complete_demo_speech.mp3")
            )
            print(f"   ✓ Speech generated: {Path(speech_file).name}")
            
            # 2. Create mixer and add tracks
            print("\n   Step 2: Setting up Multi-Track Mix")
            mixer = AudioMixerV2()
            
            # Add speech track
            speech_track = mixer.add_track(speech_file, "speech", start_time=0.0)
            print(f"   ✓ Added speech track")
            
            # 3. Music selection (simulated - would use actual file)
            print("\n   Step 3: Music Selection and Integration")
            music_track = self.music_system.select_music("validation", duration=25.0)
            if music_track and music_track.file_path.exists():
                mixer.add_track(str(music_track.file_path), "music", start_time=0.0)
                print(f"   ✓ Added music track: {music_track.file_path.name}")
            else:
                print(f"   ◦ Music track simulated (no library files available)")
                print(f"   ◦ Would use: supportive_gentle mood")
            
            # 4. SFX integration
            print("\n   Step 4: Sound Effects Integration")
            sfx_timing = self.sfx_library.create_sfx_timing_map(25.0, "validation")
            
            sfx_added = 0
            for event in sfx_timing[:2]:  # Limit to 2 SFX for demo
                if event['sfx']:
                    try:
                        # Generate SFX if needed
                        if not event['sfx'].file_path or not Path(event['sfx'].file_path).exists():
                            if hasattr(event['sfx'], 'category'):
                                generated_sfx = self.sfx_library._generate_fallback_sfx(
                                    event['sfx'].category, "gentle"
                                )
                                if generated_sfx and generated_sfx.file_path:
                                    mixer.add_track(generated_sfx.file_path, "sfx", event['time'])
                                    sfx_added += 1
                                    print(f"   ✓ Added generated SFX at {event['time']:.1f}s")
                        else:
                            mixer.add_track(str(event['sfx'].file_path), "sfx", event['time'])
                            sfx_added += 1
                            print(f"   ✓ Added SFX at {event['time']:.1f}s")
                    except Exception as e:
                        print(f"   ◦ SFX generation skipped: {e}")
            
            print(f"   → Total SFX added: {sfx_added}")
            
            # 5. Apply mixing preset
            print("\n   Step 5: Applying Professional Audio Processing")
            try:
                mixer.apply_preset("documentary_cinematic")
                print(f"   ✓ Applied documentary cinematic preset")
                print(f"     • Speech: Warmth boost, presence enhancement")
                print(f"     • Music: Intelligent ducking, emotional support")
                print(f"     • Master: Cinematic warmth, professional limiting")
            except Exception as e:
                print(f"   ◦ Preset application limited: {e}")
            
            # 6. Final mix and analysis
            print("\n   Step 6: Final Mix and Quality Analysis")
            try:
                final_audio = mixer.mix_tracks(total_duration=25.0)
                print(f"   ✓ Mixed {len(mixer.tracks)} tracks")
                
                # Quality analysis
                quality = mixer.analyze_mix_quality()
                print(f"\n   📊 Audio Quality Metrics:")
                print(f"     Peak Level: {quality['peak_level_db']:.1f} dB")
                print(f"     RMS Level: {quality['rms_level_db']:.1f} dB")
                print(f"     Estimated LUFS: {quality['estimated_lufs']:.1f}")
                print(f"     Dynamic Range: {quality['dynamic_range_db']:.1f} dB")
                print(f"     Overall Quality: {quality['quality_assessment']['overall']}")
                
                # Export in multiple formats
                print(f"\n   Step 7: Multi-Format Export")
                export_formats = ["podcast_mp3", "youtube_aac", "high_quality_wav"]
                
                for format_name in export_formats:
                    output_file = self.output_dir / f"complete_demo_{format_name.replace('_', '.')}"
                    try:
                        success = mixer.export_mix(str(output_file), format_name)
                        if success:
                            print(f"     ✓ Exported: {output_file.name}")
                        else:
                            print(f"     ◦ Export simulated: {format_name}")
                    except Exception as e:
                        print(f"     ◦ Export limited: {format_name} - {e}")
                
            except Exception as e:
                print(f"   ◦ Mixing simulated due to library limitations: {e}")
            
            # 7. Generate mixing report
            print(f"\n   Step 8: Professional Mixing Report")
            try:
                report = mixer.get_mixing_report()
                print(f"     Total Tracks: {report['mix_info']['total_tracks']}")
                print(f"     Mix Duration: {report['mix_info']['mix_duration']:.1f}s")
                print(f"     Sample Rate: {report['mix_info']['sample_rate']} Hz")
                
                if report['recommendations']:
                    print(f"     Recommendations:")
                    for rec in report['recommendations'][:3]:  # Show first 3
                        print(f"       • {rec}")
                
            except Exception as e:
                print(f"     Report generation limited: {e}")
            
        except Exception as e:
            print(f"   ✗ Demo limitation: {e}")
            print(f"   ◦ This demonstrates the workflow - full functionality requires audio libraries")
    
    def demo_integration_examples(self):
        """Show how to integrate with existing V2 generators"""
        self.print_section("INTEGRATION WITH EXISTING V2 GENERATORS")
        
        print("🔗 Enhanced Generator Integration Examples:\n")
        
        # Show integration code examples
        integration_examples = {
            "ValidationGeneratorV2": """
class ValidationGeneratorV2Enhanced:
    def __init__(self):
        self.voice_system = VoiceSystemV2()
        self.music_system = MusicSystemV2()
        self.sfx_library = SFXLibrary()
        self.mixer = AudioMixerV2()
    
    async def generate_with_audio(self, validation_message, duration=30):
        # Generate speech with Maya persona
        speech = await self.voice_system.generate_speech(
            text=validation_message,
            persona="maya",
            emotional_tone="comforting",
            content_type="validation"
        )
        
        # Select supportive music
        music = self.music_system.select_music("validation", duration)
        
        # Add gentle SFX
        sfx_timing = self.sfx_library.create_sfx_timing_map(duration, "validation")
        
        # Professional mixing
        mixer = AudioMixerV2()
        mixer.add_track(speech, "speech", 0.0)
        if music: mixer.add_track(str(music.file_path), "music", 0.0)
        
        mixer.apply_preset("documentary_cinematic")
        return mixer.mix_tracks(duration)
            """,
            
            "TipsGeneratorV2": """
class TipsGeneratorV2Enhanced:
    async def generate_tip_audio(self, tip_content, tips_list):
        # Use Dr. Sarah for authoritative delivery
        speech = await self.voice_system.generate_speech(
            text=tip_content,
            persona="dr_sarah",
            emotional_tone="instructional",
            content_type="tips"
        )
        
        # Uplifting music for educational content
        music = self.music_system.select_music("tips", duration=45)
        
        # Text reveal SFX for each tip
        for i, tip in enumerate(tips_list):
            reveal_sfx = self.sfx_library.get_sfx("text_reveal", "tip_presentation")
            mixer.add_track(reveal_sfx.file_path, "sfx", start_time=i*8+5)
        
        mixer.apply_preset("podcast_standard")
        return mixer.mix_tracks()
            """,
            
            "ChaosGeneratorV2": """
class ChaosGeneratorV2Enhanced:
    async def generate_chaos_story_audio(self, story_segments):
        # Narrator persona for dramatic storytelling
        speech_files = []
        for segment in story_segments:
            speech = await self.voice_system.generate_speech(
                text=segment['text'],
                persona="narrator", 
                emotional_tone=segment.get('emotion', 'dramatic'),
                content_type="chaos"
            )
            speech_files.append(speech)
        
        # Dynamic music that builds tension then resolves
        music = self.music_system.select_music("chaos", emotional_context="dramatic")
        
        # Strategic notifications and transitions
        notification_times = self.analyze_story_for_key_moments(story_segments)
        for time_point in notification_times:
            alert_sfx = self.sfx_library.get_sfx("notification", "chaos_moment")
            mixer.add_track(alert_sfx.file_path, "sfx", time_point)
        
        mixer.apply_preset("documentary_cinematic")
        return mixer.mix_tracks()
            """
        }
        
        for generator_name, code_example in integration_examples.items():
            print(f"   {generator_name}:")
            print("   " + "\n   ".join(code_example.strip().split('\n')))
            print()
    
    def generate_system_summary(self):
        """Generate a summary of the complete audio system"""
        self.print_section("AUDIO SYSTEM V2 - COMPLETE SUMMARY")
        
        print("🎯 System Capabilities:")
        
        # Voice System
        personas = self.voice_system.list_personas()
        print(f"\n   Voice System V2:")
        print(f"     • {len(personas)} Professional Voice Personas")
        print(f"     • SSML Support with Emotional Intelligence")
        print(f"     • Fallback Chain: ElevenLabs → Azure → Google → Edge")
        print(f"     • Content-Aware Persona Selection")
        
        # Music System  
        moods = list(self.music_system.config.get('moods', {}).keys())
        print(f"\n   Music Intelligence V2:")
        print(f"     • {len(moods)} Intelligent Mood Categories")
        print(f"     • Beat Detection and Audio Analysis")
        print(f"     • Dynamic Volume Ducking")
        print(f"     • Royalty-Free Source Integration")
        
        # SFX System
        sfx_categories = list(self.sfx_library.config.get('categories', {}).keys())
        print(f"\n   Sound Effects Library:")
        print(f"     • {len(sfx_categories)} Professional SFX Categories")
        print(f"     • Procedural Generation Fallbacks")
        print(f"     • Context-Aware Selection")
        print(f"     • Intelligent Timing and Placement")
        
        # Mixer System
        presets = list(AudioMixerV2().presets.get('content_presets', {}).keys())
        formats = list(AudioMixerV2().presets.get('export_formats', {}).keys())
        print(f"\n   Audio Mixer V2:")
        print(f"     • {len(presets)} Professional Mixing Presets")
        print(f"     • {len(formats)} Platform-Optimized Export Formats")
        print(f"     • Multi-Track Processing with EQ/Compression/Limiting")
        print(f"     • Automatic Quality Analysis and Reporting")
        
        print(f"\n📈 Quality Standards:")
        print(f"     • 44.1kHz+ sample rate, -14 LUFS loudness normalization")
        print(f"     • Professional EQ, compression, and limiting")
        print(f"     • Intelligent speech ducking and crossfades")
        print(f"     • Platform compliance (YouTube, Podcast, Social Media)")
        
        print(f"\n🚀 Integration Benefits:")
        print(f"     • Transforms content from good to professional quality")
        print(f"     • Emotional intelligence enhances audience connection")
        print(f"     • Automated workflow reduces production time")
        print(f"     • Consistent brand voice across all content")
        
        print(f"\n💡 Usage:")
        print(f"     • CLI tools for individual components")
        print(f"     • Python API for generator integration")
        print(f"     • Batch processing for efficiency")
        print(f"     • Comprehensive configuration system")
        
        print(f"\n📁 Files Created:")
        output_files = list(self.output_dir.glob("*"))
        if output_files:
            for file in output_files:
                print(f"     • {file.name}")
        else:
            print(f"     • Demo files in: {self.output_dir}")
        
        print(f"\n🎉 The Audio System V2 provides podcast and documentary-quality")
        print(f"    audio that enhances emotional connection and engagement!")


async def main():
    """Run the complete audio system demonstration"""
    demo = AudioSystemDemo()
    
    print("🎬 KIIN CONTENT FACTORY - AUDIO SYSTEM V2 DEMO")
    print("=" * 60)
    print("Demonstrating world-class audio enhancement capabilities")
    print(f"Demo output directory: {demo.output_dir}")
    
    try:
        # Run all demonstrations
        await demo.demo_voice_personas()
        demo.demo_music_intelligence()
        demo.demo_sfx_library()
        await demo.demo_complete_audio_mixing()
        demo.demo_integration_examples()
        demo.generate_system_summary()
        
        print(f"\n{'='*60}")
        print(" DEMO COMPLETE - AUDIO SYSTEM V2 READY FOR PRODUCTION")
        print(f"{'='*60}")
        print(f"\nNext Steps:")
        print(f"1. Add music files to assets/music/ directories")
        print(f"2. Record or download SFX to assets/sfx/ directories") 
        print(f"3. Configure TTS providers (optional premium services)")
        print(f"4. Integrate with existing V2 generators")
        print(f"5. Test with real content and iterate")
        
    except Exception as e:
        print(f"\nDemo Error: {e}")
        print("Note: Some features require additional dependencies or audio files")


if __name__ == "__main__":
    asyncio.run(main())