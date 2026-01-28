#!/usr/bin/env python3
"""
FAQ Video Generator

Generate quick FAQ videos (15-30 seconds) for common caregiver questions.
Clean, helpful format with text-to-speech narration.
"""

import json
import argparse
import os
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
import tempfile

class FAQVideoGenerator:
    def __init__(self, config_path: Optional[str] = None):
        """Initialize with FAQ data."""
        if config_path is None:
            # Default to config directory relative to this script
            script_dir = Path(__file__).parent
            config_path = script_dir.parent / "config" / "faqs.json"
        
        self.config_path = Path(config_path)
        self.faqs_data = self.load_faqs()
        
    def load_faqs(self) -> Dict:
        """Load FAQ data from JSON config."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ FAQ file not found: {self.config_path}")
            print("💡 Make sure faqs.json exists in the config directory")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing FAQ file: {e}")
            return {}
    
    def get_faq_by_id(self, faq_id: int) -> Optional[Dict]:
        """Get FAQ by ID number."""
        if 'faqs' not in self.faqs_data:
            return None
        
        for faq in self.faqs_data['faqs']:
            if faq['id'] == faq_id:
                return faq
        return None
    
    def search_faqs(self, query: str) -> List[Dict]:
        """Search FAQs by keyword or topic."""
        if 'faqs' not in self.faqs_data:
            return []
        
        query_lower = query.lower()
        matches = []
        
        for faq in self.faqs_data['faqs']:
            # Search in question, answer, category, and keywords
            if (query_lower in faq['question'].lower() or 
                query_lower in faq['answer'].lower() or
                query_lower in faq['category'].lower() or
                any(query_lower in keyword.lower() for keyword in faq.get('keywords', []))):
                matches.append(faq)
        
        return matches
    
    def get_faqs_by_category(self, category: str) -> List[Dict]:
        """Get all FAQs in a specific category."""
        if 'faqs' not in self.faqs_data:
            return []
        
        return [faq for faq in self.faqs_data['faqs'] if faq['category'] == category]
    
    def create_video_script(self, faq: Dict) -> str:
        """Create video script from FAQ data."""
        question = faq['question']
        answer = faq['answer']
        
        # Format script for video
        script = f"""TITLE: FAQ #{faq['id']}

QUESTION: {question}

ANSWER: {answer}

DURATION: {faq['duration']} seconds
CATEGORY: {faq['category']}
"""
        return script
    
    def generate_text_overlay(self, faq: Dict, output_path: str) -> bool:
        """Generate simple text overlay video using ffmpeg."""
        try:
            # Create text content
            question_text = f"Q: {faq['question']}"
            answer_text = f"A: {faq['answer']}"
            
            # Split long lines for better readability
            def split_text(text, max_length=60):
                words = text.split()
                lines = []
                current_line = ""
                
                for word in words:
                    if len(current_line + " " + word) <= max_length:
                        current_line = current_line + " " + word if current_line else word
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = word
                
                if current_line:
                    lines.append(current_line)
                
                return "\\n".join(lines)
            
            question_formatted = split_text(question_text, 50)
            answer_formatted = split_text(answer_text, 45)
            
            # Calculate timing
            total_duration = faq['duration']
            question_duration = min(5, total_duration * 0.3)
            answer_duration = total_duration - question_duration
            
            # Create temporary text file for complex text overlay
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                temp_file.write(f"{question_formatted}\n\n{answer_formatted}")
                temp_text_file = temp_file.name
            
            # FFmpeg command for simple video with text overlay
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi', '-i', f'color=c=#2E4A62:s=1080x1920:d={total_duration}',
                '-vf', f"""
                drawtext=fontfile=/System/Library/Fonts/Arial.ttf:
                text='{question_formatted}':
                fontsize=48:fontcolor=white:x=(w-text_w)/2:y=300:
                enable='between(t,0,{question_duration})',
                drawtext=fontfile=/System/Library/Fonts/Arial.ttf:
                text='{answer_formatted}':
                fontsize=42:fontcolor=#F0F8FF:x=(w-text_w)/2:y=500:
                enable='between(t,{question_duration},{total_duration})',
                drawtext=fontfile=/System/Library/Fonts/Arial.ttf:
                text='FAQ #{faq["id"]} | {faq["category"]}':
                fontsize=32:fontcolor=#87CEEB:x=(w-text_w)/2:y=1700:
                enable='between(t,0,{total_duration})'
                """.replace('\n', '').replace(' ', ''),
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                '-r', '30', '-t', str(total_duration),
                str(output_path)
            ]
            
            # Run ffmpeg
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Clean up temp file
            os.unlink(temp_text_file)
            
            if result.returncode == 0:
                print(f"✅ Video created: {output_path}")
                return True
            else:
                print(f"❌ FFmpeg error: {result.stderr}")
                return False
                
        except FileNotFoundError:
            print("❌ FFmpeg not found. Please install FFmpeg to generate videos.")
            print("💡 On Mac: brew install ffmpeg")
            print("💡 On Ubuntu: sudo apt install ffmpeg")
            return False
        except Exception as e:
            print(f"❌ Error creating video: {e}")
            return False
    
    def generate_audio_script(self, faq: Dict) -> str:
        """Generate text-to-speech script."""
        return f"{faq['question']} {faq['answer']}"
    
    def create_faq_video(self, faq_id: int, output_path: str, format_type: str = 'simple') -> bool:
        """Create a single FAQ video."""
        faq = self.get_faq_by_id(faq_id)
        if not faq:
            print(f"❌ FAQ #{faq_id} not found")
            return False
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"🎬 Creating video for FAQ #{faq_id}: {faq['question']}")
        
        if format_type == 'simple':
            return self.generate_text_overlay(faq, output_path)
        else:
            # Future: could add more sophisticated video generation
            print(f"❌ Video format '{format_type}' not yet supported")
            return False
    
    def create_all_videos(self, output_dir: str, format_type: str = 'simple') -> int:
        """Create videos for all FAQs."""
        if 'faqs' not in self.faqs_data:
            print("❌ No FAQ data loaded")
            return 0
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        success_count = 0
        total_faqs = len(self.faqs_data['faqs'])
        
        print(f"🎬 Creating {total_faqs} FAQ videos in {output_dir}")
        
        for faq in self.faqs_data['faqs']:
            output_file = output_dir / f"faq_{faq['id']:02d}.mp4"
            if self.create_faq_video(faq['id'], output_file, format_type):
                success_count += 1
            else:
                print(f"⚠️ Failed to create video for FAQ #{faq['id']}")
        
        print(f"🎉 Successfully created {success_count}/{total_faqs} videos")
        return success_count
    
    def list_faqs(self) -> None:
        """List all available FAQs."""
        if 'faqs' not in self.faqs_data:
            print("❌ No FAQ data loaded")
            return
        
        categories = self.faqs_data.get('categories', {})
        
        print("📋 Available FAQs:\n")
        
        current_category = None
        for faq in sorted(self.faqs_data['faqs'], key=lambda x: (x['category'], x['id'])):
            if faq['category'] != current_category:
                current_category = faq['category']
                category_desc = categories.get(current_category, current_category)
                print(f"\n🔸 {current_category.upper()} - {category_desc}")
                print("─" * 60)
            
            duration_badge = f"({faq['duration']}s)"
            print(f"  {faq['id']:2d}. {faq['question']} {duration_badge}")

def main():
    parser = argparse.ArgumentParser(
        description="Generate quick FAQ videos for caregiver questions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --question 1 --output faq_1.mp4
  %(prog)s --all --output-dir ./faqs/
  %(prog)s --category medication --output-dir ./medication_faqs/
  %(prog)s --search "medication" --output-dir ./search_results/
  %(prog)s --list
        """
    )
    
    parser.add_argument('--question', type=int, help='FAQ ID number to generate video for')
    parser.add_argument('--output', help='Output video file path')
    parser.add_argument('--output-dir', help='Output directory for multiple videos')
    parser.add_argument('--all', action='store_true', help='Generate videos for all FAQs')
    parser.add_argument('--category', help='Generate videos for specific category')
    parser.add_argument('--search', help='Search and generate videos for matching FAQs')
    parser.add_argument('--list', action='store_true', help='List all available FAQs')
    parser.add_argument('--format', default='simple', choices=['simple'], 
                       help='Video format type (currently only simple)')
    parser.add_argument('--config', help='Path to custom FAQs JSON file')
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = FAQVideoGenerator(args.config)
    
    if not generator.faqs_data:
        return 1
    
    # List FAQs
    if args.list:
        generator.list_faqs()
        return 0
    
    # Single FAQ video
    if args.question:
        if not args.output:
            args.output = f"faq_{args.question}.mp4"
        
        if generator.create_faq_video(args.question, args.output, args.format):
            return 0
        else:
            return 1
    
    # Multiple videos
    if args.all or args.category or args.search:
        if not args.output_dir:
            args.output_dir = './faqs'
        
        if args.all:
            generator.create_all_videos(args.output_dir, args.format)
        elif args.category:
            faqs = generator.get_faqs_by_category(args.category)
            if not faqs:
                print(f"❌ No FAQs found in category '{args.category}'")
                return 1
            
            print(f"🎬 Creating videos for {len(faqs)} FAQs in category '{args.category}'")
            success_count = 0
            for faq in faqs:
                output_file = Path(args.output_dir) / f"faq_{faq['id']:02d}.mp4"
                if generator.create_faq_video(faq['id'], output_file, args.format):
                    success_count += 1
            
            print(f"🎉 Successfully created {success_count}/{len(faqs)} videos")
        
        elif args.search:
            faqs = generator.search_faqs(args.search)
            if not faqs:
                print(f"❌ No FAQs found matching '{args.search}'")
                return 1
            
            print(f"🎬 Creating videos for {len(faqs)} FAQs matching '{args.search}'")
            success_count = 0
            for faq in faqs:
                output_file = Path(args.output_dir) / f"faq_{faq['id']:02d}.mp4"
                if generator.create_faq_video(faq['id'], output_file, args.format):
                    success_count += 1
            
            print(f"🎉 Successfully created {success_count}/{len(faqs)} videos")
        
        return 0
    
    # No action specified
    parser.print_help()
    print(f"\n💡 Hint: Use --list to see available FAQs")
    return 1

if __name__ == '__main__':
    exit(main())