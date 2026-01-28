# Kiin Audio Enhancement System

Professional voice and music system for caregiving content creation. This system provides intelligent voice selection and background music mixing optimized for family caregiving content.

## 🚀 Quick Start

```bash
# Install dependencies (if not already installed)
pip install edge-tts opencv-python

# Demo the complete system
./venv/bin/python src/demo_audio_system.py

# Create a voice preview
./venv/bin/python src/voice_manager.py --preview "en-US-AriaNeural" --content-type validation

# List music moods
./venv/bin/python src/music_mixer.py --list-moods

# Create music library structure  
./venv/bin/python src/music_mixer.py --create-library assets/music
```

## 📁 System Architecture

```
kiin-content/
├── src/
│   ├── voice_manager.py      # Voice selection and TTS management
│   ├── music_mixer.py        # Background music mixing with ducking
│   └── demo_audio_system.py  # Complete system demonstration
├── config/
│   └── audio_config.json     # Centralized audio configuration
├── assets/
│   ├── MUSIC_SOURCES.md      # Free music source guide
│   ├── music/                # Organized music library by mood
│   └── *.mp3                 # Generated voice previews
└── README_AUDIO_SYSTEM.md    # This file
```

## 🎤 Voice Manager (`voice_manager.py`)

Intelligently selects Edge-TTS voices optimized for different types of caregiving content.

### Content Type Profiles

| Content Type | Voice Characteristics | Primary Voices |
|-------------|----------------------|----------------|
| **Validation** | Warm, empathetic, nurturing | Jenny, Aria, Natasha |
| **Confessions** | Intimate, soft, understanding | Sara, Sonia, Clara |
| **Tips** | Clear, authoritative, confident | Davis, Ryan, Jason |
| **Sandwich Gen** | Energetic, relatable, friendly | Amber, Ashley, William |
| **General** | Versatile, pleasant, engaging | Aria, Libby, Liam |

### Usage Examples

```bash
# List recommended voices for specific content
./venv/bin/python src/voice_manager.py --list --content-type validation

# Get detailed recommendations with tips
./venv/bin/python src/voice_manager.py --recommend --content-type confessions

# Generate voice preview with content-optimized text
./venv/bin/python src/voice_manager.py --preview "en-US-JennyNeural" --content-type validation

# Custom preview text
./venv/bin/python src/voice_manager.py --preview "en-GB-RyanNeural" --text "Your custom message here"

# Analyze all voices for caregiving suitability
./venv/bin/python src/voice_manager.py --analyze-all
```

## 🎵 Music Mixer (`music_mixer.py`)

Adds mood-appropriate background music to videos with intelligent audio ducking to maintain speech clarity.

### Music Moods

| Mood | Volume | Duck Ratio | Best For | Characteristics |
|------|--------|------------|----------|----------------|
| **Calm** | 0.15 | 0.30 | General content | Peaceful, non-intrusive |
| **Warm** | 0.18 | 0.25 | Validation content | Emotional, supportive |
| **Intimate** | 0.12 | 0.20 | Personal stories | Minimal, unobtrusive |
| **Professional** | 0.16 | 0.40 | Tips & advice | Clear, modern |
| **Energetic** | 0.22 | 0.45 | Sandwich gen | Rhythmic, engaging |
| **Uplifting** | 0.20 | 0.35 | Motivational | Inspiring, hopeful |

### Usage Examples

```bash
# Mix video with specific music file
./venv/bin/python src/music_mixer.py --video input.mp4 --music ambient.mp3 --output mixed.mp4

# Use mood-based mixing
./venv/bin/python src/music_mixer.py --video input.mp4 --mood calm --output mixed.mp4

# Content-type automatic mood selection
./venv/bin/python src/music_mixer.py --video input.mp4 --content-type validation --output mixed.mp4

# Custom volume and ducking
./venv/bin/python src/music_mixer.py --video input.mp4 --mood warm --volume 0.2 --duck-ratio 0.3 --output mixed.mp4

# Get video information
./venv/bin/python src/music_mixer.py --info input.mp4

# Validate music file quality
./venv/bin/python src/music_mixer.py --validate-music track.mp3
```

## 📊 Audio Configuration (`config/audio_config.json`)

Central configuration file containing:
- Voice profiles with speech settings
- Music mood parameters  
- Content type mappings
- Quality presets (podcast, social media, YouTube)
- Mixing parameters
- Free music source references

### Key Sections

```json
{
  "voice_profiles": {
    "validation": {
      "primary_voices": ["en-US-JennyNeural", "en-US-AriaNeural"],
      "speech_settings": {"rate": "0.85", "pitch": "-5%"}
    }
  },
  "music_moods": {
    "warm": {
      "volume_level": 0.18,
      "duck_ratio": 0.25,
      "characteristics": ["emotional", "supportive"]
    }
  }
}
```

## 🎼 Free Music Sources (`assets/MUSIC_SOURCES.md`)

Comprehensive guide to royalty-free music sources with:
- **Primary Sources**: YouTube Audio Library, Freemusicarchive, Incompetech
- **Mood-Specific Recommendations**: Curated tracks for each content type
- **License Information**: Clear usage rights and attribution requirements
- **Quality Guidelines**: What makes good background music for caregiving content

### Recommended Music Characteristics

- **Instrumental only** (no vocals)
- **Consistent volume** throughout track
- **3-5 minute duration** for easy looping
- **Warm, organic sounds** (acoustic guitar, piano, strings)
- **Minimal percussion** to avoid distraction
- **Professional mixing quality**

## 🛠 Technical Requirements

### Dependencies
```bash
pip install edge-tts opencv-python
```

### Optional (for video mixing)
- **FFmpeg**: Required for background music mixing
  - macOS: `brew install ffmpeg`
  - Ubuntu/Debian: `apt install ffmpeg`
  - Windows: Download from https://ffmpeg.org/

### Supported Formats
- **Audio Input**: MP3, WAV, AAC, M4A, OGG
- **Video Input**: MP4, AVI, MOV, MKV (any FFmpeg-supported format)
- **Output**: MP4 with AAC audio, MP3 for voice previews

## 🎯 Content Creation Workflow

### 1. Voice Selection
```bash
# Choose voice for your content type
./venv/bin/python src/voice_manager.py --recommend --content-type tips

# Generate preview to test
./venv/bin/python src/voice_manager.py --preview "en-US-DavisNeural" --content-type tips
```

### 2. Music Preparation
```bash
# Create organized music library
./venv/bin/python src/music_mixer.py --create-library assets/music

# Download music from sources in MUSIC_SOURCES.md
# Place files in appropriate mood folders: assets/music/calm/, assets/music/warm/, etc.

# Validate music quality
./venv/bin/python src/music_mixer.py --validate-music assets/music/calm/peaceful_track.mp3
```

### 3. Video Enhancement
```bash
# Get content-type music suggestion
./venv/bin/python src/music_mixer.py --suggest-content validation

# Mix video with appropriate background music
./venv/bin/python src/music_mixer.py --video raw_video.mp4 --content-type validation --output final_video.mp4
```

## 🎨 Customization

### Adding New Content Types
1. Edit `config/audio_config.json`
2. Add voice profile with recommended voices
3. Add content type mapping with music mood
4. Update both voice_manager.py and music_mixer.py if needed

### Custom Voice Settings
```python
# In audio_config.json
"custom_content": {
  "primary_voices": ["en-US-CustomNeural"],
  "speech_settings": {
    "rate": "0.90",
    "pitch": "+1%",
    "volume": "95%"
  },
  "recommended_music_mood": "professional"
}
```

### Custom Music Moods
```python
# In audio_config.json
"custom_mood": {
  "description": "Your custom mood description",
  "volume_level": 0.15,
  "duck_ratio": 0.30,
  "characteristics": ["custom", "characteristics"]
}
```

## 🔧 Troubleshooting

### Voice Issues
- **No audio generated**: Voice name might be incorrect, check available voices
- **Poor quality**: Try different voices from the same profile
- **Text errors**: Ensure text is properly escaped and not too long

### Music Issues  
- **FFmpeg not found**: Install FFmpeg (see requirements above)
- **No music files**: Create music library and add files from MUSIC_SOURCES.md
- **Audio too loud/quiet**: Adjust volume and duck_ratio parameters

### Common Solutions
```bash
# Check system status
./venv/bin/python src/demo_audio_system.py

# List all available voices
./venv/bin/python src/voice_manager.py --list

# Test FFmpeg availability
./venv/bin/python src/music_mixer.py --info test_video.mp4
```

## 📈 Quality Assurance

### Voice Quality Checklist
- [ ] Voice matches content emotional tone
- [ ] Clear pronunciation and pacing
- [ ] Appropriate accent for target audience
- [ ] Consistent volume levels

### Music Quality Checklist  
- [ ] Music enhances, doesn't distract from speech
- [ ] Appropriate mood for content type
- [ ] Smooth fade-in/fade-out
- [ ] Speech remains clearly audible
- [ ] No sudden volume changes

### Final Output Checklist
- [ ] Audio levels are consistent throughout
- [ ] No clipping or distortion
- [ ] Speech is primary focus
- [ ] Music supports emotional tone
- [ ] Professional mixing quality

## 📞 Support

For questions, issues, or feature requests:
1. Check this documentation first
2. Run the demo system: `./venv/bin/python src/demo_audio_system.py`
3. Review configuration: `config/audio_config.json`
4. Check free music guide: `assets/MUSIC_SOURCES.md`

## 🔄 Updates

This system is designed to be easily maintainable:
- **Voice profiles**: Update when new Edge-TTS voices become available
- **Music sources**: Regularly check for new royalty-free music
- **Configuration**: Adjust parameters based on content performance
- **Dependencies**: Keep edge-tts and other packages updated

---

*System Version: 1.0*  
*Last Updated: January 2024*  
*Compatible with: Edge-TTS 6.1+, FFmpeg 4.0+*