# Instagram Carousel Generator for Caregiver Content

Professional-quality carousel slides for Instagram that generate 3x more engagement than single posts. Designed specifically for caregivers and support communities.

## Features

- **5 Template Types:** Tips, Signs, Communication, Myth-busting, and Story-based formats
- **Professional Design:** Clean, modern layouts with consistent branding
- **Instagram Optimized:** 1080x1080 PNG images ready for direct upload
- **Progress Indicators:** Dot navigation and swipe hints
- **10+ Pre-written Topics:** Ready-to-use caregiver content
- **Easy Customization:** JSON-based content database for quick updates

## Quick Start

1. **Setup Virtual Environment:**
   ```bash
   cd kiin-content
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Generate Your First Carousel:**
   ```bash
   python src/carousel_generator.py --topic communication_tips
   ```

3. **Upload to Instagram:**
   - Open Instagram app
   - Create new post → Select Multiple
   - Choose all generated slides in order
   - Add caption and hashtags
   - Post! 🚀

## Usage

### List Available Topics
```bash
python src/carousel_generator.py --list
```

### Get Topic Information
```bash
python src/carousel_generator.py --info communication_tips
```

### Generate Specific Carousel
```bash
python src/carousel_generator.py --topic communication_tips --output-dir ./my-carousels/
```

### Available Topics

| Topic | Template | Description |
|-------|----------|-------------|
| `communication_tips` | Tips | 5 ways to communicate better with your loved one |
| `burnout_signs` | Signs | Warning signs of caregiver burnout |
| `guilt_phrases` | Communication | What to say instead of guilt-inducing phrases |
| `dementia_myths` | Truth | Common myths about dementia care |
| `self_care_journey` | Story | A caregiver's path from burnout to balance |
| `medication_tips` | Tips | Safe medication management strategies |
| `respite_care` | Tips | Finding and using quality respite care |
| `hospital_advocacy` | Tips | Advocating effectively in hospital settings |
| `financial_planning` | Tips | Planning for long-term care costs |
| `depression_signs` | Signs | Recognizing caregiver depression |

## Template Types

### 🎯 Tips Format
Perfect for educational "how-to" content:
- Cover: "5 Tips for [Topic]"
- Slides: One actionable tip per slide
- Visual: Clean layout with icons and large text

### ⚠️ Signs Format  
Ideal for awareness and recognition:
- Cover: "5 Signs You Might Be [Topic]"
- Slides: Warning signs or symptoms
- Visual: Attention-grabbing orange headers

### 💬 Communication Format
Great for conversation guides:
- Cover: "What to Say Instead of [Topic]"
- Slides: Split design showing wrong vs right phrases
- Visual: Red/green color coding

### 🔍 Truth Format
Perfect for myth-busting content:
- Cover: "The Truth About [Topic]"
- Slides: Myth vs Reality comparisons
- Visual: Clear fact-checking layout

### 📖 Story Format
Engaging narrative progression:
- Cover: "[Topic]: A Caregiver's Journey" 
- Slides: Chapter-based storytelling
- Visual: Emotion-based color themes

## Customization

### Adding New Topics

Edit `config/carousel_content.json`:

```json
{
  "topics": {
    "your_new_topic": {
      "template": "tips",
      "title": "Your Topic Title",
      "hook": "Compelling subtitle that draws people in",
      "slides": [
        {
          "title": "First Tip",
          "content": "Detailed explanation of the tip...",
          "visual_hint": "💡"
        }
      ]
    }
  }
}
```

### Brand Colors

Customize the color scheme in the JSON file:

```json
{
  "brand": {
    "colors": {
      "primary": "#2C5F77",    // Main brand color
      "secondary": "#7FB3C8",  // Accent color
      "accent": "#F4A460",     // Highlight color
      "background": "#FEFEFE", // Background
      "text_dark": "#2C3E50",  // Dark text
      "text_light": "#FFFFFF"  // Light text
    }
  }
}
```

## Instagram Best Practices

### Engagement Tips
- **Hook in first 3 words:** Start covers with attention-grabbing phrases
- **One point per slide:** Don't overcrowd content
- **Include CTAs:** Every carousel ends with clear call-to-action
- **Use swipe hints:** Help users know there's more content

### Caption Strategy
```
🧠 Better communication transforms relationships.

Which tip will you try first? 

Save this post for when you need it →

Follow @youraccount for more caregiver tips
#caregiver #communication #mentalhealth #support
```

### Hashtag Strategy
Mix popular and niche tags:
- **Popular:** #caregiver #mentalhealth #selfcare
- **Niche:** #caregiverburnout #dementia #eldercare
- **Branded:** Your unique hashtags

## Technical Details

- **Image Format:** PNG (high quality, transparent backgrounds)
- **Dimensions:** 1080x1080 pixels (Instagram square)
- **Fonts:** System fonts with automatic fallbacks
- **Dependencies:** Python 3.8+, Pillow (PIL)

## File Structure

```
kiin-content/
├── src/
│   └── carousel_generator.py    # Main generator script
├── config/
│   └── carousel_content.json    # Content database
├── carousels/                   # Generated output (created automatically)
├── requirements.txt             # Python dependencies
└── README.md                   # This file
```

## Troubleshooting

### Font Issues
If fonts look wrong:
1. System will automatically fallback to default fonts
2. For custom fonts, add TTF files to system font directory
3. Update font paths in the `_load_fonts()` method

### Virtual Environment
Always activate the virtual environment before running:
```bash
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### Output Directory
Generator creates output directories automatically. Default is `./carousels/`

## Contributing

To add new content:
1. Edit `config/carousel_content.json`
2. Test with `--info` command
3. Generate sample carousel
4. Verify all slides look professional

## License

This tool is designed for creating original caregiver content. Please respect Instagram's community guidelines and ensure all content provides genuine value to your audience.

---

**Ready to boost your Instagram engagement?** Start with `python src/carousel_generator.py --list` to see all available topics! 🚀