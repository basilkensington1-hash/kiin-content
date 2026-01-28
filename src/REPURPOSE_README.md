# Content Repurposing Tool 🔄

A comprehensive tool to transform one piece of content into multiple formats for different social media platforms.

## Features

✅ **Video → Multiple Formats**: Convert one video into square (Instagram), story (TikTok), thumbnails, and quote cards  
✅ **Carousel → Video**: Turn static carousel images into animated videos  
✅ **Quote → Multiple Formats**: Create quote cards, videos, and captions from text  
✅ **Text Extraction**: Extract transcripts from videos for blogs and captions  
✅ **Automated Captions**: Generate platform-optimized social media captions  

## Quick Start

### Installation

```bash
# Install dependencies
source venv/bin/activate  # or activate your virtual environment
pip install -r src/requirements_repurpose.txt

# Ensure ffmpeg is installed (for video processing)
# macOS:
brew install ffmpeg

# Ubuntu/Debian:
sudo apt install ffmpeg
```

### Basic Usage

```bash
# Generate all formats from a video
python src/repurpose.py --input your_video.mp4 --all

# Convert carousel to video
python src/repurpose.py --carousel ./carousels/topic/ --to-video

# Create quote cards and video
python src/repurpose.py --quote "Transform your mindset, transform your life" --all

# Extract transcript only
python src/repurpose.py --extract-text --input video.mp4
```

## Platform Formats

### Video Outputs
- **Square (1080×1080)**: Instagram feed posts
- **Story (1080×1920)**: Instagram Stories, TikTok, YouTube Shorts
- **Landscape (1920×1080)**: YouTube videos, Facebook

### Image Outputs
- **Quote Cards**: Branded graphics with text overlay
- **Thumbnails**: Video preview images
- **Story Graphics**: Vertical format images

### Text Outputs
- **Transcripts**: Full text from video audio
- **Captions**: Platform-optimized social media descriptions
- **Key Quotes**: Extracted impactful statements

## Command Examples

### Video Processing

```bash
# Process a video to all formats
python src/repurpose.py --input content/my_video.mp4 --all --output-dir output/

# This creates:
# - my_video_square.mp4 (Instagram feed)
# - my_video_story.mp4 (Stories/TikTok)
# - my_video_thumbnail.png (YouTube thumbnail)
# - my_video_quote_card.png (Quote graphic)
# - my_video_transcript.txt (Full transcript)
# - my_video_caption.txt (Social media caption)
```

### Carousel Animation

```bash
# Convert existing carousel to video
python src/repurpose.py --carousel ./carousels/communication_tips/ --to-video

# Creates an animated video cycling through each slide
```

### Quote Graphics

```bash
# Create multiple quote formats
python src/repurpose.py --quote "Your powerful message here" --all

# Generates:
# - quote_square.png (Instagram feed)
# - quote_story.png (Stories format)
# - quote_video.mp4 (Animated quote)
# - quote_caption.txt (Social media copy)
```

### Text Extraction

```bash
# Extract transcript for blog posts or newsletters
python src/repurpose.py --extract-text --input webinar.mp4

# Creates: webinar_transcript.txt
```

## Output Structure

```
output/
├── video_square.mp4      # Instagram feed video
├── video_story.mp4       # Stories/TikTok video
├── video_thumbnail.png   # YouTube thumbnail
├── video_quote_card.png  # Quote graphic
├── video_transcript.txt  # Full transcript
└── video_caption.txt     # Social media caption
```

## Customization

### Brand Colors
Edit the `brand_colors` dictionary in `repurpose.py`:

```python
self.brand_colors = {
    'primary': '#YOUR_PRIMARY_COLOR',
    'secondary': '#YOUR_SECONDARY_COLOR',
    'accent': '#YOUR_ACCENT_COLOR',
    # ... more colors
}
```

### Platform Dimensions
Modify the `dimensions` dictionary for custom sizes:

```python
self.dimensions = {
    'square': (1080, 1080),    # Instagram feed
    'story': (1080, 1920),     # Stories/TikTok
    'custom': (1200, 800),     # Your custom format
}
```

## Workflow Integration

### Daily Content Creation
```bash
# Morning: Create original video
# Afternoon: Generate all repurposed formats
python src/repurpose.py --input daily_content.mp4 --all

# Evening: Post across platforms using generated assets
```

### Batch Processing
```bash
# Process multiple videos
for video in content/*.mp4; do
    python src/repurpose.py --input "$video" --all
done
```

### Automation Scripts
Create shell scripts for common workflows:

```bash
#!/bin/bash
# repurpose_daily.sh
VIDEO_DIR="content/$(date +%Y-%m-%d)"
OUTPUT_DIR="output/$(date +%Y-%m-%d)"

for video in "$VIDEO_DIR"/*.mp4; do
    python src/repurpose.py --input "$video" --all --output-dir "$OUTPUT_DIR"
done
```

## Platform-Specific Optimizations

### Instagram
- **Feed**: Use square format videos (1:1)
- **Stories**: Use story format (9:16) with text overlay
- **Reels**: Optimize for mobile viewing, add captions

### TikTok
- **Format**: Always use story format (9:16)
- **Hooks**: Ensure strong opening within first 3 seconds
- **Captions**: Keep text overlay minimal but impactful

### YouTube
- **Thumbnails**: Use generated thumbnails as starting point
- **Shorts**: Use story format content
- **Long-form**: Use transcript for video descriptions

### LinkedIn
- **Posts**: Square or landscape formats work well
- **Captions**: Use more professional language
- **Carousels**: Convert carousel images to LinkedIn document posts

## Troubleshooting

### Common Issues

**FFmpeg not found**
```bash
# Install ffmpeg
brew install ffmpeg  # macOS
sudo apt install ffmpeg  # Ubuntu
```

**OpenCV import error**
```bash
# Install OpenCV
pip install opencv-python
```

**Font errors**
```bash
# The script uses system fonts as fallback
# On macOS: Uses Arial (built-in)
# On Linux: Falls back to default fonts
```

### Performance Tips

- **Batch processing**: Process multiple files together
- **Output organization**: Use dated output directories
- **Storage**: Clean up temporary files regularly

## Advanced Features

### Transcript Enhancement
Install Whisper for better transcription:
```bash
pip install openai-whisper
```

### Custom Quote Extraction
Modify the `extract_key_quote` function to use AI services for better quote selection.

### Automated Posting
Integrate with social media APIs to automatically post generated content.

## Contributing

To extend the repurposing tool:

1. Add new platform dimensions in `dimensions` dictionary
2. Create new processing functions following the existing pattern
3. Update command-line arguments as needed
4. Test with sample content

## Support

For issues or feature requests:
1. Check the existing functionality in `repurpose.py`
2. Review the documentation in `docs/REPURPOSING_GUIDE.md`
3. Test with sample files before processing important content

## License

This tool is part of the KIIN Content creation system.

---

**Quick Reference:**

```bash
# All formats from video
python src/repurpose.py --input video.mp4 --all

# Carousel to video
python src/repurpose.py --carousel ./folder/ --to-video

# Quote to all formats  
python src/repurpose.py --quote "Text" --all

# Extract transcript only
python src/repurpose.py --extract-text --input video.mp4
```