#!/usr/bin/env python3
"""
Voice Manager for Kiin Content - Professional TTS Voice Selection
Manages multiple Edge-TTS voices optimized for caregiving and family content
"""

import argparse
import asyncio
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import edge_tts


class VoiceManager:
    """Manages Edge-TTS voices for different content types"""
    
    def __init__(self):
        self.config_path = Path(__file__).parent.parent / "config" / "audio_config.json"
        self.voices_cache = None
        
        # Predefined voice profiles for caregiving content
        self.voice_profiles = {
            "validation": {
                "primary": ["en-US-JennyNeural", "en-US-AriaNeural", "en-AU-NatashaNeural"],
                "characteristics": ["warm", "empathetic", "nurturing", "gentle"],
                "description": "Warm, nurturing voices for validation content"
            },
            "confessions": {
                "primary": ["en-US-SaraNeural", "en-GB-SoniaNeural", "en-CA-ClaraNeural"],
                "characteristics": ["intimate", "soft", "understanding", "non-judgmental"],
                "description": "Intimate, soft voices for confessions and personal stories"
            },
            "tips": {
                "primary": ["en-US-DavisNeural", "en-GB-RyanNeural", "en-US-JasonNeural"],
                "characteristics": ["clear", "authoritative", "confident", "informative"],
                "description": "Clear, authoritative voices for tips and advice"
            },
            "sandwich_gen": {
                "primary": ["en-US-AmberNeural", "en-US-AshleyNeural", "en-AU-WilliamNeural"],
                "characteristics": ["energetic", "relatable", "conversational", "friendly"],
                "description": "Energetic, relatable voices for sandwich generation content"
            },
            "general": {
                "primary": ["en-US-AriaNeural", "en-GB-LibbyNeural", "en-CA-LiamNeural"],
                "characteristics": ["versatile", "pleasant", "clear", "engaging"],
                "description": "Versatile voices suitable for general content"
            }
        }
    
    async def get_available_voices(self, force_refresh: bool = False) -> List[Dict]:
        """Get all available Edge-TTS voices with caching"""
        if self.voices_cache is None or force_refresh:
            try:
                voices = await edge_tts.list_voices()
                # Filter for high-quality neural voices
                self.voices_cache = [
                    v for v in voices 
                    if 'Neural' in v.get('ShortName', '') 
                    and v.get('Locale', '').startswith('en-')
                ]
                print(f"✓ Found {len(self.voices_cache)} high-quality English neural voices")
            except Exception as e:
                print(f"✗ Error fetching voices: {e}")
                return []
        return self.voices_cache
    
    def get_suitable_voices_for_content(self, content_type: str) -> List[str]:
        """Get recommended voices for specific content type"""
        if content_type not in self.voice_profiles:
            content_type = "general"
        
        return self.voice_profiles[content_type]["primary"]
    
    def get_content_types(self) -> List[str]:
        """Get all available content types"""
        return list(self.voice_profiles.keys())
    
    def get_voice_characteristics(self, content_type: str) -> List[str]:
        """Get voice characteristics for content type"""
        if content_type not in self.voice_profiles:
            content_type = "general"
        return self.voice_profiles[content_type]["characteristics"]
    
    async def preview_voice(self, voice_name: str, text: str = None, output_file: str = None) -> str:
        """Generate a voice preview"""
        if text is None:
            text = "Hi, I'm here to support you on your caregiving journey. Every small act of care makes a difference."
        
        if output_file is None:
            output_file = f"preview_{voice_name.replace('-', '_')}.mp3"
        
        try:
            # Create the TTS communication object
            communicate = edge_tts.Communicate(text, voice_name)
            
            # Save to file
            await communicate.save(output_file)
            
            print(f"✓ Preview saved: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"✗ Error generating preview for {voice_name}: {e}")
            return ""
    
    async def analyze_voice_suitability(self, voice_info: Dict) -> Dict:
        """Analyze if a voice is suitable for caregiving content"""
        voice_name = voice_info.get('ShortName', '')
        gender = voice_info.get('Gender', '').lower()
        locale = voice_info.get('Locale', '')
        
        # Scoring based on characteristics beneficial for caregiving content
        score = 0
        notes = []
        
        # Gender considerations (both are good, slight preference varies by content type)
        if gender == 'female':
            score += 5
            notes.append("Female voice - often perceived as nurturing")
        elif gender == 'male':
            score += 4
            notes.append("Male voice - can convey authority and comfort")
        
        # Locale preferences (US/UK/CA/AU are primary targets)
        if locale in ['en-US', 'en-GB', 'en-CA', 'en-AU']:
            score += 10
            notes.append(f"Primary English locale: {locale}")
        else:
            score += 3
            notes.append(f"Secondary English locale: {locale}")
        
        # Neural voice quality
        if 'Neural' in voice_name:
            score += 15
            notes.append("High-quality neural voice")
        
        # Specific voice name analysis
        nurturing_names = ['aria', 'jenny', 'sara', 'clara', 'natasha', 'sonia']
        authoritative_names = ['davis', 'ryan', 'jason', 'william', 'liam']
        energetic_names = ['amber', 'ashley', 'libby']
        
        name_lower = voice_name.lower()
        if any(name in name_lower for name in nurturing_names):
            score += 8
            notes.append("Voice name suggests nurturing qualities")
        elif any(name in name_lower for name in authoritative_names):
            score += 6
            notes.append("Voice name suggests authoritative qualities")
        elif any(name in name_lower for name in energetic_names):
            score += 7
            notes.append("Voice name suggests energetic qualities")
        
        # Determine suitability
        if score >= 25:
            suitability = "Excellent"
        elif score >= 20:
            suitability = "Very Good"
        elif score >= 15:
            suitability = "Good"
        elif score >= 10:
            suitability = "Fair"
        else:
            suitability = "Poor"
        
        return {
            "voice_name": voice_name,
            "score": score,
            "suitability": suitability,
            "notes": notes,
            "gender": gender,
            "locale": locale
        }
    
    async def list_voices(self, content_type: str = None, detailed: bool = False) -> None:
        """List available voices, optionally filtered by content type"""
        voices = await self.get_available_voices()
        
        if not voices:
            print("No voices available")
            return
        
        if content_type:
            if content_type not in self.voice_profiles:
                print(f"Unknown content type: {content_type}")
                print(f"Available types: {', '.join(self.get_content_types())}")
                return
            
            recommended = self.get_suitable_voices_for_content(content_type)
            print(f"\n🎯 Recommended voices for '{content_type}' content:")
            print(f"Description: {self.voice_profiles[content_type]['description']}")
            print(f"Characteristics: {', '.join(self.voice_profiles[content_type]['characteristics'])}")
            print("\nPrimary recommendations:")
            
            for voice_name in recommended:
                voice_info = next((v for v in voices if v.get('ShortName') == voice_name), None)
                if voice_info:
                    gender = voice_info.get('Gender', 'Unknown')
                    locale = voice_info.get('Locale', 'Unknown')
                    print(f"  • {voice_name} ({gender}, {locale})")
                else:
                    print(f"  • {voice_name} (not available)")
            
            if detailed:
                print("\nAll suitable voices (analyzed):")
                for voice in voices:
                    analysis = await self.analyze_voice_suitability(voice)
                    if analysis['score'] >= 15:  # Only show good or better voices
                        print(f"  • {analysis['voice_name']} - {analysis['suitability']} (Score: {analysis['score']})")
                        print(f"    {analysis['gender']}, {analysis['locale']}")
                        if analysis['notes']:
                            print(f"    Notes: {'; '.join(analysis['notes'])}")
        
        else:
            print(f"\n📋 All available high-quality English neural voices ({len(voices)} total):")
            
            if detailed:
                for voice in voices:
                    analysis = await self.analyze_voice_suitability(voice)
                    print(f"  • {analysis['voice_name']} - {analysis['suitability']} (Score: {analysis['score']})")
                    print(f"    {analysis['gender']}, {analysis['locale']}")
            else:
                for voice in voices:
                    gender = voice.get('Gender', 'Unknown')
                    locale = voice.get('Locale', 'Unknown')
                    voice_name = voice.get('ShortName', 'Unknown')
                    print(f"  • {voice_name} ({gender}, {locale})")
    
    async def recommend_voices(self, content_type: str) -> None:
        """Provide detailed voice recommendations for content type"""
        if content_type not in self.voice_profiles:
            print(f"Unknown content type: {content_type}")
            print(f"Available types: {', '.join(self.get_content_types())}")
            return
        
        print(f"\n🎯 Voice Recommendations for '{content_type.title()}' Content")
        print("=" * 60)
        
        profile = self.voice_profiles[content_type]
        print(f"Description: {profile['description']}")
        print(f"Desired characteristics: {', '.join(profile['characteristics'])}")
        
        print("\n🏆 Primary Recommendations:")
        for i, voice_name in enumerate(profile['primary'], 1):
            print(f"{i}. {voice_name}")
        
        print(f"\n💡 Usage Tips for {content_type} content:")
        
        tips = {
            "validation": [
                "Use slower speech rate (0.8-0.9x) for calming effect",
                "Slightly lower pitch for warmth",
                "Add natural pauses between sentences",
                "Consider background music: soft piano or ambient sounds"
            ],
            "confessions": [
                "Use intimate, conversational tone",
                "Normal to slightly slower pace",
                "Avoid overly dramatic inflection",
                "Background: minimal or no music for intimacy"
            ],
            "tips": [
                "Clear, confident delivery",
                "Standard speech rate",
                "Emphasize key points with natural inflection",
                "Background: light, non-distracting instrumental"
            ],
            "sandwich_gen": [
                "Energetic but not overwhelming",
                "Slightly faster pace to convey enthusiasm",
                "Natural conversational style",
                "Background: upbeat but subtle ambient music"
            ],
            "general": [
                "Balanced, pleasant delivery",
                "Standard speech rate and pitch",
                "Clear articulation",
                "Adaptable to various background music styles"
            ]
        }
        
        for tip in tips.get(content_type, []):
            print(f"  • {tip}")
    
    def generate_voice_script(self, content_type: str, voice_name: str) -> str:
        """Generate a sample script optimized for the voice and content type"""
        scripts = {
            "validation": [
                "Your feelings are completely valid, and you're not alone in this journey.",
                "It's okay to feel overwhelmed - caring for someone you love is one of life's greatest challenges and honors.",
                "You're doing an amazing job, even when it doesn't feel like it."
            ],
            "confessions": [
                "Sometimes I wonder if I'm doing enough, if I'm being the caregiver my loved one deserves.",
                "The truth is, caregiving changes you in ways you never expected.",
                "It's okay to admit that some days are harder than others - that's just being human."
            ],
            "tips": [
                "Here are three essential strategies that can transform your caregiving experience.",
                "First, establish a consistent daily routine that works for both you and your loved one.",
                "Remember: taking care of yourself isn't selfish - it's essential for sustainable caregiving."
            ],
            "sandwich_gen": [
                "If you're juggling kids and aging parents, you're definitely not alone in feeling stretched thin.",
                "Let's talk about practical strategies that can help you manage both generations with confidence.",
                "The good news? There are proven ways to create harmony between caring for kids and parents."
            ],
            "general": [
                "Welcome to a community where your caregiving journey is understood and supported.",
                "Today we're sharing insights that can make a real difference in your daily experience.",
                "Every caregiver's story matters, and yours is no exception."
            ]
        }
        
        sample_lines = scripts.get(content_type, scripts["general"])
        return " ".join(sample_lines)


async def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Voice Manager for Kiin Content - Professional TTS Voice Selection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python voice_manager.py --list
  python voice_manager.py --list --content-type validation --detailed
  python voice_manager.py --recommend --content-type confessions
  python voice_manager.py --preview "en-US-AriaNeural" --text "Hello, welcome to Kiin"
  python voice_manager.py --preview "en-US-JennyNeural" --content-type validation
        """
    )
    
    parser.add_argument('--list', action='store_true', help='List available voices')
    parser.add_argument('--content-type', type=str, choices=['validation', 'confessions', 'tips', 'sandwich_gen', 'general'], 
                       help='Content type for voice recommendations')
    parser.add_argument('--detailed', action='store_true', help='Show detailed voice analysis')
    parser.add_argument('--recommend', action='store_true', help='Get voice recommendations for content type')
    parser.add_argument('--preview', type=str, help='Generate preview for specific voice (provide voice name)')
    parser.add_argument('--text', type=str, help='Custom text for preview (optional)')
    parser.add_argument('--output', type=str, help='Output file for preview (optional)')
    parser.add_argument('--analyze-all', action='store_true', help='Analyze all voices for caregiving suitability')
    
    args = parser.parse_args()
    
    vm = VoiceManager()
    
    if args.list:
        await vm.list_voices(args.content_type, args.detailed)
    
    elif args.recommend:
        if not args.content_type:
            print("Content type required for recommendations. Use --content-type")
            print(f"Available types: {', '.join(vm.get_content_types())}")
        else:
            await vm.recommend_voices(args.content_type)
    
    elif args.preview:
        # Generate appropriate text if content type is specified
        text = args.text
        if not text and args.content_type:
            text = vm.generate_voice_script(args.content_type, args.preview)
        
        output_file = await vm.preview_voice(args.preview, text, args.output)
        if output_file:
            print(f"🎵 Voice preview ready: {output_file}")
            if args.content_type:
                print(f"Optimized for: {args.content_type} content")
    
    elif args.analyze_all:
        print("🔍 Analyzing all voices for caregiving content suitability...")
        voices = await vm.get_available_voices()
        
        excellent_voices = []
        for voice in voices:
            analysis = await vm.analyze_voice_suitability(voice)
            if analysis['suitability'] in ['Excellent', 'Very Good']:
                excellent_voices.append(analysis)
        
        print(f"\n🏆 Top {len(excellent_voices)} voices for caregiving content:")
        for analysis in sorted(excellent_voices, key=lambda x: x['score'], reverse=True):
            print(f"  • {analysis['voice_name']} - {analysis['suitability']} (Score: {analysis['score']})")
            print(f"    {analysis['gender']}, {analysis['locale']}")
            if analysis['notes']:
                print(f"    Notes: {'; '.join(analysis['notes'])}")
            print()
    
    else:
        parser.print_help()
        print(f"\nAvailable content types: {', '.join(vm.get_content_types())}")


if __name__ == "__main__":
    asyncio.run(main())