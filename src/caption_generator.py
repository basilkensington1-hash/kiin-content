#!/usr/bin/env python3
"""
Kiin Content Caption & Hashtag Generator

Generates authentic, research-based captions and hashtags for caregiving content
based on viral content mechanics analysis.

Usage:
    python caption_generator.py --content-type validation --platform tiktok
    python caption_generator.py --content-type confessions --platform instagram --custom
"""

import argparse
import json
import os
import random
from typing import Dict, List, Optional
import sys

class CaptionGenerator:
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the caption generator with templates."""
        if config_path is None:
            # Default to config file relative to this script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(script_dir, '..', 'config', 'captions_templates.json')
        
        self.config_path = config_path
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        """Load caption templates from JSON config."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Error: Templates file not found at {self.config_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Error: Invalid JSON in templates file: {e}")
            sys.exit(1)
    
    def get_content_types(self) -> List[str]:
        """Get list of available content types."""
        return list(self.templates['content_types'].keys())
    
    def get_platforms(self) -> List[str]:
        """Get list of available platforms."""
        return list(self.templates['platform_optimizations'].keys())
    
    def generate_caption(self, content_type: str, template_format: Optional[str] = None, 
                        custom_variables: Optional[Dict[str, str]] = None) -> Dict:
        """Generate a caption based on content type and optional template format."""
        if content_type not in self.templates['content_types']:
            raise ValueError(f"Invalid content type. Available: {self.get_content_types()}")
        
        content_config = self.templates['content_types'][content_type]
        templates = content_config['caption_templates']
        
        # Select template
        if template_format:
            template = next((t for t in templates if t['format'] == template_format), None)
            if not template:
                available_formats = [t['format'] for t in templates]
                raise ValueError(f"Invalid template format. Available for {content_type}: {available_formats}")
        else:
            template = random.choice(templates)
        
        # Handle variables
        caption_text = template['template']
        variables_needed = template.get('variables', [])
        
        if custom_variables:
            # Use provided variables
            for var in variables_needed:
                if var in custom_variables:
                    caption_text = caption_text.replace(f'{{{var}}}', custom_variables[var])
        else:
            # Use example values or prompt for them
            if 'example' in template:
                return {
                    'caption': template['example'],
                    'format': template['format'],
                    'variables_needed': variables_needed,
                    'template': template['template']
                }
        
        return {
            'caption': caption_text,
            'format': template['format'],
            'variables_needed': variables_needed,
            'template': template['template']
        }
    
    def get_hashtags(self, content_type: str, platform: str, limit: Optional[int] = None) -> List[str]:
        """Get hashtags for specific content type and platform."""
        if content_type not in self.templates['content_types']:
            raise ValueError(f"Invalid content type. Available: {self.get_content_types()}")
        
        if platform not in self.get_platforms():
            raise ValueError(f"Invalid platform. Available: {self.get_platforms()}")
        
        content_config = self.templates['content_types'][content_type]
        hashtags = content_config['hashtags'].get(platform, [])
        
        if limit and limit < len(hashtags):
            # Randomize but keep first few as they're usually most important
            important_tags = hashtags[:3]  # Keep first 3 as core tags
            remaining_tags = hashtags[3:]
            random.shuffle(remaining_tags)
            hashtags = important_tags + remaining_tags[:limit-3]
        
        return hashtags
    
    def get_cta_variations(self, content_type: str) -> List[str]:
        """Get CTA variations for content type."""
        if content_type not in self.templates['content_types']:
            raise ValueError(f"Invalid content type. Available: {self.get_content_types()}")
        
        return self.templates['content_types'][content_type]['cta_variations']
    
    def get_platform_optimization(self, platform: str) -> Dict:
        """Get platform-specific optimization guidelines."""
        if platform not in self.get_platforms():
            raise ValueError(f"Invalid platform. Available: {self.get_platforms()}")
        
        return self.templates['platform_optimizations'][platform]
    
    def interactive_caption_builder(self, content_type: str, template_format: Optional[str] = None) -> Dict:
        """Interactive mode to build custom caption with variable prompts."""
        content_config = self.templates['content_types'][content_type]
        templates = content_config['caption_templates']
        
        # Select template
        if template_format:
            template = next((t for t in templates if t['format'] == template_format), None)
            if not template:
                available_formats = [t['format'] for t in templates]
                raise ValueError(f"Invalid template format. Available for {content_type}: {available_formats}")
        else:
            print(f"\n📝 Available template formats for {content_type}:")
            for i, t in enumerate(templates, 1):
                print(f"  {i}. {t['format']}")
            
            while True:
                try:
                    choice = input(f"\nSelect template (1-{len(templates)}): ").strip()
                    template = templates[int(choice) - 1]
                    break
                except (ValueError, IndexError):
                    print("Invalid choice. Please enter a number from the list.")
        
        # Get variables
        variables_needed = template.get('variables', [])
        custom_variables = {}
        
        if variables_needed:
            print(f"\n✍️  Fill in the template variables for '{template['format']}' format:")
            print(f"Example: {template.get('example', 'No example available')}")
            print(f"\nTemplate: {template['template']}")
            print("\nEnter values for each variable:")
            
            for var in variables_needed:
                value = input(f"  {var}: ").strip()
                if value:
                    custom_variables[var] = value
        
        return self.generate_caption(content_type, template['format'], custom_variables)

def main():
    parser = argparse.ArgumentParser(
        description="Generate authentic captions and hashtags for Kiin content",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Quick generation with example caption
    python caption_generator.py --content-type validation --platform tiktok
    
    # Interactive mode with custom variables
    python caption_generator.py --content-type confessions --platform instagram --custom
    
    # Generate multiple options
    python caption_generator.py --content-type tips --platform youtube --count 3
    
    # List all available options
    python caption_generator.py --list
        """
    )
    
    parser.add_argument(
        '--content-type', 
        choices=['validation', 'confessions', 'tips', 'sandwich', 'chaos'],
        help='Type of content to generate caption for'
    )
    
    parser.add_argument(
        '--platform',
        choices=['tiktok', 'instagram', 'youtube'],
        help='Platform to optimize for'
    )
    
    parser.add_argument(
        '--template-format',
        help='Specific template format to use (e.g., personal_story_lead, wisdom_share)'
    )
    
    parser.add_argument(
        '--custom',
        action='store_true',
        help='Interactive mode to customize variables'
    )
    
    parser.add_argument(
        '--count',
        type=int,
        default=1,
        help='Number of caption variations to generate (default: 1)'
    )
    
    parser.add_argument(
        '--hashtag-limit',
        type=int,
        help='Limit number of hashtags (useful for platforms with limits)'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available content types and formats'
    )
    
    parser.add_argument(
        '--config',
        help='Path to custom templates config file'
    )
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = CaptionGenerator(args.config)
    
    # Handle list request
    if args.list:
        print("🎯 Available Content Types:")
        for content_type in generator.get_content_types():
            content_config = generator.templates['content_types'][content_type]
            print(f"\n  📂 {content_type}")
            print(f"     Description: {content_config['description']}")
            print(f"     Template formats:")
            for template in content_config['caption_templates']:
                print(f"       • {template['format']}")
        
        print(f"\n📱 Available Platforms: {', '.join(generator.get_platforms())}")
        return
    
    # Validate required arguments
    if not args.content_type:
        print("❌ Error: --content-type is required (use --list to see options)")
        sys.exit(1)
    
    if not args.platform and not args.custom:
        print("❌ Error: --platform is required (use --list to see options)")
        sys.exit(1)
    
    try:
        print(f"🎨 Generating {args.content_type} content" + (f" for {args.platform}" if args.platform else ""))
        print("=" * 50)
        
        # Generate captions
        for i in range(args.count):
            if args.count > 1:
                print(f"\n📝 Option {i + 1}:")
                print("-" * 20)
            
            # Generate caption
            if args.custom:
                result = generator.interactive_caption_builder(args.content_type, args.template_format)
            else:
                result = generator.generate_caption(args.content_type, args.template_format)
            
            print(f"\n✨ Caption ({result['format']} format):")
            print(result['caption'])
            
            # Generate hashtags if platform specified
            if args.platform:
                hashtags = generator.get_hashtags(args.content_type, args.platform, args.hashtag_limit)
                print(f"\n🏷️  Hashtags for {args.platform}:")
                print(' '.join(hashtags))
                
                # Show platform optimization tips
                platform_opts = generator.get_platform_optimization(args.platform)
                print(f"\n💡 {args.platform.title()} Optimization Tips:")
                for key, value in platform_opts.items():
                    if key != 'content_notes':
                        print(f"   • {key.replace('_', ' ').title()}: {value}")
            
            # Show CTA variations
            cta_variations = generator.get_cta_variations(args.content_type)
            print(f"\n📢 Alternative CTAs:")
            for j, cta in enumerate(random.sample(cta_variations, min(3, len(cta_variations))), 1):
                print(f"   {j}. {cta}")
            
            print("\n" + "=" * 50)
        
        # Show copy-paste ready version
        if not args.custom and args.platform:
            print("\n📋 COPY-PASTE READY:")
            print("-" * 20)
            final_result = generator.generate_caption(args.content_type, args.template_format)
            final_hashtags = generator.get_hashtags(args.content_type, args.platform, args.hashtag_limit)
            
            print(final_result['caption'])
            print()
            print(' '.join(final_hashtags))
            print()
            print("✅ Ready to post!")
    
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()