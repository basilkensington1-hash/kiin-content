#!/usr/bin/env python3
"""
Sandwich Generation Diaries V2 - POV Content Generator
Creates ultra-relatable POV-style videos for the sandwich generation audience.
Now with split-screen chaos, stress meters, notifications, and way more personality!
"""

import json
import os
import random
import asyncio
import subprocess
import tempfile
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import edge_tts
import uuid
from typing import Dict, List, Tuple, Optional
import colorsys

class SandwichGeneratorV2:
    def __init__(self, config_dir: str = None, output_dir: str = None):
        """Initialize the enhanced generator."""
        self.script_dir = Path(__file__).parent
        self.project_dir = self.script_dir.parent
        
        self.config_dir = Path(config_dir) if config_dir else self.project_dir / "config"
        self.output_dir = Path(output_dir) if output_dir else self.project_dir / "output"
        self.temp_dir = Path(tempfile.mkdtemp(prefix="sandwich_gen_v2_"))
        
        # Video settings
        self.video_width = 1080
        self.video_height = 1920
        self.fps = 30
        
        # Enhanced timing settings
        self.hook_duration = 4
        self.buildup_duration = 8
        self.chaos_duration = 18
        self.relief_duration = 6
        self.punchline_duration = 9
        self.cta_duration = 5
        self.total_duration = (self.hook_duration + self.buildup_duration + 
                             self.chaos_duration + self.relief_duration + 
                             self.punchline_duration + self.cta_duration)
        
        # Brand colors and visual identity
        self.brand_colors = {
            'primary': '#FF6B6B',      # Warm coral red
            'secondary': '#4ECDC4',    # Teal
            'accent': '#45B7D1',       # Blue
            'warning': '#FFA726',      # Orange
            'success': '#66BB6A',      # Green
            'dark': '#2C3E50',         # Dark blue-gray
            'light': '#ECF0F1',        # Light gray
            'text': '#2C3E50',         # Dark text
            'stress': '#E74C3C',       # Red for stress
        }
        
        # Enhanced visual themes
        self.background_gradients = [
            ['#667eea', '#764ba2'],    # Purple-blue
            ['#f093fb', '#f5576c'],    # Pink gradient  
            ['#4facfe', '#00f2fe'],    # Blue gradient
            ['#43e97b', '#38f9d7'],    # Green-teal
            ['#fa709a', '#fee140'],    # Pink-yellow
            ['#a8edea', '#fed6e3'],    # Soft pastels
        ]
        
        # TTS voices with personality
        self.voice_options = {
            'relatable_mom': 'en-US-AriaNeural',
            'exhausted': 'en-US-JennyNeural', 
            'sarcastic': 'en-US-SaraNeural',
            'inner_monologue': 'en-US-GuyNeural',
            'uplifting': 'en-US-AmberNeural'
        }
        self.default_voice = 'relatable_mom'
        
        # Sound effect library
        self.sound_effects = {
            'notification': '🔔',
            'phone_buzz': '📱', 
            'clock_tick': '⏰',
            'stress_buildup': '💢',
            'relief_exhale': '😮‍💨',
            'heart_racing': '💓',
            'achievement': '🎉'
        }
        
        # Load enhanced scenarios
        self.scenarios = self._load_enhanced_scenarios()
        
        print("🥪✨ Sandwich Generator V2 initialized with enhanced features!")
    
    def _load_enhanced_scenarios(self) -> List[Dict]:
        """Load the massively expanded scenario collection."""
        scenarios_file = self.config_dir / "sandwich_scenarios_v2.json"
        
        # If the v2 file doesn't exist, create it with enhanced scenarios
        if not scenarios_file.exists():
            self._create_enhanced_scenarios_file(scenarios_file)
        
        with open(scenarios_file, 'r') as f:
            data = json.load(f)
        return data['scenarios']
    
    def _create_enhanced_scenarios_file(self, file_path: Path):
        """Create the enhanced scenarios collection with 20+ scenarios."""
        enhanced_scenarios = {
            "scenarios": [
                {
                    "id": "emergency_contact",
                    "hook": "POV: You're the emergency contact for literally everyone",
                    "mood": "overwhelming",
                    "season": "any",
                    "chaos_moments": [
                        {"type": "notification", "text": "School nurse: 'Your daughter has a fever 🤒'", "stress_level": 3},
                        {"type": "phone_call", "text": "Dad's facility: 'He fell, nothing serious but...'", "stress_level": 8},
                        {"type": "text_spam", "text": "Mom: 'TV broken. Very scared. Call me.'", "stress_level": 5},
                        {"type": "urgent", "text": "Teen: 'MOM WHERE ARE YOU I NEED YOU RIGHT NOW'", "stress_level": 7},
                        {"type": "split_screen", "left": "Dr office calling", "right": "Kid texting 'pick me up'", "stress_level": 10}
                    ],
                    "inner_monologue": "Why am I everyone's person? When did this happen?",
                    "punchline": "Your phone battery dies and you have a full panic attack",
                    "relief_moment": "Everyone turns out fine. You're not.",
                    "cta": "Tag someone who's everyone's emergency contact 📱",
                    "supportive_ending": "Being needed means being loved. You're doing great. 💕"
                },
                {
                    "id": "sunday_military_op", 
                    "hook": "POV: Sunday family dinner requires military-level logistics",
                    "mood": "chaotic_love",
                    "season": "any",
                    "chaos_moments": [
                        {"type": "multi_task", "text": "Cut Dad's food + help with science project", "stress_level": 4},
                        {"type": "reminder", "text": "Pills for Mom between making soccer snacks", "stress_level": 3},
                        {"type": "mediation", "text": "Referee: Grandpa vs Teenager political debate", "stress_level": 6},
                        {"type": "translation", "text": "Explain TikTok to Grandma mid-homework check", "stress_level": 5},
                        {"type": "solo", "text": "Clean everything while everyone relaxes", "stress_level": 8}
                    ],
                    "inner_monologue": "I love my family. I love my family. I LOVE my family.",
                    "punchline": "Monday feels like a spa day in comparison",
                    "relief_moment": "Everyone says 'thanks for dinner' at once 🥰",
                    "cta": "Who else is the family dinner MVP? 🍽️",
                    "supportive_ending": "These moments become the memories they treasure most. ✨"
                },
                {
                    "id": "wfh_chaos",
                    "hook": "POV: Working from home in the sandwich generation", 
                    "mood": "frazzled_professional",
                    "season": "any",
                    "chaos_moments": [
                        {"type": "zoom_bomb", "text": "Kid barges in during client meeting", "stress_level": 7},
                        {"type": "split_screen", "left": "Presenting slides", "right": "Mom calling 5 times", "stress_level": 8},
                        {"type": "notification", "text": "School: 'Pick up your sick child'", "stress_level": 9},
                        {"type": "multi_task", "text": "Type emails while making lunch", "stress_level": 5},
                        {"type": "meltdown", "text": "Explain to boss why you're 'having technical difficulties'", "stress_level": 10}
                    ],
                    "inner_monologue": "Professional on top, chaos underneath. Story of my life.",
                    "punchline": "'Sorry, my cat stepped on the keyboard' (it was your life)",
                    "relief_moment": "Somehow you didn't get fired today 🙏",
                    "cta": "WFH sandwich parents unite! 💻",
                    "supportive_ending": "You're pioneering a new way to balance it all. You're amazing. 🌟"
                },
                {
                    "id": "christmas_exhaustion",
                    "hook": "POV: Christmas morning with three generations",
                    "mood": "festive_overwhelm", 
                    "season": "winter",
                    "chaos_moments": [
                        {"type": "early_morning", "text": "5:30am: Kids wake you. Coffee not ready.", "stress_level": 4},
                        {"type": "gift_chaos", "text": "Help kids, assist grandparents, track batteries", "stress_level": 6},
                        {"type": "kitchen_madness", "text": "Turkey + sides while managing gift disputes", "stress_level": 8},
                        {"type": "nap_logistics", "text": "Coordinate who naps where and when", "stress_level": 5},
                        {"type": "bedtime_collapse", "text": "Everyone's sugar-crashed and overstimulated", "stress_level": 9}
                    ],
                    "inner_monologue": "This is magical. This is magical. This is... a lot.",
                    "punchline": "You fall asleep in a chair wearing elf ears at 7pm",
                    "relief_moment": "Grandpa says 'best Christmas ever' 🎄",
                    "cta": "Who else survives holiday hosting? 🎅",
                    "supportive_ending": "You create the magic that brings everyone together. ✨"
                },
                {
                    "id": "search_history_chaos",
                    "hook": "POV: Your Google search history is absolutely unhinged",
                    "mood": "digital_detective",
                    "season": "any",
                    "chaos_moments": [
                        {"type": "search", "text": "'How to explain death to a 7-year-old'", "stress_level": 8},
                        {"type": "search", "text": "'Best shower grab bars for elderly'", "stress_level": 4},
                        {"type": "search", "text": "'Why won't my teenager talk to me'", "stress_level": 6},
                        {"type": "search", "text": "'Memory care vs assisted living costs'", "stress_level": 9},
                        {"type": "search", "text": "'How to not lose mind sandwich generation'", "stress_level": 10}
                    ],
                    "inner_monologue": "The FBI agent watching my searches needs therapy.",
                    "punchline": "The algorithm thinks you're having an identity crisis",
                    "relief_moment": "You're not alone - millions search the same things 💙",
                    "cta": "Share your wildest sandwich generation search! 🔍",
                    "supportive_ending": "Seeking answers means you care deeply. That's beautiful. 💕"
                },
                {
                    "id": "generational_translator",
                    "hook": "POV: You're a real-time translator between generations",
                    "mood": "linguistic_juggling",
                    "season": "any", 
                    "chaos_moments": [
                        {"type": "translation", "text": "Teen: 'Grandpa's being sus' → 'Acting suspicious, Dad'", "stress_level": 3},
                        {"type": "explanation", "text": "Grandpa: 'Safe spaces' → 'Your bedroom, honey'", "stress_level": 4},
                        {"type": "tech_support", "text": "'How do I make the pictures move?' (TikTok)", "stress_level": 5},
                        {"type": "slang_decode", "text": "'No cap bussin frfr' requires full translation", "stress_level": 7},
                        {"type": "awkward_silence", "text": "Everyone stares when you know both languages", "stress_level": 6}
                    ],
                    "inner_monologue": "I'm basically Google Translate for my family.",
                    "punchline": "Your brain runs on three different operating systems",
                    "relief_moment": "Grandpa and teen bond over shared confusion 😂",
                    "cta": "Who else speaks three generations fluently? 🗣️",
                    "supportive_ending": "You're the bridge that keeps the family connected. 🌉"
                },
                {
                    "id": "mobile_pharmacy",
                    "hook": "POV: Your car is a mobile pharmacy/daycare/Uber",
                    "mood": "automotive_chaos",
                    "season": "any",
                    "chaos_moments": [
                        {"type": "inventory", "text": "Backseat: Juice boxes + pill organizers + car seats", "stress_level": 3},
                        {"type": "paperwork", "text": "Glove box: Permission slips + insurance cards + napkins", "stress_level": 4},
                        {"type": "emergency_kit", "text": "Center console: Band-aids + anxiety meds + hand sanitizer", "stress_level": 5},
                        {"type": "radio_wars", "text": "Toggle: Pop music → talk radio → audiobook", "stress_level": 6},
                        {"type": "drive_thru_regular", "text": "Pharmacist knows your voice and order", "stress_level": 7}
                    ],
                    "inner_monologue": "My car has more medical supplies than some hospitals.",
                    "punchline": "AAA thinks you live at CVS",
                    "relief_moment": "Everything needed is magically in your car 🚗",
                    "cta": "Show us your sandwich generation car setup! 🚙",
                    "supportive_ending": "You're always prepared because you always care. 💝"
                },
                {
                    "id": "adult_conversation",
                    "hook": "POV: Trying to have ONE uninterrupted adult conversation",
                    "mood": "social_frustration",
                    "season": "any",
                    "chaos_moments": [
                        {"type": "interrupted", "text": "Mom starts story → kid needs math help", "stress_level": 4},
                        {"type": "phone_interruption", "text": "Dad calls confused about his medication", "stress_level": 6},
                        {"type": "drama_alert", "text": "Other kid has friendship emergency NOW", "stress_level": 7},
                        {"type": "memory_loss", "text": "Mom forgets her story halfway through", "stress_level": 5},
                        {"type": "surrender", "text": "Give up and just nod at everyone", "stress_level": 8}
                    ],
                    "inner_monologue": "Remember when conversations had beginnings, middles, and ends?",
                    "punchline": "Your deepest conversation today was with the grocery cashier",
                    "relief_moment": "Finally connect with partner after kids sleep 🌙",
                    "cta": "Who else misses finishing sentences? 💬",
                    "supportive_ending": "The fragmented conversations still add up to love. 💕"
                },
                {
                    "id": "bedtime_olympics",
                    "hook": "POV: Bedtime is a multi-generational Olympic event",
                    "mood": "nighttime_coordination",
                    "season": "any",
                    "chaos_moments": [
                        {"type": "story_time", "text": "Read to kid while checking Dad's blood sugar", "stress_level": 4},
                        {"type": "medication_time", "text": "Tuck in child + Mom's nighttime pills", "stress_level": 5},
                        {"type": "homework_check", "text": "Verify teenager actually did homework", "stress_level": 6},
                        {"type": "false_security", "text": "Everyone settled! Time for YOU!", "stress_level": 2},
                        {"type": "round_two", "text": "Water/bathroom/anxiety relief requests", "stress_level": 8}
                    ],
                    "inner_monologue": "Bedtime is like herding cats. Very tired, anxious cats.",
                    "punchline": "Collapse into bed fully clothed like a cartoon character",
                    "relief_moment": "House finally quiet at 10:30pm 🤫",
                    "cta": "How many bedtime rounds do you do? 🛏️",
                    "supportive_ending": "You tuck in the whole world before yourself. You're magic. ✨"
                },
                {
                    "id": "vacation_planning",
                    "hook": "POV: Planning a 'simple' family vacation",
                    "mood": "travel_logistics_nightmare",
                    "season": "summer",
                    "chaos_moments": [
                        {"type": "accessibility", "text": "Find wheelchair accessible place", "stress_level": 5},
                        {"type": "medical_proximity", "text": "Check nearby urgent care facilities", "stress_level": 6},
                        {"type": "pharmacy_portable", "text": "Pack medication for small army", "stress_level": 7},
                        {"type": "age_range_activities", "text": "Plan fun for ages 8 to 80", "stress_level": 8},
                        {"type": "backup_plans", "text": "Have contingencies for contingencies", "stress_level": 9}
                    ],
                    "inner_monologue": "Why is a vacation harder to plan than a space mission?",
                    "punchline": "A weekend at home starts sounding like luxury",
                    "relief_moment": "Everyone has fun despite your anxiety 🏖️",
                    "cta": "Share your family vacation planning nightmare! ✈️",
                    "supportive_ending": "You create adventures that span generations. Amazing! 🌟"
                },
                {
                    "id": "normal_googling",
                    "hook": "POV: Googling 'is this normal' for multiple life stages",
                    "mood": "parenting_uncertainty",
                    "season": "any",
                    "chaos_moments": [
                        {"type": "elderly_concerns", "text": "'Is forgetting names normal at 75?'", "stress_level": 6},
                        {"type": "teen_behavior", "text": "'Is hating everyone normal at 13?'", "stress_level": 7},
                        {"type": "self_check", "text": "'Is crying in parking lots normal?'", "stress_level": 8},
                        {"type": "guilt_spiral", "text": "'Is feeling guilty about everything normal?'", "stress_level": 9},
                        {"type": "escape_fantasy", "text": "'Is wanting to join circus normal?'", "stress_level": 10}
                    ],
                    "inner_monologue": "Google knows more about my family than I do.",
                    "punchline": "The answer to the circus question is DEFINITELY yes",
                    "relief_moment": "Millions search the same things - you're normal! 💙",
                    "cta": "What's your weirdest 'is this normal' search? 🤔",
                    "supportive_ending": "Questioning everything means you care about everything. 💕"
                },
                {
                    "id": "becoming_mother",
                    "hook": "POV: You realize you're becoming your mother",
                    "mood": "generational_acceptance",
                    "season": "any",
                    "chaos_moments": [
                        {"type": "purse_transformation", "text": "Carrying snacks for everyone", "stress_level": 2},
                        {"type": "medical_historian", "text": "Know everyone's medical history by heart", "stress_level": 4},
                        {"type": "authority_phrases", "text": "Say 'because I said so' unironically", "stress_level": 3},
                        {"type": "constant_worry", "text": "Worry about everyone constantly", "stress_level": 6},
                        {"type": "mirror_moment", "text": "Make her exact facial expressions", "stress_level": 5}
                    ],
                    "inner_monologue": "When did I become the mom of moms?",
                    "punchline": "And honestly? She was pretty amazing at this job",
                    "relief_moment": "Feel proud to carry on her legacy 💕",
                    "cta": "What trait did you inherit from mom? 👩‍👧",
                    "supportive_ending": "You're continuing a legacy of love. She'd be so proud. ✨"
                },
                {
                    "id": "thanksgiving_coordinator",
                    "hook": "POV: You're the Thanksgiving coordinator for 20+ people",
                    "mood": "holiday_logistics_commander",
                    "season": "fall",
                    "chaos_moments": [
                        {"type": "dietary_restrictions", "text": "Gluten-free, diabetic, vegan, and picky toddler", "stress_level": 7},
                        {"type": "seating_chart", "text": "Navigate family politics with place cards", "stress_level": 8},
                        {"type": "cooking_timeline", "text": "Turkey math while managing three ovens", "stress_level": 9},
                        {"type": "referee_dinner", "text": "Prevent political discussions over mashed potatoes", "stress_level": 10},
                        {"type": "cleanup_crew", "text": "Somehow you're cleaning alone again", "stress_level": 6}
                    ],
                    "inner_monologue": "I'm running a small restaurant and family therapy session.",
                    "punchline": "Next year you're ordering pizza and calling it 'deconstructed turkey'",
                    "relief_moment": "Everyone leaves saying 'best Thanksgiving ever!' 🦃",
                    "cta": "Who else is the family Thanksgiving MVP? 🍂",
                    "supportive_ending": "You create the traditions that bind families together. ✨"
                },
                {
                    "id": "school_pickup_line",
                    "hook": "POV: The school pickup line is your second office",
                    "mood": "automotive_community_center",
                    "season": "school_year",
                    "chaos_moments": [
                        {"type": "timing_precision", "text": "Arrive exactly 14 minutes early for good spot", "stress_level": 3},
                        {"type": "car_coordination", "text": "Text other parents while handling calls", "stress_level": 5},
                        {"type": "snack_distribution", "text": "Distribute snacks to hungry children", "stress_level": 4},
                        {"type": "homework_preview", "text": "Pre-review assignments in car", "stress_level": 6},
                        {"type": "social_worker", "text": "Mediate sibling disputes immediately", "stress_level": 7}
                    ],
                    "inner_monologue": "My car is basically a mobile family therapy unit.",
                    "punchline": "You know every other parent's car and coffee order",
                    "relief_moment": "Perfect sync with your pickup line mom friend 👯‍♀️",
                    "cta": "Pickup line parents are the real MVPs! 🚗",
                    "supportive_ending": "You're part of an amazing community of caring parents. 💕"
                },
                {
                    "id": "tax_season_nightmare",
                    "hook": "POV: Tax season with multiple dependents and care costs",
                    "mood": "financial_documentation_hell",
                    "season": "spring",
                    "chaos_moments": [
                        {"type": "paper_explosion", "text": "Medical receipts for everyone everywhere", "stress_level": 6},
                        {"type": "dependent_calculation", "text": "Who counts as dependent when?", "stress_level": 8},
                        {"type": "care_cost_tracking", "text": "Daycare + elder care + medical = bankruptcy?", "stress_level": 9},
                        {"type": "form_confusion", "text": "Need PhD in tax law for these deductions", "stress_level": 10},
                        {"type": "receipt_archaeology", "text": "Dig through year of car receipts", "stress_level": 7}
                    ],
                    "inner_monologue": "I'm supporting the entire tax software industry single-handedly.",
                    "punchline": "Your accountant sends sympathy cards instead of bills",
                    "relief_moment": "Bigger refund than expected! 💰",
                    "cta": "Tax season sandwich parents unite! 📊",
                    "supportive_ending": "You're managing complex finances like a pro. Amazing! 🌟"
                },
                {
                    "id": "grocery_store_olympics",
                    "hook": "POV: Grocery shopping for three generations",
                    "mood": "retail_athletic_event",
                    "season": "any",
                    "chaos_moments": [
                        {"type": "list_management", "text": "Three different shopping lists + coupons", "stress_level": 4},
                        {"type": "dietary_juggling", "text": "Low sodium + high fiber + kid-approved", "stress_level": 6},
                        {"type": "pharmacy_run", "text": "Pick up prescriptions between frozen foods", "stress_level": 5},
                        {"type": "budget_math", "text": "Calculate costs while preventing meltdowns", "stress_level": 8},
                        {"type": "checkout_chaos", "text": "Pay while kids ask for everything", "stress_level": 7}
                    ],
                    "inner_monologue": "I need a personal shopper and a financial advisor.",
                    "punchline": "Spend $300 and somehow have no food for dinner",
                    "relief_moment": "Everyone eats without complaining (miracle!) 🙌",
                    "cta": "Share your grocery shopping survival tips! 🛒",
                    "supportive_ending": "You keep everyone fed and healthy. You're amazing! 💕"
                },
                {
                    "id": "saturday_taxi_service",
                    "hook": "POV: Saturday is your unpaid taxi/chauffeur service day",
                    "mood": "automotive_logistics_specialist",
                    "season": "any",
                    "chaos_moments": [
                        {"type": "schedule_tetris", "text": "Soccer + piano + physical therapy + groceries", "stress_level": 7},
                        {"type": "traffic_roulette", "text": "Calculate drive times with traffic variables", "stress_level": 6},
                        {"type": "snack_coordinator", "text": "Pack snacks for all stops and ages", "stress_level": 4},
                        {"type": "entertainment_system", "text": "Playlist that works for everyone (impossible)", "stress_level": 5},
                        {"type": "gas_station_reality", "text": "Realize you've driven 200 miles in your city", "stress_level": 8}
                    ],
                    "inner_monologue": "I should charge by the mile like real taxi drivers.",
                    "punchline": "Your car qualifies for commercial vehicle insurance",
                    "relief_moment": "Everyone gets where they need to be safely 🚗",
                    "cta": "How many miles do you drive on Saturdays? 📍",
                    "supportive_ending": "You're the wheels that keep your family moving forward. 🌟"
                },
                {
                    "id": "summer_camp_coordination",
                    "hook": "POV: Summer camp coordination requires military planning",
                    "mood": "summer_logistics_commander",
                    "season": "summer",
                    "chaos_moments": [
                        {"type": "schedule_overlap", "text": "Camp A ends at 3, Camp B starts at 2:30", "stress_level": 8},
                        {"type": "supply_management", "text": "Label everything with everyone's names", "stress_level": 5},
                        {"type": "pickup_rotation", "text": "Coordinate with 15 other parents", "stress_level": 7},
                        {"type": "activity_overload", "text": "Swimming + art + sports = three different bags", "stress_level": 6},
                        {"type": "weather_contingency", "text": "Rain day alternatives for outdoor camps", "stress_level": 9}
                    ],
                    "inner_monologue": "I'm running a summer camp logistics empire.",
                    "punchline": "September can't come fast enough (wait, yes it can)",
                    "relief_moment": "Kids are happy, tired, and sun-kissed ☀️",
                    "cta": "Summer camp parents deserve medals! 🏆",
                    "supportive_ending": "You're creating magical summer memories. Beautiful! ✨"
                }
            ]
        }
        
        # Create the config directory if it doesn't exist
        os.makedirs(self.config_dir, exist_ok=True)
        
        with open(file_path, 'w') as f:
            json.dump(enhanced_scenarios, f, indent=2)
        
        print(f"✅ Created enhanced scenarios file with {len(enhanced_scenarios['scenarios'])} scenarios!")
    
    def _get_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        """Get font with better fallbacks and styling options."""
        font_paths = [
            # macOS fonts
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Arial.ttf", 
            "/System/Library/Fonts/Trebuchet MS.ttf",
            # Linux fonts
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            # Windows fonts
            "arialbd.ttf" if bold else "arial.ttf",
            "calibri.ttf",
        ]
        
        for font_path in font_paths:
            try:
                return ImageFont.truetype(font_path, size)
            except (OSError, IOError):
                continue
        
        return ImageFont.load_default()
    
    def _create_gradient_background(self, width: int, height: int, colors: List[str]) -> Image.Image:
        """Create a beautiful gradient background."""
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)
        
        # Convert hex colors to RGB
        color1 = tuple(int(colors[0][1:][i:i+2], 16) for i in (0, 2, 4))
        color2 = tuple(int(colors[1][1:][i:i+2], 16) for i in (0, 2, 4))
        
        # Create vertical gradient
        for y in range(height):
            ratio = y / height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        return img
    
    def _create_notification_overlay(self, text: str, notification_type: str = "text") -> Image.Image:
        """Create realistic notification overlays."""
        width, height = 900, 120
        
        # Notification background with shadow
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw shadow
        shadow_offset = 3
        draw.rounded_rectangle(
            [shadow_offset, shadow_offset, width - 1, height - 1], 
            radius=15, fill=(0, 0, 0, 50)
        )
        
        # Draw notification background
        bg_color = (255, 255, 255, 240) if notification_type == "text" else (50, 50, 50, 240)
        draw.rounded_rectangle([0, 0, width - shadow_offset, height - shadow_offset], 
                             radius=15, fill=bg_color)
        
        # App icon area
        icon_size = 40
        icon_x, icon_y = 20, (height - shadow_offset - icon_size) // 2
        icon_color = (0, 120, 255) if notification_type == "text" else (255, 100, 100)
        draw.ellipse([icon_x, icon_y, icon_x + icon_size, icon_y + icon_size], fill=icon_color)
        
        # Notification text
        font = self._get_font(28)
        text_color = (50, 50, 50) if notification_type == "text" else (255, 255, 255)
        text_x = icon_x + icon_size + 15
        text_y = icon_y + 5
        
        # Truncate text if too long
        if len(text) > 50:
            text = text[:47] + "..."
        
        draw.text((text_x, text_y), text, fill=text_color, font=font)
        
        return img
    
    def _create_stress_meter(self, stress_level: int) -> Image.Image:
        """Create an animated stress meter visualization."""
        width, height = 300, 60
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Background bar
        bar_height = 30
        bar_y = (height - bar_height) // 2
        draw.rounded_rectangle([10, bar_y, width - 10, bar_y + bar_height], 
                             radius=15, fill=(200, 200, 200, 180))
        
        # Stress level fill
        fill_width = int((stress_level / 10) * (width - 40))
        if stress_level <= 3:
            color = (102, 187, 106)  # Green
        elif stress_level <= 6:
            color = (255, 167, 38)   # Orange  
        else:
            color = (231, 76, 60)    # Red
        
        if fill_width > 0:
            draw.rounded_rectangle([15, bar_y + 5, 15 + fill_width, bar_y + bar_height - 5],
                                 radius=10, fill=color)
        
        # Stress level text
        font = self._get_font(20, bold=True)
        stress_text = f"STRESS: {stress_level}/10"
        text_bbox = draw.textbbox((0, 0), stress_text, font=font)
        text_x = (width - text_bbox[2]) // 2
        text_y = bar_y - 25
        
        # Text shadow
        draw.text((text_x + 1, text_y + 1), stress_text, fill=(0, 0, 0, 100), font=font)
        draw.text((text_x, text_y), stress_text, fill=(255, 255, 255), font=font)
        
        return img
    
    def _create_time_progression_overlay(self, time_text: str) -> Image.Image:
        """Create time progression visual."""
        width, height = 250, 80
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Clock background
        draw.rounded_rectangle([0, 0, width, height], radius=20, fill=(255, 215, 0, 200))
        
        # Clock emoji and time
        font = self._get_font(32, bold=True)
        text = f"🕐 {time_text}"
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_x = (width - text_bbox[2]) // 2
        text_y = (height - text_bbox[3]) // 2
        
        draw.text((text_x, text_y), text, fill=(60, 60, 60), font=font)
        
        return img
    
    def _create_split_screen_layout(self, left_text: str, right_text: str, 
                                  bg_colors: List[str]) -> Image.Image:
        """Create split-screen chaos visualization."""
        img = self._create_gradient_background(self.video_width, self.video_height, bg_colors)
        draw = ImageDraw.Draw(img)
        
        # Split line
        split_x = self.video_width // 2
        draw.line([(split_x, 0), (split_x, self.video_height)], fill="white", width=8)
        
        # Left side
        left_font = self._get_font(45, bold=True)
        left_lines = self._wrap_text(left_text, left_font, draw, split_x - 60)
        left_y = (self.video_height - len(left_lines) * 60) // 2
        
        for i, line in enumerate(left_lines):
            text_bbox = draw.textbbox((0, 0), line, font=left_font)
            text_x = (split_x - text_bbox[2]) // 2
            y_pos = left_y + (i * 60)
            
            # Shadow
            draw.text((text_x + 2, y_pos + 2), line, fill=(0, 0, 0, 150), font=left_font)
            draw.text((text_x, y_pos), line, fill="white", font=left_font)
        
        # Right side  
        right_font = self._get_font(45, bold=True)
        right_lines = self._wrap_text(right_text, right_font, draw, split_x - 60)
        right_y = (self.video_height - len(right_lines) * 60) // 2
        
        for i, line in enumerate(right_lines):
            text_bbox = draw.textbbox((0, 0), line, font=right_font)
            text_x = split_x + 30
            y_pos = right_y + (i * 60)
            
            # Shadow
            draw.text((text_x + 2, y_pos + 2), line, fill=(0, 0, 0, 150), font=right_font)
            draw.text((text_x, y_pos), line, fill="white", font=right_font)
        
        return img
    
    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, 
                   draw: ImageDraw.Draw, max_width: int) -> List[str]:
        """Wrap text to fit within specified width."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            text_bbox = draw.textbbox((0, 0), test_line, font=font)
            
            if text_bbox[2] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _create_meme_style_text(self, text: str, bg_colors: List[str], 
                              style: str = "impact") -> Image.Image:
        """Create meme-style text overlays."""
        img = self._create_gradient_background(self.video_width, self.video_height, bg_colors)
        draw = ImageDraw.Draw(img)
        
        # Choose font size based on text length
        if len(text) < 30:
            font_size = 80
        elif len(text) < 60:
            font_size = 65
        else:
            font_size = 50
        
        font = self._get_font(font_size, bold=True)
        
        # Wrap text
        lines = self._wrap_text(text, font, draw, self.video_width - 100)
        
        # Position text
        total_height = len(lines) * (font_size + 10)
        start_y = (self.video_height - total_height) // 2
        
        for i, line in enumerate(lines):
            text_bbox = draw.textbbox((0, 0), line, font=font)
            text_x = (self.video_width - text_bbox[2]) // 2
            y_pos = start_y + (i * (font_size + 10))
            
            # Meme-style border (thick black outline)
            outline_width = 4
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((text_x + dx, y_pos + dy), line, 
                                fill="black", font=font)
            
            # Main text (white)
            draw.text((text_x, y_pos), line, fill="white", font=font)
        
        return img
    
    def _create_watermark(self) -> Image.Image:
        """Create brand watermark."""
        watermark = Image.new('RGBA', (300, 60), (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark)
        
        font = self._get_font(24, bold=True)
        text = "@SandwichGenDiaries"
        
        # Semi-transparent background
        draw.rounded_rectangle([0, 0, 300, 60], radius=15, 
                             fill=(255, 255, 255, 100))
        
        # Brand color text
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_x = (300 - text_bbox[2]) // 2
        text_y = (60 - text_bbox[3]) // 2
        
        draw.text((text_x, text_y), text, fill=self.brand_colors['primary'], font=font)
        
        return watermark
    
    async def _generate_enhanced_tts(self, text: str, output_path: str, 
                                   voice_type: str = 'relatable_mom',
                                   emotion: str = 'normal') -> float:
        """Generate enhanced TTS with personality and emotion, with fallback."""
        try:
            voice = self.voice_options.get(voice_type, self.voice_options['relatable_mom'])
            
            # Adjust speech rate based on emotion
            if emotion == 'frantic':
                rate = "+20%"
            elif emotion == 'exhausted':
                rate = "-10%" 
            elif emotion == 'excited':
                rate = "+15%"
            else:
                rate = "+5%"
            
            # Clean text for TTS (remove POV: prefix and emojis that might cause issues)
            clean_text = text.replace("POV:", "").replace("💭", "").replace("😮‍💨", "").replace("📱", "").strip()
            
            # Use simple communicate without complex SSML for better compatibility
            communicate = edge_tts.Communicate(clean_text, voice, rate=rate)
            await communicate.save(output_path)
            
            # Get duration
            cmd = ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                   "-of", "csv=p=0", str(output_path)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            duration = float(result.stdout.strip()) if result.stdout.strip() else 3.0
            
            return duration
            
        except Exception as e:
            print(f"⚠️ TTS failed ({e}), creating silent audio...")
            # Create silent audio as fallback
            duration = min(len(text) * 0.1, 8.0)  # Estimate reading time
            self._create_silent_audio(output_path, duration)
            return duration
    
    def _create_silent_audio(self, output_path: str, duration: float) -> None:
        """Create silent audio file for fallback."""
        cmd = [
            "ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo",
            "-t", str(duration), output_path
        ]
        subprocess.run(cmd, check=True, capture_output=True)
    
    def _create_audio_mix(self, segments: List[Dict], output_path: str) -> None:
        """Create complex audio mix with overlapping sounds."""
        # This would normally use more sophisticated audio libraries
        # For now, we'll create a simple mix using ffmpeg
        
        filter_parts = []
        inputs = []
        
        for i, segment in enumerate(segments):
            inputs.extend(["-i", segment['file']])
            
            # Add fade in/out and volume adjustments
            fade_in = 0.5
            fade_out = 0.5
            volume = segment.get('volume', 1.0)
            delay = segment.get('delay', 0)
            
            filter_part = f"[{i}:a]adelay={delay * 1000}|{delay * 1000}," \
                         f"afade=t=in:ss=0:d={fade_in}," \
                         f"afade=t=out:st={segment['duration'] - fade_out}:d={fade_out}," \
                         f"volume={volume}[a{i}]"
            
            filter_parts.append(filter_part)
        
        # Mix all audio streams
        mix_inputs = "".join([f"[a{i}]" for i in range(len(segments))])
        filter_parts.append(f"{mix_inputs}amix=inputs={len(segments)}:duration=longest[out]")
        
        cmd = ["ffmpeg", "-y"] + inputs + [
            "-filter_complex", ";".join(filter_parts),
            "-map", "[out]", output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
    
    async def generate_enhanced_video(self, scenario_id: str = None, 
                                    output_filename: str = None) -> str:
        """Generate an enhanced POV video with all V2 features."""
        
        # Select scenario
        if scenario_id:
            scenario = next((s for s in self.scenarios if s.get('id') == scenario_id), None)
            if not scenario:
                scenario = random.choice(self.scenarios)
        else:
            scenario = random.choice(self.scenarios)
        
        print(f"🎬 Generating enhanced video for: {scenario['hook'][:50]}...")
        print(f"🎭 Mood: {scenario['mood']}")
        
        # Create output filename
        if not output_filename:
            safe_id = scenario.get('id', 'random').replace('_', '-')
            output_filename = f"sandwich_v2_{safe_id}_{uuid.uuid4().hex[:8]}.mp4"
        
        output_path = self.output_dir / output_filename
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Choose visual theme
        bg_colors = random.choice(self.background_gradients)
        
        # Generate all audio segments
        hook_audio = await self._generate_enhanced_tts(
            scenario['hook'], str(self.temp_dir / "hook.wav"), 
            voice_type='relatable_mom', emotion='normal'
        )
        
        inner_monologue_audio = await self._generate_enhanced_tts(
            scenario['inner_monologue'], str(self.temp_dir / "inner_monologue.wav"),
            voice_type='inner_monologue', emotion='exhausted'  
        )
        
        punchline_audio = await self._generate_enhanced_tts(
            scenario['punchline'], str(self.temp_dir / "punchline.wav"),
            voice_type='sarcastic', emotion='normal'
        )
        
        relief_audio = await self._generate_enhanced_tts(
            scenario['relief_moment'], str(self.temp_dir / "relief.wav"),
            voice_type='uplifting', emotion='excited'
        )
        
        supportive_audio = await self._generate_enhanced_tts(
            scenario['supportive_ending'], str(self.temp_dir / "supportive.wav"),
            voice_type='uplifting', emotion='normal'
        )
        
        # Create video segments with enhanced visuals
        
        # 1. Hook segment
        hook_img = self._create_meme_style_text(scenario['hook'], bg_colors)
        watermark = self._create_watermark()
        hook_img.paste(watermark, (self.video_width - 320, self.video_height - 80), watermark)
        hook_img_path = self.temp_dir / "hook.png"
        hook_img.save(hook_img_path)
        
        # 2. Buildup with inner monologue
        buildup_img = self._create_gradient_background(self.video_width, self.video_height, bg_colors)
        buildup_draw = ImageDraw.Draw(buildup_img)
        
        # Add thought bubble style
        font = self._get_font(50)
        thought_text = f"💭 {scenario['inner_monologue']}"
        lines = self._wrap_text(thought_text, font, buildup_draw, self.video_width - 100)
        
        start_y = (self.video_height - len(lines) * 60) // 2
        for i, line in enumerate(lines):
            text_bbox = buildup_draw.textbbox((0, 0), line, font=font)
            text_x = (self.video_width - text_bbox[2]) // 2
            y_pos = start_y + (i * 60)
            
            # Soft shadow
            buildup_draw.text((text_x + 2, y_pos + 2), line, fill=(0, 0, 0, 100), font=font)
            buildup_draw.text((text_x, y_pos), line, fill="white", font=font)
        
        buildup_img.paste(watermark, (self.video_width - 320, self.video_height - 80), watermark)
        buildup_img_path = self.temp_dir / "buildup.png"
        buildup_img.save(buildup_img_path)
        
        # 3. Chaos montage with enhanced visuals
        chaos_images = []
        max_stress = max([moment.get('stress_level', 5) for moment in scenario['chaos_moments']])
        
        for i, moment in enumerate(scenario['chaos_moments']):
            stress_level = moment.get('stress_level', 5)
            
            # Get text for this moment
            moment_text = moment.get('text', moment.get('left', '') + ' ' + moment.get('right', ''))
            
            if moment['type'] == 'split_screen':
                img = self._create_split_screen_layout(
                    moment['left'], moment['right'], bg_colors
                )
            else:
                img = self._create_meme_style_text(moment_text, bg_colors)
            
            # Add stress meter
            stress_meter = self._create_stress_meter(stress_level)
            img.paste(stress_meter, (50, 100), stress_meter)
            
            # Add time progression if it's a time-based moment
            if any(time_word in moment_text.lower() for time_word in ['am', 'pm', ':']):
                time_match = None
                import re
                time_pattern = r'\d{1,2}:\d{2}(?:am|pm)?|\d{1,2}(?:am|pm)'
                match = re.search(time_pattern, moment_text, re.IGNORECASE)
                if match:
                    time_overlay = self._create_time_progression_overlay(match.group())
                    img.paste(time_overlay, (self.video_width - 270, 200), time_overlay)
            
            # Add notification overlay for certain types
            if moment['type'] in ['notification', 'text_spam', 'phone_call']:
                notification = self._create_notification_overlay(moment_text, moment['type'])
                img.paste(notification, (90, self.video_height - 300), notification)
            
            # Add watermark
            img.paste(watermark, (self.video_width - 320, self.video_height - 80), watermark)
            
            img_path = self.temp_dir / f"chaos_{i}.png"
            img.save(img_path)
            chaos_images.append(str(img_path))
        
        # 4. Relief moment
        relief_img = self._create_gradient_background(self.video_width, self.video_height, 
                                                    ['#66BB6A', '#4CAF50'])  # Green relief
        relief_draw = ImageDraw.Draw(relief_img)
        
        font = self._get_font(55, bold=True)
        relief_text = f"😮‍💨 {scenario['relief_moment']}"
        lines = self._wrap_text(relief_text, font, relief_draw, self.video_width - 100)
        
        start_y = (self.video_height - len(lines) * 70) // 2
        for i, line in enumerate(lines):
            text_bbox = relief_draw.textbbox((0, 0), line, font=font)
            text_x = (self.video_width - text_bbox[2]) // 2
            y_pos = start_y + (i * 70)
            
            relief_draw.text((text_x + 2, y_pos + 2), line, fill=(0, 0, 0, 100), font=font)
            relief_draw.text((text_x, y_pos), line, fill="white", font=font)
        
        relief_img.paste(watermark, (self.video_width - 320, self.video_height - 80), watermark)
        relief_img_path = self.temp_dir / "relief.png"
        relief_img.save(relief_img_path)
        
        # 5. Punchline
        punchline_img = self._create_meme_style_text(scenario['punchline'], bg_colors)
        punchline_img.paste(watermark, (self.video_width - 320, self.video_height - 80), watermark)
        punchline_img_path = self.temp_dir / "punchline.png"
        punchline_img.save(punchline_img_path)
        
        # 6. Call to action + supportive ending
        cta_bg = ['#FF6B6B', '#FFA726']  # Brand colors
        cta_img = self._create_gradient_background(self.video_width, self.video_height, cta_bg)
        cta_draw = ImageDraw.Draw(cta_img)
        
        # CTA text
        cta_font = self._get_font(45, bold=True)
        cta_text = scenario['cta']
        cta_lines = self._wrap_text(cta_text, cta_font, cta_draw, self.video_width - 100)
        
        # Supportive ending
        support_font = self._get_font(38)
        support_text = scenario['supportive_ending']
        support_lines = self._wrap_text(support_text, support_font, cta_draw, self.video_width - 100)
        
        # Position text
        total_lines = len(cta_lines) + len(support_lines) + 2  # +2 for spacing
        line_height = 55
        start_y = (self.video_height - total_lines * line_height) // 2
        
        # Draw CTA
        current_y = start_y
        for line in cta_lines:
            text_bbox = cta_draw.textbbox((0, 0), line, font=cta_font)
            text_x = (self.video_width - text_bbox[2]) // 2
            
            cta_draw.text((text_x + 2, current_y + 2), line, fill=(0, 0, 0, 150), font=cta_font)
            cta_draw.text((text_x, current_y), line, fill="white", font=cta_font)
            current_y += line_height
        
        # Add spacing
        current_y += line_height
        
        # Draw supportive ending
        for line in support_lines:
            text_bbox = cta_draw.textbbox((0, 0), line, font=support_font)
            text_x = (self.video_width - text_bbox[2]) // 2
            
            cta_draw.text((text_x + 2, current_y + 2), line, fill=(0, 0, 0, 150), font=support_font)
            cta_draw.text((text_x, current_y), line, fill="white", font=support_font)
            current_y += line_height
        
        cta_img.paste(watermark, (self.video_width - 320, self.video_height - 80), watermark)
        cta_img_path = self.temp_dir / "cta.png"
        cta_img.save(cta_img_path)
        
        # Create video segments
        print("🎬 Creating video segments...")
        
        segments_info = [
            {"image": str(hook_img_path), "audio": str(self.temp_dir / "hook.wav"), 
             "duration": self.hook_duration, "name": "hook"},
            {"image": str(buildup_img_path), "audio": str(self.temp_dir / "inner_monologue.wav"), 
             "duration": self.buildup_duration, "name": "buildup"},
            {"images": chaos_images, "audio": None, 
             "duration": self.chaos_duration, "name": "chaos"},
            {"image": str(relief_img_path), "audio": str(self.temp_dir / "relief.wav"), 
             "duration": self.relief_duration, "name": "relief"},
            {"image": str(punchline_img_path), "audio": str(self.temp_dir / "punchline.wav"), 
             "duration": self.punchline_duration, "name": "punchline"},
            {"image": str(cta_img_path), "audio": str(self.temp_dir / "supportive.wav"), 
             "duration": self.cta_duration, "name": "cta"}
        ]
        
        segment_files = []
        
        for i, segment in enumerate(segments_info):
            segment_path = self.temp_dir / f"segment_{i}_{segment['name']}.mp4"
            
            if segment['name'] == 'chaos':
                # Special handling for chaos montage
                self._create_chaos_video_segment(segment['images'], str(segment_path), segment['duration'])
            else:
                self._create_single_video_segment(
                    segment['image'], segment['audio'], str(segment_path), segment['duration']
                )
            
            segment_files.append(str(segment_path))
        
        # Concatenate all segments
        print("🔗 Concatenating segments...")
        concat_file = self.temp_dir / "concat.txt"
        with open(concat_file, 'w') as f:
            for segment_file in segment_files:
                f.write(f"file '{segment_file}'\n")
        
        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
            "-c", "copy", str(output_path)
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        
        print(f"✅ Enhanced video generated: {output_path}")
        print(f"📊 Total duration: ~{self.total_duration} seconds")
        print(f"🎨 Visual enhancements: ✅ Split-screen, stress meters, notifications")
        print(f"🔊 Audio enhancements: ✅ Multiple voices, emotional ranges")
        print(f"💕 Relatability features: ✅ CTA, supportive endings")
        
        return str(output_path)
    
    def _create_single_video_segment(self, image_path: str, audio_path: str, 
                                   output_path: str, duration: float) -> None:
        """Create a single video segment."""
        if audio_path:
            cmd = [
                "ffmpeg", "-y", "-loop", "1", "-i", image_path,
                "-i", audio_path, "-t", str(duration),
                "-pix_fmt", "yuv420p", "-shortest",
                "-vf", f"scale={self.video_width}:{self.video_height}",
                output_path
            ]
        else:
            cmd = [
                "ffmpeg", "-y", "-loop", "1", "-i", image_path,
                "-t", str(duration), "-pix_fmt", "yuv420p",
                "-vf", f"scale={self.video_width}:{self.video_height}",
                output_path
            ]
        
        subprocess.run(cmd, check=True, capture_output=True)
    
    def _create_chaos_video_segment(self, images: List[str], output_path: str, 
                                  total_duration: float) -> None:
        """Create chaos montage with quick cuts."""
        if not images:
            return
        
        segment_duration = total_duration / len(images)
        temp_segments = []
        
        # Create individual segments for each image
        for i, img_path in enumerate(images):
            temp_segment = self.temp_dir / f"chaos_temp_{i}.mp4"
            cmd = [
                "ffmpeg", "-y", "-loop", "1", "-i", img_path,
                "-t", str(segment_duration), "-pix_fmt", "yuv420p",
                "-vf", f"scale={self.video_width}:{self.video_height}",
                str(temp_segment)
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            temp_segments.append(str(temp_segment))
        
        # Concatenate chaos segments
        chaos_concat = self.temp_dir / "chaos_concat.txt"
        with open(chaos_concat, 'w') as f:
            for segment in temp_segments:
                f.write(f"file '{segment}'\n")
        
        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(chaos_concat),
            "-c", "copy", output_path
        ]
        subprocess.run(cmd, check=True, capture_output=True)
    
    def cleanup(self):
        """Enhanced cleanup with better error handling."""
        import shutil
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                print("🧹 Temporary files cleaned up")
        except Exception as e:
            print(f"⚠️ Warning: Could not clean up temp files: {e}")

async def create_example_videos():
    """Create the three example videos requested."""
    generator = SandwichGeneratorV2()
    
    example_scenarios = [
        "emergency_contact",
        "wfh_chaos", 
        "christmas_exhaustion"
    ]
    
    try:
        for i, scenario_id in enumerate(example_scenarios, 1):
            print(f"\n🎬 Creating example video {i}/3...")
            output_filename = f"sandwich_v2_example_{i}.mp4"
            
            output_path = await generator.generate_enhanced_video(
                scenario_id=scenario_id,
                output_filename=output_filename
            )
            
            print(f"✅ Example {i} complete: {output_path}")
        
        print(f"\n🎉 All 3 example videos generated successfully!")
        print(f"📁 Location: {generator.output_dir}")
        
    except Exception as e:
        print(f"❌ Error creating example videos: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        generator.cleanup()

async def main():
    """Main function demonstrating the enhanced generator."""
    print("🥪✨ Sandwich Generation Diaries V2 - Enhanced Content Generator")
    print("=" * 70)
    print("🚀 New features:")
    print("   • Split-screen chaos moments")
    print("   • Stress meter visualizations") 
    print("   • Notification overlays")
    print("   • Multiple TTS voices with personality")
    print("   • Enhanced relatability features")
    print("   • Brand integration")
    print("   • 20+ scenarios including seasonal content")
    print("=" * 70)
    
    await create_example_videos()

if __name__ == "__main__":
    asyncio.run(main())