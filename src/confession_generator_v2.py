#!/usr/bin/env python3
"""
Kiin Confessions Generator V2 - 10x Enhanced
Creates intimate, emotionally intelligent video content for caregivers.

NEW FEATURES:
- Breathing background effects with subtle movement
- Handwritten/typewriter text styling with emotional emphasis
- Soft vignette effects for intimacy
- Anonymous visual elements and silhouettes
- Whisper-mode TTS with emotional voice selection
- Ambient music integration with room tone
- Expanded confessions database (40+) with categories
- Emotional design with color shifts and intelligent pausing
- Full brand integration with watermarks
- Response/community confessions
"""

import json
import random
import os
import subprocess
import tempfile
import asyncio
import math
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import cv2

# Import Kiin utilities
from brand_utils import KiinBrand, get_brand_colors
from voice_manager import VoiceManager
from music_mixer import MusicMixer
from effects import KiinEffectsLibrary

class ConfessionGeneratorV2:
    def __init__(self, config_path=None, output_dir=None):
        """Initialize the enhanced confession generator"""
        self.base_dir = Path(__file__).parent.parent
        self.config_path = config_path or self.base_dir / "config" / "confessions_v2.json"
        self.output_dir = Path(output_dir or self.base_dir / "output")
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Initialize brand and utilities
        self.brand = KiinBrand()
        self.voice_manager = VoiceManager()
        self.music_mixer = MusicMixer()
        
        # Initialize professional effects library
        self.effects = KiinEffectsLibrary(1080, 1920, 30)
        self.effects = VideoEffects()
        
        # Video specifications
        self.width = 1080
        self.height = 1920
        self.fps = 24
        
        # Load enhanced confessions
        self.confessions = self.load_enhanced_confessions()
        
        # Emotional analysis keywords for intelligent design
        self.emotional_keywords = {
            "pain": ["hurt", "pain", "ache", "suffer", "agony", "grief", "loss", "cry", "tears"],
            "guilt": ["guilty", "shame", "terrible", "bad", "wrong", "selfish", "fault"],
            "fear": ["afraid", "scared", "terrified", "worry", "anxious", "panic"],
            "anger": ["angry", "furious", "rage", "frustrated", "mad", "annoyed"],
            "hopelessness": ["hopeless", "trapped", "stuck", "empty", "numb", "lost"],
            "love": ["love", "care", "cherish", "precious", "dear", "adore"],
            "strength": ["strong", "resilient", "brave", "courage", "endure"],
            "hope": ["hope", "better", "healing", "light", "tomorrow", "future"]
        }
        
        # Color schemes for emotional states
        self.emotion_colors = {
            "pain": {"primary": (180, 140, 140), "accent": (200, 160, 160)},
            "guilt": {"primary": (140, 140, 180), "accent": (160, 160, 200)},
            "fear": {"primary": (150, 150, 150), "accent": (170, 170, 170)},
            "anger": {"primary": (200, 150, 130), "accent": (220, 170, 150)},
            "hopelessness": {"primary": (130, 140, 150), "accent": (150, 160, 170)},
            "love": {"primary": (180, 160, 140), "accent": (200, 180, 160)},
            "strength": {"primary": (140, 180, 160), "accent": (160, 200, 180)},
            "hope": {"primary": (160, 180, 140), "accent": (180, 200, 160)},
            "neutral": {"primary": (160, 160, 160), "accent": (180, 180, 180)}
        }
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def load_enhanced_confessions(self):
        """Load enhanced confessions database"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    return data['confessions']
            except (FileNotFoundError, json.JSONDecodeError):
                pass
        
        # Create enhanced confessions if file doesn't exist
        return self.create_enhanced_confessions()
    
    def create_enhanced_confessions(self):
        """Create expanded confessions database with categories"""
        enhanced_confessions = [
            # GUILT Category
            {
                "id": 1,
                "category": "guilt",
                "emotional_weight": "heavy",
                "hook": "The thing I'm afraid to admit as a caregiver...",
                "confession": "some days I resent the person I'm caring for. And then I feel terrible for feeling that.",
                "validation": "You're not alone in feeling this way. Resentment and love can coexist.",
                "duration_target": 22,
                "pause_points": [8, 15],
                "emphasis_words": ["resent", "terrible", "alone"]
            },
            {
                "id": 2,
                "category": "guilt", 
                "emotional_weight": "medium",
                "hook": "I feel guilty for missing my old life",
                "confession": "when I know their life has changed so much more than mine has.",
                "validation": "Both of your losses matter equally.",
                "duration_target": 18,
                "pause_points": [6, 12],
                "emphasis_words": ["guilty", "missing", "losses", "matter"]
            },
            {
                "id": 3,
                "category": "guilt",
                "emotional_weight": "heavy",
                "hook": "The guilt hits hardest when",
                "confession": "I catch myself getting impatient with them for something they can't control.",
                "validation": "Patience has limits. You're beautifully human.",
                "duration_target": 20,
                "pause_points": [5, 13],
                "emphasis_words": ["guilt", "impatient", "control", "human"]
            },
            
            # GRIEF Category
            {
                "id": 4,
                "category": "grief",
                "emotional_weight": "heavy",
                "hook": "Nobody tells you that caring for someone you love",
                "confession": "sometimes feels like grieving them while they're still here.",
                "validation": "Anticipatory grief is real grief. This pain is part of love.",
                "duration_target": 24,
                "pause_points": [7, 16],
                "emphasis_words": ["grieving", "still here", "grief", "love"]
            },
            {
                "id": 5,
                "category": "grief",
                "emotional_weight": "heavy",
                "hook": "The hardest part about being a caregiver",
                "confession": "is watching someone slowly disappear and pretending you're okay with it.",
                "validation": "Your grief is valid, even while they're still alive.",
                "duration_target": 25,
                "pause_points": [8, 18],
                "emphasis_words": ["disappear", "pretending", "grief", "valid"]
            },
            {
                "id": 6,
                "category": "grief",
                "emotional_weight": "medium",
                "hook": "Nobody prepared me for",
                "confession": "how lonely it would feel to watch someone fade away in slow motion.",
                "validation": "Loneliness in caregiving is one of the hardest parts.",
                "duration_target": 21,
                "pause_points": [5, 14],
                "emphasis_words": ["lonely", "fade", "slow motion", "hardest"]
            },
            
            # FRUSTRATION Category  
            {
                "id": 7,
                "category": "frustration",
                "emotional_weight": "medium",
                "hook": "I love my mom. But some days",
                "confession": "I fantasize about what my life would be like if I didn't have to do this.",
                "validation": "Dreaming of freedom doesn't make you selfish. It makes you human.",
                "duration_target": 23,
                "pause_points": [6, 16],
                "emphasis_words": ["fantasize", "freedom", "selfish", "human"]
            },
            {
                "id": 8,
                "category": "frustration",
                "emotional_weight": "heavy", 
                "hook": "Nobody talks about how",
                "confession": "you can love someone deeply and still feel trapped by caring for them.",
                "validation": "Love and resentment can coexist. You're not broken.",
                "duration_target": 21,
                "pause_points": [5, 14],
                "emphasis_words": ["love", "trapped", "coexist", "broken"]
            },
            {
                "id": 9,
                "category": "frustration",
                "emotional_weight": "medium",
                "hook": "The cruelest irony of caregiving",
                "confession": "is that the better job you do, the longer your sentence becomes.",
                "validation": "Loving well shouldn't feel like punishment.",
                "duration_target": 19,
                "pause_points": [6, 13],
                "emphasis_words": ["irony", "sentence", "punishment"]
            },
            
            # HOPE Category
            {
                "id": 10,
                "category": "hope",
                "emotional_weight": "light",
                "hook": "Some days are harder than others, but",
                "confession": "I'm learning that caring for someone is also caring for the deepest parts of myself.",
                "validation": "Growth happens in the hardest moments. You're becoming who you're meant to be.",
                "duration_target": 26,
                "pause_points": [7, 18],
                "emphasis_words": ["learning", "caring", "growth", "meant to be"]
            },
            {
                "id": 11,
                "category": "hope",
                "emotional_weight": "light",
                "hook": "I used to think strength meant",
                "confession": "never breaking down. Now I know it means getting back up after you do.",
                "validation": "True strength isn't avoiding the fall. It's in the rising.",
                "duration_target": 22,
                "pause_points": [6, 15],
                "emphasis_words": ["strength", "breaking", "getting back up", "rising"]
            },
            {
                "id": 12,
                "category": "hope",
                "emotional_weight": "light",
                "hook": "The unexpected gift of caregiving",
                "confession": "is discovering how much love your heart can actually hold.",
                "validation": "Love expands us in ways we never imagined possible.",
                "duration_target": 20,
                "pause_points": [6, 13],
                "emphasis_words": ["gift", "discovering", "love", "expands"]
            },
            
            # ISOLATION Category
            {
                "id": 13,
                "category": "isolation",
                "emotional_weight": "heavy",
                "hook": "Sometimes I lock myself in the bathroom",
                "confession": "just to cry for five minutes without anyone needing something from me.",
                "validation": "Even caregivers need space to fall apart. Those tears are sacred.",
                "duration_target": 24,
                "pause_points": [8, 17],
                "emphasis_words": ["cry", "needing", "space", "sacred"]
            },
            {
                "id": 14,
                "category": "isolation",
                "emotional_weight": "heavy",
                "hook": "The most isolating thing about caregiving",
                "confession": "is that everyone expects you to be grateful for the 'time together' when it's slowly killing you.",
                "validation": "Your suffering doesn't negate your love. Both can be true.",
                "duration_target": 28,
                "pause_points": [8, 20],
                "emphasis_words": ["isolating", "grateful", "killing", "suffering", "love"]
            },
            {
                "id": 15,
                "category": "isolation",
                "emotional_weight": "medium",
                "hook": "I smile when friends talk about their weekend plans",
                "confession": "but inside I'm remembering what spontaneity used to feel like.",
                "validation": "Mourning your freedom is natural. You haven't lost yourself completely.",
                "duration_target": 23,
                "pause_points": [8, 16],
                "emphasis_words": ["smile", "spontaneity", "mourning", "freedom"]
            },
            
            # IDENTITY Category
            {
                "id": 16,
                "category": "identity",
                "emotional_weight": "medium",
                "hook": "I used to be a whole person",
                "confession": "with dreams and plans. Now I'm just someone who gives medications and changes sheets.",
                "validation": "You haven't disappeared. You're still there, just buried under the care.",
                "duration_target": 25,
                "pause_points": [6, 17],
                "emphasis_words": ["whole", "dreams", "disappeared", "buried"]
            },
            {
                "id": 17,
                "category": "identity",
                "emotional_weight": "medium",
                "hook": "I smile and nod when people say",
                "confession": "'you're so strong' but inside I'm screaming that I never wanted to be this strong.",
                "validation": "Strength isn't a choice you made. It was thrust upon you.",
                "duration_target": 26,
                "pause_points": [7, 18],
                "emphasis_words": ["strong", "screaming", "choice", "thrust"]
            },
            
            # FEAR Category
            {
                "id": 18,
                "category": "fear",
                "emotional_weight": "heavy",
                "hook": "The thing that keeps me up at night:",
                "confession": "wondering if I'm doing enough, or if I'm secretly hoping it will end soon.",
                "validation": "These thoughts don't make you a bad person. They make you human.",
                "duration_target": 24,
                "pause_points": [6, 17],
                "emphasis_words": ["keeps me up", "enough", "hoping", "human"]
            },
            {
                "id": 19,
                "category": "fear",
                "emotional_weight": "heavy",
                "hook": "The thing I'll never say out loud:",
                "confession": "sometimes I wonder if they'd be better off if I just... wasn't here to enable their dependence.",
                "validation": "These dark thoughts don't define you. They're just thoughts.",
                "duration_target": 27,
                "pause_points": [7, 19],
                "emphasis_words": ["never say", "better off", "dependence", "define"]
            },
            
            # NUMBNESS Category
            {
                "id": 20,
                "category": "numbness",
                "emotional_weight": "medium",
                "hook": "The worst part isn't the physical exhaustion",
                "confession": "it's the emotional numbness that creeps in to protect you from caring too much.",
                "validation": "Numbness is sometimes survival. Your heart is still beating underneath.",
                "duration_target": 26,
                "pause_points": [7, 18],
                "emphasis_words": ["exhaustion", "numbness", "protect", "survival", "beating"]
            },
            
            # COMMUNITY RESPONSE Confessions
            {
                "id": 21,
                "category": "response",
                "emotional_weight": "medium",
                "hook": "To the caregiver who thinks they're failing:",
                "confession": "I see you in the grocery store, tired but still choosing their favorite foods. You're not failing.",
                "validation": "Small acts of love are never small. They're everything.",
                "duration_target": 24,
                "pause_points": [7, 17],
                "emphasis_words": ["failing", "tired", "choosing", "everything"]
            },
            {
                "id": 22,
                "category": "response",
                "emotional_weight": "light",
                "hook": "To the caregiver who feels invisible:",
                "confession": "Your sacrifices are seen, even when no one acknowledges them out loud.",
                "validation": "You are witnessed. Your love matters. You matter.",
                "duration_target": 20,
                "pause_points": [6, 13],
                "emphasis_words": ["invisible", "sacrifices", "witnessed", "matter"]
            },
            {
                "id": 23,
                "category": "response",
                "emotional_weight": "light",
                "hook": "To the caregiver who's reading this at 2 AM:",
                "confession": "because you can't sleep for worrying—you're not alone in the dark.",
                "validation": "Thousands of us are awake with you, carrying the same love and fear.",
                "duration_target": 22,
                "pause_points": [8, 15],
                "emphasis_words": ["2 AM", "worrying", "alone", "thousands", "love"]
            },
            
            # Additional original-style confessions
            {
                "id": 24,
                "category": "guilt",
                "emotional_weight": "medium",
                "hook": "I pretend to be asleep",
                "confession": "when they call my name at night, hoping they'll figure it out themselves just once.",
                "validation": "Needing rest doesn't make you selfish. It makes you human.",
                "duration_target": 21,
                "pause_points": [5, 14],
                "emphasis_words": ["pretend", "hoping", "selfish", "human"]
            },
            {
                "id": 25,
                "category": "frustration",
                "emotional_weight": "heavy",
                "hook": "I have imaginary conversations",
                "confession": "with the person they used to be, telling them how angry I am at what they've become.",
                "validation": "Grieving who someone was is part of loving who they are now.",
                "duration_target": 25,
                "pause_points": [6, 17],
                "emphasis_words": ["imaginary", "angry", "become", "grieving"]
            },
            {
                "id": 26,
                "category": "fear",
                "emotional_weight": "heavy",
                "hook": "I'm terrified of the day",
                "confession": "when I'll feel relieved instead of devastated, and what that will say about who I've become.",
                "validation": "Relief after suffering doesn't diminish your love. It honors your endurance.",
                "duration_target": 26,
                "pause_points": [5, 18],
                "emphasis_words": ["terrified", "relieved", "devastated", "endurance"]
            },
            {
                "id": 27,
                "category": "hope",
                "emotional_weight": "light",
                "hook": "Yesterday they smiled",
                "confession": "when I played their favorite song, and for a moment, we both remembered who we used to be.",
                "validation": "These moments of recognition are gifts. Hold them gently.",
                "duration_target": 24,
                "pause_points": [4, 16],
                "emphasis_words": ["smiled", "remembered", "gifts", "gently"]
            },
            {
                "id": 28,
                "category": "identity",
                "emotional_weight": "medium",
                "hook": "I catch glimpses of my old self",
                "confession": "in windows and mirrors, and I barely recognize the person staring back.",
                "validation": "Caregiving changes you. That doesn't mean you're lost forever.",
                "duration_target": 22,
                "pause_points": [7, 15],
                "emphasis_words": ["glimpses", "barely", "recognize", "lost"]
            },
            {
                "id": 29,
                "category": "isolation",
                "emotional_weight": "heavy",
                "hook": "Friends stopped calling",
                "confession": "not because they don't care, but because they don't know what to say to someone who's disappearing.",
                "validation": "Your friendships aren't broken. They're paused, waiting for you to return.",
                "duration_target": 25,
                "pause_points": [5, 17],
                "emphasis_words": ["stopped", "disappearing", "broken", "waiting"]
            },
            {
                "id": 30,
                "category": "guilt",
                "emotional_weight": "medium",
                "hook": "I eat their favorite foods",
                "confession": "in secret because I'm afraid they'll think I'm mocking their dietary restrictions.",
                "validation": "Taking small pleasures doesn't make you cruel. It makes you survive.",
                "duration_target": 23,
                "pause_points": [5, 16],
                "emphasis_words": ["secret", "mocking", "pleasures", "survive"]
            },
            
            # More response/community confessions
            {
                "id": 31,
                "category": "response",
                "emotional_weight": "light",
                "hook": "To the caregiver counting pills at midnight:",
                "confession": "your vigilance is an act of love, even when it feels like a prison sentence.",
                "validation": "Every pill counted is a prayer. Every dose given is hope.",
                "duration_target": 21,
                "pause_points": [6, 14],
                "emphasis_words": ["counting", "vigilance", "prison", "prayer"]
            },
            {
                "id": 32,
                "category": "response",
                "emotional_weight": "medium",
                "hook": "To the caregiver who snapped today:",
                "confession": "your patience isn't infinite, and that's okay. Tomorrow you'll try again.",
                "validation": "Perfect caregivers don't exist. Loving ones do. You are one.",
                "duration_target": 22,
                "pause_points": [6, 15],
                "emphasis_words": ["snapped", "patience", "tomorrow", "perfect"]
            },
            {
                "id": 33,
                "category": "hope",
                "emotional_weight": "light",
                "hook": "Some nights I dream",
                "confession": "about who I'll be when this is over, and I'm surprised to find I'm still in there somewhere.",
                "validation": "The person you were is not lost. They're just resting, waiting to emerge.",
                "duration_target": 25,
                "pause_points": [4, 17],
                "emphasis_words": ["dream", "surprised", "resting", "emerge"]
            },
            {
                "id": 34,
                "category": "numbness",
                "emotional_weight": "medium",
                "hook": "I've become an expert",
                "confession": "at smiling when people ask how I'm doing, even though I haven't felt 'fine' in months.",
                "validation": "Social armor serves a purpose. But you don't have to wear it here.",
                "duration_target": 24,
                "pause_points": [5, 16],
                "emphasis_words": ["expert", "smiling", "fine", "armor"]
            },
            {
                "id": 35,
                "category": "fear",
                "emotional_weight": "heavy",
                "hook": "I practice conversations",
                "confession": "about funeral arrangements in my head, then feel guilty for thinking ahead.",
                "validation": "Planning doesn't mean wishing. It means loving them enough to be prepared.",
                "duration_target": 23,
                "pause_points": [5, 15],
                "emphasis_words": ["practice", "funeral", "guilty", "prepared"]
            },
            {
                "id": 36,
                "category": "frustration",
                "emotional_weight": "medium",
                "hook": "I'm tired of being the strong one,",
                "confession": "the one who has all the answers, when I'm just figuring it out as I go.",
                "validation": "Nobody expects you to be perfect. Except maybe you.",
                "duration_target": 21,
                "pause_points": [7, 15],
                "emphasis_words": ["tired", "strong", "answers", "perfect"]
            },
            {
                "id": 37,
                "category": "identity",
                "emotional_weight": "medium",
                "hook": "I forgot what my laugh sounds like",
                "confession": "when it's not forced, not performed, just pure and spontaneous and mine.",
                "validation": "Your joy isn't gone forever. It's just hibernating, waiting for spring.",
                "duration_target": 23,
                "pause_points": [7, 16],
                "emphasis_words": ["forgot", "laugh", "forced", "hibernating"]
            },
            {
                "id": 38,
                "category": "grief",
                "emotional_weight": "heavy",
                "hook": "I mourn in installments,",
                "confession": "little pieces of grief for each thing they lose, each memory that slips away.",
                "validation": "Gradual loss requires gradual grieving. There's no timeline for this kind of love.",
                "duration_target": 24,
                "pause_points": [5, 16],
                "emphasis_words": ["mourn", "installments", "grief", "timeline"]
            },
            {
                "id": 39,
                "category": "response",
                "emotional_weight": "light",
                "hook": "To the caregiver who thinks no one notices:",
                "confession": "the way you adjust their pillow, remember their stories, protect their dignity—it's beautiful.",
                "validation": "Every small act of care ripples out into the universe. You are making it better.",
                "duration_target": 26,
                "pause_points": [8, 18],
                "emphasis_words": ["notices", "dignity", "beautiful", "ripples"]
            },
            {
                "id": 40,
                "category": "hope",
                "emotional_weight": "light",
                "hook": "Today I realized",
                "confession": "that love isn't just what I'm giving—it's what I'm becoming in the process.",
                "validation": "Caregiving transforms the giver as much as the receiver. You are being refined by love.",
                "duration_target": 24,
                "pause_points": [4, 16],
                "emphasis_words": ["realized", "becoming", "transforms", "refined"]
            }
        ]
        
        # Save to config file
        config_data = {"confessions": enhanced_confessions}
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        print(f"✅ Created enhanced confessions database with {len(enhanced_confessions)} confessions")
        print(f"📁 Saved to: {self.config_path}")
        
        return enhanced_confessions
    
    def analyze_emotional_content(self, confession: Dict) -> Dict:
        """Analyze emotional content for intelligent design decisions"""
        full_text = f"{confession['hook']} {confession['confession']} {confession['validation']}"
        text_lower = full_text.lower()
        
        # Count emotional keywords
        emotion_scores = {}
        for emotion, keywords in self.emotional_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                emotion_scores[emotion] = score
        
        # Determine primary emotion
        primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0] if emotion_scores else "neutral"
        
        # Calculate overall emotional weight
        weight_map = {"light": 1, "medium": 2, "heavy": 3}
        emotional_weight = weight_map.get(confession.get("emotional_weight", "medium"), 2)
        
        return {
            "primary_emotion": primary_emotion,
            "emotion_scores": emotion_scores,
            "emotional_weight": emotional_weight,
            "emphasis_words": confession.get("emphasis_words", []),
            "pause_points": confession.get("pause_points", [])
        }
    
    def create_breathing_background(self, emotion_data: Dict, frame_num: int, total_frames: int) -> Image.Image:
        """Create breathing/pulsing background with emotional color shifts"""
        # Get base colors for emotion
        emotion = emotion_data["primary_emotion"]
        base_colors = self.emotion_colors.get(emotion, self.emotion_colors["neutral"])
        
        # Breathing effect parameters
        breath_cycle = 4.0  # seconds per breath
        breath_frames = breath_cycle * self.fps
        breath_phase = (frame_num % breath_frames) / breath_frames * 2 * math.pi
        
        # Breathing intensity (0.95 to 1.05)
        breath_intensity = 1.0 + 0.05 * math.sin(breath_phase)
        
        # Color shift over time
        time_phase = frame_num / total_frames
        
        # Create base gradient
        image = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(image)
        
        primary_color = base_colors["primary"]
        accent_color = base_colors["accent"]
        
        # Apply breathing effect to colors
        primary_adj = tuple(int(c * breath_intensity) for c in primary_color)
        accent_adj = tuple(int(c * breath_intensity) for c in accent_color)
        
        # Create breathing gradient
        for y in range(self.height):
            pos = y / self.height
            
            # Complex gradient with breathing effect
            if pos < 0.3:
                # Top section - slightly lighter
                blend_factor = pos / 0.3
                r = int(primary_adj[0] + (accent_adj[0] - primary_adj[0]) * blend_factor * 0.3)
                g = int(primary_adj[1] + (accent_adj[1] - primary_adj[1]) * blend_factor * 0.3)
                b = int(primary_adj[2] + (accent_adj[2] - primary_adj[2]) * blend_factor * 0.3)
            elif pos < 0.7:
                # Middle section - main color
                blend_factor = (pos - 0.3) / 0.4
                breathing_offset = 10 * math.sin(breath_phase + pos * math.pi)
                r = int(primary_adj[0] + breathing_offset)
                g = int(primary_adj[1] + breathing_offset)
                b = int(primary_adj[2] + breathing_offset)
            else:
                # Bottom section - darker
                blend_factor = (pos - 0.7) / 0.3
                r = int(primary_adj[0] * (1.0 - blend_factor * 0.2))
                g = int(primary_adj[1] * (1.0 - blend_factor * 0.2))
                b = int(primary_adj[2] * (1.0 - blend_factor * 0.2))
            
            # Clamp values
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))
        
        # Add subtle vignette effect
        self.add_vignette_effect(image, emotion_data["emotional_weight"])
        
        # Add subtle anonymous/intimate overlay
        self.add_intimate_overlay(image, frame_num, total_frames)
        
        return image
    
    def add_vignette_effect(self, image: Image.Image, emotional_weight: int):
        """Add soft vignette for intimacy"""
        # Create vignette mask
        vignette = Image.new('L', (self.width, self.height), 255)
        draw = ImageDraw.Draw(vignette)
        
        # Vignette strength based on emotional weight
        strength = 0.1 + (emotional_weight * 0.05)  # 0.1 to 0.25
        
        center_x, center_y = self.width // 2, self.height // 2
        max_dist = math.sqrt(center_x**2 + center_y**2)
        
        for x in range(self.width):
            for y in range(self.height):
                dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                alpha = max(0, 255 - int(dist / max_dist * 255 * strength))
                if alpha < 255:
                    vignette.putpixel((x, y), alpha)
        
        # Apply vignette
        vignette_img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        vignette_img.putalpha(vignette)
        
        # Convert to RGBA for blending
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Blend with very subtle darkness
        darkened = Image.new('RGBA', (self.width, self.height), (0, 0, 0, int(255 * strength * 0.3)))
        darkened.putalpha(vignette)
        
        image = Image.alpha_composite(image, darkened).convert('RGB')
        return image
    
    def add_intimate_overlay(self, image: Image.Image, frame_num: int, total_frames: int):
        """Add subtle intimate/anonymous visual elements"""
        overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Very subtle texture particles
        time_phase = frame_num / total_frames
        
        for i in range(15):  # Sparse particles
            x = int((math.sin(time_phase * 2 * math.pi + i) * 0.1 + 0.5) * self.width)
            y = int((math.cos(time_phase * 1.5 * math.pi + i * 0.7) * 0.2 + 0.5) * self.height)
            
            # Very faint, small particles
            size = random.randint(1, 3)
            alpha = random.randint(5, 15)  # Very subtle
            color = (255, 255, 255, alpha)
            
            draw.ellipse([x-size, y-size, x+size, y+size], fill=color)
        
        # Blend overlay
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        image = Image.alpha_composite(image, overlay).convert('RGB')
    
    def get_handwritten_font(self, size: int = 60) -> ImageFont.FreeTypeFont:
        """Get handwritten-style font for intimate feel"""
        # Try to find handwritten-style fonts
        handwritten_fonts = [
            "/System/Library/Fonts/Bradley Hand Bold.ttf",  # macOS
            "/System/Library/Fonts/Chalkduster.ttf",        # macOS
            "/System/Library/Fonts/Marker Felt.ttc",        # macOS
        ]
        
        for font_path in handwritten_fonts:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, size)
                except:
                    pass
        
        # Fallback to elegant fonts
        elegant_fonts = [
            "/System/Library/Fonts/Times.ttc",
            "/System/Library/Fonts/Georgia.ttf", 
        ]
        
        for font_path in elegant_fonts:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, size)
                except:
                    pass
        
        # Final fallback
        try:
            return ImageFont.truetype("arial.ttf", size)
        except:
            return ImageFont.load_default()
    
    def create_typewriter_text_frames(self, confession: Dict, total_duration: float) -> List[Image.Image]:
        """Create frames with typewriter/handwritten text and emotional emphasis"""
        emotion_data = self.analyze_emotional_content(confession)
        
        hook = confession['hook']
        content = confession['confession']
        validation = confession['validation']
        
        total_frames = int(total_duration * self.fps)
        frames = []
        
        # Enhanced fonts with emotion-based sizing
        base_size = 52 if emotion_data["emotional_weight"] >= 2 else 48
        hook_font = self.get_handwritten_font(base_size + 8)
        content_font = self.get_handwritten_font(base_size)
        validation_font = self.get_handwritten_font(base_size - 4)
        emphasis_font = self.get_handwritten_font(base_size + 4)  # For emphasized words
        
        # Enhanced timing with emotional pauses
        hook_frames = int(total_frames * 0.25)
        content_frames = int(total_frames * 0.55)
        validation_frames = total_frames - hook_frames - content_frames
        
        # Get emphasis words and pause points
        emphasis_words = set(emotion_data["emphasis_words"])
        pause_points = confession.get("pause_points", [])
        
        # Split text into words for typewriter effect
        hook_words = hook.split()
        content_words = content.split()
        validation_words = validation.split()
        
        # Create frames with typewriter effect
        for frame_num in range(total_frames):
            # Create breathing background
            bg = self.create_breathing_background(emotion_data, frame_num, total_frames)
            draw = ImageDraw.Draw(bg)
            
            current_y = 300  # Starting position
            margin = 80
            max_width = self.width - (2 * margin)
            line_spacing = 35
            section_spacing = 50
            
            if frame_num < hook_frames:
                # Hook phase with typewriter effect
                progress = frame_num / hook_frames
                words_to_show = int(progress * len(hook_words))
                char_progress = (progress * len(hook_words)) % 1
                
                # Show complete words plus partial word
                visible_text = " ".join(hook_words[:words_to_show])
                if words_to_show < len(hook_words):
                    partial_word = hook_words[words_to_show]
                    chars_to_show = int(char_progress * len(partial_word))
                    visible_text += " " + partial_word[:chars_to_show]
                
                # Render with emphasis
                self.draw_text_with_emphasis(draw, visible_text, hook_font, emphasis_font, 
                                           emphasis_words, current_y, max_width, 
                                           emotion_data["primary_emotion"])
                
            elif frame_num < hook_frames + content_frames:
                # Content phase
                content_frame = frame_num - hook_frames
                
                # Show full hook (slightly faded)
                hook_color = self.get_text_color(emotion_data["primary_emotion"], 0.7)
                hook_lines = self.wrap_text_intelligent(hook, hook_font, max_width)
                current_y = self.draw_lines(draw, hook_lines, hook_font, hook_color, 
                                          current_y, line_spacing)
                current_y += section_spacing
                
                # Typewriter effect for content
                progress = content_frame / content_frames
                
                # Add pauses at emotional points
                adjusted_progress = self.apply_emotional_pauses(progress, pause_points, content)
                
                words_to_show = int(adjusted_progress * len(content_words))
                char_progress = (adjusted_progress * len(content_words)) % 1
                
                visible_content = " ".join(content_words[:words_to_show])
                if words_to_show < len(content_words):
                    partial_word = content_words[words_to_show]
                    chars_to_show = int(char_progress * len(partial_word))
                    visible_content += " " + partial_word[:chars_to_show]
                
                self.draw_text_with_emphasis(draw, visible_content, content_font, emphasis_font,
                                           emphasis_words, current_y, max_width,
                                           emotion_data["primary_emotion"])
                
            else:
                # Validation phase
                validation_frame = frame_num - hook_frames - content_frames
                
                # Show full hook and content (faded)
                hook_color = self.get_text_color(emotion_data["primary_emotion"], 0.6)
                content_color = self.get_text_color(emotion_data["primary_emotion"], 0.8)
                
                hook_lines = self.wrap_text_intelligent(hook, hook_font, max_width)
                current_y = self.draw_lines(draw, hook_lines, hook_font, hook_color, 
                                          current_y, line_spacing)
                current_y += section_spacing * 0.7
                
                content_lines = self.wrap_text_intelligent(content, content_font, max_width)
                current_y = self.draw_lines(draw, content_lines, content_font, content_color,
                                          current_y, line_spacing)
                current_y += section_spacing
                
                # Typewriter effect for validation
                progress = validation_frame / validation_frames
                words_to_show = int(progress * len(validation_words))
                char_progress = (progress * len(validation_words)) % 1
                
                visible_validation = " ".join(validation_words[:words_to_show])
                if words_to_show < len(validation_words):
                    partial_word = validation_words[words_to_show]
                    chars_to_show = int(char_progress * len(partial_word))
                    visible_validation += " " + partial_word[:chars_to_show]
                
                # Validation text with warm, hopeful color
                validation_color = self.get_text_color("hope", 1.0)
                validation_lines = self.wrap_text_intelligent(visible_validation, validation_font, max_width)
                self.draw_lines(draw, validation_lines, validation_font, validation_color,
                              current_y, line_spacing)
            
            frames.append(bg)
        
        return frames
    
    def get_text_color(self, emotion: str, alpha: float = 1.0) -> Tuple[int, int, int]:
        """Get text color based on emotion"""
        brand_colors = get_brand_colors()
        
        emotion_text_colors = {
            "pain": (80, 60, 60),
            "guilt": (70, 70, 90),
            "fear": (80, 80, 80),
            "anger": (90, 70, 60),
            "hopelessness": (70, 80, 90),
            "love": (90, 70, 60),
            "strength": (60, 90, 70),
            "hope": (70, 90, 60),
            "neutral": (60, 60, 60)
        }
        
        base_color = emotion_text_colors.get(emotion, emotion_text_colors["neutral"])
        return tuple(int(c * alpha) for c in base_color)
    
    def wrap_text_intelligent(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        """Intelligent text wrapping that keeps phrases together"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = current_line + [word]
            bbox = font.getbbox(" ".join(test_line))
            width = bbox[2] - bbox[0]
            
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(" ".join(current_line))
        
        return lines
    
    def draw_text_with_emphasis(self, draw: ImageDraw.Draw, text: str, 
                              regular_font: ImageFont.FreeTypeFont,
                              emphasis_font: ImageFont.FreeTypeFont,
                              emphasis_words: set, start_y: int, max_width: int, 
                              emotion: str) -> int:
        """Draw text with emphasized emotional words"""
        lines = self.wrap_text_intelligent(text, regular_font, max_width)
        current_y = start_y
        line_spacing = 35
        
        regular_color = self.get_text_color(emotion, 1.0)
        emphasis_color = self.get_text_color("hope", 1.0)  # Warm emphasis
        
        for line in lines:
            words = line.split()
            current_x = 80  # Left margin
            
            for word in words:
                # Clean word for emphasis check
                clean_word = word.lower().strip('.,!?";:')
                is_emphasized = clean_word in emphasis_words
                
                font = emphasis_font if is_emphasized else regular_font
                color = emphasis_color if is_emphasized else regular_color
                
                # Draw word
                draw.text((current_x, current_y), word, fill=color, font=font)
                
                # Move x position for next word
                bbox = font.getbbox(word + " ")
                current_x += bbox[2] - bbox[0]
            
            current_y += line_spacing
        
        return current_y
    
    def draw_lines(self, draw: ImageDraw.Draw, lines: List[str], 
                   font: ImageFont.FreeTypeFont, color: Tuple[int, int, int],
                   start_y: int, line_spacing: int) -> int:
        """Draw multiple lines of text"""
        current_y = start_y
        
        for line in lines:
            bbox = font.getbbox(line)
            x = (self.width - (bbox[2] - bbox[0])) // 2  # Center text
            draw.text((x, current_y), line, fill=color, font=font)
            current_y += line_spacing
        
        return current_y
    
    def apply_emotional_pauses(self, progress: float, pause_points: List[int], 
                              text: str) -> float:
        """Apply intelligent pauses at emotional moments"""
        if not pause_points:
            return progress
        
        words = text.split()
        total_words = len(words)
        
        # Convert pause points to relative positions (0-1)
        pause_positions = [p / total_words for p in pause_points]
        
        # Apply pauses by slowing progress at pause points
        for pause_pos in pause_positions:
            if abs(progress - pause_pos) < 0.05:  # Near pause point
                # Slow down progress
                return progress * 0.85
        
        return progress
    
    async def create_whisper_audio(self, confession: Dict, duration: float) -> str:
        """Create intimate whisper-mode audio with emotional voice selection"""
        emotion_data = self.analyze_emotional_content(confession)
        
        # Select voice based on content type and emotion
        content_type = "confessions"
        suitable_voices = self.voice_manager.get_suitable_voices_for_content(content_type)
        
        # Choose voice based on emotion
        emotion = emotion_data["primary_emotion"]
        if emotion in ["pain", "grief", "fear"]:
            voice = "en-US-SaraNeural"  # Soft, empathetic
        elif emotion in ["hope", "love", "strength"]:
            voice = "en-CA-ClaraNeural"  # Warm, encouraging
        elif emotion in ["guilt", "numbness"]:
            voice = "en-GB-SoniaNeural"  # Understanding, gentle
        else:
            voice = suitable_voices[0] if suitable_voices else "en-US-AriaNeural"
        
        # Combine text with emotional pausing
        full_text = self.create_emotional_text_timing(confession, emotion_data)
        
        output_path = self.temp_dir / "whisper_audio.wav"
        
        import edge_tts
        communicate = edge_tts.Communicate(full_text, voice)
        
        # Whisper-mode settings
        communicate.rate = "-30%"  # Slower for intimacy
        communicate.pitch = "-10Hz"  # Lower pitch
        
        await communicate.save(str(output_path))
        
        return str(output_path)
    
    def create_emotional_text_timing(self, confession: Dict, emotion_data: Dict) -> str:
        """Create text with SSML pauses for emotional timing"""
        hook = confession['hook']
        content = confession['confession']
        validation = confession['validation']
        
        # Add pauses based on emotional weight
        weight = emotion_data["emotional_weight"]
        short_pause = "<break time='0.8s'/>" if weight >= 2 else "<break time='0.5s'/>"
        long_pause = "<break time='1.5s'/>" if weight >= 3 else "<break time='1.0s'/>"
        
        # Add emphasis to emotional words
        emphasis_words = emotion_data["emphasis_words"]
        
        def add_emphasis(text):
            words = text.split()
            result = []
            for word in words:
                clean_word = word.lower().strip('.,!?";:')
                if clean_word in emphasis_words:
                    result.append(f"<emphasis level='moderate'>{word}</emphasis>")
                else:
                    result.append(word)
            return " ".join(result)
        
        # Construct SSML text
        emotional_text = f"""
        <speak>
            <prosody rate='slow' pitch='low'>
                {add_emphasis(hook)}
                {long_pause}
                {add_emphasis(content)}
                {long_pause}
                <prosody rate='x-slow' pitch='+2Hz'>
                    {add_emphasis(validation)}
                </prosody>
            </prosody>
        </speak>
        """
        
        return emotional_text.strip()
    
    async def add_ambient_music(self, video_path: str, confession: Dict) -> str:
        """Add ambient music based on emotional content"""
        emotion_data = self.analyze_emotional_content(confession)
        
        # Map emotion to mood
        emotion_mood_map = {
            "pain": "intimate",
            "grief": "intimate",
            "guilt": "calm", 
            "fear": "calm",
            "anger": "calm",
            "hopelessness": "intimate",
            "love": "warm",
            "strength": "warm",
            "hope": "uplifting",
            "neutral": "calm"
        }
        
        mood = emotion_mood_map.get(emotion_data["primary_emotion"], "intimate")
        
        # Generate output path
        output_path = self.temp_dir / f"confession_with_music_{int(time.time())}.mp4"
        
        # Use music mixer to add ambient music
        success = self.music_mixer.mix_video_with_music(
            video_path,
            None,  # Let it choose based on mood
            str(output_path),
            mood=mood
        )
        
        if success:
            return str(output_path)
        else:
            return video_path  # Return original if mixing fails
    
    def add_branding_elements(self, video_path: str) -> str:
        """Add subtle branding elements"""
        output_path = self.temp_dir / f"branded_confession_{int(time.time())}.mp4"
        
        # Add watermark using effects
        success = self.effects.add_watermark(
            video_path,
            str(output_path),
            position="bottom_right",
            opacity=0.4  # Very subtle
        )
        
        if success:
            return str(output_path)
        else:
            return video_path
    
    def save_enhanced_frames_as_video(self, frames: List[Image.Image], 
                                     output_path: str, audio_path: str = None) -> bool:
        """Save frames as video with enhanced encoding"""
        # Save frames
        frame_pattern = self.temp_dir / "enhanced_frame_%05d.png"
        
        for i, frame in enumerate(frames):
            frame.save(self.temp_dir / f"enhanced_frame_{i:05d}.png")
        
        # Enhanced FFmpeg command
        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(self.fps),
            "-i", str(self.temp_dir / "enhanced_frame_%05d.png"),
        ]
        
        if audio_path and os.path.exists(audio_path):
            cmd.extend([
                "-i", audio_path,
                "-c:v", "h264_videotoolbox",  # Hardware encoding
                "-b:v", "3M",  # Higher quality
                "-c:a", "aac",
                "-b:a", "128k",
                "-shortest",
                "-movflags", "+faststart"  # Web optimization
            ])
        else:
            cmd.extend([
                "-c:v", "h264_videotoolbox",
                "-b:v", "3M",
                "-movflags", "+faststart"
            ])
        
        cmd.extend(["-pix_fmt", "yuv420p", str(output_path)])
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Enhanced encoding failed: {e}")
            return False
    
    def cleanup(self):
        """Clean up temporary files"""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
        self.effects.cleanup()
    
    async def generate_confession_v2(self, confession_id: int = None, 
                                   category: str = None,
                                   output_name: str = "confession_v2.mp4") -> str:
        """Generate enhanced confession video with 10x improvements"""
        try:
            # Select confession
            if confession_id is not None:
                confession = next((c for c in self.confessions if c['id'] == confession_id), None)
                if not confession:
                    raise ValueError(f"Confession ID {confession_id} not found")
            elif category:
                category_confessions = [c for c in self.confessions if c.get('category') == category]
                if not category_confessions:
                    raise ValueError(f"No confessions found for category: {category}")
                confession = random.choice(category_confessions)
            else:
                confession = random.choice(self.confessions)
            
            print(f"🎬 Generating V2 confession: '{confession['hook'][:50]}...'")
            print(f"📊 Category: {confession.get('category', 'unknown')}")
            print(f"⚖️ Emotional weight: {confession.get('emotional_weight', 'medium')}")
            
            # Analyze emotional content
            emotion_data = self.analyze_emotional_content(confession)
            print(f"🎭 Primary emotion: {emotion_data['primary_emotion']}")
            
            duration = confession.get('duration_target', 22)
            
            # Create enhanced visual frames
            print("🎨 Creating enhanced visual frames with breathing effects...")
            frames = self.create_typewriter_text_frames(confession, duration)
            
            # Create whisper-mode audio
            print("🎤 Generating whisper-mode audio...")
            audio_path = await self.create_whisper_audio(confession, duration)
            
            # Save initial video
            temp_video = self.temp_dir / "confession_base.mp4"
            print("🎥 Rendering enhanced video...")
            success = self.save_enhanced_frames_as_video(frames, str(temp_video), audio_path)
            
            if not success:
                raise Exception("Failed to render base video")
            
            # Add ambient music
            print("🎵 Adding emotional ambient music...")
            video_with_music = await self.add_ambient_music(str(temp_video), confession)
            
            # Add branding
            print("🏷️ Adding subtle branding...")
            final_video = self.add_branding_elements(video_with_music)
            
            # Copy to output location
            output_path = self.output_dir / output_name
            import shutil
            shutil.copy2(final_video, output_path)
            
            print(f"\n✅ Enhanced confession video generated!")
            print(f"📍 Location: {output_path}")
            print(f"📏 Dimensions: {self.width}x{self.height} (9:16)")
            print(f"⏱️ Duration: ~{duration} seconds")
            print(f"🎭 Emotion: {emotion_data['primary_emotion']}")
            print(f"💬 Confession ID: {confession['id']}")
            print(f"🏷️ Category: {confession.get('category', 'general')}")
            
            # Print categories summary
            categories = {}
            for c in self.confessions:
                cat = c.get('category', 'general')
                categories[cat] = categories.get(cat, 0) + 1
            
            print(f"\n📊 Available categories: {', '.join(f'{k}({v})' for k, v in categories.items())}")
            
            return str(output_path)
            
        except Exception as e:
            print(f"❌ Error generating V2 confession: {e}")
            raise
        finally:
            self.cleanup()

def main():
    """Enhanced CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Kiin Confessions Generator V2 - 10x Enhanced",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python confession_generator_v2.py --confession-id 5 --output confession_v2_example_1.mp4
  python confession_generator_v2.py --category guilt --output guilt_confession.mp4
  python confession_generator_v2.py --category hope --output hopeful_confession.mp4
  python confession_generator_v2.py --list-categories
  python confession_generator_v2.py --create-examples
        """
    )
    
    parser.add_argument("--confession-id", type=int, help="Specific confession ID")
    parser.add_argument("--category", type=str, help="Select by category")
    parser.add_argument("--output", "-o", default="confession_v2.mp4", help="Output filename")
    parser.add_argument("--list-categories", action="store_true", help="List available categories")
    parser.add_argument("--create-examples", action="store_true", help="Create 3 example videos")
    parser.add_argument("--config", help="Path to enhanced confessions JSON")
    parser.add_argument("--output-dir", help="Output directory")
    
    args = parser.parse_args()
    
    generator = ConfessionGeneratorV2(
        config_path=args.config,
        output_dir=args.output_dir
    )
    
    if args.list_categories:
        categories = {}
        for confession in generator.confessions:
            cat = confession.get('category', 'general')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(confession['id'])
        
        print("📊 Available confession categories:")
        for category, ids in categories.items():
            print(f"  • {category}: {len(ids)} confessions (IDs: {', '.join(map(str, ids[:5]))}{'...' if len(ids) > 5 else ''})")
        return
    
    if args.create_examples:
        print("🎬 Creating 3 example confession videos...")
        
        examples = [
            {"category": "guilt", "output": "confession_v2_example_1.mp4"},
            {"category": "hope", "output": "confession_v2_example_2.mp4"}, 
            {"category": "response", "output": "confession_v2_example_3.mp4"}
        ]
        
        for i, example in enumerate(examples, 1):
            print(f"\n📹 Creating example {i}/3: {example['category']} confession")
            try:
                asyncio.run(generator.generate_confession_v2(
                    category=example["category"],
                    output_name=example["output"]
                ))
            except Exception as e:
                print(f"❌ Failed to create example {i}: {e}")
        
        print(f"\n🎉 Example creation complete!")
        return
    
    # Generate single video
    asyncio.run(generator.generate_confession_v2(
        confession_id=args.confession_id,
        category=args.category,
        output_name=args.output
    ))

if __name__ == "__main__":
    main()