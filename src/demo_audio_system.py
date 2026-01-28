#!/usr/bin/env python3
"""
Demo Audio System for Kiin Content
Demonstrates the complete audio enhancement workflow
"""

import asyncio
import json
from pathlib import Path
from voice_manager import VoiceManager
from music_mixer import MusicMixer


async def demo_voice_system():
    """Demonstrate voice manager capabilities"""
    print("🎤 Kiin Voice System Demo")
    print("=" * 40)
    
    vm = VoiceManager()
    
    # Show content types
    print("\n📋 Available Content Types:")
    for i, content_type in enumerate(vm.get_content_types(), 1):
        characteristics = vm.get_voice_characteristics(content_type)
        print(f"{i}. {content_type.title()}: {', '.join(characteristics)}")
    
    # Demo voice recommendations for each content type
    print("\n🎯 Voice Recommendations by Content Type:")
    for content_type in ["validation", "tips", "confessions"]:
        voices = vm.get_suitable_voices_for_content(content_type)
        print(f"\n{content_type.title()}:")
        for voice in voices:
            print(f"  • {voice}")
    
    # Create sample previews
    print("\n🎵 Creating Sample Voice Previews...")
    sample_content = {
        "validation": "You're doing an amazing job caring for your loved one, even when it doesn't feel like it.",
        "tips": "Here are three essential strategies that can transform your caregiving experience.",
        "confessions": "Sometimes I wonder if I'm doing enough, if I'm being the caregiver my loved one deserves."
    }
    
    for content_type, text in sample_content.items():
        primary_voices = vm.get_suitable_voices_for_content(content_type)
        if primary_voices:
            voice = primary_voices[0]  # Use first recommended voice
            output_file = f"sample_{content_type}_{voice.replace('-', '_')}.mp3"
            
            try:
                result = await vm.preview_voice(voice, text, output_file)
                if result:
                    print(f"  ✓ {content_type}: {output_file}")
            except Exception as e:
                print(f"  ✗ Error with {content_type}: {e}")


def demo_music_system():
    """Demonstrate music mixer capabilities"""
    print("\n\n🎵 Kiin Music System Demo")
    print("=" * 40)
    
    mixer = MusicMixer()
    
    # Show mood mappings
    print("\n📊 Content Type → Music Mood Mapping:")
    for content_type, mood in mixer.content_mood_map.items():
        print(f"  {content_type.title()} → {mood}")
    
    # Show mood characteristics
    print("\n🎼 Music Mood Characteristics:")
    for mood, config in mixer.mood_mappings.items():
        print(f"\n{mood.title()}:")
        print(f"  Volume: {config['volume_level']:.2f}")
        print(f"  Duck Ratio: {config['duck_ratio']:.2f}")
        print(f"  Style: {', '.join(config['characteristics'])}")
    
    # Demo music suggestions
    print("\n💡 Music Suggestions by Content Type:")
    for content_type in ["validation", "tips", "sandwich_gen"]:
        suggestion = mixer.suggest_music_for_content_type(content_type)
        if suggestion:
            print(f"\n{content_type.title()}:")
            print(f"  Mood: {mixer.content_mood_map[content_type]}")
            print(f"  Tracks: {', '.join(suggestion['suggested_tracks'][:3])}...")


def create_usage_examples():
    """Create practical usage examples"""
    print("\n\n📝 Usage Examples")
    print("=" * 40)
    
    examples = {
        "Voice Selection": [
            "# List all voices for validation content",
            "./venv/bin/python src/voice_manager.py --list --content-type validation",
            "",
            "# Get detailed recommendations for tips content", 
            "./venv/bin/python src/voice_manager.py --recommend --content-type tips",
            "",
            "# Create voice preview",
            './venv/bin/python src/voice_manager.py --preview "en-US-AriaNeural" --text "Welcome to Kiin"'
        ],
        
        "Music Mixing": [
            "# Mix video with specific music file",
            "./venv/bin/python src/music_mixer.py --video input.mp4 --music calm_track.mp3 --output result.mp4",
            "",
            "# Mix video with mood-based music",
            "./venv/bin/python src/music_mixer.py --video input.mp4 --mood warm --output result.mp4",
            "",
            "# Mix based on content type",
            "./venv/bin/python src/music_mixer.py --video input.mp4 --content-type validation --output result.mp4"
        ],
        
        "Setup Commands": [
            "# Create music library structure",
            "./venv/bin/python src/music_mixer.py --create-library assets/music",
            "",
            "# List available music moods",
            "./venv/bin/python src/music_mixer.py --list-moods",
            "",
            "# Validate music file before use",
            "./venv/bin/python src/music_mixer.py --validate-music assets/music/calm/track.mp3"
        ]
    }
    
    for category, commands in examples.items():
        print(f"\n{category}:")
        for command in commands:
            if command.startswith("#"):
                print(f"  {command}")
            elif command.strip():
                print(f"  $ {command}")
            else:
                print()


def analyze_current_setup():
    """Analyze current system setup and provide recommendations"""
    print("\n\n🔍 System Analysis")
    print("=" * 40)
    
    config_path = Path("config/audio_config.json")
    music_path = Path("assets/music")
    voice_samples = Path("assets").glob("*preview*.mp3")
    
    print(f"\n📁 File Structure:")
    print(f"  Config file: {'✓' if config_path.exists() else '✗'} {config_path}")
    print(f"  Music library: {'✓' if music_path.exists() else '✗'} {music_path}")
    print(f"  Voice samples: {len(list(voice_samples))} files")
    
    if config_path.exists():
        try:
            with open(config_path) as f:
                config = json.load(f)
            print(f"\n⚙️ Configuration:")
            print(f"  Voice profiles: {len(config.get('voice_profiles', {}))}")
            print(f"  Music moods: {len(config.get('music_moods', {}))}")
            print(f"  Quality presets: {len(config.get('quality_presets', {}))}")
        except Exception as e:
            print(f"  Error reading config: {e}")
    
    # Check for dependencies
    print(f"\n🔧 Dependencies:")
    try:
        import edge_tts
        print("  ✓ edge-tts installed")
    except ImportError:
        print("  ✗ edge-tts missing")
    
    try:
        import cv2
        print("  ✓ opencv-python installed")
    except ImportError:
        print("  ✗ opencv-python missing")
    
    # Check external tools
    mixer = MusicMixer()
    ffmpeg_available = mixer.check_ffmpeg()
    print(f"  {'✓' if ffmpeg_available else '✗'} FFmpeg available")
    
    if not ffmpeg_available:
        print("\n💡 To install FFmpeg:")
        print("  macOS: brew install ffmpeg")
        print("  Ubuntu/Debian: apt install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/")


async def main():
    """Main demo function"""
    print("🎬 Kiin Audio Enhancement System Demo")
    print("Demonstrating voice selection and music mixing capabilities")
    print("=" * 60)
    
    try:
        await demo_voice_system()
        demo_music_system()
        create_usage_examples()
        analyze_current_setup()
        
        print("\n\n🎉 Demo Complete!")
        print("\nNext Steps:")
        print("1. Install FFmpeg for video mixing capabilities")
        print("2. Add music files to assets/music/ folders")
        print("3. Test with your content using the examples above")
        print("4. Customize voice and music settings in config/audio_config.json")
        
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        print("Make sure all dependencies are installed and try again.")


if __name__ == "__main__":
    asyncio.run(main())