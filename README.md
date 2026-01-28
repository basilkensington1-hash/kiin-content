# "You're Not Alone" Validation Series Generator

A fully automated content pipeline for generating caregiver validation videos with calming visuals and gentle audio.

## Overview

This tool creates short (12-20 second), vertical (9:16) videos that provide emotional validation for caregivers. Each video features calming gradient backgrounds, elegant text animation, and gentle text-to-speech narration of carefully crafted validation messages.

## Features

- **FREE tools only**: Uses edge-tts, FFmpeg, and PIL
- **Professional quality**: 1080x1920 vertical videos optimized for social media
- **Emotional intelligence**: 24 carefully crafted validation messages across 4 categories
- **Automated pipeline**: Generate videos with a single command
- **Customizable**: Use custom messages or select from predefined categories

## Installation

1. **Clone and setup**:
   ```bash
   cd /Users/nick/clawd/kiin-content
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Install FFmpeg** (if not already installed):
   ```bash
   # macOS
   brew install ffmpeg
   
   # Ubuntu/Debian
   sudo apt update && sudo apt install ffmpeg
   
   # Windows
   # Download from https://ffmpeg.org/download.html
   ```

## Usage

### Basic Usage

Generate a random validation video:
```bash
source venv/bin/activate
python src/validation_generator.py --output my_video.mp4
```

### Custom Message

Create a video with your own message:
```bash
python src/validation_generator.py \
  --message "You're doing better than you think you are. 💙" \
  --output custom_validation.mp4
```

### Category-Specific Videos

Generate from specific validation categories:
```bash
# Permission statements
python src/validation_generator.py --category permission_statements --output permission.mp4

# Guilt relief
python src/validation_generator.py --category guilt_relief --output guilt_relief.mp4

# Burnout acknowledgment  
python src/validation_generator.py --category burnout_acknowledgment --output burnout.mp4

# Caregiver identity
python src/validation_generator.py --category caregiver_identity --output identity.mp4
```

## Message Categories

### Permission Statements
Messages that give caregivers explicit permission to feel and need things:
- "You're allowed to feel frustrated..."
- "It's okay to say no sometimes..."
- "You're allowed to grieve the life you planned..."

### Guilt Relief  
Messages that address common caregiver guilt:
- "That moment when you snapped at them? You're not a monster..."
- "You're not failing because you had to ask for help..."
- "Your worst caregiving day doesn't erase all your best ones..."

### Burnout Acknowledgment
Messages that validate exhaustion and overwhelm:
- "If you're running on empty today, that's not weakness..."
- "Your exhaustion is real. Your overwhelm is valid..."
- "To the caregiver who feels invisible: I see you..."

### Caregiver Identity
Messages about maintaining personal identity:
- "You are more than just a caregiver..."
- "Before you became their caregiver, you were someone too..."
- "You're not selfish for wanting to remember who you are..."

## Technical Specifications

- **Resolution**: 1080x1920 (9:16 vertical)
- **Frame Rate**: 24 fps (optimized for smooth generation)
- **Duration**: 12-20 seconds (based on message length)
- **Audio**: Microsoft edge-tts "en-US-AriaNeural" voice
- **Visual**: Calming gradient backgrounds with fade-in/stable/fade-out text animation
- **Format**: MP4 with H.264 video and AAC audio

## File Structure

```
kiin-content/
├── src/
│   └── validation_generator.py     # Main generator script
├── config/
│   └── validation_messages.json   # Message database
├── output/
│   └── validation_example.mp4     # Example output
├── requirements.txt                # Python dependencies
└── README.md                      # This file
```

## Customization

### Adding New Messages

Edit `config/validation_messages.json` to add new validation messages:

```json
{
  "your_category": [
    {
      "text": "Your validation message here 💙",
      "duration": 15
    }
  ]
}
```

### Modifying Visual Style

The gradient colors can be customized in the `ValidationVideoGenerator` class:

```python
self.gradient_colors = [
    [(135, 206, 250), (221, 160, 221)],  # Sky blue to plum
    # Add your own color combinations here
]
```

## Performance Notes

- Frame generation is CPU-intensive; expect 1-2 minutes per video
- Progress is shown during generation
- Videos are optimized for social media sharing
- Generated videos are approximately 100-300KB each

## Troubleshooting

### Common Issues

1. **FFmpeg not found**: Install FFmpeg and ensure it's in your PATH
2. **Permission errors**: Ensure output directory is writable
3. **Slow generation**: This is normal; frame generation is CPU-intensive

### Debug Mode

To test individual components:
```python
# Test imports
python -c "import edge_tts; import PIL; import numpy; print('All imports successful')"

# Test message loading
python -c "from src.validation_generator import ValidationVideoGenerator; g = ValidationVideoGenerator(); print(g.get_random_message())"
```

## Example Output

The generated `validation_example.mp4` demonstrates the full pipeline with:
- Elegant gradient background (soft blues and purples)
- Smooth text fade-in animation
- Clear, professional typography
- Gentle female TTS narration
- Appropriate pacing for emotional content

## Production Usage

This tool is designed for:
- Social media content creation (Instagram Stories, TikTok, etc.)
- Caregiver support communities
- Mental health awareness campaigns
- Automated content scheduling

Videos are ready to post without additional editing, though you may add music or branding as needed.

---

*Built with ❤️ for the caregiving community*