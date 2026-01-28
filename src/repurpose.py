#!/usr/bin/env python3
"""
Content Repurposing System
-------------------------
Turn one piece of content into multiple formats for different platforms.

Usage Examples:
    # Video to multiple formats
    python repurpose.py --input video.mp4 --all
    
    # Carousel to video
    python repurpose.py --carousel ./carousels/topic/ --to-video
    
    # Quote to multiple formats
    python repurpose.py --quote "Your text" --all
    
    # Extract transcript
    python repurpose.py --extract-text --input video.mp4
"""

import argparse
import os
import sys
import json
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ContentRepurposer:
    """Main class for content repurposing functionality."""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Platform dimensions
        self.dimensions = {
            'square': (1080, 1080),    # Instagram feed
            'story': (1080, 1920),     # Instagram/TikTok stories  
            'landscape': (1920, 1080), # YouTube
            'portrait': (1080, 1350),  # Instagram portrait
            'thumbnail': (1280, 720),  # YouTube thumbnail
            'card': (1080, 1080),     # Quote card
        }
        
        # Brand colors (can be customized)
        self.brand_colors = {
            'primary': '#2E3440',    # Dark blue-gray
            'secondary': '#5E81AC',  # Blue
            'accent': '#88C0D0',     # Light blue
            'success': '#A3BE8C',    # Green
            'warning': '#EBCB8B',    # Yellow
            'error': '#BF616A',      # Red
            'text': '#ECEFF4',       # Light gray
            'background': '#3B4252'  # Medium gray
        }

    def extract_audio_from_video(self, video_path: str) -> str:
        """Extract audio from video file."""
        video_path = Path(video_path)
        audio_path = self.output_dir / f"{video_path.stem}_audio.wav"
        
        cmd = [
            'ffmpeg', '-y', '-i', str(video_path),
            '-vn', '-acodec', 'pcm_s16le', '-ar', '16000',
            str(audio_path)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Audio extracted to: {audio_path}")
            return str(audio_path)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to extract audio: {e}")
            return None

    def transcribe_audio(self, audio_path: str) -> str:
        """Transcribe audio to text using whisper."""
        try:
            import whisper
            model = whisper.load_model("base")
            result = model.transcribe(audio_path)
            return result["text"].strip()
        except ImportError:
            logger.warning("Whisper not installed. Using placeholder transcript.")
            return "Transcript unavailable - install whisper: pip install openai-whisper"
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return "Transcription failed"

    def generate_caption_from_transcript(self, transcript: str, max_length: int = 2200) -> str:
        """Generate social media caption from transcript."""
        # Simple caption generation - can be enhanced with AI
        lines = transcript.split('.')
        
        # Take first few sentences that fit within limit
        caption_parts = []
        current_length = 0
        
        for line in lines[:3]:  # Max 3 sentences
            line = line.strip()
            if not line:
                continue
                
            if current_length + len(line) < max_length - 50:  # Leave room for hashtags
                caption_parts.append(line)
                current_length += len(line)
            else:
                break
        
        caption = '. '.join(caption_parts)
        if not caption.endswith('.'):
            caption += '.'
            
        # Add engagement hooks
        hooks = [
            "\n\n💭 What's your experience with this?",
            "\n\n🤔 Have you tried this approach?",
            "\n\n📝 Share your thoughts in the comments!",
            "\n\n💡 Which tip resonates most with you?"
        ]
        
        import random
        caption += random.choice(hooks)
        
        # Add hashtags
        caption += "\n\n#selfcare #mentalhealth #wellbeing #mindfulness #growth"
        
        return caption

    def extract_key_quote(self, transcript: str) -> str:
        """Extract a key quote from transcript."""
        sentences = [s.strip() for s in transcript.split('.') if s.strip()]
        
        # Simple heuristic: find shorter, impactful sentences
        candidates = []
        for sentence in sentences:
            word_count = len(sentence.split())
            if 5 <= word_count <= 20:  # Good quote length
                # Prefer sentences with emotional or action words
                power_words = ['transform', 'change', 'growth', 'journey', 'discover', 
                             'overcome', 'strength', 'heal', 'empowered', 'breakthrough']
                
                score = sum(1 for word in power_words if word.lower() in sentence.lower())
                candidates.append((sentence, score, word_count))
        
        if candidates:
            # Sort by score, then by length (shorter preferred)
            candidates.sort(key=lambda x: (-x[1], x[2]))
            return candidates[0][0]
        
        # Fallback: return first sentence if no good candidates
        return sentences[0] if sentences else "Transform your mindset"

    def resize_video_to_format(self, input_path: str, output_path: str, 
                              target_format: str, crop_mode: str = "center") -> bool:
        """Resize video to target format."""
        target_width, target_height = self.dimensions[target_format]
        
        # Get input video info
        cap = cv2.VideoCapture(input_path)
        input_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        input_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        
        # Calculate crop parameters
        input_aspect = input_width / input_height
        target_aspect = target_width / target_height
        
        if crop_mode == "center":
            if input_aspect > target_aspect:
                # Input is wider - crop width
                new_width = int(input_height * target_aspect)
                crop_x = (input_width - new_width) // 2
                crop_y = 0
                crop_w = new_width
                crop_h = input_height
            else:
                # Input is taller - crop height
                new_height = int(input_width / target_aspect)
                crop_x = 0
                crop_y = (input_height - new_height) // 2
                crop_w = input_width
                crop_h = new_height
        else:
            # For now, just use center crop
            crop_x, crop_y, crop_w, crop_h = 0, 0, input_width, input_height
        
        # Build ffmpeg command
        cmd = [
            'ffmpeg', '-y', '-i', input_path,
            '-vf', f'crop={crop_w}:{crop_h}:{crop_x}:{crop_y},scale={target_width}:{target_height}',
            '-c:a', 'copy',
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Video resized to {target_format}: {output_path}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to resize video: {e}")
            return False

    def generate_thumbnail(self, video_path: str, output_path: str, timestamp: float = 2.0) -> bool:
        """Generate thumbnail from video at specified timestamp."""
        cmd = [
            'ffmpeg', '-y', '-i', video_path,
            '-ss', str(timestamp), '-vframes', '1',
            '-vf', f"scale={self.dimensions['thumbnail'][0]}:{self.dimensions['thumbnail'][1]}",
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Thumbnail generated: {output_path}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to generate thumbnail: {e}")
            return False

    def create_quote_card(self, quote: str, output_path: str, format_type: str = 'square') -> bool:
        """Create a quote card image."""
        width, height = self.dimensions[format_type]
        
        # Create image with gradient background
        img = Image.new('RGB', (width, height), self.brand_colors['background'])
        draw = ImageDraw.Draw(img)
        
        # Add gradient effect
        for i in range(height):
            alpha = i / height
            color = self._blend_colors(self.brand_colors['background'], 
                                     self.brand_colors['primary'], alpha)
            draw.line([(0, i), (width, i)], fill=color)
        
        # Load fonts (fallback to default if custom not available)
        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Arial Bold.ttf", 
                                          int(width * 0.08))
            quote_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 
                                          int(width * 0.05))
        except:
            title_font = ImageFont.load_default()
            quote_font = ImageFont.load_default()
        
        # Add quote text with word wrapping
        quote_lines = self._wrap_text(quote, quote_font, width * 0.8)
        
        # Calculate total text height
        bbox = quote_font.getbbox("Ag")
        line_height = (bbox[3] - bbox[1]) * 1.4
        total_height = len(quote_lines) * line_height
        
        # Start position (centered vertically)
        y_start = (height - total_height) // 2
        
        # Draw quote lines
        for i, line in enumerate(quote_lines):
            bbox = quote_font.getbbox(line)
            line_width = bbox[2] - bbox[0]
            x = (width - line_width) // 2
            y = y_start + i * line_height
            
            # Add text shadow
            draw.text((x+3, y+3), line, font=quote_font, fill='#000000')
            draw.text((x, y), line, font=quote_font, fill=self.brand_colors['text'])
        
        # Add decorative elements
        self._add_quote_decorations(draw, width, height)
        
        # Save image
        img.save(output_path, quality=95)
        logger.info(f"Quote card created: {output_path}")
        return True

    def _blend_colors(self, color1: str, color2: str, alpha: float) -> str:
        """Blend two hex colors."""
        def hex_to_rgb(hex_color):
            return tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))
        
        def rgb_to_hex(rgb):
            return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        
        rgb1 = hex_to_rgb(color1)
        rgb2 = hex_to_rgb(color2)
        
        blended = tuple(int(rgb1[i] * (1 - alpha) + rgb2[i] * alpha) for i in range(3))
        return rgb_to_hex(blended)

    def _wrap_text(self, text: str, font, max_width: float) -> List[str]:
        """Wrap text to fit within specified width."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            line_text = ' '.join(current_line)
            
            bbox = font.getbbox(line_text)
            if (bbox[2] - bbox[0]) > max_width:
                if len(current_line) > 1:
                    current_line.pop()
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Single word is too long, just add it
                    lines.append(word)
                    current_line = []
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines

    def _add_quote_decorations(self, draw, width: int, height: int):
        """Add decorative elements to quote card."""
        # Add quote marks
        quote_size = int(width * 0.15)
        draw.text((width * 0.1, height * 0.15), '"', 
                 font=ImageFont.load_default(), fill=self.brand_colors['accent'])
        
        # Add subtle border
        border_width = 3
        draw.rectangle([border_width, border_width, 
                       width - border_width, height - border_width], 
                      outline=self.brand_colors['accent'], width=border_width)

    def create_carousel_video(self, carousel_dir: str, output_path: str) -> bool:
        """Convert carousel images to animated video."""
        carousel_path = Path(carousel_dir)
        
        # Get all images from carousel directory
        image_files = []
        for ext in ['*.png', '*.jpg', '*.jpeg']:
            image_files.extend(carousel_path.glob(ext))
        
        if not image_files:
            logger.error(f"No images found in {carousel_dir}")
            return False
        
        # Sort images naturally
        image_files.sort(key=lambda x: x.name)
        
        # Create temporary directory for processed images
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Resize all images to consistent size
            target_size = self.dimensions['square']
            processed_files = []
            
            for i, img_file in enumerate(image_files):
                # Load and resize image
                img = Image.open(img_file)
                img = ImageOps.fit(img, target_size, Image.Resampling.LANCZOS)
                
                # Save processed image
                processed_file = temp_path / f"frame_{i:03d}.png"
                img.save(processed_file)
                processed_files.append(processed_file)
            
            # Create video from images
            duration_per_slide = 3  # seconds
            cmd = [
                'ffmpeg', '-y',
                '-framerate', f'1/{duration_per_slide}',
                '-pattern_type', 'glob',
                '-i', str(temp_path / 'frame_*.png'),
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-r', '30',
                output_path
            ]
            
            try:
                subprocess.run(cmd, check=True, capture_output=True)
                logger.info(f"Carousel video created: {output_path}")
                return True
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to create carousel video: {e}")
                return False

    def process_video_to_all_formats(self, input_video: str) -> Dict[str, str]:
        """Process video to all platform formats."""
        video_path = Path(input_video)
        basename = video_path.stem
        results = {}
        
        # Extract audio for transcription
        audio_path = self.extract_audio_from_video(input_video)
        transcript = ""
        
        if audio_path:
            transcript = self.transcribe_audio(audio_path)
            
            # Save transcript
            transcript_path = self.output_dir / f"{basename}_transcript.txt"
            with open(transcript_path, 'w') as f:
                f.write(transcript)
            results['transcript'] = str(transcript_path)
            
            # Generate caption
            caption = self.generate_caption_from_transcript(transcript)
            caption_path = self.output_dir / f"{basename}_caption.txt"
            with open(caption_path, 'w') as f:
                f.write(caption)
            results['caption'] = str(caption_path)
        
        # Create video formats
        formats_to_create = ['square', 'story']
        for format_name in formats_to_create:
            output_path = self.output_dir / f"{basename}_{format_name}.mp4"
            if self.resize_video_to_format(input_video, str(output_path), format_name):
                results[format_name] = str(output_path)
        
        # Generate thumbnail
        thumbnail_path = self.output_dir / f"{basename}_thumbnail.png"
        if self.generate_thumbnail(input_video, str(thumbnail_path)):
            results['thumbnail'] = str(thumbnail_path)
        
        # Create quote card if transcript available
        if transcript:
            key_quote = self.extract_key_quote(transcript)
            quote_card_path = self.output_dir / f"{basename}_quote_card.png"
            if self.create_quote_card(key_quote, str(quote_card_path)):
                results['quote_card'] = str(quote_card_path)
        
        return results

    def process_quote_to_all_formats(self, quote: str, filename_base: str = "quote") -> Dict[str, str]:
        """Process quote to multiple formats."""
        results = {}
        
        # Create quote cards in different formats
        for format_name in ['square', 'story']:
            output_path = self.output_dir / f"{filename_base}_{format_name}.png"
            if self.create_quote_card(quote, str(output_path), format_name):
                results[f'{format_name}_card'] = str(output_path)
        
        # Create simple animated video of quote
        square_card_path = self.output_dir / f"{filename_base}_square.png"
        if square_card_path.exists():
            video_path = self.output_dir / f"{filename_base}_video.mp4"
            if self._create_static_video(str(square_card_path), str(video_path)):
                results['video'] = str(video_path)
        
        # Generate caption for quote
        caption = f'"{quote}"\n\n💭 What does this mean to you?\n\n#inspiration #quotes #mindset #growth #reflection'
        caption_path = self.output_dir / f"{filename_base}_caption.txt"
        with open(caption_path, 'w') as f:
            f.write(caption)
        results['caption'] = str(caption_path)
        
        return results

    def _create_static_video(self, image_path: str, output_path: str, duration: int = 10) -> bool:
        """Create a video from a static image."""
        cmd = [
            'ffmpeg', '-y',
            '-loop', '1',
            '-i', image_path,
            '-t', str(duration),
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-r', '30',
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Static video created: {output_path}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create static video: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="Content Repurposing Tool")
    parser.add_argument('--input', help='Input video file path')
    parser.add_argument('--carousel', help='Carousel directory path')
    parser.add_argument('--quote', help='Quote text to process')
    parser.add_argument('--extract-text', action='store_true', help='Extract text only')
    parser.add_argument('--all', action='store_true', help='Generate all formats')
    parser.add_argument('--to-video', action='store_true', help='Convert carousel to video')
    parser.add_argument('--output-dir', default='output', help='Output directory')
    
    args = parser.parse_args()
    
    if not any([args.input, args.carousel, args.quote]):
        parser.print_help()
        sys.exit(1)
    
    # Initialize repurposer
    repurposer = ContentRepurposer(args.output_dir)
    
    try:
        if args.input and args.extract_text:
            # Extract text only
            audio_path = repurposer.extract_audio_from_video(args.input)
            if audio_path:
                transcript = repurposer.transcribe_audio(audio_path)
                output_path = repurposer.output_dir / f"{Path(args.input).stem}_transcript.txt"
                with open(output_path, 'w') as f:
                    f.write(transcript)
                print(f"Transcript saved to: {output_path}")
                
        elif args.input and args.all:
            # Process video to all formats
            results = repurposer.process_video_to_all_formats(args.input)
            print("Generated files:")
            for format_type, path in results.items():
                print(f"  {format_type}: {path}")
                
        elif args.carousel and args.to_video:
            # Convert carousel to video
            output_path = repurposer.output_dir / f"{Path(args.carousel).name}_video.mp4"
            if repurposer.create_carousel_video(args.carousel, str(output_path)):
                print(f"Carousel video created: {output_path}")
                
        elif args.quote and args.all:
            # Process quote to all formats
            results = repurposer.process_quote_to_all_formats(args.quote)
            print("Generated files:")
            for format_type, path in results.items():
                print(f"  {format_type}: {path}")
                
        else:
            print("Invalid argument combination. Use --help for usage information.")
            
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()