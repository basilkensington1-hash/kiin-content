#!/usr/bin/env python3
"""
Kiin Advanced Visual Effects Library
Professional-grade animations and effects for video generation
"""

import os
import math
import random
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union, Callable
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np

class AdvancedEffectsLibrary:
    """Professional-grade visual effects library for video content"""
    
    def __init__(self, width: int = 1080, height: int = 1920, fps: int = 30):
        self.width = width
        self.height = height
        self.fps = fps
        self.frame_time = 1.0 / fps
        
        # Cache for expensive operations
        self._font_cache = {}
        self._gradient_cache = {}
        self._noise_cache = {}
        
        # Professional color schemes
        self.color_schemes = {
            'warm': [(255, 200, 150), (255, 150, 100), (255, 100, 80)],
            'cool': [(150, 200, 255), (100, 150, 255), (80, 120, 255)],
            'sunset': [(255, 94, 77), (255, 154, 0), (255, 206, 84)],
            'ocean': [(64, 224, 208), (72, 61, 139), (25, 25, 112)],
            'forest': [(34, 139, 34), (107, 142, 35), (154, 205, 50)],
            'monochrome': [(64, 64, 64), (128, 128, 128), (192, 192, 192)],
            'vibrant': [(255, 0, 150), (0, 255, 150), (150, 0, 255)],
            'professional': [(41, 98, 255), (0, 184, 148), (255, 159, 67)]
        }

    # ==================== TEXT ANIMATIONS ====================
    
    def typewriter_effect(self, text: str, frame: int, total_frames: int, 
                         font: ImageFont.FreeTypeFont, color: Tuple[int, int, int],
                         position: Tuple[int, int], speed_curve: str = 'linear') -> Image.Image:
        """Create professional typewriter effect with variable timing"""
        image = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Apply speed curve
        if speed_curve == 'ease_in':
            progress = math.sin((frame / total_frames) * math.pi / 2)
        elif speed_curve == 'ease_out':
            progress = 1 - math.cos((frame / total_frames) * math.pi / 2)
        elif speed_curve == 'ease_in_out':
            progress = 0.5 * (1 - math.cos((frame / total_frames) * math.pi))
        else:  # linear
            progress = frame / total_frames
        
        # Calculate how many characters to show
        chars_to_show = int(len(text) * progress)
        visible_text = text[:chars_to_show]
        
        # Add blinking cursor for last 10% of animation
        if frame > total_frames * 0.9 and frame % 20 < 10:
            visible_text += '|'
        
        draw.text(position, visible_text, font=font, fill=color)
        return image
    
    def fade_in_words(self, text: str, frame: int, total_frames: int,
                     font: ImageFont.FreeTypeFont, color: Tuple[int, int, int],
                     position: Tuple[int, int], emphasis_words: List[str] = None) -> Image.Image:
        """Fade in text word by word with emphasis"""
        image = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        words = text.split()
        progress = frame / total_frames
        words_to_show = int(len(words) * progress)
        
        x, y = position
        line_height = font.getbbox('Ay')[3] * 1.5
        current_line_words = []
        lines = []
        
        # Wrap words into lines
        for word in words[:words_to_show + 1]:
            test_line = current_line_words + [word]
            test_text = ' '.join(test_line)
            bbox = font.getbbox(test_text)
            if bbox[2] - bbox[0] > self.width - x * 2:
                if current_line_words:
                    lines.append(current_line_words)
                    current_line_words = [word]
                else:
                    lines.append([word])
            else:
                current_line_words = test_line
        
        if current_line_words:
            lines.append(current_line_words)
        
        # Render each line with word-by-word fade
        current_word_index = 0
        for line_idx, line_words in enumerate(lines):
            line_y = y + line_idx * line_height
            line_x = x
            
            for word_idx, word in enumerate(line_words):
                if current_word_index < words_to_show:
                    # Fully visible
                    word_color = color
                elif current_word_index == words_to_show:
                    # Fading in
                    fade_progress = (progress * len(words)) - words_to_show
                    alpha = int(255 * fade_progress)
                    word_color = (*color[:3], alpha)
                else:
                    # Not yet visible
                    current_word_index += 1
                    continue
                
                # Emphasize certain words
                if emphasis_words and word.lower().strip('.,!?') in [w.lower() for w in emphasis_words]:
                    # Create glow effect for emphasized words
                    glow_image = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
                    glow_draw = ImageDraw.Draw(glow_image)
                    
                    # Draw multiple times with blur for glow
                    for offset in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
                        glow_draw.text((line_x + offset[0], line_y + offset[1]), word, 
                                     font=font, fill=(*color, 100))
                    
                    glow_image = glow_image.filter(ImageFilter.GaussianBlur(radius=1))
                    image.alpha_composite(glow_image)
                
                draw.text((line_x, line_y), word, font=font, fill=word_color)
                
                # Move to next word position
                word_bbox = font.getbbox(word)
                line_x += (word_bbox[2] - word_bbox[0]) + font.getbbox(' ')[2]
                current_word_index += 1
        
        return image
    
    def kinetic_typography(self, text: str, frame: int, total_frames: int,
                          font: ImageFont.FreeTypeFont, color: Tuple[int, int, int],
                          motion_path: str = 'wave') -> Image.Image:
        """Create kinetic typography with motion paths"""
        image = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Split into characters for individual animation
        chars = list(text)
        char_spacing = font.getbbox('M')[2] * 1.1
        
        # Calculate starting position to center text
        total_width = len(chars) * char_spacing
        start_x = (self.width - total_width) / 2
        center_y = self.height / 2
        
        for i, char in enumerate(chars):
            if char == ' ':
                continue
                
            # Character-specific timing
            char_delay = i * 0.1  # Stagger animation
            char_progress = max(0, min(1, (frame / total_frames - char_delay) / 0.8))
            
            if char_progress <= 0:
                continue
            
            char_x = start_x + i * char_spacing
            
            if motion_path == 'wave':
                # Wave motion
                wave_offset = math.sin((frame * 0.1) + (i * 0.5)) * 30
                char_y = center_y + wave_offset
                
            elif motion_path == 'bounce':
                # Bounce effect
                bounce_height = 100 * (1 - char_progress) * abs(math.sin(char_progress * math.pi * 3))
                char_y = center_y - bounce_height
                
            elif motion_path == 'spiral':
                # Spiral motion
                angle = char_progress * math.pi * 4 + i * 0.5
                radius = 50 * (1 - char_progress)
                char_x += math.cos(angle) * radius
                char_y = center_y + math.sin(angle) * radius
                
            elif motion_path == 'zoom':
                # Zoom in effect
                scale = 0.1 + 0.9 * char_progress
                char_font_size = int(font.size * scale)
                scaled_font = self._get_font(char_font_size)
                char_y = center_y
                
            else:  # 'slide' - default
                # Slide in from sides
                if i % 2 == 0:
                    char_x = -50 + (start_x + i * char_spacing + 50) * char_progress
                else:
                    char_x = self.width + 50 - (self.width + 50 - start_x - i * char_spacing) * char_progress
                char_y = center_y
            
            # Apply fade-in
            char_alpha = int(255 * char_progress)
            char_color = (*color[:3], char_alpha)
            
            # Draw character with motion
            current_font = scaled_font if motion_path == 'zoom' else font
            draw.text((char_x, char_y), char, font=current_font, fill=char_color, anchor='mm')
        
        return image
    
    def text_reveal_animation(self, text: str, frame: int, total_frames: int,
                            font: ImageFont.FreeTypeFont, color: Tuple[int, int, int],
                            position: Tuple[int, int], reveal_type: str = 'slide') -> Image.Image:
        """Create text reveal animations with multiple styles"""
        image = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        progress = frame / total_frames
        
        # Create text image
        text_img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_img)
        text_draw.text(position, text, font=font, fill=color)
        
        if reveal_type == 'slide':
            # Slide reveal
            reveal_x = int(self.width * progress)
            mask = Image.new('L', (self.width, self.height), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rectangle([0, 0, reveal_x, self.height], fill=255)
            
        elif reveal_type == 'circular':
            # Circular reveal from center
            center_x, center_y = self.width // 2, self.height // 2
            radius = int(max(self.width, self.height) * progress)
            mask = Image.new('L', (self.width, self.height), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse([center_x - radius, center_y - radius, 
                             center_x + radius, center_y + radius], fill=255)
            
        elif reveal_type == 'blinds':
            # Venetian blinds effect
            mask = Image.new('L', (self.width, self.height), 0)
            mask_draw = ImageDraw.Draw(mask)
            blind_height = 20
            blind_spacing = 40
            for y in range(0, self.height, blind_spacing):
                blind_width = int(self.width * progress)
                mask_draw.rectangle([0, y, blind_width, y + blind_height], fill=255)
                
        else:  # 'fade'
            # Simple fade
            alpha = int(255 * progress)
            alpha_layer = Image.new('RGBA', (self.width, self.height), (255, 255, 255, alpha))
            text_img.putalpha(ImageEnhance.Color(text_img.split()[-1]).enhance(progress))
            return text_img
        
        # Apply mask
        text_img.putalpha(mask)
        image.alpha_composite(text_img)
        
        return image
    
    def subtitle_popup_animation(self, text: str, frame: int, total_frames: int,
                               font: ImageFont.FreeTypeFont, color: Tuple[int, int, int],
                               bg_color: Tuple[int, int, int] = (0, 0, 0)) -> Image.Image:
        """Create subtitle-style pop-up animations"""
        image = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        progress = frame / total_frames
        
        # Split text into lines that fit
        lines = self._wrap_text_to_lines(text, font, self.width - 100)
        line_height = font.getbbox('Ay')[3] * 1.3
        total_text_height = len(lines) * line_height
        
        # Animation phases
        if progress < 0.2:
            # Slide up phase
            slide_progress = progress / 0.2
            y_offset = 100 * (1 - slide_progress)
            alpha = int(255 * slide_progress)
        elif progress > 0.8:
            # Fade out phase
            fade_progress = (progress - 0.8) / 0.2
            y_offset = 0
            alpha = int(255 * (1 - fade_progress))
        else:
            # Hold phase
            y_offset = 0
            alpha = 255
        
        # Position subtitles at bottom
        start_y = self.height - total_text_height - 100 + y_offset
        
        for i, line in enumerate(lines):
            line_y = start_y + i * line_height
            
            # Get text dimensions for background
            bbox = font.getbbox(line)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Center text
            text_x = (self.width - text_width) // 2
            
            # Draw background with rounded corners
            bg_padding = 20
            bg_rect = [
                text_x - bg_padding,
                line_y - bg_padding // 2,
                text_x + text_width + bg_padding,
                line_y + text_height + bg_padding // 2
            ]
            
            # Create rounded rectangle for background
            bg_img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
            bg_draw = ImageDraw.Draw(bg_img)
            bg_draw.rounded_rectangle(bg_rect, radius=10, 
                                    fill=(*bg_color, int(200 * alpha / 255)))
            
            # Add subtle shadow
            shadow_offset = 2
            shadow_rect = [r + shadow_offset for r in bg_rect]
            bg_draw.rounded_rectangle(shadow_rect, radius=10,
                                    fill=(0, 0, 0, int(50 * alpha / 255)))
            
            image.alpha_composite(bg_img)
            
            # Draw text
            text_color = (*color, alpha)
            draw.text((text_x, line_y), line, font=font, fill=text_color)
        
        return image

    # ==================== BACKGROUND EFFECTS ====================
    
    def animated_gradient_background(self, frame: int, total_frames: int,
                                   colors: List[Tuple[int, int, int]],
                                   direction: str = 'vertical',
                                   speed: float = 1.0,
                                   pattern: str = 'linear') -> Image.Image:
        """Create animated gradient backgrounds with multiple patterns"""
        
        # Animate color cycling
        time_factor = (frame / total_frames) * speed
        
        if len(colors) >= 2:
            # Interpolate between colors based on time
            cycle_progress = (math.sin(time_factor * 2 * math.pi) + 1) / 2
            
            # Blend between first two colors
            color1 = colors[0]
            color2 = colors[1] if len(colors) > 1 else colors[0]
            
            if len(colors) > 2:
                # Use third color for more complex animation
                color3 = colors[2]
                
                # Create three-way blend
                if cycle_progress < 0.33:
                    blend_factor = cycle_progress * 3
                    start_color = self._blend_colors(color1, color2, blend_factor)
                    end_color = self._blend_colors(color2, color3, blend_factor)
                elif cycle_progress < 0.67:
                    blend_factor = (cycle_progress - 0.33) * 3
                    start_color = self._blend_colors(color2, color3, blend_factor)
                    end_color = self._blend_colors(color3, color1, blend_factor)
                else:
                    blend_factor = (cycle_progress - 0.67) * 3
                    start_color = self._blend_colors(color3, color1, blend_factor)
                    end_color = self._blend_colors(color1, color2, blend_factor)
            else:
                # Simple two-color blend
                start_color = self._blend_colors(color1, color2, cycle_progress)
                end_color = self._blend_colors(color2, color1, cycle_progress)
        else:
            start_color = end_color = colors[0]
        
        # Create gradient based on pattern
        if pattern == 'radial':
            return self._create_radial_gradient(start_color, end_color, time_factor)
        elif pattern == 'diagonal':
            return self._create_diagonal_gradient(start_color, end_color, direction, time_factor)
        elif pattern == 'wave':
            return self._create_wave_gradient(start_color, end_color, time_factor)
        else:  # linear
            return self._create_linear_gradient(start_color, end_color, direction, time_factor)
    
    def particle_system(self, frame: int, total_frames: int,
                       count: int = 50, style: str = 'floating',
                       motion: str = 'gentle', colors: List[Tuple[int, int, int]] = None) -> Image.Image:
        """Create animated particle effects"""
        image = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        if colors is None:
            colors = [(255, 255, 255), (200, 200, 255), (255, 200, 200)]
        
        time_factor = frame / total_frames
        
        # Generate consistent particle positions using frame as seed
        random.seed(42)  # Consistent across frames
        particles = []
        
        for i in range(count):
            # Base position
            base_x = random.uniform(0, self.width)
            base_y = random.uniform(0, self.height)
            
            # Particle properties
            particle_size = random.uniform(1, 8 if style == 'floating' else 15)
            particle_phase = random.uniform(0, 2 * math.pi)
            particle_speed = random.uniform(0.5, 2.0)
            particle_color = random.choice(colors)
            
            # Apply motion
            if motion == 'gentle':
                # Slow floating motion
                x = base_x + math.sin(time_factor * particle_speed + particle_phase) * 30
                y = base_y + math.cos(time_factor * particle_speed * 0.7 + particle_phase) * 20
                
            elif motion == 'rising':
                # Rising bubbles
                y = (base_y + time_factor * self.height * particle_speed) % (self.height + 100) - 50
                x = base_x + math.sin(time_factor * 4 + particle_phase) * 20
                
            elif motion == 'swirling':
                # Swirling motion
                angle = time_factor * particle_speed * 2 + particle_phase
                radius = 50 + math.sin(time_factor * 3 + particle_phase) * 30
                x = self.width / 2 + math.cos(angle) * radius
                y = self.height / 2 + math.sin(angle) * radius
                
            else:  # 'random'
                # Random Brownian motion
                random.seed(42 + i + frame)  # Frame-dependent seed
                x = base_x + random.uniform(-50, 50)
                y = base_y + random.uniform(-50, 50)
            
            # Keep particles in bounds with wrapping
            x = x % self.width
            y = y % self.height
            
            # Calculate alpha based on distance from center and time
            center_dist = math.sqrt((x - self.width/2)**2 + (y - self.height/2)**2)
            max_dist = math.sqrt((self.width/2)**2 + (self.height/2)**2)
            distance_alpha = 1 - (center_dist / max_dist) * 0.5
            
            # Time-based alpha animation
            time_alpha = 0.3 + 0.7 * (math.sin(time_factor * 4 + particle_phase) + 1) / 2
            
            final_alpha = int(255 * distance_alpha * time_alpha)
            particle_color_with_alpha = (*particle_color, final_alpha)
            
            # Draw particle based on style
            if style == 'floating':
                # Soft circles
                draw.ellipse([x - particle_size/2, y - particle_size/2,
                            x + particle_size/2, y + particle_size/2],
                           fill=particle_color_with_alpha)
                
            elif style == 'sparkles':
                # Star shapes
                self._draw_star(draw, x, y, particle_size, particle_color_with_alpha)
                
            elif style == 'bubbles':
                # Circles with highlights
                draw.ellipse([x - particle_size/2, y - particle_size/2,
                            x + particle_size/2, y + particle_size/2],
                           fill=particle_color_with_alpha,
                           outline=(*particle_color, int(final_alpha * 0.8)))
                # Highlight
                highlight_size = particle_size * 0.3
                draw.ellipse([x - particle_size/4, y - particle_size/4,
                            x - particle_size/4 + highlight_size,
                            y - particle_size/4 + highlight_size],
                           fill=(255, 255, 255, int(final_alpha * 0.6)))
        
        return image
    
    def bokeh_overlay(self, frame: int, total_frames: int,
                     intensity: float = 0.5,
                     color_scheme: str = 'warm') -> Image.Image:
        """Create bokeh blur effects"""
        image = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        colors = self.color_schemes.get(color_scheme, self.color_schemes['warm'])
        time_factor = frame / total_frames
        
        # Generate bokeh circles
        random.seed(123)  # Consistent positioning
        num_circles = int(15 * intensity)
        
        for i in range(num_circles):
            # Base properties
            x = random.uniform(0, self.width)
            y = random.uniform(0, self.height)
            base_size = random.uniform(20, 120)
            color = random.choice(colors)
            
            # Animate size and alpha
            size_animation = 1 + 0.3 * math.sin(time_factor * 2 + i * 0.5)
            alpha_animation = 0.1 + 0.4 * (math.sin(time_factor * 3 + i * 0.7) + 1) / 2
            
            final_size = base_size * size_animation
            final_alpha = int(255 * alpha_animation * intensity)
            
            # Create soft circle with gradient
            circle_img = Image.new('RGBA', (int(final_size * 2), int(final_size * 2)), (0, 0, 0, 0))
            circle_draw = ImageDraw.Draw(circle_img)
            
            # Draw multiple circles for soft edge
            for radius_factor in [1.0, 0.8, 0.6, 0.4, 0.2]:
                current_alpha = int(final_alpha * radius_factor)
                current_radius = final_size * radius_factor
                
                circle_draw.ellipse(
                    [final_size - current_radius, final_size - current_radius,
                     final_size + current_radius, final_size + current_radius],
                    fill=(*color, current_alpha)
                )
            
            # Blur the circle
            circle_img = circle_img.filter(ImageFilter.GaussianBlur(radius=3))
            
            # Paste onto main image
            paste_x = int(x - final_size)
            paste_y = int(y - final_size)
            image.paste(circle_img, (paste_x, paste_y), circle_img)
        
        return image
    
    def parallax_layers(self, frame: int, total_frames: int,
                       layers: List[Dict]) -> Image.Image:
        """Create parallax scrolling effect with multiple layers"""
        image = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        
        time_factor = frame / total_frames
        
        for layer in layers:
            layer_img = layer['image']
            speed = layer.get('speed', 1.0)
            direction = layer.get('direction', 'horizontal')
            opacity = layer.get('opacity', 1.0)
            
            # Calculate offset based on speed and time
            if direction == 'horizontal':
                offset = int((time_factor * speed * self.width) % (layer_img.width + self.width))
                for x_pos in [-layer_img.width + offset, offset]:
                    if opacity < 1.0:
                        layer_copy = layer_img.copy()
                        layer_copy.putalpha(int(255 * opacity))
                        image.paste(layer_copy, (x_pos, 0), layer_copy)
                    else:
                        image.paste(layer_img, (x_pos, 0))
                        
            elif direction == 'vertical':
                offset = int((time_factor * speed * self.height) % (layer_img.height + self.height))
                for y_pos in [-layer_img.height + offset, offset]:
                    if opacity < 1.0:
                        layer_copy = layer_img.copy()
                        layer_copy.putalpha(int(255 * opacity))
                        image.paste(layer_copy, (0, y_pos), layer_copy)
                    else:
                        image.paste(layer_img, (0, y_pos))
        
        return image
    
    def pattern_overlay(self, frame: int, total_frames: int,
                       pattern_type: str = 'noise',
                       intensity: float = 0.1,
                       animated: bool = True) -> Image.Image:
        """Create pattern overlays (noise, grain, texture)"""
        
        if pattern_type == 'noise':
            return self._create_noise_pattern(frame, total_frames, intensity, animated)
        elif pattern_type == 'grain':
            return self._create_grain_pattern(frame, total_frames, intensity, animated)
        elif pattern_type == 'dots':
            return self._create_dots_pattern(frame, total_frames, intensity, animated)
        elif pattern_type == 'lines':
            return self._create_lines_pattern(frame, total_frames, intensity, animated)
        else:
            # Default to noise
            return self._create_noise_pattern(frame, total_frames, intensity, animated)

    # ==================== TRANSITION EFFECTS ====================
    
    def crossfade_transition(self, image_a: Image.Image, image_b: Image.Image,
                           frame: int, total_frames: int,
                           easing: str = 'linear') -> Image.Image:
        """Create smooth crossfade transitions"""
        progress = frame / total_frames
        
        # Apply easing
        if easing == 'ease_in':
            progress = progress ** 2
        elif easing == 'ease_out':
            progress = 1 - (1 - progress) ** 2
        elif easing == 'ease_in_out':
            progress = 3 * progress ** 2 - 2 * progress ** 3
        
        # Blend images
        alpha_a = int(255 * (1 - progress))
        alpha_b = int(255 * progress)
        
        result = Image.new('RGBA', (self.width, self.height))
        
        # Apply alpha to each image
        if image_a.mode != 'RGBA':
            image_a = image_a.convert('RGBA')
        if image_b.mode != 'RGBA':
            image_b = image_b.convert('RGBA')
        
        # Create alpha masks
        image_a_alpha = image_a.copy()
        image_a_alpha.putalpha(alpha_a)
        
        image_b_alpha = image_b.copy()
        image_b_alpha.putalpha(alpha_b)
        
        # Composite
        result.paste((0, 0, 0, 0), [0, 0, self.width, self.height])
        result = Image.alpha_composite(result, image_a_alpha)
        result = Image.alpha_composite(result, image_b_alpha)
        
        return result
    
    def zoom_transition(self, image_a: Image.Image, image_b: Image.Image,
                       frame: int, total_frames: int,
                       direction: str = 'in',
                       center_point: Tuple[int, int] = None) -> Image.Image:
        """Create zoom-in/out transitions"""
        progress = frame / total_frames
        
        if center_point is None:
            center_point = (self.width // 2, self.height // 2)
        
        result = Image.new('RGBA', (self.width, self.height))
        
        if direction == 'in':
            # Zoom into image A, reveal image B
            if progress < 0.5:
                # Zoom into A
                zoom_factor = 1 + progress * 2  # 1x to 2x
                zoomed_a = self._zoom_image(image_a, zoom_factor, center_point)
                result.paste(zoomed_a, (0, 0))
            else:
                # Zoom from B (very zoomed) to normal
                zoom_factor = 4 - (progress - 0.5) * 6  # 4x to 1x
                zoomed_b = self._zoom_image(image_b, zoom_factor, center_point)
                result.paste(zoomed_b, (0, 0))
                
        else:  # direction == 'out'
            # Zoom out from A, zoom into B
            if progress < 0.5:
                # Zoom out from A
                zoom_factor = 1 - progress * 0.5  # 1x to 0.5x
                zoomed_a = self._zoom_image(image_a, zoom_factor, center_point)
                result.paste(zoomed_a, (0, 0))
            else:
                # Zoom into B from small
                zoom_factor = (progress - 0.5) * 2  # 0x to 1x
                zoomed_b = self._zoom_image(image_b, zoom_factor, center_point)
                result.paste(zoomed_b, (0, 0))
        
        return result
    
    def slide_transition(self, image_a: Image.Image, image_b: Image.Image,
                        frame: int, total_frames: int,
                        direction: str = 'left') -> Image.Image:
        """Create slide transitions"""
        progress = frame / total_frames
        result = Image.new('RGBA', (self.width, self.height))
        
        if direction == 'left':
            # Slide A to left, B comes from right
            offset_a = -int(self.width * progress)
            offset_b = self.width - int(self.width * progress)
            result.paste(image_a, (offset_a, 0))
            result.paste(image_b, (offset_b, 0))
            
        elif direction == 'right':
            # Slide A to right, B comes from left
            offset_a = int(self.width * progress)
            offset_b = -self.width + int(self.width * progress)
            result.paste(image_a, (offset_a, 0))
            result.paste(image_b, (offset_b, 0))
            
        elif direction == 'up':
            # Slide A up, B comes from bottom
            offset_a = -int(self.height * progress)
            offset_b = self.height - int(self.height * progress)
            result.paste(image_a, (0, offset_a))
            result.paste(image_b, (0, offset_b))
            
        elif direction == 'down':
            # Slide A down, B comes from top
            offset_a = int(self.height * progress)
            offset_b = -self.height + int(self.height * progress)
            result.paste(image_a, (0, offset_a))
            result.paste(image_b, (0, offset_b))
        
        return result
    
    def morph_transition(self, image_a: Image.Image, image_b: Image.Image,
                        frame: int, total_frames: int,
                        style: str = 'elastic') -> Image.Image:
        """Create morphing transitions"""
        progress = frame / total_frames
        
        if style == 'elastic':
            # Elastic distortion effect
            distortion = math.sin(progress * math.pi) * 50
            
            # Create morphed version by blending with distortion
            morphed_a = self._apply_wave_distortion(image_a, distortion, 'horizontal')
            morphed_b = self._apply_wave_distortion(image_b, -distortion, 'horizontal')
            
            # Blend the morphed images
            return self.crossfade_transition(morphed_a, morphed_b, frame, total_frames)
            
        elif style == 'ripple':
            # Ripple effect outward from center
            center_x, center_y = self.width // 2, self.height // 2
            ripple_radius = progress * math.sqrt(self.width**2 + self.height**2)
            
            result = image_a.copy()
            for y in range(self.height):
                for x in range(self.width):
                    distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                    if distance < ripple_radius:
                        # Inside ripple, show image B
                        pixel_b = image_b.getpixel((x, y))
                        # Add ripple distortion
                        wave_offset = int(10 * math.sin(distance * 0.1))
                        try:
                            result.putpixel((x + wave_offset, y), pixel_b)
                        except IndexError:
                            pass
            
            return result
            
        else:  # 'swirl'
            # Swirling morph
            return self._apply_swirl_transition(image_a, image_b, progress)

    # ==================== VISUAL POLISH ====================
    
    def add_drop_shadow(self, image: Image.Image, offset: Tuple[int, int] = (5, 5),
                       blur_radius: int = 3, shadow_color: Tuple[int, int, int] = (0, 0, 0),
                       opacity: float = 0.5) -> Image.Image:
        """Add professional drop shadows"""
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Create shadow layer
        shadow = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        
        # Create shadow from alpha channel
        alpha_channel = image.split()[-1]
        shadow_layer = Image.new('RGB', (self.width, self.height), shadow_color)
        shadow_layer.putalpha(alpha_channel)
        
        # Apply opacity
        enhancer = ImageEnhance.Color(shadow_layer)
        shadow_layer = enhancer.enhance(opacity)
        
        # Apply blur
        shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        
        # Offset shadow
        shadow_with_offset = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        shadow_with_offset.paste(shadow_layer, offset)
        
        # Composite original image on top of shadow
        result = shadow_with_offset
        result = Image.alpha_composite(result, image)
        
        return result
    
    def add_glow_effect(self, image: Image.Image, glow_color: Tuple[int, int, int] = (255, 255, 255),
                       intensity: float = 0.8, radius: int = 10) -> Image.Image:
        """Add glow effects for emphasis"""
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Create multiple glow layers for smooth effect
        result = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        
        # Multiple blur passes for smooth glow
        for i, (blur_radius, glow_opacity) in enumerate([(radius, intensity), 
                                                        (radius//2, intensity*0.7), 
                                                        (radius//4, intensity*0.5)]):
            glow_layer = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
            
            # Extract alpha and create colored glow
            alpha_channel = image.split()[-1]
            colored_glow = Image.new('RGBA', (self.width, self.height), (*glow_color, 0))
            colored_glow.putalpha(alpha_channel)
            
            # Apply blur and opacity
            colored_glow = colored_glow.filter(ImageFilter.GaussianBlur(radius=blur_radius))
            enhancer = ImageEnhance.Color(colored_glow)
            colored_glow = enhancer.enhance(glow_opacity)
            
            glow_layer = Image.alpha_composite(glow_layer, colored_glow)
            result = Image.alpha_composite(result, glow_layer)
        
        # Add original image on top
        result = Image.alpha_composite(result, image)
        return result
    
    def add_vignette(self, image: Image.Image, intensity: float = 0.5,
                    color: Tuple[int, int, int] = (0, 0, 0)) -> Image.Image:
        """Add vignette effects"""
        result = image.copy()
        
        # Create radial gradient mask
        vignette_mask = Image.new('L', (self.width, self.height), 255)
        center_x, center_y = self.width // 2, self.height // 2
        max_distance = math.sqrt(center_x**2 + center_y**2)
        
        for y in range(self.height):
            for x in range(self.width):
                distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                vignette_factor = 1 - (distance / max_distance) * intensity
                vignette_factor = max(0, min(1, vignette_factor))
                vignette_mask.putpixel((x, y), int(255 * vignette_factor))
        
        # Create vignette layer
        vignette_layer = Image.new('RGBA', (self.width, self.height), (*color, 255))
        vignette_layer.putalpha(vignette_mask)
        
        # Apply vignette
        if result.mode != 'RGBA':
            result = result.convert('RGBA')
        
        # Invert alpha for darkening effect
        inverted_mask = ImageEnhance.Color(vignette_mask).enhance(0)  # Invert
        vignette_layer.putalpha(inverted_mask)
        
        result = Image.alpha_composite(result, vignette_layer)
        return result
    
    def apply_color_grading(self, image: Image.Image, mood: str) -> Image.Image:
        """Apply professional color grading"""
        result = image.copy()
        
        if mood == 'warm':
            # Increase reds/oranges, decrease blues
            enhancer = ImageEnhance.Color(result)
            result = enhancer.enhance(1.2)  # Boost saturation
            
            # Split channels and adjust
            if result.mode == 'RGB' or result.mode == 'RGBA':
                r, g, b = result.split()[:3]
                
                # Enhance reds and reduce blues
                r = ImageEnhance.Brightness(r).enhance(1.1)
                b = ImageEnhance.Brightness(b).enhance(0.9)
                
                if result.mode == 'RGBA':
                    result = Image.merge('RGBA', (r, g, b, result.split()[3]))
                else:
                    result = Image.merge('RGB', (r, g, b))
                    
        elif mood == 'cool':
            # Increase blues, decrease reds
            enhancer = ImageEnhance.Color(result)
            result = enhancer.enhance(1.1)
            
            if result.mode == 'RGB' or result.mode == 'RGBA':
                r, g, b = result.split()[:3]
                
                # Enhance blues and reduce reds
                b = ImageEnhance.Brightness(b).enhance(1.1)
                r = ImageEnhance.Brightness(r).enhance(0.9)
                
                if result.mode == 'RGBA':
                    result = Image.merge('RGBA', (r, g, b, result.split()[3]))
                else:
                    result = Image.merge('RGB', (r, g, b))
                    
        elif mood == 'vintage':
            # Desaturate and add sepia tone
            enhancer = ImageEnhance.Color(result)
            result = enhancer.enhance(0.7)  # Reduce saturation
            
            # Add sepia overlay
            sepia_overlay = Image.new('RGBA', (self.width, self.height), (222, 184, 135, 50))
            if result.mode != 'RGBA':
                result = result.convert('RGBA')
            result = Image.alpha_composite(result, sepia_overlay)
            
        elif mood == 'dramatic':
            # High contrast, desaturated with selective color
            # Increase contrast
            enhancer = ImageEnhance.Contrast(result)
            result = enhancer.enhance(1.3)
            
            # Reduce overall saturation
            enhancer = ImageEnhance.Color(result)
            result = enhancer.enhance(0.8)
            
        return result
    
    def add_film_grain(self, image: Image.Image, amount: float = 0.1) -> Image.Image:
        """Add film grain texture"""
        if image.mode != 'RGBA':
            result = image.convert('RGBA')
        else:
            result = image.copy()
        
        # Create noise pattern
        grain = self._create_noise_pattern(0, 1, amount, False)
        grain = grain.convert('L')  # Convert to grayscale
        
        # Create grain overlay
        grain_overlay = Image.new('RGBA', (self.width, self.height), (128, 128, 128, 0))
        grain_overlay.putalpha(grain)
        
        # Blend with overlay mode
        result = Image.alpha_composite(result, grain_overlay)
        return result

    # ==================== HELPER METHODS ====================
    
    def _get_font(self, size: int) -> ImageFont.FreeTypeFont:
        """Get cached font"""
        if size not in self._font_cache:
            try:
                font_paths = [
                    "/System/Library/Fonts/Helvetica.ttc",
                    "/System/Library/Fonts/Arial.ttf",
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
                ]
                
                for font_path in font_paths:
                    if os.path.exists(font_path):
                        self._font_cache[size] = ImageFont.truetype(font_path, size)
                        break
                else:
                    self._font_cache[size] = ImageFont.load_default()
            except:
                self._font_cache[size] = ImageFont.load_default()
        
        return self._font_cache[size]
    
    def _blend_colors(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int], 
                     factor: float) -> Tuple[int, int, int]:
        """Blend two colors with given factor (0.0 = color1, 1.0 = color2)"""
        return tuple(
            int(color1[i] * (1 - factor) + color2[i] * factor) 
            for i in range(3)
        )
    
    def _create_linear_gradient(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int],
                              direction: str, time_factor: float) -> Image.Image:
        """Create linear gradient with animation"""
        image = Image.new('RGB', (self.width, self.height))
        
        # Add subtle movement to gradient
        offset = int(20 * math.sin(time_factor * 2))
        
        if direction == 'vertical':
            for y in range(self.height):
                factor = ((y + offset) % self.height) / self.height
                color = self._blend_colors(color1, color2, factor)
                for x in range(self.width):
                    image.putpixel((x, y), color)
        else:  # horizontal
            for x in range(self.width):
                factor = ((x + offset) % self.width) / self.width
                color = self._blend_colors(color1, color2, factor)
                for y in range(self.height):
                    image.putpixel((x, y), color)
        
        return image
    
    def _create_radial_gradient(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int],
                              time_factor: float) -> Image.Image:
        """Create radial gradient"""
        image = Image.new('RGB', (self.width, self.height))
        
        center_x = self.width // 2 + int(50 * math.sin(time_factor))
        center_y = self.height // 2 + int(30 * math.cos(time_factor * 1.3))
        max_distance = math.sqrt(self.width**2 + self.height**2) / 2
        
        for y in range(self.height):
            for x in range(self.width):
                distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                factor = min(1.0, distance / max_distance)
                color = self._blend_colors(color1, color2, factor)
                image.putpixel((x, y), color)
        
        return image
    
    def _create_diagonal_gradient(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int],
                                direction: str, time_factor: float) -> Image.Image:
        """Create diagonal gradient"""
        image = Image.new('RGB', (self.width, self.height))
        
        diagonal_length = math.sqrt(self.width**2 + self.height**2)
        offset = int(50 * math.sin(time_factor * 2))
        
        for y in range(self.height):
            for x in range(self.width):
                if direction == 'top_left_to_bottom_right':
                    distance = (x + y + offset) % diagonal_length
                else:  # 'top_right_to_bottom_left'
                    distance = (self.width - x + y + offset) % diagonal_length
                
                factor = distance / diagonal_length
                color = self._blend_colors(color1, color2, factor)
                image.putpixel((x, y), color)
        
        return image
    
    def _create_wave_gradient(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int],
                            time_factor: float) -> Image.Image:
        """Create wave-pattern gradient"""
        image = Image.new('RGB', (self.width, self.height))
        
        for y in range(self.height):
            for x in range(self.width):
                wave = math.sin((x + time_factor * 100) * 0.01) * math.sin((y + time_factor * 50) * 0.008)
                factor = (wave + 1) / 2  # Normalize to 0-1
                color = self._blend_colors(color1, color2, factor)
                image.putpixel((x, y), color)
        
        return image
    
    def _create_noise_pattern(self, frame: int, total_frames: int, 
                            intensity: float, animated: bool) -> Image.Image:
        """Create animated noise pattern"""
        image = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        
        # Use frame for animation
        seed = frame if animated else 42
        random.seed(seed)
        
        # Generate noise
        for y in range(0, self.height, 2):  # Skip pixels for performance
            for x in range(0, self.width, 2):
                noise_value = random.randint(0, 255)
                alpha = int(intensity * 255)
                
                # Apply noise to 2x2 block for efficiency
                for dy in range(2):
                    for dx in range(2):
                        if x + dx < self.width and y + dy < self.height:
                            image.putpixel((x + dx, y + dy), (noise_value, noise_value, noise_value, alpha))
        
        return image
    
    def _create_grain_pattern(self, frame: int, total_frames: int,
                            intensity: float, animated: bool) -> Image.Image:
        """Create film grain pattern"""
        image = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        seed = frame if animated else 42
        random.seed(seed)
        
        # Generate grain dots
        num_grains = int(self.width * self.height * intensity * 0.01)
        for _ in range(num_grains):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            brightness = random.randint(0, 255)
            alpha = random.randint(50, 150)
            
            draw.point((x, y), fill=(brightness, brightness, brightness, alpha))
        
        return image
    
    def _create_dots_pattern(self, frame: int, total_frames: int,
                           intensity: float, animated: bool) -> Image.Image:
        """Create animated dots pattern"""
        image = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        dot_spacing = 20
        dot_size = int(3 * intensity)
        
        time_offset = frame * 0.1 if animated else 0
        
        for y in range(0, self.height, dot_spacing):
            for x in range(0, self.width, dot_spacing):
                # Animate dot alpha
                distance_factor = math.sqrt((x - self.width/2)**2 + (y - self.height/2)**2) / 100
                alpha_factor = (math.sin(time_offset + distance_factor) + 1) / 2
                alpha = int(intensity * 255 * alpha_factor)
                
                if alpha > 0:
                    draw.ellipse([x - dot_size, y - dot_size, 
                                x + dot_size, y + dot_size], 
                               fill=(255, 255, 255, alpha))
        
        return image
    
    def _create_lines_pattern(self, frame: int, total_frames: int,
                            intensity: float, animated: bool) -> Image.Image:
        """Create animated lines pattern"""
        image = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        line_spacing = 30
        time_offset = frame * 0.05 if animated else 0
        
        # Vertical lines
        for x in range(0, self.width, line_spacing):
            alpha = int(intensity * 255 * (math.sin(time_offset + x * 0.01) + 1) / 2)
            if alpha > 0:
                draw.line([(x, 0), (x, self.height)], 
                         fill=(255, 255, 255, alpha), width=1)
        
        # Horizontal lines
        for y in range(0, self.height, line_spacing):
            alpha = int(intensity * 255 * (math.cos(time_offset + y * 0.01) + 1) / 2)
            if alpha > 0:
                draw.line([(0, y), (self.width, y)], 
                         fill=(255, 255, 255, alpha), width=1)
        
        return image
    
    def _draw_star(self, draw: ImageDraw.Draw, x: float, y: float, 
                   size: float, color: Tuple[int, int, int, int]):
        """Draw a star shape"""
        points = []
        for i in range(10):  # 5 points, 2 coordinates each
            angle = (i * math.pi) / 5
            if i % 2 == 0:
                # Outer point
                px = x + size * math.cos(angle)
                py = y + size * math.sin(angle)
            else:
                # Inner point
                px = x + size * 0.5 * math.cos(angle)
                py = y + size * 0.5 * math.sin(angle)
            points.append((px, py))
        
        draw.polygon(points, fill=color)
    
    def _wrap_text_to_lines(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = current_line + [word]
            test_text = ' '.join(test_line)
            bbox = font.getbbox(test_text)
            
            if bbox[2] - bbox[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _zoom_image(self, image: Image.Image, zoom_factor: float, 
                   center_point: Tuple[int, int]) -> Image.Image:
        """Zoom image around center point"""
        if zoom_factor <= 0:
            return Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
            
        # Calculate new size
        new_width = int(self.width * zoom_factor)
        new_height = int(self.height * zoom_factor)
        
        # Resize image
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Calculate crop position to center on center_point
        crop_x = max(0, (new_width - self.width) // 2)
        crop_y = max(0, (new_height - self.height) // 2)
        
        # Crop to original dimensions
        if new_width >= self.width and new_height >= self.height:
            result = resized.crop((crop_x, crop_y, crop_x + self.width, crop_y + self.height))
        else:
            # If zoomed out, center small image on background
            result = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
            paste_x = (self.width - new_width) // 2
            paste_y = (self.height - new_height) // 2
            result.paste(resized, (paste_x, paste_y))
        
        return result
    
    def _apply_wave_distortion(self, image: Image.Image, amplitude: float, 
                             direction: str) -> Image.Image:
        """Apply wave distortion to image"""
        result = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        
        for y in range(self.height):
            for x in range(self.width):
                if direction == 'horizontal':
                    offset = int(amplitude * math.sin(y * 0.05))
                    source_x = (x - offset) % self.width
                    source_y = y
                else:  # vertical
                    offset = int(amplitude * math.sin(x * 0.05))
                    source_x = x
                    source_y = (y - offset) % self.height
                
                try:
                    pixel = image.getpixel((source_x, source_y))
                    result.putpixel((x, y), pixel)
                except IndexError:
                    pass
        
        return result
    
    def _apply_swirl_transition(self, image_a: Image.Image, image_b: Image.Image, 
                              progress: float) -> Image.Image:
        """Apply swirl transition between images"""
        result = image_a.copy()
        
        center_x, center_y = self.width // 2, self.height // 2
        max_distance = math.sqrt(center_x**2 + center_y**2)
        
        for y in range(self.height):
            for x in range(self.width):
                dx = x - center_x
                dy = y - center_y
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance < max_distance * progress:
                    # Apply swirl transformation
                    angle = math.atan2(dy, dx) + (progress * 2 * math.pi * distance / max_distance)
                    new_x = center_x + int(distance * math.cos(angle))
                    new_y = center_y + int(distance * math.sin(angle))
                    
                    # Clamp coordinates
                    new_x = max(0, min(self.width - 1, new_x))
                    new_y = max(0, min(self.height - 1, new_y))
                    
                    try:
                        pixel = image_b.getpixel((new_x, new_y))
                        result.putpixel((x, y), pixel)
                    except IndexError:
                        pass
        
        return result

# ==================== MOTION GRAPHICS ====================

class MotionGraphics(AdvancedEffectsLibrary):
    """Specialized motion graphics components"""
    
    def progress_indicator(self, frame: int, total_frames: int, progress: float,
                          style: str = 'bar', color: Tuple[int, int, int] = (41, 98, 255)) -> Image.Image:
        """Create animated progress indicators"""
        image = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        animated_progress = progress + 0.1 * math.sin(frame * 0.2)  # Subtle animation
        animated_progress = max(0, min(1, animated_progress))
        
        if style == 'bar':
            # Horizontal progress bar
            bar_width = int(self.width * 0.8)
            bar_height = 20
            bar_x = (self.width - bar_width) // 2
            bar_y = self.height - 100
            
            # Background
            draw.rounded_rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height], 
                                 radius=10, fill=(200, 200, 200, 100))
            
            # Progress
            progress_width = int(bar_width * animated_progress)
            if progress_width > 0:
                draw.rounded_rectangle([bar_x, bar_y, bar_x + progress_width, bar_y + bar_height],
                                     radius=10, fill=color)
                
        elif style == 'circular':
            # Circular progress
            center_x, center_y = self.width // 2, self.height - 100
            radius = 30
            thickness = 8
            
            # Background circle
            draw.ellipse([center_x - radius, center_y - radius,
                        center_x + radius, center_y + radius],
                       outline=(200, 200, 200), width=thickness)
            
            # Progress arc
            if animated_progress > 0:
                end_angle = -90 + (360 * animated_progress)
                # Note: PIL doesn't support arc drawing easily, so we'll use a workaround
                # Draw small segments to approximate an arc
                segments = int(360 * animated_progress)
                for i in range(segments):
                    angle = math.radians(-90 + (i * 360 / segments))
                    x1 = center_x + (radius - thickness//2) * math.cos(angle)
                    y1 = center_y + (radius - thickness//2) * math.sin(angle)
                    draw.ellipse([x1-2, y1-2, x1+2, y1+2], fill=color)
                    
        elif style == 'dots':
            # Dot-based progress
            num_dots = 10
            dot_spacing = 40
            total_width = (num_dots - 1) * dot_spacing
            start_x = (self.width - total_width) // 2
            dot_y = self.height - 100
            
            active_dots = int(num_dots * animated_progress)
            
            for i in range(num_dots):
                dot_x = start_x + i * dot_spacing
                
                if i <= active_dots:
                    # Active dot with pulse animation
                    pulse = 1 + 0.3 * math.sin(frame * 0.3 + i * 0.5)
                    dot_size = int(8 * pulse)
                    draw.ellipse([dot_x - dot_size, dot_y - dot_size,
                                dot_x + dot_size, dot_y + dot_size], fill=color)
                else:
                    # Inactive dot
                    draw.ellipse([dot_x - 4, dot_y - 4, dot_x + 4, dot_y + 4],
                               fill=(200, 200, 200))
        
        return image
    
    def animated_icon(self, frame: int, total_frames: int, icon_type: str,
                     color: Tuple[int, int, int] = (255, 255, 255),
                     position: Tuple[int, int] = None, size: int = 60) -> Image.Image:
        """Create animated icons with motion"""
        if position is None:
            position = (self.width // 2, self.height // 2)
        
        image = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        x, y = position
        time_factor = frame / total_frames
        
        # Add subtle floating animation
        float_offset = int(10 * math.sin(time_factor * 4))
        y += float_offset
        
        if icon_type == 'heart_beat':
            # Beating heart
            beat_scale = 1 + 0.3 * abs(math.sin(time_factor * 8))
            current_size = int(size * beat_scale)
            
            # Draw heart shape
            draw.ellipse([x - current_size//3, y - current_size//4, 
                         x, y + current_size//4], fill=color)
            draw.ellipse([x, y - current_size//4, 
                         x + current_size//3, y + current_size//4], fill=color)
            draw.polygon([(x - current_size//3, y), 
                         (x, y + current_size//2), 
                         (x + current_size//3, y)], fill=color)
            
        elif icon_type == 'spinning_gear':
            # Spinning gear
            rotation_angle = time_factor * 360 * 2  # 2 full rotations
            
            # Draw gear teeth (simplified as star)
            num_teeth = 8
            for i in range(num_teeth):
                angle = math.radians(rotation_angle + (i * 360 / num_teeth))
                outer_x = x + size * 0.8 * math.cos(angle)
                outer_y = y + size * 0.8 * math.sin(angle)
                inner_angle = math.radians(rotation_angle + ((i + 0.5) * 360 / num_teeth))
                inner_x = x + size * 0.5 * math.cos(inner_angle)
                inner_y = y + size * 0.5 * math.sin(inner_angle)
                
                draw.polygon([(x, y), (outer_x, outer_y), (inner_x, inner_y)], fill=color)
            
            # Center circle
            draw.ellipse([x - size//4, y - size//4, x + size//4, y + size//4], fill=color)
            
        elif icon_type == 'growing_plant':
            # Growing plant animation
            growth = time_factor  # 0 to 1
            
            # Stem
            stem_height = int(size * growth)
            draw.line([(x, y + size//2), (x, y + size//2 - stem_height)], 
                     fill=color, width=4)
            
            if growth > 0.3:
                # Leaves (appear after 30% growth)
                leaf_size = int(size * 0.3 * (growth - 0.3) / 0.7)
                # Left leaf
                draw.ellipse([x - leaf_size - 10, y + size//4 - leaf_size//2,
                            x - 10, y + size//4 + leaf_size//2], fill=color)
                # Right leaf
                draw.ellipse([x + 10, y + size//4 - leaf_size//2,
                            x + 10 + leaf_size, y + size//4 + leaf_size//2], fill=color)
            
            if growth > 0.7:
                # Flower (appears at 70% growth)
                flower_size = int(size * 0.4 * (growth - 0.7) / 0.3)
                draw.ellipse([x - flower_size, y + size//2 - stem_height - flower_size,
                            x + flower_size, y + size//2 - stem_height + flower_size], fill=(255, 100, 100))
                            
        elif icon_type == 'bouncing_ball':
            # Bouncing ball
            bounce_height = abs(math.sin(time_factor * 6)) * size
            ball_y = y + size//2 - bounce_height
            
            # Ball gets squashed at bottom
            squash_factor = 1 - (bounce_height / size) * 0.3
            ball_width = int(size * 0.4 / squash_factor)
            ball_height = int(size * 0.4 * squash_factor)
            
            draw.ellipse([x - ball_width, ball_y - ball_height,
                         x + ball_width, ball_y + ball_height], fill=color)
        
        return image
    
    def chart_animation(self, frame: int, total_frames: int, data: List[float],
                       labels: List[str] = None, chart_type: str = 'bar',
                       color_scheme: str = 'professional') -> Image.Image:
        """Create animated charts and statistics"""
        image = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        colors = self.color_schemes[color_scheme]
        
        # Animation progress
        progress = frame / total_frames
        
        # Chart area
        chart_x = int(self.width * 0.1)
        chart_y = int(self.height * 0.3)
        chart_width = int(self.width * 0.8)
        chart_height = int(self.height * 0.4)
        
        max_value = max(data) if data else 1
        
        if chart_type == 'bar':
            # Animated bar chart
            bar_width = chart_width // len(data) - 10
            
            for i, value in enumerate(data):
                # Animate bar growth
                animated_value = value * min(1.0, progress * 2 - i * 0.1)
                
                bar_height = int((animated_value / max_value) * chart_height)
                bar_x = chart_x + i * (bar_width + 10)
                bar_y = chart_y + chart_height - bar_height
                
                # Color cycling
                color = colors[i % len(colors)]
                
                # Draw bar with animation
                draw.rectangle([bar_x, bar_y, bar_x + bar_width, chart_y + chart_height], 
                             fill=color)
                
                # Value label
                font = self._get_font(24)
                value_text = f"{animated_value:.1f}"
                text_bbox = font.getbbox(value_text)
                text_x = bar_x + (bar_width - (text_bbox[2] - text_bbox[0])) // 2
                draw.text((text_x, bar_y - 30), value_text, font=font, fill=(255, 255, 255))
                
                # Category label if provided
                if labels and i < len(labels):
                    label_text = labels[i]
                    label_bbox = font.getbbox(label_text)
                    label_x = bar_x + (bar_width - (label_bbox[2] - label_bbox[0])) // 2
                    draw.text((label_x, chart_y + chart_height + 10), 
                             label_text, font=font, fill=(200, 200, 200))
                             
        elif chart_type == 'line':
            # Animated line chart
            if len(data) > 1:
                points = []
                segment_width = chart_width / (len(data) - 1)
                
                for i, value in enumerate(data):
                    animated_value = value * min(1.0, progress * 2 - i * 0.1)
                    
                    point_x = chart_x + i * segment_width
                    point_y = chart_y + chart_height - (animated_value / max_value) * chart_height
                    points.append((point_x, point_y))
                    
                    # Draw data points
                    if progress > i * 0.1:
                        draw.ellipse([point_x - 5, point_y - 5, point_x + 5, point_y + 5], 
                                   fill=colors[0])
                
                # Draw line segments as they're revealed
                revealed_points = int(progress * len(points))
                if revealed_points > 1:
                    for i in range(min(revealed_points - 1, len(points) - 1)):
                        draw.line([points[i], points[i + 1]], fill=colors[0], width=3)
        
        return image
    
    def logo_animation(self, frame: int, total_frames: int, logo_path: str = None,
                      animation_type: str = 'fade_in') -> Image.Image:
        """Create logo animations"""
        image = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        
        if logo_path and os.path.exists(logo_path):
            logo = Image.open(logo_path).convert('RGBA')
        else:
            # Create placeholder logo
            logo = Image.new('RGBA', (200, 100), (255, 255, 255, 0))
            logo_draw = ImageDraw.Draw(logo)
            font = self._get_font(36)
            logo_draw.text((10, 30), "LOGO", font=font, fill=(255, 255, 255))
            
        progress = frame / total_frames
        
        if animation_type == 'fade_in':
            # Simple fade in
            alpha = int(255 * progress)
            logo.putalpha(alpha)
            
        elif animation_type == 'slide_in':
            # Slide in from left
            offset = int((1 - progress) * self.width)
            logo_x = -logo.width + offset
            logo_y = (self.height - logo.height) // 2
            
        elif animation_type == 'zoom_in':
            # Zoom in from center
            scale = 0.1 + 0.9 * progress
            scaled_size = (int(logo.width * scale), int(logo.height * scale))
            logo = logo.resize(scaled_size, Image.Resampling.LANCZOS)
            
        elif animation_type == 'rotate_in':
            # Rotate while fading in
            angle = (1 - progress) * 360
            logo = logo.rotate(angle, expand=1)
            alpha = int(255 * progress)
            logo.putalpha(alpha)
        
        # Center logo
        logo_x = (self.width - logo.width) // 2
        logo_y = (self.height - logo.height) // 2
        
        image.paste(logo, (logo_x, logo_y), logo)
        return image
    
    def call_to_action_animation(self, frame: int, total_frames: int, 
                               cta_text: str, style: str = 'pulse') -> Image.Image:
        """Create animated call-to-action elements"""
        image = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        time_factor = frame / total_frames
        
        # Position at bottom
        cta_y = self.height - 200
        
        if style == 'pulse':
            # Pulsing button
            pulse_scale = 1 + 0.2 * math.sin(time_factor * 8)
            
            # Button background
            button_width = int(300 * pulse_scale)
            button_height = int(80 * pulse_scale)
            button_x = (self.width - button_width) // 2
            
            # Draw button with gradient effect
            draw.rounded_rectangle([button_x, cta_y, button_x + button_width, cta_y + button_height],
                                 radius=40, fill=(255, 159, 67))
            
            # Button text
            font = self._get_font(int(32 * pulse_scale))
            text_bbox = font.getbbox(cta_text)
            text_width = text_bbox[2] - text_bbox[0]
            text_x = button_x + (button_width - text_width) // 2
            text_y = cta_y + (button_height - (text_bbox[3] - text_bbox[1])) // 2
            
            draw.text((text_x, text_y), cta_text, font=font, fill=(255, 255, 255))
            
        elif style == 'glow':
            # Glowing text effect
            glow_intensity = 0.5 + 0.5 * math.sin(time_factor * 6)
            
            font = self._get_font(48)
            
            # Create glow effect
            for offset in range(1, 8):
                glow_alpha = int(100 * glow_intensity / offset)
                for dx in [-offset, 0, offset]:
                    for dy in [-offset, 0, offset]:
                        if dx != 0 or dy != 0:
                            text_bbox = font.getbbox(cta_text)
                            text_width = text_bbox[2] - text_bbox[0]
                            text_x = (self.width - text_width) // 2 + dx
                            draw.text((text_x, cta_y + dy), cta_text, 
                                    font=font, fill=(255, 159, 67, glow_alpha))
            
            # Main text
            text_bbox = font.getbbox(cta_text)
            text_width = text_bbox[2] - text_bbox[0]
            text_x = (self.width - text_width) // 2
            draw.text((text_x, cta_y), cta_text, font=font, fill=(255, 255, 255))
            
        elif style == 'bounce':
            # Bouncing text
            bounce_height = abs(math.sin(time_factor * 6)) * 30
            bounce_y = cta_y - bounce_height
            
            font = self._get_font(42)
            text_bbox = font.getbbox(cta_text)
            text_width = text_bbox[2] - text_bbox[0]
            text_x = (self.width - text_width) // 2
            
            # Shadow effect
            shadow_y = bounce_y + 5
            draw.text((text_x + 2, shadow_y + 2), cta_text, 
                     font=font, fill=(0, 0, 0, 100))
            
            # Main text
            draw.text((text_x, bounce_y), cta_text, 
                     font=font, fill=(255, 159, 67))
        
        return image


# Export the main class
__all__ = ['AdvancedEffectsLibrary', 'MotionGraphics']