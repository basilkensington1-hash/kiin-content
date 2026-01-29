#!/usr/bin/env python3
"""
Kiin Content Factory - Template Generator
Generates content templates based on input parameters.
"""

import json
import os
import random
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class TemplateRequest:
    """Template generation request parameters"""
    content_type: str  # video, social, caption, email, document
    category: str      # confession, tips, story, quote, data
    platform: str      # instagram_post, tiktok, youtube, etc.
    mood: str         # hope, comfort, energy, calm, urgency
    duration: Optional[str] = None
    custom_params: Optional[Dict[str, Any]] = None

class TemplateGenerator:
    def __init__(self, base_path: str = "/Users/nick/clawd/kiin-content"):
        self.base_path = Path(base_path)
        self.templates_path = self.base_path / "templates"
        self.brand_path = self.base_path / "brand"
        
        # Load brand configuration
        self.brand_config = self._load_brand_config()
        
    def _load_brand_config(self) -> Dict[str, Any]:
        """Load the enhanced brand configuration"""
        brand_file = self.brand_path / "brand_config_enhanced.json"
        if brand_file.exists():
            with open(brand_file, 'r') as f:
                return json.load(f)
        
        # Fallback to basic config
        basic_file = self.brand_path / "brand_config.json"
        with open(basic_file, 'r') as f:
            return json.load(f)
    
    def get_available_templates(self, content_type: str = None) -> Dict[str, List[str]]:
        """Get all available templates organized by type"""
        templates = {}
        
        template_dirs = [
            "video", "social", "captions", "email", "docs"
        ]
        
        for template_dir in template_dirs:
            if content_type and template_dir != content_type:
                continue
                
            dir_path = self.templates_path / template_dir
            if dir_path.exists():
                templates[template_dir] = []
                
                # Walk through subdirectories to find JSON templates
                for subdir in dir_path.rglob("*.json"):
                    relative_path = subdir.relative_to(dir_path)
                    templates[template_dir].append(str(relative_path))
        
        return templates
    
    def generate_template(self, request: TemplateRequest) -> Dict[str, Any]:
        """Generate a template based on the request"""
        
        # Find matching templates
        matching_templates = self._find_matching_templates(request)
        
        if not matching_templates:
            return self._create_default_template(request)
        
        # Select best matching template
        base_template = self._select_best_template(matching_templates, request)
        
        # Customize template for specific request
        customized_template = self._customize_template(base_template, request)
        
        return customized_template
    
    def _find_matching_templates(self, request: TemplateRequest) -> List[Dict[str, Any]]:
        """Find templates that match the request criteria"""
        matching_templates = []
        
        # Build search path
        if request.content_type == "video":
            search_path = self.templates_path / "video" / request.category
        elif request.content_type == "social":
            search_path = self.templates_path / "social" / request.platform
        elif request.content_type == "caption":
            search_path = self.templates_path / "captions"
        elif request.content_type == "email":
            search_path = self.templates_path / "email"
        else:
            return []
        
        if not search_path.exists():
            return []
        
        # Load matching templates
        for template_file in search_path.glob("*.json"):
            try:
                with open(template_file, 'r') as f:
                    template_data = json.load(f)
                    template_data['_source_file'] = str(template_file)
                    
                    # Check if template matches mood
                    if hasattr(template_data, 'emotional_tone'):
                        if template_data.get('emotional_tone') == request.mood:
                            matching_templates.append(template_data)
                        elif request.mood in str(template_data):
                            matching_templates.append(template_data)
                    else:
                        matching_templates.append(template_data)
                        
            except json.JSONDecodeError:
                continue
        
        return matching_templates
    
    def _select_best_template(self, templates: List[Dict[str, Any]], request: TemplateRequest) -> Dict[str, Any]:
        """Select the best matching template from candidates"""
        
        # Score templates based on match quality
        scored_templates = []
        
        for template in templates:
            score = 0
            
            # Exact mood match
            if template.get('emotional_tone') == request.mood:
                score += 10
            
            # Category match
            if template.get('category') == request.category:
                score += 15
            
            # Platform match
            if template.get('platform') == request.platform:
                score += 15
            
            # Duration match (if specified)
            if request.duration and template.get('duration'):
                # Simple duration matching logic
                if request.duration in template.get('duration', ''):
                    score += 5
            
            scored_templates.append((score, template))
        
        # Return highest scoring template
        if scored_templates:
            scored_templates.sort(key=lambda x: x[0], reverse=True)
            return scored_templates[0][1]
        
        # Fallback to first template
        return templates[0] if templates else {}
    
    def _customize_template(self, template: Dict[str, Any], request: TemplateRequest) -> Dict[str, Any]:
        """Customize template based on specific request parameters"""
        
        customized = template.copy()
        
        # Apply mood-specific customizations
        if request.mood in self.brand_config.get('colors', {}).get('emotional_palettes', {}):
            mood_colors = self.brand_config['colors']['emotional_palettes'][request.mood]
            
            # Update color scheme if template has one
            if 'color_scheme' in customized:
                customized['color_scheme'].update(mood_colors)
        
        # Apply custom parameters
        if request.custom_params:
            for key, value in request.custom_params.items():
                if key in customized:
                    if isinstance(customized[key], dict) and isinstance(value, dict):
                        customized[key].update(value)
                    else:
                        customized[key] = value
        
        # Add generation metadata
        customized['_generation_info'] = {
            'request': request.__dict__,
            'generated_from': template.get('_source_file', 'unknown'),
            'mood_applied': request.mood,
            'customizations_applied': bool(request.custom_params)
        }
        
        return customized
    
    def _create_default_template(self, request: TemplateRequest) -> Dict[str, Any]:
        """Create a default template when no matches found"""
        
        # Get mood colors
        mood_colors = self.brand_config.get('colors', {}).get('emotional_palettes', {}).get(
            request.mood, self.brand_config.get('colors', {})
        )
        
        default_template = {
            "template_name": f"Generated {request.category.title()} Template",
            "content_type": request.content_type,
            "category": request.category,
            "emotional_tone": request.mood,
            "color_scheme": mood_colors,
            "font_pairings": self.brand_config.get('typography', {}),
            "brand_guidelines": self.brand_config.get('voice', {}),
            "_generation_info": {
                "type": "default_generated",
                "request": request.__dict__,
                "note": "No matching template found, created default"
            }
        }
        
        return default_template
    
    def save_generated_template(self, template: Dict[str, Any], output_path: str = None) -> str:
        """Save generated template to file"""
        
        if not output_path:
            # Generate filename based on template properties
            name_parts = [
                template.get('content_type', 'template'),
                template.get('category', ''),
                template.get('emotional_tone', ''),
                'generated'
            ]
            filename = '_'.join(filter(None, name_parts)) + '.json'
            output_path = self.templates_path / "generated" / filename
        
        # Ensure directory exists
        os.makedirs(output_path.parent, exist_ok=True)
        
        # Save template
        with open(output_path, 'w') as f:
            json.dump(template, f, indent=2)
        
        return str(output_path)

def main():
    """Command line interface for template generator"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate Kiin content templates')
    parser.add_argument('--content-type', required=False, 
                       choices=['video', 'social', 'caption', 'email', 'document'],
                       help='Type of content template to generate')
    parser.add_argument('--category', 
                       choices=['confession', 'tips', 'story', 'quote', 'data'],
                       help='Content category (for video templates)')
    parser.add_argument('--platform',
                       choices=['instagram_post', 'instagram_story', 'tiktok', 'youtube', 'linkedin'],
                       help='Social media platform (for social templates)')
    parser.add_argument('--mood', required=False,
                       choices=['hope', 'comfort', 'energy', 'calm', 'urgency'],
                       help='Emotional tone for the template')
    parser.add_argument('--duration', help='Duration for video templates (e.g., "15-30s")')
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--list-templates', action='store_true',
                       help='List all available templates')
    
    args = parser.parse_args()
    
    generator = TemplateGenerator()
    
    if args.list_templates:
        templates = generator.get_available_templates()
        print("Available templates:")
        for content_type, template_list in templates.items():
            print(f"\n{content_type.title()}:")
            for template in template_list:
                print(f"  - {template}")
        return
    
    # Validate required arguments for generation
    if not args.content_type or not args.mood:
        parser.error("--content-type and --mood are required for template generation")
    
    # Create request
    request = TemplateRequest(
        content_type=args.content_type,
        category=args.category or '',
        platform=args.platform or '',
        mood=args.mood,
        duration=args.duration
    )
    
    # Generate template
    template = generator.generate_template(request)
    
    # Save or print
    if args.output:
        saved_path = generator.save_generated_template(template, args.output)
        print(f"Template saved to: {saved_path}")
    else:
        print(json.dumps(template, indent=2))

if __name__ == "__main__":
    main()