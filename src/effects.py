#!/usr/bin/env python3
"""
Kiin Professional Video Effects Library
Complete rewrite with 20+ professional effects for stunning video production
"""

import os
import math
import random
import tempfile
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Callable
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
import numpy as np

# Import our advanced effects
from advanced_effects import AdvancedEffectsLibrary, MotionGraphics

class KiinEffectsLibrary:
    """Professional video effects library with 20+ cinematic effects"""
    
    def __init__(self, width: int = 1080, height: int = 1920, fps: int = 30):
        self.width = width
        self.height = height
        self.fps = fps
        self.frame_time = 1.0 / fps
        
        # Initialize advanced effects engine
        self.advanced_effects = AdvancedEffectsLibrary(width, height, fps)
        self.motion_graphics = MotionGraphics(width, height, fps)
        
        # Professional color palettes
        self.color_palettes = {
            'kiin_brand': {
                'primary': (41, 98, 255),
                'secondary': (0, 184, 148), 
                'accent': (255, 159, 67),
                'danger': (255, 82, 82),
                'success': (46, 213, 115),
                'warning': (255, 177, 43),
                'dark': (45, 52, 54),
                'light': (223, 230, 233)
            },
            'cinematic_warm': {
                'primary': (255, 183, 77),
                'secondary': (255, 118, 117),
                'accent': (255, 209, 102),
                'shadow': (154, 68, 66),
                'highlight': (255, 234, 167)
            },
            'cinematic_cool': {
                'primary': (116, 185, 255),
                'secondary': (162, 155, 254), 
                'accent': (95, 207, 192),
                'shadow': (58, 89, 149),
                'highlight': (199, 236, 254)
            },
            'dramatic': {
                'primary': (255, 255, 255),
                'secondary': (128, 128, 128),
                'accent': (255, 215, 0),
                'shadow': (32, 32, 32),
                'highlight': (255, 255, 255)
            },
            'organic': {
                'primary': (76, 175, 80),
                'secondary': (139, 195, 74),
                'accent': (255, 193, 7),
                'shadow': (56, 142, 60),
                'highlight': (200, 230, 201)
            }
        }
        
        # Transition presets for different moods
        self.transition_presets = {
            'chaos_to_calm': {
                'type': 'morph',
                'style': 'ripple',
                'speed': 'slow',
                'easing': 'ease_out'
            },
            'problem_to_solution': {
                'type': 'slide',
                'direction': 'left',
                'speed': 'medium',
                'easing': 'ease_in_out'
            },
            'insight_reveal': {
                'type': 'zoom',
                'direction': 'in',
                'speed': 'fast',
                'easing': 'ease_in'
            },
            'emotional_shift': {
                'type': 'crossfade',
                'speed': 'slow',
                'easing': 'ease_in_out'
            }
        }

    # ==================== TEXT EFFECTS ====================
    
    def typewriter_with_cursor(self, text: str, frame: int, total_frames: int,
                              position: Tuple[int, int], font_size: int = 48,
                              color: Tuple[int, int, int] = (255, 255, 255),
                              cursor_blink: bool = True,
                              typing_speed: str = 'variable') -> Image.Image:
        """Advanced typewriter effect with customizable cursor and speed"""
        font = self._get_professional_font(font_size, 'medium')
        
        return self.advanced_effects.typewriter_effect(
            text, frame, total_frames, font, color, position, typing_speed
        )
    
    def cinematic_title_reveal(self, text: str, subtitle: str, frame: int, total_frames: int,
                              style: str = 'epic', palette: str = 'cinematic_warm') -> Image.Image:
        """Cinematic title cards with subtitle support"""
        image = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        colors = self.color_palettes[palette]
        progress = frame / total_frames
        
        # Background with subtle animation
        bg = self.advanced_effects.animated_gradient_background(
            frame, total_frames, 
            [colors['primary'], colors['secondary'], colors['accent']],
            'diagonal', speed=0.5
        )
        image = Image.alpha_composite(image.convert('RGBA'), bg)
        
        if style == 'epic':
            # Main title with dramatic entrance
            main_font = self._get_professional_font(72, 'bold')
            
            # Animate title entrance
            if progress < 0.6:
                # Zoom and fade in
                title_progress = progress / 0.6
                scale = 0.3 + 0.7 * title_progress
                alpha = int(255 * title_progress)
                
                # Position and scale
                title_img = self.advanced_effects.kinetic_typography(
                    text, int(frame * title_progress), int(total_frames * 0.6),
                    main_font, (*colors['primary'], alpha), 'zoom'
                )
                image = Image.alpha_composite(image, title_img)
            
            # Subtitle entrance
            if progress > 0.4 and subtitle:
                subtitle_progress = (progress - 0.4) / 0.6
                subtitle_font = self._get_professional_font(36, 'regular')
                
                subtitle_img = self.advanced_effects.fade_in_words(
                    subtitle, int(frame * subtitle_progress), int(total_frames * 0.6),
                    subtitle_font, colors['accent'], 
                    (self.width // 2, self.height // 2 + 100)
                )
                image = Image.alpha_composite(image, subtitle_img)
                
        elif style == 'minimal':
            # Clean, minimal style
            title_font = self._get_professional_font(64, 'light')
            
            # Simple fade with perfect typography
            title_alpha = int(255 * progress)
            draw.text((self.width // 2, self.height // 2 - 50), text,
                     font=title_font, fill=(*colors['primary'], title_alpha), anchor='mm')
            
            if subtitle and progress > 0.5:
                subtitle_font = self._get_professional_font(28, 'regular')
                subtitle_alpha = int(255 * (progress - 0.5) / 0.5)
                draw.text((self.width // 2, self.height // 2 + 50), subtitle,
                         font=subtitle_font, fill=(*colors['secondary'], subtitle_alpha), anchor='mm')
        
        # Add subtle particle effects
        particles = self.advanced_effects.particle_system(
            frame, total_frames, count=30, style='floating', 
            motion='gentle', colors=[colors['accent'], colors['highlight']]
        )
        image = Image.alpha_composite(image, particles)
        
        return image
    
    def kinetic_text_emphasis(self, text: str, emphasis_words: List[str],
                             frame: int, total_frames: int,
                             base_position: Tuple[int, int],
                             style: str = 'bounce') -> Image.Image:
        """Kinetic typography with word emphasis"""
        
        return self.advanced_effects.fade_in_words(
            text, frame, total_frames,
            self._get_professional_font(42), 
            self.color_palettes['kiin_brand']['primary'],
            base_position, emphasis_words
        )
    
    def subtitle_professional(self, text: str, frame: int, total_frames: int,
                             timing: str = 'standard') -> Image.Image:
        """Professional subtitle styling with timing"""
        
        return self.advanced_effects.subtitle_popup_animation(
            text, frame, total_frames,
            self._get_professional_font(38, 'medium'),
            (255, 255, 255), (0, 0, 0)
        )

    # ==================== BACKGROUND SYSTEMS ====================
    
    def animated_gradient_pro(self, frame: int, total_frames: int,
                             palette: str = 'kiin_brand',
                             style: str = 'flowing',
                             intensity: float = 1.0) -> Image.Image:
        """Professional animated gradients with brand consistency"""
        colors = list(self.color_palettes[palette].values())[:3]
        
        if style == 'flowing':
            return self.advanced_effects.animated_gradient_background(
                frame, total_frames, colors, 'radial', speed=0.3, pattern='wave'
            )
        elif style == 'cinematic':
            return self.advanced_effects.animated_gradient_background(
                frame, total_frames, colors, 'diagonal', speed=0.2, pattern='linear'
            )
        elif style == 'energetic':
            return self.advanced_effects.animated_gradient_background(
                frame, total_frames, colors, 'vertical', speed=1.0, pattern='wave'
            )
        else:
            return self.advanced_effects.animated_gradient_background(
                frame, total_frames, colors, 'vertical', speed=0.5, pattern='linear'
            )
    
    def premium_particle_system(self, frame: int, total_frames: int,
                               theme: str = 'professional',
                               density: str = 'medium') -> Image.Image:
        """Premium particle effects for different content themes"""
        
        density_map = {'low': 20, 'medium': 50, 'high': 100}
        count = density_map.get(density, 50)
        
        if theme == 'professional':
            colors = [self.color_palettes['kiin_brand']['primary'],
                     self.color_palettes['kiin_brand']['secondary']]
            return self.advanced_effects.particle_system(
                frame, total_frames, count, 'floating', 'gentle', colors
            )
        elif theme == 'energetic':
            colors = [self.color_palettes['cinematic_warm']['accent'],
                     self.color_palettes['cinematic_warm']['primary']]
            return self.advanced_effects.particle_system(
                frame, total_frames, count, 'sparkles', 'rising', colors
            )
        elif theme == 'calming':
            colors = [self.color_palettes['organic']['primary'],
                     self.color_palettes['organic']['highlight']]
            return self.advanced_effects.particle_system(
                frame, total_frames, count, 'bubbles', 'gentle', colors
            )
        else:
            return self.advanced_effects.particle_system(
                frame, total_frames, count, 'floating', 'gentle', 
                [(255, 255, 255), (200, 200, 255)]
            )
    
    def cinematic_bokeh(self, frame: int, total_frames: int,
                       mood: str = 'warm', intensity: float = 0.7) -> Image.Image:
        """Cinematic bokeh effects for emotional depth"""
        
        color_schemes = {
            'warm': 'sunset',
            'cool': 'ocean', 
            'dramatic': 'monochrome',
            'peaceful': 'forest',
            'energetic': 'vibrant'
        }
        
        scheme = color_schemes.get(mood, 'warm')
        return self.advanced_effects.bokeh_overlay(frame, total_frames, intensity, scheme)
    
    def dynamic_pattern_overlay(self, frame: int, total_frames: int,
                               pattern: str = 'noise', strength: float = 0.15) -> Image.Image:
        """Dynamic pattern overlays for texture and depth"""
        
        return self.advanced_effects.pattern_overlay(
            frame, total_frames, pattern, strength, animated=True
        )

    # ==================== TRANSITION EFFECTS ====================
    
    def smart_scene_transition(self, image_a: Image.Image, image_b: Image.Image,
                              frame: int, total_frames: int,
                              scene_context: str = 'neutral') -> Image.Image:
        """Context-aware scene transitions"""
        
        preset = self.transition_presets.get(scene_context, self.transition_presets['emotional_shift'])
        
        if preset['type'] == 'crossfade':
            return self.advanced_effects.crossfade_transition(
                image_a, image_b, frame, total_frames, preset['easing']
            )
        elif preset['type'] == 'slide':
            return self.advanced_effects.slide_transition(
                image_a, image_b, frame, total_frames, preset['direction']
            )
        elif preset['type'] == 'zoom':
            return self.advanced_effects.zoom_transition(
                image_a, image_b, frame, total_frames, preset['direction']
            )
        elif preset['type'] == 'morph':
            return self.advanced_effects.morph_transition(
                image_a, image_b, frame, total_frames, preset['style']
            )
        else:
            return self.advanced_effects.crossfade_transition(
                image_a, image_b, frame, total_frames
            )
    
    def emotional_transition(self, image_a: Image.Image, image_b: Image.Image,
                           frame: int, total_frames: int,
                           emotion_from: str, emotion_to: str) -> Image.Image:
        """Emotion-based transitions (anxiety->calm, sad->hopeful, etc.)"""
        
        # Map emotions to transition styles
        emotion_map = {
            ('anxiety', 'calm'): 'ripple_out',
            ('sad', 'hopeful'): 'gentle_zoom',
            ('angry', 'peaceful'): 'wave_wash',
            ('confused', 'clear'): 'focus_pull',
            ('tired', 'energized'): 'burst_in'
        }
        
        transition_key = (emotion_from, emotion_to)
        style = emotion_map.get(transition_key, 'crossfade')
        
        if style == 'ripple_out':
            return self.advanced_effects.morph_transition(image_a, image_b, frame, total_frames, 'ripple')
        elif style == 'gentle_zoom':
            return self.advanced_effects.zoom_transition(image_a, image_b, frame, total_frames, 'in')
        elif style == 'wave_wash':
            return self.advanced_effects.morph_transition(image_a, image_b, frame, total_frames, 'elastic')
        else:
            return self.advanced_effects.crossfade_transition(image_a, image_b, frame, total_frames, 'ease_out')

    # ==================== VISUAL POLISH ====================
    
    def professional_text_treatment(self, text_image: Image.Image,
                                   style: str = 'premium') -> Image.Image:
        """Professional text treatments (shadows, glows, outlines)"""
        
        if style == 'premium':
            # Multiple shadow layers for depth
            result = self.advanced_effects.add_drop_shadow(text_image, (3, 3), 2, (0, 0, 0), 0.3)
            result = self.advanced_effects.add_drop_shadow(result, (6, 6), 4, (0, 0, 0), 0.15)
            return result
            
        elif style == 'glow':
            return self.advanced_effects.add_glow_effect(text_image, (255, 255, 255), 0.8, 12)
            
        elif style == 'dramatic':
            # High contrast with strong shadows
            result = self.advanced_effects.add_drop_shadow(text_image, (8, 8), 6, (0, 0, 0), 0.8)
            result = self.advanced_effects.add_glow_effect(result, (255, 255, 255), 0.4, 6)
            return result
            
        else:
            return text_image
    
    def cinematic_color_grading(self, image: Image.Image, grade: str = 'warm') -> Image.Image:
        """Professional color grading presets"""
        
        return self.advanced_effects.apply_color_grading(image, grade)
    
    def adaptive_vignette(self, image: Image.Image, content_type: str = 'standard') -> Image.Image:
        """Content-aware vignette application"""
        
        intensity_map = {
            'dramatic': 0.8,
            'cinematic': 0.6,
            'standard': 0.4,
            'subtle': 0.2,
            'bright': 0.1
        }
        
        intensity = intensity_map.get(content_type, 0.4)
        return self.advanced_effects.add_vignette(image, intensity)
    
    def film_grain_texture(self, image: Image.Image, style: str = 'modern') -> Image.Image:
        """Professional film grain and texture"""
        
        grain_amounts = {
            'vintage': 0.3,
            'classic': 0.2,
            'modern': 0.1,
            'subtle': 0.05
        }
        
        amount = grain_amounts.get(style, 0.1)
        return self.advanced_effects.add_film_grain(image, amount)

    # ==================== MOTION GRAPHICS ====================
    
    def progress_visualization(self, frame: int, total_frames: int,
                             progress_value: float, style: str = 'modern',
                             context: str = 'tip_progress') -> Image.Image:
        """Advanced progress indicators for different contexts"""
        
        color = self.color_palettes['kiin_brand']['primary']
        
        return self.motion_graphics.progress_indicator(
            frame, total_frames, progress_value, style, color
        )
    
    def animated_icons_library(self, frame: int, total_frames: int,
                              icon_type: str, context: str = 'neutral') -> Image.Image:
        """Library of animated icons for content enhancement"""
        
        color_contexts = {
            'positive': self.color_palettes['kiin_brand']['success'],
            'negative': self.color_palettes['kiin_brand']['danger'], 
            'warning': self.color_palettes['kiin_brand']['warning'],
            'neutral': self.color_palettes['kiin_brand']['primary'],
            'emotional': self.color_palettes['cinematic_warm']['primary']
        }
        
        color = color_contexts.get(context, self.color_palettes['kiin_brand']['primary'])
        
        return self.motion_graphics.animated_icon(
            frame, total_frames, icon_type, color
        )
    
    def data_story_charts(self, frame: int, total_frames: int,
                         data: List[float], chart_type: str = 'impact',
                         story_context: str = 'improvement') -> Image.Image:
        """Storytelling through animated data visualization"""
        
        # Map story context to labels and colors
        story_configs = {
            'improvement': {
                'labels': ['Before', 'After', 'Goal'],
                'colors': 'success_progression'
            },
            'comparison': {
                'labels': ['Option A', 'Option B', 'Recommended'],
                'colors': 'comparison'
            },
            'progress': {
                'labels': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                'colors': 'progression'
            }
        }
        
        config = story_configs.get(story_context, story_configs['improvement'])
        
        return self.motion_graphics.chart_animation(
            frame, total_frames, data, config['labels'], chart_type, 'professional'
        )
    
    def call_to_action_pro(self, frame: int, total_frames: int,
                          cta_text: str, urgency: str = 'medium') -> Image.Image:
        """Professional call-to-action animations"""
        
        style_map = {
            'low': 'fade',
            'medium': 'pulse', 
            'high': 'bounce',
            'urgent': 'glow'
        }
        
        style = style_map.get(urgency, 'pulse')
        
        return self.motion_graphics.call_to_action_animation(
            frame, total_frames, cta_text, style
        )
    
    def logo_brand_animation(self, frame: int, total_frames: int,
                           animation_style: str = 'signature') -> Image.Image:
        """Professional brand logo animations"""
        
        return self.motion_graphics.logo_animation(
            frame, total_frames, None, animation_style
        )

    # ==================== ADVANCED COMPOSITIONS ====================
    
    def layered_composition(self, layers: List[Dict], frame: int, total_frames: int) -> Image.Image:
        """Professional multi-layer composition"""
        result = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        
        for layer in layers:
            layer_image = layer['image']
            blend_mode = layer.get('blend_mode', 'normal')
            opacity = layer.get('opacity', 1.0)
            
            # Apply opacity
            if opacity < 1.0:
                layer_image = self._apply_opacity(layer_image, opacity)
            
            # Apply blend mode
            if blend_mode == 'multiply':
                result = self._blend_multiply(result, layer_image)
            elif blend_mode == 'overlay':
                result = self._blend_overlay(result, layer_image)
            elif blend_mode == 'screen':
                result = self._blend_screen(result, layer_image)
            else:  # normal
                result = Image.alpha_composite(result, layer_image)
        
        return result
    
    def parallax_background_system(self, frame: int, total_frames: int,
                                  theme: str = 'minimal') -> Image.Image:
        """Professional parallax background systems"""
        
        # Create multiple layers for parallax
        layers = []
        
        if theme == 'minimal':
            # Subtle geometric shapes moving at different speeds
            bg_layer = self._create_geometric_layer(frame, total_frames, 'circles', 0.2)
            mid_layer = self._create_geometric_layer(frame, total_frames, 'lines', 0.5)
            
            layers = [
                {'image': bg_layer, 'speed': 0.2, 'direction': 'horizontal', 'opacity': 0.3},
                {'image': mid_layer, 'speed': 0.5, 'direction': 'vertical', 'opacity': 0.2}
            ]
            
        elif theme == 'organic':
            # Natural flowing patterns
            wave_layer = self._create_wave_layer(frame, total_frames, 'gentle')
            particle_layer = self.premium_particle_system(frame, total_frames, 'calming', 'low')
            
            layers = [
                {'image': wave_layer, 'speed': 0.3, 'direction': 'horizontal', 'opacity': 0.4},
                {'image': particle_layer, 'speed': 0.1, 'direction': 'vertical', 'opacity': 0.6}
            ]
        
        return self.advanced_effects.parallax_layers(frame, total_frames, layers)
    
    def mood_responsive_effects(self, base_image: Image.Image, 
                               mood: str, intensity: float = 1.0) -> Image.Image:
        """Apply effects based on content mood"""
        
        result = base_image.copy()
        
        if mood == 'energetic':
            # Bright, saturated, high contrast
            enhancer = ImageEnhance.Color(result)
            result = enhancer.enhance(1.3 * intensity)
            enhancer = ImageEnhance.Contrast(result)
            result = enhancer.enhance(1.2 * intensity)
            
        elif mood == 'calming':
            # Soft, muted, low contrast
            enhancer = ImageEnhance.Color(result)
            result = enhancer.enhance(0.8)
            enhancer = ImageEnhance.Brightness(result)
            result = enhancer.enhance(1.1)
            result = result.filter(ImageFilter.GaussianBlur(radius=0.5 * intensity))
            
        elif mood == 'dramatic':
            # High contrast, desaturated
            enhancer = ImageEnhance.Contrast(result)
            result = enhancer.enhance(1.4 * intensity)
            enhancer = ImageEnhance.Color(result)
            result = enhancer.enhance(0.7)
            
        elif mood == 'warm':
            # Warm tones, soft glow
            result = self.cinematic_color_grading(result, 'warm')
            if intensity > 0.5:
                result = self.advanced_effects.add_glow_effect(result, (255, 200, 150), 0.3 * intensity, 8)
                
        elif mood == 'professional':
            # Clean, sharp, balanced
            enhancer = ImageEnhance.Sharpness(result)
            result = enhancer.enhance(1.1 * intensity)
            enhancer = ImageEnhance.Contrast(result)
            result = enhancer.enhance(1.05 * intensity)
        
        return result

    # ==================== PERFORMANCE OPTIMIZATIONS ====================
    
    def create_effect_sequence(self, effects_config: Dict, total_frames: int) -> List[Callable]:
        """Pre-calculate effect sequence for performance"""
        sequence = []
        
        for frame in range(total_frames):
            frame_effects = []
            for effect_name, config in effects_config.items():
                if self._should_apply_effect(effect_name, config, frame, total_frames):
                    frame_effects.append((effect_name, config))
            sequence.append(frame_effects)
        
        return sequence
    
    def batch_process_effects(self, images: List[Image.Image], 
                             effects: List[str]) -> List[Image.Image]:
        """Batch process multiple images with same effects"""
        results = []
        
        for image in images:
            result = image
            for effect in effects:
                if hasattr(self, effect):
                    effect_func = getattr(self, effect)
                    result = effect_func(result)
            results.append(result)
        
        return results

    # ==================== UTILITY METHODS ====================
    
    def _get_professional_font(self, size: int, weight: str = 'regular') -> ImageFont.FreeTypeFont:
        """Get professional typography"""
        try:
            weight_map = {
                'light': 'HelveticaNeue-Light',
                'regular': 'HelveticaNeue',
                'medium': 'HelveticaNeue-Medium',
                'bold': 'HelveticaNeue-Bold'
            }
            
            font_name = weight_map.get(weight, 'HelveticaNeue')
            
            font_paths = [
                f"/System/Library/Fonts/{font_name}.ttc",
                f"/System/Library/Fonts/Helvetica.ttc",
                "/System/Library/Fonts/Arial.ttf"
            ]
            
            for path in font_paths:
                if os.path.exists(path):
                    return ImageFont.truetype(path, size)
            
            return ImageFont.load_default()
            
        except Exception:
            return ImageFont.load_default()
    
    def _apply_opacity(self, image: Image.Image, opacity: float) -> Image.Image:
        """Apply opacity to image"""
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Get alpha channel
        alpha = image.split()[-1]
        # Apply opacity
        alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
        # Reassemble image
        image.putalpha(alpha)
        return image
    
    def _blend_multiply(self, base: Image.Image, overlay: Image.Image) -> Image.Image:
        """Multiply blend mode"""
        # Simplified multiply blend
        if base.mode != 'RGBA':
            base = base.convert('RGBA')
        if overlay.mode != 'RGBA':
            overlay = overlay.convert('RGBA')
        
        # For simplicity, use alpha composite
        return Image.alpha_composite(base, overlay)
    
    def _blend_overlay(self, base: Image.Image, overlay: Image.Image) -> Image.Image:
        """Overlay blend mode"""
        return Image.alpha_composite(base, overlay)
    
    def _blend_screen(self, base: Image.Image, overlay: Image.Image) -> Image.Image:
        """Screen blend mode"""
        return Image.alpha_composite(base, overlay)
    
    def _should_apply_effect(self, effect_name: str, config: Dict, 
                           frame: int, total_frames: int) -> bool:
        """Determine if effect should be applied at this frame"""
        start_frame = config.get('start_frame', 0)
        end_frame = config.get('end_frame', total_frames)
        
        return start_frame <= frame < end_frame
    
    def _create_geometric_layer(self, frame: int, total_frames: int,
                               shape_type: str, speed: float) -> Image.Image:
        """Create geometric pattern layer"""
        image = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        time_offset = (frame / total_frames) * speed * 100
        
        if shape_type == 'circles':
            for i in range(5):
                x = (i * 200 + time_offset) % (self.width + 100) - 50
                y = (i * 150) % self.height
                radius = 30 + 20 * math.sin(frame * 0.1 + i)
                
                draw.ellipse([x - radius, y - radius, x + radius, y + radius],
                           outline=(255, 255, 255, 50), width=2)
                           
        elif shape_type == 'lines':
            for i in range(10):
                y = (i * 100 + time_offset) % (self.height + 50) - 25
                draw.line([(0, y), (self.width, y)], fill=(255, 255, 255, 30), width=1)
        
        return image
    
    def _create_wave_layer(self, frame: int, total_frames: int, style: str) -> Image.Image:
        """Create wave pattern layer"""
        image = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        
        for y in range(0, self.height, 4):
            for x in range(0, self.width, 4):
                wave = math.sin((x + frame * 2) * 0.01) * math.sin((y + frame) * 0.008)
                alpha = int(abs(wave) * 50)
                
                if alpha > 0:
                    color = (255, 255, 255, alpha)
                    image.putpixel((x, y), color)
        
        return image

    # ==================== VIDEO GENERATION HELPERS ====================
    
    def create_professional_video_frame(self, content: Dict, frame: int, total_frames: int,
                                      section_type: str = 'standard') -> Image.Image:
        """Create a complete professional video frame"""
        
        # Base composition
        base = self.animated_gradient_pro(frame, total_frames, 'kiin_brand', 'flowing')
        
        # Add background effects based on section type
        if section_type in ['dramatic', 'problem']:
            particles = self.premium_particle_system(frame, total_frames, 'professional', 'low')
            base = Image.alpha_composite(base, particles)
            
        elif section_type in ['solution', 'positive']:
            particles = self.premium_particle_system(frame, total_frames, 'energetic', 'medium')
            bokeh = self.cinematic_bokeh(frame, total_frames, 'warm', 0.5)
            base = Image.alpha_composite(base, particles)
            base = Image.alpha_composite(base, bokeh)
        
        # Add content-specific effects
        if 'title' in content:
            title_effect = self.cinematic_title_reveal(
                content['title'], content.get('subtitle', ''),
                frame, total_frames, 'epic', 'cinematic_warm'
            )
            base = Image.alpha_composite(base, title_effect)
        
        # Apply mood-responsive effects
        mood = content.get('mood', 'professional')
        base = self.mood_responsive_effects(base, mood)
        
        # Add finishing touches
        base = self.adaptive_vignette(base, section_type)
        base = self.film_grain_texture(base, 'modern')
        
        return base


# Main Effects Instance
def create_effects_library(width: int = 1080, height: int = 1920, fps: int = 30) -> KiinEffectsLibrary:
    """Factory function to create effects library"""
    return KiinEffectsLibrary(width, height, fps)


# Export main class and factory
__all__ = ['KiinEffectsLibrary', 'create_effects_library']