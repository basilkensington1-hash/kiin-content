"""
Social Caption Generator - Platform-specific caption generation and optimization.
"""

import json
import re
import random
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class SocialCaptionGenerator:
    """Generate optimized captions for different social media platforms"""
    
    def __init__(self, config_path: str = "config/caption_templates.json"):
        self.config_path = config_path
        self.templates = self._load_templates()
        
        # Platform-specific specs
        self.platform_specs = {
            'instagram': {
                'max_length': 2200,
                'optimal_length': 150,
                'supports_newlines': True,
                'emoji_friendly': True,
                'hashtag_style': 'separate_or_integrated',
                'tone': 'casual_inspirational'
            },
            'tiktok': {
                'max_length': 2200,
                'optimal_length': 100,
                'supports_newlines': True,
                'emoji_friendly': True,
                'hashtag_style': 'integrated',
                'tone': 'casual_engaging'
            },
            'youtube': {
                'max_length': 5000,
                'optimal_length': 200,
                'supports_newlines': True,
                'emoji_friendly': False,
                'hashtag_style': 'description_end',
                'tone': 'informative'
            },
            'twitter': {
                'max_length': 280,
                'optimal_length': 120,
                'supports_newlines': True,
                'emoji_friendly': True,
                'hashtag_style': 'integrated',
                'tone': 'conversational'
            },
            'linkedin': {
                'max_length': 3000,
                'optimal_length': 300,
                'supports_newlines': True,
                'emoji_friendly': False,
                'hashtag_style': 'minimal',
                'tone': 'professional'
            },
            'pinterest': {
                'max_length': 500,
                'optimal_length': 200,
                'supports_newlines': True,
                'emoji_friendly': True,
                'hashtag_style': 'descriptive',
                'tone': 'helpful'
            },
            'facebook': {
                'max_length': 63206,  # Practically unlimited
                'optimal_length': 250,
                'supports_newlines': True,
                'emoji_friendly': True,
                'hashtag_style': 'minimal',
                'tone': 'community_focused'
            }
        }
        
        # Common caregiver themes and messaging
        self.caregiver_themes = {
            'support': {
                'keywords': ['support', 'community', 'together', 'help'],
                'emotional_tone': 'warm',
                'call_to_action': 'share_support'
            },
            'tips': {
                'keywords': ['tips', 'advice', 'help', 'guide'],
                'emotional_tone': 'helpful',
                'call_to_action': 'save_share'
            },
            'validation': {
                'keywords': ['valid', 'normal', 'okay', 'understand'],
                'emotional_tone': 'reassuring',
                'call_to_action': 'relate'
            },
            'self_care': {
                'keywords': ['self-care', 'wellness', 'rest', 'recharge'],
                'emotional_tone': 'nurturing',
                'call_to_action': 'self_reflect'
            },
            'awareness': {
                'keywords': ['awareness', 'education', 'learn', 'understand'],
                'emotional_tone': 'informative',
                'call_to_action': 'educate_others'
            }
        }
    
    def _load_templates(self) -> Dict[str, Any]:
        """Load caption templates"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._get_default_templates()
        except Exception as e:
            logger.error(f"Error loading caption templates: {e}")
            return self._get_default_templates()
    
    def _get_default_templates(self) -> Dict[str, Any]:
        """Get default caption templates"""
        return {
            "hooks": {
                "question": [
                    "Have you ever felt {emotion}?",
                    "What would you tell someone who {situation}?",
                    "Is it just me, or do you also {feeling}?"
                ],
                "statement": [
                    "Here's what no one tells you about {topic}:",
                    "The truth about {topic} that caregivers need to hear:",
                    "This changed everything for me as a caregiver:"
                ],
                "story": [
                    "Yesterday, something happened that made me realize...",
                    "I used to think {belief}, but then...",
                    "My {relationship} taught me something important:"
                ]
            },
            "body_frameworks": {
                "tip": {
                    "structure": "Hook + Problem + Solution + Why it works",
                    "templates": [
                        "{hook}\n\nThe challenge: {problem}\n\nWhat helped me: {solution}\n\nWhy this works: {explanation}"
                    ]
                },
                "validation": {
                    "structure": "Hook + Feeling + Normalization + Encouragement",
                    "templates": [
                        "{hook}\n\nYou're not alone in feeling {feeling}.\n\nThis is completely normal because {reason}.\n\n{encouragement}"
                    ]
                },
                "story": {
                    "structure": "Hook + Situation + Lesson + Application",
                    "templates": [
                        "{hook}\n\n{situation}\n\nWhat I learned: {lesson}\n\nHow this applies to you: {application}"
                    ]
                }
            },
            "call_to_actions": {
                "share_support": [
                    "Drop a ❤️ if you can relate",
                    "Share your experience in the comments",
                    "Tag someone who needs to hear this"
                ],
                "save_share": [
                    "Save this for later",
                    "Share with a fellow caregiver",
                    "Which tip will you try first?"
                ],
                "relate": [
                    "Can you relate?",
                    "Have you been there?",
                    "What's your experience with this?"
                ],
                "self_reflect": [
                    "What self-care do you need today?",
                    "How will you recharge this week?",
                    "What's one thing you'll do for yourself?"
                ],
                "educate_others": [
                    "Share to spread awareness",
                    "Help others understand by sharing",
                    "Let's educate together"
                ]
            },
            "emojis": {
                "support": ["❤️", "🤗", "💙", "🫂"],
                "strength": ["💪", "🦋", "🌟", "✨"],
                "wellness": ["🌱", "🌺", "☀️", "🕊️"],
                "care": ["💕", "🌸", "🤲", "💝"],
                "community": ["👥", "🤝", "👋", "💬"]
            },
            "tone_adjustments": {
                "professional": {
                    "remove_emojis": True,
                    "formal_language": True,
                    "avoid_slang": True
                },
                "casual": {
                    "use_contractions": True,
                    "conversational": True,
                    "emoji_friendly": True
                },
                "inspirational": {
                    "uplifting_words": True,
                    "positive_framing": True,
                    "motivational_ctas": True
                }
            }
        }
    
    def generate_caption(self, content_data: Dict[str, Any], platform: str, 
                        theme: Optional[str] = None, variation: str = "A") -> str:
        """Generate optimized caption for specific platform"""
        
        # Get platform specifications
        spec = self.platform_specs.get(platform, {})
        max_length = spec.get('max_length', 2200)
        optimal_length = spec.get('optimal_length', 150)
        tone = spec.get('tone', 'casual')
        
        # Determine theme if not provided
        if not theme:
            theme = self._detect_theme(content_data.get('description', ''))
        
        # Generate base caption
        caption = self._generate_base_caption(content_data, theme, platform)
        
        # Apply platform-specific formatting
        caption = self._apply_platform_formatting(caption, platform)
        
        # Apply tone adjustments
        caption = self._apply_tone_adjustments(caption, tone)
        
        # Optimize length
        caption = self._optimize_length(caption, max_length, optimal_length)
        
        # Add variation for A/B testing
        if variation == "B":
            caption = self._create_variation(caption, platform)
        
        logger.info(f"Generated {platform} caption ({len(caption)} chars)")
        return caption
    
    def _detect_theme(self, content_text: str) -> str:
        """Detect the main theme of content"""
        content_lower = content_text.lower()
        
        theme_scores = {}
        for theme_name, theme_data in self.caregiver_themes.items():
            score = 0
            for keyword in theme_data['keywords']:
                if keyword in content_lower:
                    score += 1
            theme_scores[theme_name] = score
        
        # Return theme with highest score, default to 'support'
        if theme_scores:
            return max(theme_scores, key=theme_scores.get)
        return 'support'
    
    def _generate_base_caption(self, content_data: Dict[str, Any], theme: str, platform: str) -> str:
        """Generate the base caption structure"""
        
        # Choose hook style based on platform
        hook_style = self._choose_hook_style(platform)
        hook = self._generate_hook(content_data, theme, hook_style)
        
        # Generate body based on content type
        content_type = content_data.get('type', 'tip')
        body = self._generate_body(content_data, theme, content_type)
        
        # Add call to action
        theme_data = self.caregiver_themes.get(theme, {})
        cta_type = theme_data.get('call_to_action', 'share_support')
        cta = self._generate_cta(cta_type, platform)
        
        # Combine parts
        caption_parts = [hook, body]
        
        if cta:
            caption_parts.append(cta)
        
        return '\n\n'.join(caption_parts)
    
    def _choose_hook_style(self, platform: str) -> str:
        """Choose appropriate hook style for platform"""
        platform_hook_preferences = {
            'instagram': 'question',
            'tiktok': 'statement', 
            'youtube': 'statement',
            'twitter': 'question',
            'linkedin': 'statement',
            'pinterest': 'statement',
            'facebook': 'story'
        }
        
        return platform_hook_preferences.get(platform, 'question')
    
    def _generate_hook(self, content_data: Dict[str, Any], theme: str, style: str) -> str:
        """Generate engaging hook"""
        hooks = self.templates.get('hooks', {}).get(style, [])
        
        if not hooks:
            return content_data.get('title', '')
        
        # Choose random hook template
        hook_template = random.choice(hooks)
        
        # Fill in variables based on content
        variables = self._extract_hook_variables(content_data, theme)
        
        try:
            return hook_template.format(**variables)
        except KeyError:
            # If variables don't match, return simple hook
            return content_data.get('title', '')
    
    def _extract_hook_variables(self, content_data: Dict[str, Any], theme: str) -> Dict[str, str]:
        """Extract variables for hook templates"""
        description = content_data.get('description', '')
        title = content_data.get('title', '')
        
        # Common variables
        variables = {
            'topic': theme.replace('_', ' '),
            'emotion': 'overwhelmed',
            'situation': 'feel like you\'re doing everything wrong',
            'feeling': 'struggle with caregiver guilt',
            'belief': 'I had to do everything perfectly',
            'relationship': 'experience as a caregiver'
        }
        
        # Theme-specific variables
        if theme == 'support':
            variables.update({
                'emotion': 'alone in this journey',
                'situation': 'need someone to understand',
                'feeling': 'need extra support'
            })
        elif theme == 'tips':
            variables.update({
                'topic': 'caregiver burnout',
                'situation': 'are struggling with daily care tasks'
            })
        elif theme == 'validation':
            variables.update({
                'emotion': 'guilty for needing a break',
                'feeling': 'question your caregiving abilities'
            })
        elif theme == 'self_care':
            variables.update({
                'emotion': 'guilty for taking time for yourself',
                'situation': 'neglect your own needs'
            })
        
        return variables
    
    def _generate_body(self, content_data: Dict[str, Any], theme: str, content_type: str) -> str:
        """Generate the main body content"""
        
        frameworks = self.templates.get('body_frameworks', {})
        framework = frameworks.get(content_type, frameworks.get('tip', {}))
        
        templates = framework.get('templates', [])
        if not templates:
            return content_data.get('description', '')
        
        # Choose template
        template = random.choice(templates)
        
        # Fill in variables
        variables = self._extract_body_variables(content_data, theme)
        
        try:
            return template.format(**variables)
        except KeyError:
            return content_data.get('description', '')
    
    def _extract_body_variables(self, content_data: Dict[str, Any], theme: str) -> Dict[str, str]:
        """Extract variables for body templates"""
        description = content_data.get('description', '')
        
        # Base variables from content
        variables = {
            'problem': 'feeling overwhelmed by caregiving responsibilities',
            'solution': 'taking things one day at a time',
            'explanation': 'small steps lead to sustainable progress',
            'feeling': 'exhausted and overwhelmed',
            'reason': 'caregiving is one of life\'s biggest challenges',
            'encouragement': 'You\'re doing better than you think. ❤️',
            'situation': 'I was struggling to balance everything',
            'lesson': 'it\'s okay to ask for help',
            'application': 'don\'t try to do everything alone'
        }
        
        # Try to extract specific information from description
        if 'tip' in description.lower():
            # Extract tips if mentioned
            sentences = description.split('.')
            for sentence in sentences:
                if any(word in sentence.lower() for word in ['try', 'do', 'use', 'practice']):
                    variables['solution'] = sentence.strip()
                    break
        
        return variables
    
    def _generate_cta(self, cta_type: str, platform: str) -> str:
        """Generate call-to-action"""
        ctas = self.templates.get('call_to_actions', {}).get(cta_type, [])
        
        if not ctas:
            return ""
        
        # Choose appropriate CTA for platform
        platform_cta_preferences = {
            'instagram': 0,  # Index preference for Instagram
            'tiktok': 1,
            'youtube': 2,
            'twitter': 0,
            'linkedin': 2,
            'pinterest': 1,
            'facebook': 0
        }
        
        preferred_index = platform_cta_preferences.get(platform, 0)
        if preferred_index < len(ctas):
            return ctas[preferred_index]
        else:
            return random.choice(ctas)
    
    def _apply_platform_formatting(self, caption: str, platform: str) -> str:
        """Apply platform-specific formatting"""
        spec = self.platform_specs.get(platform, {})
        
        # Handle newlines
        if not spec.get('supports_newlines', True):
            caption = caption.replace('\n\n', ' | ').replace('\n', ' ')
        
        # Handle emojis
        if not spec.get('emoji_friendly', True):
            caption = self._remove_emojis(caption)
        else:
            caption = self._optimize_emojis(caption, platform)
        
        return caption
    
    def _remove_emojis(self, text: str) -> str:
        """Remove emojis from text"""
        # Simple emoji removal pattern
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"  # dingbats
            "\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE
        )
        return emoji_pattern.sub('', text)
    
    def _optimize_emojis(self, caption: str, platform: str) -> str:
        """Optimize emoji usage for platform"""
        
        # Platform-specific emoji preferences
        emoji_limits = {
            'instagram': 5,  # Can use more emojis
            'tiktok': 3,     # Moderate emoji use
            'youtube': 2,    # Conservative
            'twitter': 2,    # Space is limited
            'linkedin': 0,   # Professional, no emojis
            'pinterest': 3,  # Moderate
            'facebook': 3    # Moderate
        }
        
        limit = emoji_limits.get(platform, 3)
        
        # Count existing emojis
        emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]+', caption))
        
        # Add appropriate emojis if under limit
        if emoji_count < limit:
            caption = self._add_relevant_emojis(caption, platform, limit - emoji_count)
        
        return caption
    
    def _add_relevant_emojis(self, caption: str, platform: str, max_add: int) -> str:
        """Add relevant emojis to caption"""
        
        # Determine caption theme for emoji selection
        emoji_categories = self.templates.get('emojis', {})
        
        relevant_emojis = []
        caption_lower = caption.lower()
        
        # Check for relevant emoji categories
        if any(word in caption_lower for word in ['support', 'community', 'together']):
            relevant_emojis.extend(emoji_categories.get('support', []))
        
        if any(word in caption_lower for word in ['strong', 'strength', 'power']):
            relevant_emojis.extend(emoji_categories.get('strength', []))
        
        if any(word in caption_lower for word in ['care', 'love', 'heart']):
            relevant_emojis.extend(emoji_categories.get('care', []))
        
        if any(word in caption_lower for word in ['wellness', 'self-care', 'health']):
            relevant_emojis.extend(emoji_categories.get('wellness', []))
        
        # Add emojis strategically
        added = 0
        if relevant_emojis and added < max_add:
            # Add one emoji at the end
            caption += f" {random.choice(relevant_emojis)}"
            added += 1
        
        return caption
    
    def _apply_tone_adjustments(self, caption: str, tone: str) -> str:
        """Apply tone-specific adjustments"""
        
        tone_rules = self.templates.get('tone_adjustments', {}).get(tone, {})
        
        if tone_rules.get('formal_language'):
            # Make language more formal
            caption = caption.replace("you're", "you are")
            caption = caption.replace("don't", "do not")
            caption = caption.replace("can't", "cannot")
        
        if tone_rules.get('use_contractions'):
            # Make language more casual
            caption = caption.replace("you are", "you're")
            caption = caption.replace("do not", "don't")
            caption = caption.replace("cannot", "can't")
        
        if tone_rules.get('remove_emojis'):
            caption = self._remove_emojis(caption)
        
        return caption
    
    def _optimize_length(self, caption: str, max_length: int, optimal_length: int) -> str:
        """Optimize caption length for platform"""
        
        if len(caption) <= optimal_length:
            return caption
        
        if len(caption) > max_length:
            # Must truncate
            caption = caption[:max_length - 3] + "..."
        
        elif len(caption) > optimal_length * 1.5:
            # Try to shorten while keeping meaning
            caption = self._smart_truncate(caption, optimal_length)
        
        return caption
    
    def _smart_truncate(self, text: str, target_length: int) -> str:
        """Intelligently truncate text while preserving meaning"""
        
        if len(text) <= target_length:
            return text
        
        # Try to end at sentence boundary
        sentences = text.split('.')
        truncated = ""
        
        for sentence in sentences:
            if len(truncated + sentence + ".") <= target_length:
                truncated += sentence + "."
            else:
                break
        
        if truncated:
            return truncated.strip()
        
        # If no sentence boundaries work, truncate at word boundary
        words = text.split()
        truncated_words = []
        char_count = 0
        
        for word in words:
            if char_count + len(word) + 1 <= target_length - 3:  # -3 for "..."
                truncated_words.append(word)
                char_count += len(word) + 1
            else:
                break
        
        return " ".join(truncated_words) + "..."
    
    def _create_variation(self, original_caption: str, platform: str) -> str:
        """Create a variation for A/B testing"""
        
        # Strategy 1: Different hook
        lines = original_caption.split('\n\n')
        if len(lines) >= 2:
            # Replace first line (hook) with alternative
            alternative_hooks = [
                "Here's something every caregiver should know:",
                "Let's talk about something important:",
                "This might be exactly what you need to hear today:"
            ]
            lines[0] = random.choice(alternative_hooks)
            return '\n\n'.join(lines)
        
        # Strategy 2: Different CTA
        cta_variations = [
            "What do you think?",
            "Have you experienced this too?",
            "Share this with someone who needs it",
            "Drop a comment if this resonates"
        ]
        
        # Replace last line if it looks like a CTA
        if len(lines) >= 2 and ('?' in lines[-1] or 'share' in lines[-1].lower()):
            lines[-1] = random.choice(cta_variations)
            return '\n\n'.join(lines)
        
        return original_caption
    
    def generate_ab_test_captions(self, content_data: Dict[str, Any], 
                                 platform: str, theme: Optional[str] = None) -> Dict[str, str]:
        """Generate A/B test caption variations"""
        
        caption_a = self.generate_caption(content_data, platform, theme, "A")
        caption_b = self.generate_caption(content_data, platform, theme, "B")
        
        return {
            "variation_a": caption_a,
            "variation_b": caption_b,
            "platform": platform,
            "theme": theme or self._detect_theme(content_data.get('description', '')),
            "character_counts": {
                "a": len(caption_a),
                "b": len(caption_b)
            }
        }
    
    def analyze_caption_performance(self, caption: str, platform: str, 
                                   engagement_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze caption performance and provide insights"""
        
        analysis = {
            "caption_stats": {
                "length": len(caption),
                "word_count": len(caption.split()),
                "emoji_count": len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]+', caption)),
                "question_count": caption.count('?'),
                "exclamation_count": caption.count('!')
            },
            "performance": engagement_data,
            "insights": []
        }
        
        # Generate insights based on performance
        spec = self.platform_specs.get(platform, {})
        optimal_length = spec.get('optimal_length', 150)
        
        # Length insights
        caption_length = len(caption)
        if caption_length > optimal_length * 1.5:
            analysis["insights"].append("Caption may be too long for optimal engagement")
        elif caption_length < optimal_length * 0.5:
            analysis["insights"].append("Caption could be expanded for better context")
        
        # Emoji insights
        emoji_count = analysis["caption_stats"]["emoji_count"]
        if platform in ['instagram', 'facebook'] and emoji_count == 0:
            analysis["insights"].append("Adding 1-2 relevant emojis might increase engagement")
        elif platform == 'linkedin' and emoji_count > 0:
            analysis["insights"].append("Consider removing emojis for professional tone")
        
        # Engagement insights
        if engagement_data:
            engagement_rate = engagement_data.get('engagement_rate', 0)
            
            if engagement_rate > 5:  # High engagement
                analysis["insights"].append("Strong performance! Consider using similar caption style")
            elif engagement_rate < 1:  # Low engagement
                analysis["insights"].append("Low engagement - try shorter caption or stronger hook")
        
        return analysis