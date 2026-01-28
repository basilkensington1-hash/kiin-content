# Kiin Video Effects Templates

This directory contains example templates and guides for the Kiin video effects system.

## Available Templates

### Intro Templates
- `intro_minimal_example.mp4` - Clean, simple 2s intro
- `intro_warm_example.mp4` - Warm, welcoming 3s intro  
- `intro_professional_example.mp4` - Professional 2s intro

### Outro Templates  
- `outro_standard_example.mp4` - Standard 4s outro with follow CTA
- `outro_minimal_example.mp4` - Minimal 3.5s outro with save CTA

## Usage Examples

### Generate Custom Intro
```bash
# Minimal style, 2 seconds
python src/intro_generator.py --style minimal --duration 2 --output my_intro.mp4

# Warm style with default duration
python src/intro_generator.py --style warm --output warm_intro.mp4

# Professional style  
python src/intro_generator.py --style professional --output pro_intro.mp4
```

### Generate Custom Outro
```bash
# Follow CTA with standard style
python src/outro_generator.py --cta follow --style standard --output my_outro.mp4

# Custom CTA text
python src/outro_generator.py --cta "Subscribe for more tips!" --output custom_outro.mp4

# Save CTA with minimal style
python src/outro_generator.py --cta save --style minimal --output save_outro.mp4
```

### Assemble Complete Video
```bash
# With intro and outro
python src/video_assembler.py --main content.mp4 --add-intro --add-outro --output final.mp4

# Using pre-made intro/outro
python src/video_assembler.py --main content.mp4 --intro intro.mp4 --outro outro.mp4 --output final.mp4

# Using template
python src/video_assembler.py --main content.mp4 --template social_post --output final.mp4
```

## Available Styles

### Intro Styles
- **minimal**: Clean, simple logo animation (2.5s default)
- **warm**: Welcoming with warm colors (3.0s default)  
- **professional**: Quick, business-focused (2.0s default)

### Outro Styles
- **standard**: Primary color background with logo (4.0s default)
- **warm**: Warm background colors (5.0s default)
- **minimal**: Clean, simple design (3.5s default)
- **gradient**: Gradient background (4.5s default)

## CTA Templates
- **follow**: "Follow @kiinapp for more"
- **save**: "Save this for later"  
- **share**: "Share with friends"
- **like**: "Like if this helped"
- **subscribe**: "Subscribe for daily tips"
- **comment**: "Comment your thoughts"
- **more**: "More content like this daily"
- **app**: "Try Kiin app - link in bio"

## Video Templates

### social_post
- Minimal intro + standard outro with follow CTA
- Smooth transitions enabled

### tutorial  
- Professional intro + standard outro with save CTA
- No transitions (clean cuts)

### story
- No intro + warm outro with "more" CTA  
- Smooth transitions

### quick_tip
- Minimal intro + minimal outro with save CTA
- No transitions

## Technical Notes

- Default video size: 1080x1920 (9:16 aspect ratio for social media)
- Output format: MP4 with H.264 encoding
- Audio: AAC encoding when present
- All effects use FFmpeg for maximum compatibility

## Batch Processing

Process multiple videos at once:
```bash
python src/video_assembler.py --batch-input-dir ./raw_videos --batch-output-dir ./final_videos --template social_post
```

## Customization

The brand colors, fonts, and other assets can be customized in the `brand/` directory. The effects system automatically uses the current brand configuration.