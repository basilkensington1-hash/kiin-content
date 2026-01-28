# Kiin Video Effects System

Complete intro/outro and video effects system for branded content creation.

## Quick Start

1. **Generate an intro:**
   ```bash
   python src/intro_generator.py --style minimal --output intro.mp4
   ```

2. **Generate an outro:**
   ```bash
   python src/outro_generator.py --cta "Follow @kiinapp" --output outro.mp4
   ```

3. **Assemble complete video:**
   ```bash
   python src/video_assembler.py --main content.mp4 --add-intro --add-outro --output final.mp4
   ```

## Components

### 1. Effects Library (`src/effects.py`)
Core video effects using FFmpeg:
- Fade in/out
- Ken Burns effect (subtle zoom/pan) 
- Color grading (warm, cool, professional)
- Video information extraction
- Background generation

### 2. Intro Generator (`src/intro_generator.py`)
Branded intro clips (2-3 seconds):
- Logo animations (fade/scale, slide-in, quick fade)
- Multiple styles: minimal, warm, professional
- Brand color integration
- Automatic fade-in effects

### 3. Outro Generator (`src/outro_generator.py`) 
Branded outro clips (3-5 seconds):
- Multiple CTA templates
- Social media handle integration
- Various layout styles
- Fade-out effects

### 4. Video Assembler (`src/video_assembler.py`)
Combine intro + content + outro:
- Automatic intro/outro generation
- Smooth transitions between segments
- Audio normalization
- Quality optimization
- Batch processing
- Template system

## Command Examples

### Intro Generation
```bash
# List available styles
python src/intro_generator.py --list-styles

# Generate different styles
python src/intro_generator.py --style minimal --output intro.mp4
python src/intro_generator.py --style warm --duration 2 --output intro.mp4
python src/intro_generator.py --style professional --output intro.mp4
```

### Outro Generation
```bash
# List available CTA templates
python src/outro_generator.py --list-ctas

# Generate with different CTAs
python src/outro_generator.py --cta follow --output outro.mp4
python src/outro_generator.py --cta save --style minimal --output outro.mp4
python src/outro_generator.py --cta "Custom message!" --output outro.mp4

# Change social handle
python src/outro_generator.py --cta follow --social-handle "@myhandle" --output outro.mp4
```

### Video Assembly
```bash
# Auto-generate intro and outro
python src/video_assembler.py --main content.mp4 --add-intro --add-outro --output final.mp4

# Use existing intro/outro files
python src/video_assembler.py --main content.mp4 --intro intro.mp4 --outro outro.mp4 --output final.mp4

# Customize styles
python src/video_assembler.py --main content.mp4 --add-intro --add-outro \
  --intro-style warm --outro-style minimal --outro-cta save --output final.mp4

# Use templates
python src/video_assembler.py --main content.mp4 --template social_post --output final.mp4
python src/video_assembler.py --main content.mp4 --template tutorial --output final.mp4

# Batch processing
python src/video_assembler.py --batch-input-dir ./videos --batch-output-dir ./output --template social_post
```

## Templates

Pre-configured video templates for common use cases:

- **social_post**: Minimal intro + standard outro + follow CTA
- **tutorial**: Professional intro + save CTA
- **story**: Warm outro only with "more" CTA  
- **quick_tip**: Minimal intro/outro with save CTA

## Technical Requirements

- **FFmpeg**: Required for all video processing
- **Python 3.7+**: With Pillow and numpy
- **Brand Assets**: Logo and color configuration in `brand/` directory

## File Structure
```
src/
├── effects.py           # Core video effects library
├── intro_generator.py   # Generate branded intros
├── outro_generator.py   # Generate branded outros  
├── video_assembler.py   # Combine video segments
└── brand_utils.py       # Brand asset utilities

templates/
├── README.md            # Template documentation
├── intro_*.mp4          # Example intro templates
└── outro_*.mp4          # Example outro templates
```

## Brand Integration

The system automatically uses:
- Logo from `brand/logo.png`
- Colors from `brand/colors.json`
- Fonts from `brand/fonts.json`
- Watermark from `brand/watermark.png`

All visual elements match the Kiin brand guidelines with warm, trustworthy colors and clean typography.

## Performance Notes

- Uses FFmpeg's `fast` preset for reasonable speed
- Temporary files are automatically cleaned up
- Batch processing supported for multiple videos
- Output optimized for social media (1080x1920)

## Troubleshooting

**"Filter not found" errors**: Some FFmpeg builds have limited filters. The system falls back to simpler effects when advanced filters aren't available.

**Missing logo/brand assets**: Ensure `brand/logo.png` exists and brand configuration files are present.

**Memory issues**: Large videos or batch processing may require sufficient disk space for temporary files.

## Examples in Templates Directory

See `templates/README.md` for detailed examples and the `templates/` directory for sample output files demonstrating each style and effect.