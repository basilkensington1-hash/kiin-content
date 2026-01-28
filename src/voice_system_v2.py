#!/usr/bin/env python3
"""
Voice System V2 for Kiin Content - Professional TTS with Personas & SSML
Advanced voice management with emotional intelligence and persona-based delivery
"""

import asyncio
import json
import os
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import edge_tts
import requests
from datetime import datetime


class VoicePersona:
    """Represents a voice persona with emotional intelligence"""
    
    def __init__(self, name: str, config: Dict):
        self.name = name
        self.config = config
        self.primary_voice = config['primary_voice']
        self.fallback_voices = config.get('fallback_voices', [])
        self.characteristics = config.get('characteristics', [])
        self.ssml_settings = config.get('ssml_settings', {})
        self.emotional_range = config.get('emotional_range', {})
        
    def get_voice_for_content(self, content_type: str, emotional_tone: str = 'neutral') -> str:
        """Get the best voice for specific content and emotion"""
        # Use primary voice by default
        voice = self.primary_voice
        
        # Override based on emotional tone if configured
        if emotional_tone in self.emotional_range:
            emotion_config = self.emotional_range[emotional_tone]
            voice = emotion_config.get('preferred_voice', voice)
        
        return voice
    
    def apply_ssml_style(self, text: str, emotional_tone: str = 'neutral', 
                        content_type: str = 'general') -> str:
        """Apply SSML styling based on persona and context"""
        # Base SSML settings for this persona
        base_settings = self.ssml_settings.copy()
        
        # Adjust for emotional tone
        if emotional_tone in self.emotional_range:
            emotion_settings = self.emotional_range[emotional_tone].get('ssml_overrides', {})
            base_settings.update(emotion_settings)
        
        # Adjust for content type
        content_settings = base_settings.get(f'content_type_{content_type}', {})
        base_settings.update(content_settings)
        
        # Build SSML
        voice_attrs = []
        if 'rate' in base_settings:
            voice_attrs.append(f'rate="{base_settings["rate"]}"')
        if 'pitch' in base_settings:
            voice_attrs.append(f'pitch="{base_settings["pitch"]}"')
        if 'volume' in base_settings:
            voice_attrs.append(f'volume="{base_settings["volume"]}"')
        
        voice_tag = f'voice {" ".join(voice_attrs)}' if voice_attrs else 'voice'
        
        # Add emphasis and pauses
        styled_text = self._add_natural_pauses(text, base_settings)
        styled_text = self._add_emphasis(styled_text, base_settings)
        
        # Wrap in speak tag
        ssml = f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">'
        ssml += f'<{voice_tag}>{styled_text}</voice>'
        ssml += '</speak>'
        
        return ssml
    
    def _add_natural_pauses(self, text: str, settings: Dict) -> str:
        """Add natural pauses to text for better flow"""
        pause_settings = settings.get('pauses', {})
        
        # Add pauses after punctuation based on persona
        text = text.replace('. ', f'. <break time="{pause_settings.get("sentence", "500ms")}" />')
        text = text.replace('! ', f'! <break time="{pause_settings.get("excitement", "400ms")}" />')
        text = text.replace('? ', f'? <break time="{pause_settings.get("question", "600ms")}" />')
        text = text.replace(', ', f', <break time="{pause_settings.get("comma", "200ms")}" />')
        text = text.replace(': ', f': <break time="{pause_settings.get("colon", "300ms")}" />')
        
        # Add emphasis pauses around key phrases
        if pause_settings.get('emphasis_phrases'):
            for phrase in pause_settings['emphasis_phrases']:
                pause_time = pause_settings.get('emphasis_pause', '400ms')
                text = text.replace(phrase, f'<break time="200ms" />{phrase}<break time="{pause_time}" />')
        
        return text
    
    def _add_emphasis(self, text: str, settings: Dict) -> str:
        """Add emphasis to important parts of text"""
        emphasis_settings = settings.get('emphasis', {})
        
        # Emphasize words in ALL CAPS
        import re
        caps_words = re.findall(r'\b[A-Z]{2,}\b', text)
        for word in caps_words:
            emphasis_level = emphasis_settings.get('caps_level', 'strong')
            text = text.replace(word, f'<emphasis level="{emphasis_level}">{word.title()}</emphasis>')
        
        # Emphasize quoted text
        quoted_pattern = r'"([^"]*)"'
        quotes = re.findall(quoted_pattern, text)
        for quote in quotes:
            emphasis_level = emphasis_settings.get('quote_level', 'moderate')
            text = re.sub(f'"{re.escape(quote)}"', 
                         f'<emphasis level="{emphasis_level}">"{quote}"</emphasis>', text)
        
        return text


class VoiceSystemV2:
    """Advanced voice system with persona management and emotional intelligence"""
    
    def __init__(self):
        self.config_path = Path(__file__).parent.parent / "config" / "voice_personas.json"
        self.personas = {}
        self.available_voices = None
        self.tts_providers = ['elevenlabs', 'azure', 'google', 'edge']  # Fallback chain
        self.current_provider = 'edge'  # Start with Edge TTS (free)
        
        # Load persona configurations
        self._load_personas()
        
        # Provider-specific settings
        self.provider_settings = {
            'elevenlabs': {
                'api_key': os.getenv('ELEVENLABS_API_KEY'),
                'base_url': 'https://api.elevenlabs.io/v1'
            },
            'azure': {
                'api_key': os.getenv('AZURE_SPEECH_KEY'),
                'region': os.getenv('AZURE_SPEECH_REGION', 'eastus')
            },
            'google': {
                'api_key': os.getenv('GOOGLE_CLOUD_API_KEY'),
                'project_id': os.getenv('GOOGLE_CLOUD_PROJECT_ID')
            },
            'edge': {
                'free_tier': True
            }
        }
    
    def _load_personas(self):
        """Load voice persona configurations"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                config = json.load(f)
                
            for name, persona_config in config.get('personas', {}).items():
                self.personas[name] = VoicePersona(name, persona_config)
        else:
            # Create default personas
            self._create_default_personas()
    
    def _create_default_personas(self):
        """Create default persona configurations"""
        default_config = {
            "version": "2.0",
            "description": "Voice personas for Kiin Content Factory",
            "updated": datetime.now().isoformat(),
            
            "personas": {
                "maya": {
                    "description": "Warm, nurturing caregiver voice for validation and confessions",
                    "primary_voice": "en-US-JennyNeural",
                    "fallback_voices": ["en-US-AriaNeural", "en-AU-NatashaNeural", "en-GB-SoniaNeural"],
                    "characteristics": ["warm", "empathetic", "nurturing", "gentle", "understanding"],
                    "content_types": ["validation", "confessions", "support"],
                    
                    "ssml_settings": {
                        "rate": "0.85",
                        "pitch": "-5%",
                        "volume": "90%",
                        "pauses": {
                            "sentence": "600ms",
                            "comma": "250ms",
                            "question": "700ms",
                            "emphasis_pause": "500ms",
                            "emphasis_phrases": ["take your time", "you're not alone", "it's okay"]
                        },
                        "emphasis": {
                            "caps_level": "moderate",
                            "quote_level": "strong"
                        }
                    },
                    
                    "emotional_range": {
                        "comforting": {
                            "preferred_voice": "en-US-JennyNeural",
                            "ssml_overrides": {
                                "rate": "0.80",
                                "pitch": "-8%",
                                "volume": "85%"
                            }
                        },
                        "reassuring": {
                            "preferred_voice": "en-US-AriaNeural",
                            "ssml_overrides": {
                                "rate": "0.85",
                                "pitch": "-3%"
                            }
                        },
                        "understanding": {
                            "preferred_voice": "en-AU-NatashaNeural",
                            "ssml_overrides": {
                                "rate": "0.90",
                                "pitch": "-2%"
                            }
                        }
                    }
                },
                
                "dr_sarah": {
                    "description": "Professional, authoritative voice for tips and educational content",
                    "primary_voice": "en-US-DavisNeural",
                    "fallback_voices": ["en-GB-RyanNeural", "en-US-JasonNeural", "en-CA-LiamNeural"],
                    "characteristics": ["authoritative", "clear", "professional", "confident", "knowledgeable"],
                    "content_types": ["tips", "education", "facts", "advice"],
                    
                    "ssml_settings": {
                        "rate": "1.00",
                        "pitch": "0%",
                        "volume": "95%",
                        "pauses": {
                            "sentence": "400ms",
                            "comma": "200ms",
                            "question": "500ms",
                            "emphasis_pause": "350ms",
                            "emphasis_phrases": ["first", "second", "third", "important", "remember"]
                        },
                        "emphasis": {
                            "caps_level": "strong",
                            "quote_level": "moderate"
                        }
                    },
                    
                    "emotional_range": {
                        "instructional": {
                            "preferred_voice": "en-US-DavisNeural",
                            "ssml_overrides": {
                                "rate": "0.95",
                                "pitch": "0%"
                            }
                        },
                        "encouraging": {
                            "preferred_voice": "en-GB-RyanNeural",
                            "ssml_overrides": {
                                "rate": "1.05",
                                "pitch": "+2%"
                            }
                        }
                    }
                },
                
                "alex": {
                    "description": "Peer voice, relatable and energetic for sandwich generation content",
                    "primary_voice": "en-US-AmberNeural",
                    "fallback_voices": ["en-US-AshleyNeural", "en-AU-WilliamNeural", "en-GB-LibbyNeural"],
                    "characteristics": ["relatable", "energetic", "friendly", "conversational", "authentic"],
                    "content_types": ["sandwich_gen", "peer_support", "stories"],
                    
                    "ssml_settings": {
                        "rate": "1.05",
                        "pitch": "+2%",
                        "volume": "100%",
                        "pauses": {
                            "sentence": "300ms",
                            "comma": "150ms",
                            "question": "400ms",
                            "emphasis_pause": "250ms",
                            "emphasis_phrases": ["totally get it", "been there", "real talk"]
                        },
                        "emphasis": {
                            "caps_level": "strong",
                            "quote_level": "moderate"
                        }
                    },
                    
                    "emotional_range": {
                        "enthusiastic": {
                            "preferred_voice": "en-US-AmberNeural",
                            "ssml_overrides": {
                                "rate": "1.10",
                                "pitch": "+5%"
                            }
                        },
                        "empathetic": {
                            "preferred_voice": "en-US-AshleyNeural",
                            "ssml_overrides": {
                                "rate": "0.95",
                                "pitch": "0%"
                            }
                        }
                    }
                },
                
                "narrator": {
                    "description": "Documentary-style narrator for chaos stories and longer content",
                    "primary_voice": "en-GB-LibbyNeural",
                    "fallback_voices": ["en-US-AriaNeural", "en-CA-ClaraNeural", "en-AU-NatashaNeural"],
                    "characteristics": ["narrative", "engaging", "storytelling", "dramatic", "cinematic"],
                    "content_types": ["chaos", "stories", "narratives", "documentation"],
                    
                    "ssml_settings": {
                        "rate": "0.92",
                        "pitch": "-1%",
                        "volume": "92%",
                        "pauses": {
                            "sentence": "500ms",
                            "comma": "200ms",
                            "question": "600ms",
                            "emphasis_pause": "400ms",
                            "emphasis_phrases": ["suddenly", "meanwhile", "however", "but then"]
                        },
                        "emphasis": {
                            "caps_level": "strong",
                            "quote_level": "strong"
                        }
                    },
                    
                    "emotional_range": {
                        "dramatic": {
                            "preferred_voice": "en-GB-LibbyNeural",
                            "ssml_overrides": {
                                "rate": "0.88",
                                "pitch": "-3%"
                            }
                        },
                        "storytelling": {
                            "preferred_voice": "en-US-AriaNeural",
                            "ssml_overrides": {
                                "rate": "0.95",
                                "pitch": "0%"
                            }
                        }
                    }
                }
            }
        }
        
        # Save default config
        self.config_path.parent.mkdir(exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        # Load personas
        for name, persona_config in default_config['personas'].items():
            self.personas[name] = VoicePersona(name, persona_config)
    
    async def generate_speech(self, text: str, persona: str = 'maya', 
                            emotional_tone: str = 'neutral',
                            content_type: str = 'general',
                            output_file: str = None) -> str:
        """Generate speech with specified persona and emotional tone"""
        
        if persona not in self.personas:
            print(f"Warning: Unknown persona '{persona}', using 'maya'")
            persona = 'maya'
        
        voice_persona = self.personas[persona]
        
        # Get the best voice for this content and emotion
        voice_name = voice_persona.get_voice_for_content(content_type, emotional_tone)
        
        # Apply SSML styling
        ssml_text = voice_persona.apply_ssml_style(text, emotional_tone, content_type)
        
        # Generate output filename if not provided
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"speech_{persona}_{emotional_tone}_{timestamp}.mp3"
        
        # Try providers in fallback order
        for provider in self.tts_providers:
            try:
                result = await self._generate_with_provider(
                    ssml_text, voice_name, output_file, provider
                )
                if result:
                    return output_file
            except Exception as e:
                print(f"Provider {provider} failed: {e}")
                continue
        
        raise Exception("All TTS providers failed")
    
    async def _generate_with_provider(self, text: str, voice: str, output_file: str, 
                                    provider: str) -> bool:
        """Generate speech with specific provider"""
        
        if provider == 'edge':
            return await self._generate_edge_tts(text, voice, output_file)
        elif provider == 'elevenlabs':
            return await self._generate_elevenlabs(text, voice, output_file)
        elif provider == 'azure':
            return await self._generate_azure(text, voice, output_file)
        elif provider == 'google':
            return await self._generate_google(text, voice, output_file)
        
        return False
    
    async def _generate_edge_tts(self, text: str, voice: str, output_file: str) -> bool:
        """Generate speech using Edge TTS (free tier)"""
        try:
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_file)
            return True
        except Exception as e:
            print(f"Edge TTS error: {e}")
            return False
    
    async def _generate_elevenlabs(self, text: str, voice: str, output_file: str) -> bool:
        """Generate speech using ElevenLabs API (premium)"""
        api_key = self.provider_settings['elevenlabs']['api_key']
        if not api_key:
            return False
        
        # Map Edge voice to ElevenLabs voice
        voice_mapping = {
            'en-US-JennyNeural': 'rachel',
            'en-US-AriaNeural': 'sarah',
            'en-US-DavisNeural': 'adam',
            'en-US-AmberNeural': 'elli',
            'en-GB-LibbyNeural': 'charlotte'
        }
        
        elevenlabs_voice = voice_mapping.get(voice, 'rachel')
        
        try:
            import requests
            
            url = f"{self.provider_settings['elevenlabs']['base_url']}/text-to-speech/{elevenlabs_voice}"
            
            headers = {
                'Accept': 'audio/mpeg',
                'Content-Type': 'application/json',
                'xi-api-key': api_key
            }
            
            data = {
                'text': text,
                'model_id': 'eleven_monolingual_v1',
                'voice_settings': {
                    'stability': 0.5,
                    'similarity_boost': 0.5
                }
            }
            
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                return True
            
        except Exception as e:
            print(f"ElevenLabs error: {e}")
        
        return False
    
    async def _generate_azure(self, text: str, voice: str, output_file: str) -> bool:
        """Generate speech using Azure Cognitive Services"""
        # Implementation would go here for Azure TTS
        # Requires azure-cognitiveservices-speech package
        return False
    
    async def _generate_google(self, text: str, voice: str, output_file: str) -> bool:
        """Generate speech using Google Cloud Text-to-Speech"""
        # Implementation would go here for Google TTS
        # Requires google-cloud-texttospeech package
        return False
    
    def get_persona_info(self, persona_name: str) -> Dict:
        """Get detailed information about a voice persona"""
        if persona_name not in self.personas:
            return {}
        
        persona = self.personas[persona_name]
        return {
            'name': persona.name,
            'description': persona.config.get('description', ''),
            'characteristics': persona.characteristics,
            'content_types': persona.config.get('content_types', []),
            'primary_voice': persona.primary_voice,
            'fallback_voices': persona.fallback_voices,
            'emotional_range': list(persona.emotional_range.keys())
        }
    
    def list_personas(self) -> List[str]:
        """Get list of available personas"""
        return list(self.personas.keys())
    
    def recommend_persona(self, content_type: str, emotional_context: str = None) -> str:
        """Recommend best persona for content type and context"""
        persona_scores = {}
        
        for name, persona in self.personas.items():
            score = 0
            content_types = persona.config.get('content_types', [])
            
            # Direct content type match
            if content_type in content_types:
                score += 10
            
            # Partial content type match
            if any(ct in content_type for ct in content_types):
                score += 5
            
            # Emotional context match
            if emotional_context and emotional_context in persona.emotional_range:
                score += 8
            
            persona_scores[name] = score
        
        if not persona_scores:
            return 'maya'  # Default
        
        return max(persona_scores, key=persona_scores.get)
    
    async def batch_generate(self, scripts: List[Dict], base_output_dir: str = None) -> List[str]:
        """Generate multiple speech files with different personas"""
        
        if not base_output_dir:
            base_output_dir = tempfile.mkdtemp(prefix="kiin_speech_")
        
        output_dir = Path(base_output_dir)
        output_dir.mkdir(exist_ok=True)
        
        results = []
        
        for i, script in enumerate(scripts):
            try:
                text = script['text']
                persona = script.get('persona', 'maya')
                emotional_tone = script.get('emotional_tone', 'neutral')
                content_type = script.get('content_type', 'general')
                
                output_file = output_dir / f"speech_{i:03d}_{persona}_{emotional_tone}.mp3"
                
                result_file = await self.generate_speech(
                    text, persona, emotional_tone, content_type, str(output_file)
                )
                
                results.append(result_file)
                print(f"✓ Generated: {output_file.name}")
                
            except Exception as e:
                print(f"✗ Error generating script {i}: {e}")
                results.append(None)
        
        return results


# CLI interface
async def main():
    """Main CLI interface for Voice System V2"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Voice System V2 - Professional TTS with Personas")
    parser.add_argument('--text', type=str, help='Text to convert to speech')
    parser.add_argument('--persona', type=str, default='maya',
                       help='Voice persona (maya, dr_sarah, alex, narrator)')
    parser.add_argument('--emotion', type=str, default='neutral',
                       help='Emotional tone')
    parser.add_argument('--content-type', type=str, default='general',
                       help='Content type (validation, tips, confessions, etc.)')
    parser.add_argument('--output', type=str, help='Output file path')
    parser.add_argument('--list-personas', action='store_true',
                       help='List available personas')
    parser.add_argument('--persona-info', type=str,
                       help='Get detailed info about a persona')
    parser.add_argument('--recommend', type=str,
                       help='Recommend persona for content type')
    parser.add_argument('--batch', type=str,
                       help='JSON file with batch generation scripts')
    
    args = parser.parse_args()
    
    voice_system = VoiceSystemV2()
    
    if args.list_personas:
        print("Available Voice Personas:")
        for persona in voice_system.list_personas():
            info = voice_system.get_persona_info(persona)
            print(f"  • {persona}: {info.get('description', '')}")
    
    elif args.persona_info:
        info = voice_system.get_persona_info(args.persona_info)
        if info:
            print(f"Persona: {info['name']}")
            print(f"Description: {info['description']}")
            print(f"Characteristics: {', '.join(info['characteristics'])}")
            print(f"Content Types: {', '.join(info['content_types'])}")
            print(f"Primary Voice: {info['primary_voice']}")
            print(f"Emotional Range: {', '.join(info['emotional_range'])}")
        else:
            print(f"Persona '{args.persona_info}' not found")
    
    elif args.recommend:
        recommended = voice_system.recommend_persona(args.recommend)
        print(f"Recommended persona for '{args.recommend}': {recommended}")
        info = voice_system.get_persona_info(recommended)
        print(f"  {info.get('description', '')}")
    
    elif args.batch:
        with open(args.batch) as f:
            scripts = json.load(f)
        
        print(f"Generating {len(scripts)} speech files...")
        results = await voice_system.batch_generate(scripts)
        
        success_count = sum(1 for r in results if r)
        print(f"✓ Successfully generated {success_count}/{len(scripts)} files")
    
    elif args.text:
        output_file = await voice_system.generate_speech(
            args.text, args.persona, args.emotion, args.content_type, args.output
        )
        print(f"✓ Speech generated: {output_file}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())