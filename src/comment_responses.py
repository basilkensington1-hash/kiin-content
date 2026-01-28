#!/usr/bin/env python3
"""
Comment Response Generator

Generate warm, authentic responses to common comment types for community engagement.
Designed to feel human and supportive, like talking to a friend who understands.
"""

import json
import random
import argparse
import os
from pathlib import Path
from typing import List, Dict, Optional

class CommentResponseGenerator:
    def __init__(self, config_path: Optional[str] = None):
        """Initialize with comment templates."""
        if config_path is None:
            # Default to config directory relative to this script
            script_dir = Path(__file__).parent
            config_path = script_dir.parent / "config" / "comment_templates.json"
        
        self.config_path = Path(config_path)
        self.templates = self.load_templates()
        
    def load_templates(self) -> Dict:
        """Load comment templates from JSON config."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Template file not found: {self.config_path}")
            print("💡 Make sure comment_templates.json exists in the config directory")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing template file: {e}")
            return {}
    
    def get_available_types(self) -> List[str]:
        """Get list of available response types."""
        return list(self.templates.keys())
    
    def generate_response(self, response_type: str, name: str = "", topic: str = "", count: int = 1) -> List[str]:
        """Generate responses of specified type."""
        if response_type not in self.templates:
            available = ", ".join(self.get_available_types())
            raise ValueError(f"Unknown response type '{response_type}'. Available: {available}")
        
        templates = self.templates[response_type]
        
        if count > len(templates):
            print(f"⚠️ Requested {count} responses but only {len(templates)} templates available for '{response_type}'")
            count = len(templates)
        
        # Get random selection without repeats
        selected_templates = random.sample(templates, count)
        
        responses = []
        for template in selected_templates:
            # Replace placeholders
            response = template.format(name=name, topic=topic)
            responses.append(response)
        
        return responses
    
    def generate_contextual_response(self, comment_content: str, commenter_name: str = "") -> str:
        """Generate contextual response based on comment content analysis."""
        comment_lower = comment_content.lower()
        
        # Analyze comment sentiment and content
        if any(word in comment_lower for word in ['thank', 'grateful', 'appreciate', 'love this', 'amazing']):
            response_type = 'thank_you'
        elif any(word in comment_lower for word in ['story', 'experience', 'journey', 'struggle', 'difficult']):
            response_type = 'story_response'
        elif any(word in comment_lower for word in ['medication', 'pills', 'prescription', 'dosage']):
            response_type = 'question_medication'
        elif any(word in comment_lower for word in ['self care', 'self-care', 'burnout', 'exhausted', 'tired']):
            response_type = 'question_self_care'
        elif any(word in comment_lower for word in ['resource', 'help', 'support', 'assistance']):
            response_type = 'question_resources'
        elif '?' in comment_content:
            response_type = 'engagement_questions'
        elif any(word in comment_lower for word in ['celebrate', 'victory', 'success', 'good news', 'breakthrough']):
            response_type = 'celebration'
        else:
            response_type = 'supportive_general'
        
        return self.generate_response(response_type, name=commenter_name)[0]
    
    def generate_custom_mix(self, count: int = 10) -> List[Dict[str, str]]:
        """Generate a mixed batch of responses for variety."""
        all_responses = []
        
        # Get balanced mix from different categories
        categories = ['thank_you', 'supportive_general', 'encouragement', 'engagement_questions']
        per_category = max(1, count // len(categories))
        
        for category in categories:
            responses = self.generate_response(category, name="{name}", count=per_category)
            for response in responses:
                all_responses.append({
                    'type': category,
                    'response': response,
                    'variables': ['name'] if '{name}' in response else []
                })
        
        # Fill remaining with random selection
        remaining = count - len(all_responses)
        if remaining > 0:
            all_types = list(self.templates.keys())
            for _ in range(remaining):
                rand_type = random.choice(all_types)
                response = self.generate_response(rand_type, name="{name}")[0]
                all_responses.append({
                    'type': rand_type,
                    'response': response,
                    'variables': ['name'] if '{name}' in response else []
                })
        
        return random.sample(all_responses, count)

def main():
    parser = argparse.ArgumentParser(
        description="Generate warm, authentic comment responses for community engagement",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --type thank_you --count 5
  %(prog)s --type story_response --name "Sarah" --count 3
  %(prog)s --type question --topic "medication tracking"
  %(prog)s --contextual "Thank you so much for sharing this helpful tip!" --name "Maria"
  %(prog)s --mixed --count 10
  %(prog)s --list-types
        """
    )
    
    parser.add_argument('--type', help='Type of response to generate')
    parser.add_argument('--count', type=int, default=1, help='Number of responses to generate')
    parser.add_argument('--name', default='', help='Name to personalize responses')
    parser.add_argument('--topic', default='', help='Topic to reference in responses')
    parser.add_argument('--contextual', help='Generate response based on comment content')
    parser.add_argument('--mixed', action='store_true', help='Generate mixed batch of responses')
    parser.add_argument('--list-types', action='store_true', help='List available response types')
    parser.add_argument('--config', help='Path to custom templates JSON file')
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = CommentResponseGenerator(args.config)
    
    if not generator.templates:
        return 1
    
    # List available types
    if args.list_types:
        print("🎯 Available response types:")
        for response_type in generator.get_available_types():
            template_count = len(generator.templates[response_type])
            print(f"  • {response_type} ({template_count} templates)")
        return 0
    
    try:
        # Generate contextual response
        if args.contextual:
            response = generator.generate_contextual_response(args.contextual, args.name)
            print(f"💬 Contextual response for: \"{args.contextual}\"\n")
            print(f"✨ {response}\n")
            return 0
        
        # Generate mixed batch
        if args.mixed:
            responses = generator.generate_custom_mix(args.count)
            print(f"🎭 Mixed batch of {len(responses)} responses:\n")
            for i, item in enumerate(responses, 1):
                print(f"{i:2d}. [{item['type']}] {item['response']}")
                if item['variables']:
                    print(f"     Variables: {', '.join(item['variables'])}")
                print()
            return 0
        
        # Generate specific type
        if not args.type:
            parser.print_help()
            print(f"\n💡 Hint: Use --list-types to see available response types")
            return 1
        
        responses = generator.generate_response(args.type, args.name, args.topic, args.count)
        
        print(f"💜 {args.count} {args.type} response{'s' if args.count > 1 else ''}:")
        if args.name:
            print(f"   Personalized for: {args.name}")
        if args.topic:
            print(f"   Topic: {args.topic}")
        print()
        
        for i, response in enumerate(responses, 1):
            print(f"{i:2d}. {response}\n")
            
    except ValueError as e:
        print(f"❌ {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())