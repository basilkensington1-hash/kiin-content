# Kiin Visual Asset Generators

Professional thumbnail and quote card generators for Kiin content creation with built-in branding and emotional design systems.

## Setup

Both tools require the Pillow library. Use the existing virtual environment:

```bash
cd /Users/nick/clawd/kiin-content
source brand/logo_env/bin/activate
```

## 1. Thumbnail Generator (`thumbnail_generator.py`)

Generate eye-catching thumbnails for various social media platforms with Kiin branding and emotional color schemes.

### Basic Usage

```bash
# Text-based thumbnail
python3 src/thumbnail_generator.py --text "The thing nobody tells you..." --type validation --output thumb.png

# YouTube thumbnail with text
python3 src/thumbnail_generator.py --text "Care coordination tips" --type support --platform youtube --output youtube_thumb.png

# Instagram thumbnail with face placeholder zones
python3 src/thumbnail_generator.py --text "You're not alone" --type warm --platform instagram_feed --faces 2 --output ig_thumb.png

# Extract frame from video (requires ffmpeg)
python3 src/thumbnail_generator.py --video video.mp4 --text "Overlay text" --type validation --output video_thumb.png
```

### Parameters

- `--text`: Text overlay for the thumbnail
- `--video`: Video file to extract frame from (optional, requires ffmpeg)
- `--type`: Emotional color scheme (`validation`, `support`, `energy`, `calm`, `warm`)
- `--platform`: Target platform (`youtube`, `instagram_feed`, `instagram_story`, `twitter`, `facebook`, `linkedin`, `pinterest`, `tiktok`, `default`)
- `--output`: Output file path (auto-generated if not specified)
- `--faces`: Number of face placeholder zones to add (0-3)

### Platform Sizes

- YouTube: 1280x720
- Instagram Feed: 1080x1080  
- Instagram Story: 1080x1920
- Twitter: 1200x675
- Facebook: 1200x630
- LinkedIn: 1200x627
- Pinterest: 1000x1500
- TikTok: 1080x1920

## 2. Quote Card Generator (`quote_card_generator.py`)

Generate beautiful, shareable quote cards for Instagram and Pinterest with elegant typography and Kiin branding.

### Basic Usage

```bash
# Simple quote card
python3 src/quote_card_generator.py --quote "You're not failing. You're learning." --template warm --output quote.png

# Quote card from confession
python3 src/quote_card_generator.py --from-confession 5 --template supportive --output confession_quote.png

# With author attribution
python3 src/quote_card_generator.py --quote "Small steps make a big difference" --author "Kiin Community" --template elegant --output attributed_quote.png

# List all available templates
python3 src/quote_card_generator.py --list-templates
```

### Parameters

- `--quote`: Quote text to use
- `--from-confession`: Extract quote from confession ID (alternative to --quote)
- `--template`: Visual template to use (see templates below)
- `--author`: Quote author/attribution (optional)
- `--size`: Output size (`instagram`, `instagram_story`, `pinterest`, `square`, `wide`)
- `--output`: Output file path (auto-generated if not specified)

### Available Templates

1. **minimal** - Clean, centered text on subtle gradient background
2. **warm** - Warm orange/peach tones with soft decorative elements
3. **supportive** - Calming green tones with nurturing visual elements
4. **elegant** - Sophisticated deep blue design with refined typography
5. **modern** - Contemporary design with bold typography and geometric accents
6. **dreamy** - Soft, ethereal design with light blues and gentle textures
7. **vibrant** - Energetic multi-color gradient with dynamic elements
8. **soft_focus** - Gentle, muted colors with subtle texture and soft edges
9. **confidence** - Bold, empowering design with strong contrasts
10. **serenity** - Peaceful blue-green gradient with tranquil elements

## Features

### Automatic Kiin Branding
- Subtle watermark placement
- Brand-consistent color schemes  
- Professional typography

### Emotional Design Systems
- Color schemes that match content mood
- Typography that conveys the right tone
- Decorative elements that enhance emotion

### Multi-Platform Support
- Optimized dimensions for each platform
- Aspect ratio preservation
- High-quality output

### Professional Typography
- Intelligent text wrapping
- Optimal font sizing
- Readable text shadows and contrasts

## Configuration

### Brand Assets
- Logo: `/brand/logo.png`
- Watermark: `/brand/watermark.png`
- Brand colors: `/brand/brand_config.json`

### Templates
- Quote templates: `/config/quote_templates.json`
- Customize templates by editing this file

### Confessions
- Confession database: `/config/confessions.json`
- Used for `--from-confession` feature

## Examples

### Thumbnail Examples
```bash
# YouTube validation content
python3 src/thumbnail_generator.py --text "The guilt every caregiver feels" --type validation --platform youtube

# Instagram support post
python3 src/thumbnail_generator.py --text "You're doing better than you think" --type warm --platform instagram_feed --faces 1

# Pinterest energy content
python3 src/thumbnail_generator.py --text "5 Ways to Recharge as a Caregiver" --type energy --platform pinterest
```

### Quote Card Examples
```bash
# Supportive Instagram post
python3 src/quote_card_generator.py --quote "Taking breaks doesn't make you selfish. It makes you human." --template supportive --size instagram

# Elegant Pinterest pin
python3 src/quote_card_generator.py --quote "Strength isn't about carrying everything alone" --template elegant --size pinterest

# Warm story post
python3 src/quote_card_generator.py --quote "Every small act of care matters" --template warm --size instagram_story
```

## Output Quality

Both generators produce high-quality PNG files optimized for:
- Social media platforms
- Print materials (if needed)
- Web display
- Professional presentations

All outputs maintain Kiin's brand consistency while being visually engaging and platform-appropriate.