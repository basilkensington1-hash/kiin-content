#!/usr/bin/env python3
"""
Validation Video Generator V2 - 10x Enhanced Version
Creates professional, cinematic validation videos with particles, animation, music, and branding
"""

import argparse
import json
import math
import os
import random
import subprocess
import sys
import tempfile
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

import asyncio
import edge_tts
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np

# Import our enhanced modules
try:
    from .voice_manager import VoiceManager
    from .music_mixer import MusicMixer
    from .brand_utils import KiinBrand
    from .effects import KiinEffectsLibrary
except ImportError:
    # Fallback for running as script
    from voice_manager import VoiceManager
    from music_mixer import MusicMixer
    from brand_utils import KiinBrand
    from effects import KiinEffectsLibrary


class EnhancedValidationGenerator:
    """Next-generation validation video generator with professional effects"""
    
    def __init__(self, config_path: str = None):
        """Initialize the enhanced generator"""
        self.width = 1080
        self.height = 1920
        self.fps = 30  # Higher quality
        
        # Initialize modules
        self.voice_manager = VoiceManager()
        self.music_mixer = MusicMixer()
        self.brand = KiinBrand()
        
        # Initialize professional effects library
        self.effects = KiinEffectsLibrary(self.width, self.height, self.fps)
        
        # Paths
        if config_path is None:
            script_dir = Path(__file__).parent
            config_path = script_dir.parent / "config" / "validation_messages_v2.json"
        
        self.config_path = Path(config_path)
        self.messages = self._load_or_create_enhanced_messages()
        
        # Enhanced visual styles
        self.background_styles = {
            "gradient_calm": {
                "name": "Gradient Calm",
                "type": "gradient",
                "colors": [
                    [(135, 206, 250), (221, 160, 221)],  # Sky blue to plum
                    [(255, 182, 193), (221, 160, 221)],  # Light pink to plum
                    [(175, 238, 238), (255, 182, 193)],  # Pale turquoise to light pink
                    [(230, 230, 250), (255, 192, 203)],  # Lavender to pink
                ],
                "particles": "gentle_sparkles"
            },
            "nature_soft": {
                "name": "Soft Nature",
                "type": "nature",
                "base_colors": [(243, 246, 249), (216, 235, 216)],  # Soft nature tones
                "particles": "floating_hearts",
                "overlay": "soft_bokeh"
            },
            "abstract_warm": {
                "name": "Abstract Warm",
                "type": "abstract",
                "colors": [(255, 248, 240), (255, 228, 196), (245, 222, 179)],  # Warm abstract
                "particles": "gentle_dots",
                "flow": "organic_curves"
            },
            "brand_professional": {
                "name": "Brand Professional", 
                "type": "branded",
                "colors": "brand_palette",
                "particles": "minimal_sparkles",
                "watermark": True
            }
        }
        
        # Particle effects configurations
        self.particle_configs = {
            "gentle_sparkles": {
                "count": 15,
                "size_range": (2, 6),
                "opacity_range": (0.3, 0.7),
                "movement": "float_up",
                "speed": 0.8,
                "color": (255, 255, 255)
            },
            "floating_hearts": {
                "count": 8,
                "size_range": (8, 16),
                "opacity_range": (0.2, 0.5),
                "movement": "gentle_sway",
                "speed": 0.5,
                "shape": "heart",
                "color": (255, 192, 203)
            },
            "gentle_dots": {
                "count": 25,
                "size_range": (1, 4),
                "opacity_range": (0.4, 0.8),
                "movement": "slow_drift",
                "speed": 0.3,
                "color": (220, 220, 220)
            },
            "minimal_sparkles": {
                "count": 6,
                "size_range": (3, 8),
                "opacity_range": (0.5, 0.9),
                "movement": "subtle_twinkle",
                "speed": 0.6,
                "color": (255, 255, 255)
            }
        }
        
        # Text animation configurations
        self.text_animations = {
            "gentle_pulse": {
                "type": "scale",
                "duration": 2.0,
                "intensity": 0.05,
                "easing": "ease_in_out"
            },
            "soft_glow": {
                "type": "glow",
                "duration": 1.5,
                "intensity": 0.3,
                "color": (255, 255, 255, 100)
            },
            "word_emphasis": {
                "type": "highlight_words",
                "keywords": ["you", "valid", "okay", "enough", "matter", "love", "deserve"],
                "effect": "bold_color",
                "color": None  # Will use brand colors
            },
            "fade_cascade": {
                "type": "cascade_fade",
                "word_delay": 0.1,
                "fade_duration": 0.8
            }
        }
        
        # A/B testing variations
        self.ab_variations = {
            "color_schemes": [
                "warm_sunset", "cool_ocean", "nature_green", "lavender_dream", "brand_colors"
            ],
            "animation_speeds": [0.7, 1.0, 1.3],  # Slow, normal, fast
            "particle_densities": ["minimal", "moderate", "rich"],
            "text_positions": ["center", "lower_third", "dynamic"]
        }
        
    def _load_or_create_enhanced_messages(self) -> Dict:
        """Load enhanced messages or create from existing ones"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Create enhanced version from basic messages
            return self._create_enhanced_message_database()
    
    def _create_enhanced_message_database(self) -> Dict:
        """Create an enhanced message database with 50+ messages and series"""
        enhanced_messages = {
            "permission_statements": [
                {
                    "text": "If you've ever felt guilty for wanting just 10 minutes alone... that doesn't make you a bad caregiver. It makes you human. 💙",
                    "duration": 15,
                    "series": "Permission to Be Human",
                    "emphasis_words": ["guilty", "human", "caregiver"],
                    "mood": "warm"
                },
                {
                    "text": "You're allowed to feel frustrated. You're allowed to feel tired. You're allowed to want things to be different. 🤗",
                    "duration": 14,
                    "series": "Permission to Feel",
                    "emphasis_words": ["allowed", "frustrated", "tired"],
                    "mood": "gentle"
                },
                {
                    "text": "It's okay to say no sometimes. Setting boundaries isn't selfish - it's necessary. 🌟",
                    "duration": 12,
                    "series": "Boundaries Matter",
                    "emphasis_words": ["okay", "boundaries", "necessary"],
                    "mood": "empowering"
                },
                {
                    "text": "You don't have to be grateful for this journey every single day. Some days, it's okay to just survive it. 💚",
                    "duration": 16,
                    "series": "Permission to Struggle",
                    "emphasis_words": ["don't have to", "grateful", "survive"],
                    "mood": "understanding"
                },
                {
                    "text": "Your feelings are valid, even the messy ones. Especially the messy ones. ✨",
                    "duration": 13,
                    "series": "Feelings Are Valid",
                    "emphasis_words": ["feelings", "valid", "messy"],
                    "mood": "accepting"
                },
                {
                    "text": "You're allowed to grieve the life you planned while still loving the life you have. Both can be true. 🌈",
                    "duration": 17,
                    "series": "Dual Truths",
                    "emphasis_words": ["grieve", "loving", "both"],
                    "mood": "compassionate"
                },
                # NEW MESSAGES
                {
                    "text": "That moment when you resent your loved one? It doesn't make you evil. It makes you overwhelmed. 💙",
                    "duration": 15,
                    "series": "Permission to Feel",
                    "emphasis_words": ["resent", "evil", "overwhelmed"],
                    "mood": "understanding"
                },
                {
                    "text": "You're allowed to miss your old life. Missing freedom doesn't mean you don't love them. 🤍",
                    "duration": 14,
                    "series": "Permission to Grieve",
                    "emphasis_words": ["miss", "freedom", "love"],
                    "mood": "gentle"
                },
                {
                    "text": "It's okay to want someone else to take care of you for once. You deserve tenderness too. ✨",
                    "duration": 16,
                    "series": "You Deserve Care",
                    "emphasis_words": ["want", "care", "deserve", "tenderness"],
                    "mood": "nurturing"
                }
            ],
            "guilt_relief": [
                {
                    "text": "For the caregiver who cried in their car today... your tears don't mean you're weak. They mean you care deeply. 💙",
                    "duration": 16,
                    "series": "Tears Are Strength",
                    "emphasis_words": ["cried", "weak", "care deeply"],
                    "mood": "comforting"
                },
                {
                    "text": "That moment when you snapped at them? You're not a monster. You're a human carrying an impossible load. 🤍",
                    "duration": 15,
                    "series": "Human Moments",
                    "emphasis_words": ["snapped", "monster", "human", "impossible"],
                    "mood": "forgiving"
                },
                {
                    "text": "You're not failing because you had to ask for help. You're being smart. You're being brave. 💪",
                    "duration": 14,
                    "series": "Help Is Strength",
                    "emphasis_words": ["not failing", "help", "smart", "brave"],
                    "mood": "empowering"
                },
                {
                    "text": "The fact that you're worried about not being good enough proves you already are. Good enough caregivers worry. 🌟",
                    "duration": 17,
                    "series": "Worry Proves Love",
                    "emphasis_words": ["worried", "good enough", "proves"],
                    "mood": "reassuring"
                },
                {
                    "text": "Your worst caregiving day doesn't erase all your best ones. One bad moment isn't your whole story. 💚",
                    "duration": 16,
                    "series": "Bad Days Don't Define You",
                    "emphasis_words": ["worst", "erase", "best", "story"],
                    "mood": "perspective"
                },
                {
                    "text": "You haven't failed them by wanting your own life back sometimes. That desire makes you normal, not selfish. ✨",
                    "duration": 18,
                    "series": "Wanting Life Back",
                    "emphasis_words": ["failed", "own life", "normal", "selfish"],
                    "mood": "validating"
                },
                # NEW MESSAGES
                {
                    "text": "That time you lost your temper? It doesn't cancel out all the times you were patient. You're human. 🤗",
                    "duration": 16,
                    "series": "Human Moments", 
                    "emphasis_words": ["lost temper", "cancel", "patient", "human"],
                    "mood": "forgiving"
                },
                {
                    "text": "Feeling guilty for enjoying yourself when they can't? That guilt shows your heart, not your failure. 💙",
                    "duration": 15,
                    "series": "Guilt About Joy",
                    "emphasis_words": ["guilty", "enjoying", "heart", "failure"],
                    "mood": "understanding"
                },
                {
                    "text": "You're not responsible for their happiness 24/7. You're their caregiver, not their emotional savior. 🌟",
                    "duration": 17,
                    "series": "Boundaries Matter",
                    "emphasis_words": ["not responsible", "happiness", "caregiver", "savior"],
                    "mood": "boundaries"
                }
            ],
            "burnout_acknowledgment": [
                {
                    "text": "If you're running on empty today, that's not weakness. That's what happens when you give everything you have. 🔋",
                    "duration": 16,
                    "series": "Empty Is Natural",
                    "emphasis_words": ["empty", "weakness", "give everything"],
                    "mood": "understanding"
                },
                {
                    "text": "Some days, caregiving feels impossible. Those days don't make you less capable. They make you human. 🤗",
                    "duration": 15,
                    "series": "Impossible Days",
                    "emphasis_words": ["impossible", "less capable", "human"],
                    "mood": "normalizing"
                },
                {
                    "text": "Your exhaustion is real. Your overwhelm is valid. You don't need to power through every single moment. 💤",
                    "duration": 16,
                    "series": "Exhaustion Is Valid",
                    "emphasis_words": ["exhaustion", "real", "overwhelm", "valid", "power through"],
                    "mood": "permission"
                },
                {
                    "text": "To the caregiver who feels invisible: I see you. Your sacrifice matters. Your love matters. You matter. 👁️",
                    "duration": 16,
                    "series": "You Are Seen",
                    "emphasis_words": ["invisible", "see you", "matters", "matter"],
                    "mood": "recognition"
                },
                {
                    "text": "It's okay to feel like you're drowning some days. The waves don't last forever, even when they feel endless. 🌊",
                    "duration": 17,
                    "series": "Drowning Metaphor",
                    "emphasis_words": ["drowning", "waves", "forever", "endless"],
                    "mood": "hope"
                },
                {
                    "text": "You've been strong for so long that you've forgotten it's okay to be tired. Being tired doesn't mean giving up. 😴",
                    "duration": 17,
                    "series": "Strength and Tiredness",
                    "emphasis_words": ["strong", "forgotten", "tired", "giving up"],
                    "mood": "permission"
                },
                # NEW MESSAGES
                {
                    "text": "That bone-deep exhaustion you feel? It's not just in your head. It's the weight of loving someone this hard. 💙",
                    "duration": 16,
                    "series": "Deep Exhaustion",
                    "emphasis_words": ["bone-deep", "exhaustion", "weight", "loving"],
                    "mood": "validating"
                },
                {
                    "text": "You're allowed to feel empty even when surrounded by people who need you. Your emptiness is real too. 🤍",
                    "duration": 17,
                    "series": "Empty Among Need",
                    "emphasis_words": ["empty", "surrounded", "need you", "real"],
                    "mood": "recognition"
                },
                {
                    "text": "Some days survival mode isn't giving up - it's the bravest thing you can do. Just surviving is enough. ✨",
                    "duration": 18,
                    "series": "Survival Is Brave",
                    "emphasis_words": ["survival", "giving up", "bravest", "enough"],
                    "mood": "strength"
                }
            ],
            "caregiver_identity": [
                {
                    "text": "You are more than just a caregiver. You're a whole person with dreams, needs, and worth beyond what you do. 🌟",
                    "duration": 17,
                    "series": "More Than a Role",
                    "emphasis_words": ["more than", "whole person", "dreams", "worth"],
                    "mood": "identity"
                },
                {
                    "text": "Before you became their caregiver, you were someone too. That someone still exists and still matters. 💫",
                    "duration": 16,
                    "series": "Before and After",
                    "emphasis_words": ["before", "someone", "exists", "matters"],
                    "mood": "continuity"
                },
                {
                    "text": "Your identity isn't just about who you care for. You get to be your own person too. Both are true. 🌈",
                    "duration": 16,
                    "series": "Dual Identity",
                    "emphasis_words": ["identity", "care for", "own person", "both"],
                    "mood": "balance"
                },
                {
                    "text": "The person you were before this journey began deserves to exist alongside the caregiver you've become. 💙",
                    "duration": 16,
                    "series": "Before and After",
                    "emphasis_words": ["before", "deserves", "exist", "become"],
                    "mood": "integration"
                },
                {
                    "text": "Loving someone doesn't mean disappearing. You can care for them while also caring for yourself. 💚",
                    "duration": 16,
                    "series": "Love Without Disappearing",
                    "emphasis_words": ["loving", "disappearing", "care for", "yourself"],
                    "mood": "balance"
                },
                {
                    "text": "You're not selfish for wanting to remember who you are outside of caregiving. That's called being human. ✨",
                    "duration": 17,
                    "series": "Remembering Self",
                    "emphasis_words": ["not selfish", "remember", "outside", "human"],
                    "mood": "permission"
                },
                # NEW MESSAGES
                {
                    "text": "Your dreams didn't die when you became a caregiver. They're just waiting for you to have space to breathe. 🌟",
                    "duration": 17,
                    "series": "Dreams Don't Die", 
                    "emphasis_words": ["dreams", "die", "waiting", "breathe"],
                    "mood": "hope"
                },
                {
                    "text": "The part of you that existed before caregiving? She's still in there, even when you can't feel her. 💫",
                    "duration": 16,
                    "series": "She's Still There",
                    "emphasis_words": ["before", "still there", "can't feel"],
                    "mood": "continuity"
                },
                {
                    "text": "You don't have to choose between being a good caregiver and being yourself. You can be both. 🌈",
                    "duration": 15,
                    "series": "Both Not Either",
                    "emphasis_words": ["don't choose", "good caregiver", "yourself", "both"],
                    "mood": "integration"
                }
            ],
            # NEW CATEGORIES
            "daily_affirmations": [
                {
                    "text": "Today you don't have to be perfect. You just have to be present. That's enough. 🤍",
                    "duration": 14,
                    "series": "Daily Reminder",
                    "emphasis_words": ["don't have to", "perfect", "present", "enough"],
                    "mood": "daily_calm"
                },
                {
                    "text": "This morning, before you give to everyone else, take one moment to breathe for you. Just you. ✨",
                    "duration": 15,
                    "series": "Morning Moment",
                    "emphasis_words": ["before", "give", "breathe", "just you"],
                    "mood": "morning_peace"
                },
                {
                    "text": "Right now, in this moment, you are doing better than you think you are. Trust that. 💙",
                    "duration": 14,
                    "series": "Right Now",
                    "emphasis_words": ["right now", "better", "think", "trust"],
                    "mood": "present_moment"
                }
            ],
            "seasonal_messages": [
                {
                    "text": "As the seasons change, remember: you're allowed to change too. Growth isn't betrayal. 🍂",
                    "duration": 15,
                    "series": "Seasons of Self",
                    "emphasis_words": ["seasons change", "allowed", "growth", "betrayal"],
                    "mood": "autumn_wisdom",
                    "season": "fall"
                },
                {
                    "text": "This holiday season, your presence is the gift. Not perfection, not doing everything - just being there. 🎁",
                    "duration": 16,
                    "series": "Holiday Reality",
                    "emphasis_words": ["presence", "gift", "perfection", "being there"],
                    "mood": "holiday_peace",
                    "season": "winter"
                },
                {
                    "text": "Spring reminds us that after the hardest winters, new life is possible. You're not done blooming. 🌸",
                    "duration": 16,
                    "series": "Spring Hope",
                    "emphasis_words": ["spring", "hardest winters", "new life", "blooming"],
                    "mood": "spring_hope",
                    "season": "spring"
                },
                {
                    "text": "Summer doesn't ask permission to shine. Neither should you. Your light matters. ☀️",
                    "duration": 14,
                    "series": "Summer Strength",
                    "emphasis_words": ["summer", "permission", "shine", "light matters"],
                    "mood": "summer_confidence",
                    "season": "summer"
                }
            ],
            "weekend_reminders": [
                {
                    "text": "Weekends as a caregiver don't look like other people's weekends. And that's okay. Rest looks different for you. 🌙",
                    "duration": 17,
                    "series": "Weekend Reality",
                    "emphasis_words": ["weekends", "other people", "rest", "different"],
                    "mood": "weekend_acceptance"
                },
                {
                    "text": "Sunday night anxiety is real when tomorrow means starting the cycle all over again. You're not alone in that feeling. 💙",
                    "duration": 17,
                    "series": "Sunday Anxiety",
                    "emphasis_words": ["Sunday anxiety", "real", "cycle", "not alone"],
                    "mood": "sunday_understanding"
                }
            ]
        }
        
        # Save the enhanced database
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(enhanced_messages, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Created enhanced message database with {self._count_total_messages(enhanced_messages)} messages")
        return enhanced_messages
    
    def _count_total_messages(self, messages: Dict) -> int:
        """Count total messages across all categories"""
        return sum(len(category) for category in messages.values())
    
    def get_random_message(self, category: str = None, series: str = None, 
                          season: str = None) -> Dict:
        """Get a random message with enhanced filtering options"""
        available_messages = []
        
        if category and category in self.messages:
            available_messages = self.messages[category]
        else:
            # Get all messages from all categories
            for cat_messages in self.messages.values():
                available_messages.extend(cat_messages)
        
        # Filter by series if specified
        if series:
            available_messages = [m for m in available_messages 
                                if m.get("series") == series]
        
        # Filter by season if specified
        if season:
            available_messages = [m for m in available_messages 
                                if m.get("season") == season]
        
        if not available_messages:
            raise ValueError(f"No messages found with filters: category={category}, series={series}, season={season}")
        
        return random.choice(available_messages)
    
    def create_particle_system(self, particle_type: str, frame_num: int, total_frames: int) -> List[Dict]:
        """Create particles based on configuration"""
        if particle_type not in self.particle_configs:
            return []
        
        config = self.particle_configs[particle_type]
        particles = []
        
        for i in range(config["count"]):
            # Initialize particle with random position
            particle = {
                "x": random.uniform(0, self.width),
                "y": random.uniform(self.height * 0.2, self.height * 0.8),
                "size": random.uniform(*config["size_range"]),
                "opacity": random.uniform(*config["opacity_range"]),
                "phase": random.uniform(0, 2 * math.pi),  # For oscillating movement
                "color": config["color"],
                "shape": config.get("shape", "circle")
            }
            
            # Apply movement based on frame
            time = frame_num / self.fps
            movement_type = config["movement"]
            speed = config["speed"]
            
            if movement_type == "float_up":
                particle["y"] -= time * speed * 20
                particle["x"] += math.sin(time * speed + particle["phase"]) * 5
            elif movement_type == "gentle_sway":
                particle["x"] += math.sin(time * speed + particle["phase"]) * 15
                particle["y"] += math.cos(time * speed * 0.5 + particle["phase"]) * 8
            elif movement_type == "slow_drift":
                particle["x"] += time * speed * 10
                particle["y"] += math.sin(time * speed + particle["phase"]) * 3
            elif movement_type == "subtle_twinkle":
                # Sparkle effect - vary opacity
                particle["opacity"] *= (0.7 + 0.3 * math.sin(time * speed * 3 + particle["phase"]))
            
            # Keep particles in bounds (wrap around)
            particle["x"] = particle["x"] % self.width
            particle["y"] = particle["y"] % self.height
            
            particles.append(particle)
        
        return particles
    
    def draw_particle(self, draw: ImageDraw.Draw, particle: Dict) -> None:
        """Draw a single particle"""
        x, y = particle["x"], particle["y"]
        size = particle["size"]
        opacity = min(255, max(0, int(particle["opacity"] * 255)))
        color = particle["color"] + (opacity,)
        
        if particle["shape"] == "heart":
            # Simple heart shape using circles
            r = size // 2
            # Two circles for top of heart
            draw.ellipse([x-r//2, y-r, x+r//2, y], fill=color)
            draw.ellipse([x+r//2, y-r, x+3*r//2, y], fill=color)
            # Triangle for bottom
            draw.polygon([(x, y), (x-r, y+r), (x+r, y+r)], fill=color)
        else:
            # Default circle
            r = size // 2
            draw.ellipse([x-r, y-r, x+r, y+r], fill=color)
    
    def create_enhanced_background(self, style_name: str, frame_num: int = 0, 
                                 total_frames: int = 1) -> Image.Image:
        """Create enhanced backgrounds with multiple styles"""
        if style_name not in self.background_styles:
            style_name = "gradient_calm"
        
        style = self.background_styles[style_name]
        
        if style["type"] == "gradient":
            bg = self._create_gradient_background(style, frame_num, total_frames)
        elif style["type"] == "nature":
            bg = self._create_nature_background(style, frame_num, total_frames)
        elif style["type"] == "abstract":
            bg = self._create_abstract_background(style, frame_num, total_frames)
        elif style["type"] == "branded":
            bg = self._create_branded_background(style, frame_num, total_frames)
        else:
            bg = self._create_gradient_background(style, frame_num, total_frames)
        
        # Add particles if specified
        if "particles" in style:
            bg = self._add_particles_to_background(bg, style["particles"], frame_num, total_frames)
        
        return bg
    
    def _create_gradient_background(self, style: Dict, frame_num: int, total_frames: int) -> Image.Image:
        """Create enhanced gradient backgrounds"""
        colors = random.choice(style["colors"])
        
        # Create gradient array with subtle animation
        color1, color2 = colors
        gradient = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # Add subtle shift over time for animation
        time_shift = (frame_num / total_frames) * 0.1 if total_frames > 1 else 0
        
        for y in range(self.height):
            ratio = (y / self.height) + time_shift
            ratio = max(0, min(1, ratio))
            
            for c in range(3):
                gradient[y, :, c] = int(color1[c] * (1 - ratio) + color2[c] * ratio)
        
        bg = Image.fromarray(gradient)
        
        # Add texture layers
        bg = self._add_texture_layers(bg)
        
        return bg
    
    def _create_nature_background(self, style: Dict, frame_num: int, total_frames: int) -> Image.Image:
        """Create nature-inspired backgrounds"""
        base_colors = style["base_colors"]
        
        # Create base gradient
        bg = Image.new('RGB', (self.width, self.height), base_colors[0])
        
        # Add organic patterns
        if "overlay" in style and style["overlay"] == "soft_bokeh":
            bg = self._add_bokeh_effect(bg)
        
        return bg
    
    def _create_abstract_background(self, style: Dict, frame_num: int, total_frames: int) -> Image.Image:
        """Create abstract backgrounds with organic flow"""
        colors = style["colors"]
        
        # Create multi-layered abstract background
        bg = Image.new('RGB', (self.width, self.height), colors[0])
        
        if "flow" in style and style["flow"] == "organic_curves":
            bg = self._add_organic_curves(bg, colors)
        
        return bg
    
    def _create_branded_background(self, style: Dict, frame_num: int, total_frames: int) -> Image.Image:
        """Create branded backgrounds using brand colors"""
        # Get brand colors
        brand_primary = self.brand.get_color_rgb('primary')
        brand_secondary = self.brand.get_color_rgb('secondary')
        
        # Create gradient with brand colors
        gradient = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        for y in range(self.height):
            ratio = y / self.height
            for c in range(3):
                gradient[y, :, c] = int(brand_primary[c] * (1 - ratio) + brand_secondary[c] * ratio)
        
        bg = Image.fromarray(gradient)
        bg = self._add_texture_layers(bg)
        
        return bg
    
    def _add_texture_layers(self, bg: Image.Image) -> Image.Image:
        """Add subtle texture layers for warmth"""
        # Add noise texture
        noise = Image.new('RGB', (self.width, self.height), (255, 255, 255))
        noise_pixels = []
        for _ in range(self.width * self.height):
            val = random.randint(250, 255)
            noise_pixels.append((val, val, val))
        noise.putdata(noise_pixels)
        
        # Blend with very low opacity
        bg = Image.blend(bg, noise, 0.03)
        
        # Apply subtle blur
        bg = bg.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        return bg
    
    def _add_bokeh_effect(self, bg: Image.Image) -> Image.Image:
        """Add soft bokeh circles"""
        overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Add several soft circles
        for _ in range(8):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(50, 200)
            opacity = random.randint(10, 30)
            
            color = (255, 255, 255, opacity)
            draw.ellipse([x-size//2, y-size//2, x+size//2, y+size//2], fill=color)
        
        # Blur the overlay
        overlay = overlay.filter(ImageFilter.GaussianBlur(radius=20))
        
        # Composite with background
        bg_rgba = bg.convert('RGBA')
        bg_rgba = Image.alpha_composite(bg_rgba, overlay)
        return bg_rgba.convert('RGB')
    
    def _add_organic_curves(self, bg: Image.Image, colors: List[Tuple]) -> Image.Image:
        """Add organic flowing curves"""
        overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Draw flowing curves with gradient colors
        for i, color in enumerate(colors[1:]):
            opacity = 40 - i * 10
            curve_color = color + (opacity,)
            
            # Create wavy lines
            points = []
            for x in range(0, self.width, 20):
                y = self.height // 2 + int(100 * math.sin(x / 150 + i)) + i * 100
                points.append((x, y))
            
            if len(points) > 1:
                draw.line(points, fill=curve_color, width=60)
        
        # Blur for softness
        overlay = overlay.filter(ImageFilter.GaussianBlur(radius=30))
        
        # Composite
        bg_rgba = bg.convert('RGBA')
        bg_rgba = Image.alpha_composite(bg_rgba, overlay)
        return bg_rgba.convert('RGB')
    
    def _add_particles_to_background(self, bg: Image.Image, particle_type: str, 
                                   frame_num: int, total_frames: int) -> Image.Image:
        """Add particle effects to background"""
        # Convert to RGBA for particles
        bg_rgba = bg.convert('RGBA')
        
        # Create particle layer
        particle_layer = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(particle_layer)
        
        # Get particles for this frame
        particles = self.create_particle_system(particle_type, frame_num, total_frames)
        
        # Draw particles
        for particle in particles:
            self.draw_particle(draw, particle)
        
        # Composite particles with background
        bg_rgba = Image.alpha_composite(bg_rgba, particle_layer)
        
        return bg_rgba.convert('RGB')
    
    def get_enhanced_font(self, text: str, max_width: int, max_height: int, 
                         style: str = "default") -> Tuple[ImageFont.FreeTypeFont, int]:
        """Get enhanced fonts with multiple fallbacks and styles"""
        
        # Enhanced font paths with style variants
        font_paths = {
            "elegant": [
                "/System/Library/Fonts/Avenir.ttc",  # macOS - elegant
                "/System/Library/Fonts/Helvetica.ttc",  # macOS fallback
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",  # Linux
                "/Windows/Fonts/segoeui.ttf",  # Windows elegant
                "/Windows/Fonts/arial.ttf",  # Windows fallback
            ],
            "warm": [
                "/System/Library/Fonts/Georgia.ttf",  # Warmer serif
                "/System/Library/Fonts/Times.ttc",    # Times fallback
                "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",  # Linux
                "/Windows/Fonts/georgia.ttf",  # Windows
            ],
            "modern": [
                "/System/Library/Fonts/SFNSDisplay.ttf",  # SF Display
                "/System/Library/Fonts/Helvetica.ttc",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/Windows/Fonts/segoeui.ttf",
            ],
            "default": [
                "/System/Library/Fonts/Helvetica.ttc",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/Windows/Fonts/arial.ttf",
            ]
        }
        
        font_paths_to_try = font_paths.get(style, font_paths["default"])
        
        # Find available font
        font_path = None
        for path in font_paths_to_try:
            if os.path.exists(path):
                font_path = path
                break
        
        # Calculate optimal size
        for font_size in range(72, 30, -3):  # More granular sizing
            try:
                if font_path:
                    font = ImageFont.truetype(font_path, font_size)
                else:
                    font = ImageFont.load_default()
                    break
                
                # Test text wrapping
                lines = self._wrap_text_smart(text, font, max_width)
                total_height = self._calculate_text_height(lines, font)
                
                if total_height <= max_height:
                    return font, font_size
                    
            except (OSError, IOError):
                continue
        
        # Fallback
        return ImageFont.load_default(), 36
    
    def _wrap_text_smart(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        """Smart text wrapping that keeps phrases together"""
        words = text.split()
        lines = []
        current_line = ""
        
        # Create dummy image for text measurement
        dummy_img = Image.new('RGB', (max_width * 2, 100))
        dummy_draw = ImageDraw.Draw(dummy_img)
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            bbox = dummy_draw.textbbox((0, 0), test_line, font=font)
            line_width = bbox[2] - bbox[0]
            
            if line_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _calculate_text_height(self, lines: List[str], font: ImageFont.FreeTypeFont) -> int:
        """Calculate total height needed for text lines"""
        dummy_img = Image.new('RGB', (100, 100))
        dummy_draw = ImageDraw.Draw(dummy_img)
        
        total_height = 0
        line_spacing = 10
        
        for line in lines:
            bbox = dummy_draw.textbbox((0, 0), line, font=font)
            line_height = bbox[3] - bbox[1]
            total_height += line_height + line_spacing
        
        return total_height - line_spacing  # Remove last spacing
    
    def add_enhanced_text(self, image: Image.Image, text: str, message_data: Dict,
                         animation_frame: int = 0, total_frames: int = 1) -> Image.Image:
        """Add text with enhanced styling, animation, and emphasis"""
        
        # Get message styling info
        emphasis_words = message_data.get("emphasis_words", [])
        mood = message_data.get("mood", "calm")
        
        # Font style based on mood
        font_style = {
            "warm": "warm",
            "gentle": "elegant", 
            "empowering": "modern",
            "professional": "modern"
        }.get(mood, "elegant")
        
        # Calculate text area
        padding = 100
        text_width = self.width - (padding * 2)
        text_height = self.height // 2
        
        # Get font
        font, font_size = self.get_enhanced_font(text, text_width, text_height, font_style)
        
        # Create text layer
        text_layer = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(text_layer)
        
        # Split into lines
        lines = self._wrap_text_smart(text, font, text_width)
        
        # Calculate positioning
        line_spacing = font_size // 3
        total_height = self._calculate_text_height(lines, font)
        start_y = (self.height - total_height) // 2
        
        # Animation calculations
        time_progress = animation_frame / max(1, total_frames - 1) if total_frames > 1 else 0
        
        # Draw each line with enhanced styling
        current_y = start_y
        for line_idx, line in enumerate(lines):
            # Word-by-word rendering for emphasis
            words = line.split()
            current_x = padding
            
            # Center align calculation
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            current_x = (self.width - line_width) // 2
            
            for word_idx, word in enumerate(words):
                # Determine if word should be emphasized
                is_emphasized = any(emphasis in word.lower() for emphasis in emphasis_words)
                
                # Base color
                if is_emphasized:
                    color = self.brand.get_color_rgb('primary') if hasattr(self.brand, 'get_color_rgb') else (70, 130, 180)
                else:
                    color = (50, 50, 50)
                
                # Animation effects
                word_alpha = 255
                y_offset = 0
                scale_factor = 1.0
                
                # Cascade fade animation
                word_delay = (line_idx * len(words) + word_idx) * 0.05
                if time_progress > word_delay:
                    fade_progress = min(1.0, (time_progress - word_delay) / 0.3)
                    word_alpha = int(255 * fade_progress)
                else:
                    word_alpha = 0
                
                # Gentle pulse for emphasized words
                if is_emphasized:
                    pulse_time = time_progress * 2 * math.pi
                    scale_factor = 1.0 + 0.05 * math.sin(pulse_time)
                    pulse_alpha = int(30 * (1 + math.sin(pulse_time)) / 2)
                    
                    # Add glow effect
                    glow_color = color + (pulse_alpha,)
                    for offset in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
                        draw.text((current_x + offset[0], current_y + y_offset + offset[1]), 
                                word + " ", font=font, fill=glow_color)
                
                # Apply scale (simplified - just adjust font size)
                if scale_factor != 1.0:
                    scaled_size = int(font_size * scale_factor)
                    try:
                        scaled_font = ImageFont.truetype(font.path, scaled_size)
                    except:
                        scaled_font = font
                else:
                    scaled_font = font
                
                # Draw main text with alpha
                final_color = color + (word_alpha,)
                draw.text((current_x, current_y + y_offset), word + " ", 
                         font=scaled_font, fill=final_color)
                
                # Update position
                bbox = draw.textbbox((current_x, current_y), word + " ", font=font)
                current_x = bbox[2]
            
            current_y += font_size + line_spacing
        
        # Apply shadow for depth
        shadow_layer = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_layer)
        
        for line_idx, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            x = (self.width - line_width) // 2
            y = start_y + line_idx * (font_size + line_spacing)
            
            shadow_draw.text((x + 3, y + 3), line, font=font, fill=(0, 0, 0, 50))
        
        # Blur shadow
        shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=2))
        
        # Composite layers
        image_rgba = image.convert('RGBA')
        image_rgba = Image.alpha_composite(image_rgba, shadow_layer)
        image_rgba = Image.alpha_composite(image_rgba, text_layer)
        
        return image_rgba.convert('RGB')
    
    async def generate_enhanced_audio(self, message_data: Dict, output_path: str) -> float:
        """Generate enhanced TTS audio with optimal voice selection"""
        text = message_data["text"]
        content_category = message_data.get("series", "validation")
        
        # Get optimal voice for content type
        if "validation" in content_category.lower() or "permission" in content_category.lower():
            content_type = "validation"
        elif "guilt" in content_category.lower() or "forgiv" in content_category.lower():
            content_type = "confessions"
        else:
            content_type = "general"
        
        # Get recommended voices
        recommended_voices = self.voice_manager.get_suitable_voices_for_content(content_type)
        selected_voice = recommended_voices[0] if recommended_voices else "en-US-AriaNeural"
        
        # Clean text for TTS
        clean_text = self._clean_text_for_tts(text)
        
        # Enhanced TTS settings
        speech_rate = "+0%"  # Can be adjusted based on mood
        speech_pitch = "+0Hz"
        
        try:
            # Create TTS with enhanced settings
            communicate = edge_tts.Communicate(
                clean_text, 
                selected_voice, 
                rate=speech_rate,
                pitch=speech_pitch
            )
            await communicate.save(output_path)
            
            # Get accurate duration
            duration = await self._get_audio_duration_accurate(output_path)
            return duration
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate enhanced TTS audio: {e}")
    
    def _clean_text_for_tts(self, text: str) -> str:
        """Enhanced text cleaning for better TTS"""
        # Remove emojis and special characters
        clean_text = ''.join(char for char in text 
                           if ord(char) < 0x1F600 or ord(char) > 0x1F64F)
        
        # Remove specific emoji patterns
        emoji_patterns = ['💙', '🤗', '🌟', '💚', '✨', '🌈', '💪', '🤍', '🔋', 
                         '💤', '👁️', '🌊', '😴', '💫', '🍂', '🎁', '🌸', '☀️', '🌙']
        for emoji in emoji_patterns:
            clean_text = clean_text.replace(emoji, '')
        
        # Add natural pauses
        clean_text = clean_text.replace('...', '. ').replace('..', '. ')
        clean_text = clean_text.replace('. ', '. <break time="500ms"/> ')
        
        # Emphasize important words
        emphasis_patterns = {
            'you\'re': 'you are',
            'don\'t': 'do not',
            'can\'t': 'cannot',
            'it\'s': 'it is',
            'that\'s': 'that is'
        }
        
        for pattern, replacement in emphasis_patterns.items():
            clean_text = clean_text.replace(pattern, replacement)
        
        return clean_text.strip()
    
    async def _get_audio_duration_accurate(self, audio_path: str) -> float:
        """Get accurate audio duration using multiple methods"""
        try:
            # Try ffprobe first
            result = subprocess.run([
                'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                '-of', 'csv=p=0', audio_path
            ], capture_output=True, text=True, check=True)
            return float(result.stdout.strip())
        except:
            try:
                # Fallback to file size estimation
                file_size = os.path.getsize(audio_path)
                # Rough estimation: 1MB ≈ 60 seconds for speech
                estimated_duration = max(8.0, file_size / (1024 * 1024) * 60)
                return min(30.0, estimated_duration)  # Cap at 30 seconds
            except:
                return 12.0  # Default fallback
    
    def create_enhanced_frames(self, message_data: Dict, duration: float, 
                             temp_dir: str, style_name: str = None,
                             ab_variation: Dict = None) -> List[str]:
        """Create enhanced video frames with animations and effects"""
        
        total_frames = int(duration * self.fps)
        frame_paths = []
        
        # Determine style
        if not style_name:
            mood = message_data.get("mood", "calm")
            style_map = {
                "warm": "gradient_calm",
                "professional": "brand_professional", 
                "gentle": "nature_soft",
                "empowering": "abstract_warm"
            }
            style_name = style_map.get(mood, "gradient_calm")
        
        # Apply A/B variations if provided
        if ab_variation:
            if "background_style" in ab_variation:
                style_name = ab_variation["background_style"]
        
        # Animation phases
        fade_in_frames = min(self.fps, total_frames // 4)  # 1 second or 1/4 of video
        text_start_frame = fade_in_frames // 2  # Text starts halfway through fade-in
        text_end_frame = total_frames - fade_in_frames
        fade_out_frames = fade_in_frames
        
        print(f"  Creating {total_frames} enhanced frames with '{style_name}' style...")
        
        for frame_num in range(total_frames):
            if frame_num % self.fps == 0:  # Progress every second
                progress = (frame_num + 1) / total_frames * 100
                print(f"    Frame {frame_num + 1}/{total_frames} ({progress:.1f}%)")
            
            # Create enhanced background
            bg = self.create_enhanced_background(style_name, frame_num, total_frames)
            
            # Add text with animation
            if frame_num >= text_start_frame and frame_num < text_end_frame:
                text_frame = frame_num - text_start_frame
                text_total_frames = text_end_frame - text_start_frame
                
                bg = self.add_enhanced_text(bg, message_data["text"], message_data,
                                          text_frame, text_total_frames)
            
            # Apply global fade effects
            if frame_num < fade_in_frames:
                # Fade in
                alpha = frame_num / fade_in_frames
                bg = self._apply_fade_effect(bg, alpha)
            elif frame_num >= text_end_frame:
                # Fade out
                fade_progress = (frame_num - text_end_frame) / fade_out_frames
                alpha = 1.0 - fade_progress
                bg = self._apply_fade_effect(bg, alpha)
            
            # Add watermark if branded
            if style_name == "brand_professional":
                bg = self._add_watermark(bg)
            
            # Save frame
            frame_path = os.path.join(temp_dir, f"frame_{frame_num:06d}.png")
            bg.save(frame_path, "PNG")
            frame_paths.append(frame_path)
        
        return frame_paths
    
    def _apply_fade_effect(self, image: Image.Image, alpha: float) -> Image.Image:
        """Apply fade effect to entire image"""
        if alpha >= 1.0:
            return image
        
        # Create black image for fading
        black = Image.new('RGBA', image.size, (0, 0, 0, int(255 * (1 - alpha))))
        
        # Convert to RGBA and blend
        image_rgba = image.convert('RGBA')
        faded = Image.alpha_composite(image_rgba, black)
        
        return faded.convert('RGB')
    
    def _add_watermark(self, image: Image.Image) -> Image.Image:
        """Add brand watermark to image"""
        try:
            watermark_path = self.brand.get_watermark_path()
            if watermark_path.exists():
                watermark = Image.open(watermark_path).convert('RGBA')
                
                # Resize watermark to appropriate size
                wm_width = self.width // 6
                watermark = watermark.resize((wm_width, int(watermark.height * wm_width / watermark.width)))
                
                # Position in bottom right
                x = self.width - watermark.width - 50
                y = self.height - watermark.height - 50
                
                # Create composite
                image_rgba = image.convert('RGBA')
                image_rgba.paste(watermark, (x, y), watermark)
                
                return image_rgba.convert('RGB')
        except Exception as e:
            print(f"Warning: Could not add watermark: {e}")
        
        return image
    
    async def add_background_music(self, video_path: str, message_data: Dict, 
                                 output_path: str) -> bool:
        """Add background music using the music mixer"""
        try:
            # Determine mood for music selection
            mood = message_data.get("mood", "calm")
            content_mood_map = {
                "warm": "warm",
                "gentle": "calm",
                "empowering": "uplifting",
                "professional": "professional",
                "intimate": "intimate",
                "energetic": "energetic"
            }
            
            music_mood = content_mood_map.get(mood, "calm")
            
            # Try to use music mixer
            success = self.music_mixer.mix_video_with_music(
                video_path=video_path,
                music_path=None,  # Will auto-select based on mood
                output_path=output_path,
                mood=music_mood
            )
            
            if success:
                print(f"  ✅ Added background music (mood: {music_mood})")
                return True
            else:
                print(f"  ⚠️  Music mixing failed, using video without background music")
                # Copy original to output
                subprocess.run(['cp', video_path, output_path], check=True)
                return False
                
        except Exception as e:
            print(f"  ⚠️  Music mixing error: {e}")
            # Copy original to output
            subprocess.run(['cp', video_path, output_path], check=True)
            return False
    
    def combine_enhanced_video(self, frame_pattern: str, audio_path: str, 
                             output_path: str, duration: float) -> None:
        """Combine frames and audio with enhanced settings"""
        try:
            cmd = [
                'ffmpeg', '-y',
                '-framerate', str(self.fps),
                '-i', frame_pattern,
                '-i', audio_path,
                '-c:v', 'libx264',
                '-preset', 'slow',  # Higher quality preset
                '-crf', '18',       # Higher quality (lower CRF)
                '-pix_fmt', 'yuv420p',
                '-profile:v', 'high',
                '-level:v', '4.1',
                '-movflags', '+faststart',  # Optimize for streaming
                '-c:a', 'aac',
                '-b:a', '192k',     # Higher audio bitrate
                '-shortest',
                '-t', str(duration),
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Enhanced video creation failed: {e.stderr}")
    
    async def generate_validation_video(self, message_text: str = None, output_path: str = None,
                                      category: str = None, series: str = None,
                                      style: str = None, with_music: bool = True,
                                      ab_variation: Dict = None) -> str:
        """Generate enhanced validation video with all improvements"""
        
        # Get message data
        if message_text:
            # Create message data structure
            message_data = {
                "text": message_text,
                "duration": 15,
                "series": "Custom",
                "emphasis_words": ["you", "deserve", "enough"],
                "mood": "warm"
            }
        else:
            message_data = self.get_random_message(category, series)
        
        # Set output path
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            series_name = message_data.get("series", "validation").replace(" ", "_")
            output_path = f"validation_v2_{series_name}_{timestamp}.mp4"
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        print(f"🎬 Generating enhanced validation video...")
        print(f"📝 Message: {message_data['text'][:100]}{'...' if len(message_data['text']) > 100 else ''}")
        print(f"📚 Series: {message_data.get('series', 'Unknown')}")
        print(f"🎨 Style: {style or 'auto-detected'}")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Generate enhanced audio
                audio_path = os.path.join(temp_dir, "enhanced_audio.wav")
                print("🎤 Generating enhanced TTS audio...")
                audio_duration = await self.generate_enhanced_audio(message_data, audio_path)
                
                # Calculate video duration
                target_duration = message_data.get("duration", 15)
                video_duration = max(target_duration, audio_duration + 1.5)
                
                # Create enhanced frames
                print(f"🎨 Creating {int(video_duration * self.fps)} enhanced frames...")
                frame_paths = self.create_enhanced_frames(
                    message_data, video_duration, temp_dir, style, ab_variation
                )
                
                # Combine video
                print("🎞️ Assembling enhanced video...")
                frame_pattern = os.path.join(temp_dir, "frame_%06d.png")
                temp_video_path = os.path.join(temp_dir, "temp_video.mp4")
                
                self.combine_enhanced_video(frame_pattern, audio_path, temp_video_path, video_duration)
                
                # Add background music if requested
                if with_music:
                    print("🎵 Adding background music...")
                    final_path = output_path
                    music_success = await self.add_background_music(temp_video_path, message_data, final_path)
                    
                    if not music_success:
                        # Copy temp video to final output
                        subprocess.run(['cp', temp_video_path, output_path], check=True)
                else:
                    # Copy temp video to final output
                    subprocess.run(['cp', temp_video_path, output_path], check=True)
                
                print(f"✅ Enhanced validation video created: {output_path}")
                return output_path
                
            except Exception as e:
                raise RuntimeError(f"Failed to generate enhanced video: {e}")
    
    def generate_ab_variations(self, message_data: Dict, base_output_path: str, 
                             count: int = 3) -> List[str]:
        """Generate multiple A/B test variations of the same message"""
        variations = []
        base_name = base_output_path.replace('.mp4', '')
        
        for i in range(count):
            # Create variation parameters
            ab_variation = {
                "color_scheme": random.choice(self.ab_variations["color_schemes"]),
                "animation_speed": random.choice(self.ab_variations["animation_speeds"]),
                "particle_density": random.choice(self.ab_variations["particle_densities"]),
                "background_style": random.choice(list(self.background_styles.keys()))
            }
            
            variation_output = f"{base_name}_variant_{i+1}.mp4"
            
            print(f"\n🔄 Generating A/B variation {i+1}/{count}")
            print(f"   Variation: {ab_variation}")
            
            try:
                # Generate with variation
                asyncio.create_task(self.generate_validation_video(
                    message_text=message_data["text"],
                    output_path=variation_output,
                    style=ab_variation["background_style"],
                    ab_variation=ab_variation
                ))
                variations.append(variation_output)
            except Exception as e:
                print(f"   ⚠️ Variation {i+1} failed: {e}")
        
        return variations
    
    def list_enhanced_features(self) -> None:
        """List all enhanced features"""
        print("🚀 ENHANCED VALIDATION GENERATOR V2 FEATURES")
        print("=" * 60)
        
        print("\n🎨 VISUAL ENHANCEMENTS:")
        print("  • Particle effects: gentle sparkles, floating hearts, ambient dots")
        print("  • Multiple background styles: gradients, nature, abstract, branded")
        print("  • Animated text with gentle pulse and cascade effects")
        print("  • Word emphasis highlighting")
        print("  • Professional typography with enhanced fonts")
        print("  • Subtle bokeh and texture effects")
        
        print("\n🎵 AUDIO ENHANCEMENTS:")
        print("  • Intelligent voice selection based on content type")
        print("  • Background music integration with mood matching")
        print("  • Audio ducking for speech clarity")
        print("  • Enhanced text cleaning for natural TTS")
        
        print("\n📝 CONTENT IMPROVEMENTS:")
        print(f"  • {self._count_total_messages(self.messages)} validation messages (vs ~24 original)")
        print("  • Message series: Permission to Be Human, Feelings Are Valid, etc.")
        print("  • Seasonal and timely content")
        print("  • Enhanced emphasis word detection")
        
        print("\n🔬 A/B TESTING:")
        print("  • Multiple color schemes")
        print("  • Variable animation speeds")
        print("  • Different particle densities")
        print("  • Background style variations")
        
        print("\n🏢 BRAND INTEGRATION:")
        print("  • Automatic watermark application")
        print("  • Brand color palette integration")
        print("  • Consistent visual identity")
        print("  • Professional quality output")
        
        print(f"\n📊 AVAILABLE MESSAGE CATEGORIES: {len(self.messages)}")
        for category, messages in self.messages.items():
            series_count = len(set(msg.get('series', 'Unknown') for msg in messages))
            print(f"  • {category}: {len(messages)} messages, {series_count} series")


async def main():
    """Enhanced main function with new capabilities"""
    parser = argparse.ArgumentParser(
        description="Enhanced Validation Video Generator V2 - Professional quality videos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate with auto-selected message
  python validation_generator_v2.py
  
  # Specific category and series
  python validation_generator_v2.py --category guilt_relief --series "Human Moments"
  
  # Custom message with style
  python validation_generator_v2.py --message "You are enough" --style brand_professional
  
  # Generate A/B test variations
  python validation_generator_v2.py --ab-test --count 3
  
  # Seasonal content
  python validation_generator_v2.py --seasonal --season spring
  
  # List all features
  python validation_generator_v2.py --list-features
        """
    )
    
    parser.add_argument("--message", type=str, help="Custom message text")
    parser.add_argument("--output", type=str, help="Output video path")
    parser.add_argument("--category", type=str, 
                       help="Message category (permission_statements, guilt_relief, etc.)")
    parser.add_argument("--series", type=str, help="Message series name")
    parser.add_argument("--style", type=str, choices=list(EnhancedValidationGenerator().background_styles.keys()),
                       help="Visual style")
    parser.add_argument("--no-music", action="store_true", help="Skip background music")
    parser.add_argument("--config", type=str, help="Path to enhanced messages config")
    parser.add_argument("--ab-test", action="store_true", help="Generate A/B test variations")
    parser.add_argument("--count", type=int, default=3, help="Number of variations for A/B test")
    parser.add_argument("--seasonal", action="store_true", help="Use seasonal messages")
    parser.add_argument("--season", type=str, choices=["spring", "summer", "fall", "winter"], 
                       help="Specific season")
    parser.add_argument("--list-features", action="store_true", help="List all enhanced features")
    parser.add_argument("--create-examples", action="store_true", help="Create 3 example videos")
    
    args = parser.parse_args()
    
    try:
        # Check dependencies
        required_commands = ['ffmpeg', 'ffprobe']
        for cmd in required_commands:
            try:
                subprocess.run([cmd, '-version'], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                print(f"❌ Required command '{cmd}' not found. Please install FFmpeg.")
                sys.exit(1)
        
        # Initialize enhanced generator
        generator = EnhancedValidationGenerator(args.config)
        
        if args.list_features:
            generator.list_enhanced_features()
            return
        
        if args.create_examples:
            print("🎬 Creating 3 example videos showcasing V2 improvements...")
            
            # Example 1: Brand professional with guilt relief
            await generator.generate_validation_video(
                category="guilt_relief",
                output_path="validation_v2_example_1.mp4",
                style="brand_professional"
            )
            
            # Example 2: Nature soft with permission statements
            await generator.generate_validation_video(
                category="permission_statements", 
                output_path="validation_v2_example_2.mp4",
                style="nature_soft"
            )
            
            # Example 3: Abstract warm with seasonal
            seasonal_msg = generator.get_random_message("seasonal_messages")
            await generator.generate_validation_video(
                message_text=seasonal_msg["text"],
                output_path="validation_v2_example_3.mp4",
                style="abstract_warm"
            )
            
            print("\n🎉 Example videos created:")
            print("  • validation_v2_example_1.mp4 (Brand Professional)")
            print("  • validation_v2_example_2.mp4 (Nature Soft)")
            print("  • validation_v2_example_3.mp4 (Abstract Warm)")
            return
        
        # Handle seasonal filtering
        season = None
        if args.seasonal:
            season = args.season or "spring"  # Default to spring if seasonal but no specific season
        
        if args.ab_test:
            # Generate A/B test variations
            message_data = generator.get_random_message(args.category, args.series, season)
            base_output = args.output or "validation_v2_ab_test.mp4"
            
            variations = generator.generate_ab_variations(message_data, base_output, args.count)
            print(f"\n🎉 Generated {len(variations)} A/B test variations")
            for var in variations:
                print(f"  • {var}")
        else:
            # Generate single video
            output_path = await generator.generate_validation_video(
                message_text=args.message,
                output_path=args.output,
                category=args.category,
                series=args.series,
                style=args.style,
                with_music=not args.no_music
            )
            
            print(f"\n🎉 Enhanced validation video created: {output_path}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())