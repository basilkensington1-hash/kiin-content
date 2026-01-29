# Sound Effects Library for Kiin Content Factory

This directory contains professional sound effects organized by category for context-aware content enhancement.

## Directory Structure

```
sfx/
├── notification/       - Attention-getting sounds for chaos content
├── transition/         - Smooth sounds for section changes
├── emotional_accent/   - Subtle sounds for emotional moments
├── text_reveal/        - Sounds for text animations and reveals
└── ambient/           - Background atmosphere and room tone
```

## File Requirements

### Audio Specifications
- **Format**: WAV preferred (44.1kHz, 16-bit+), MP3 acceptable (128kbps+)
- **Channels**: Mono preferred for SFX, stereo for ambient
- **Duration**: Varies by category (see below)
- **Peak Levels**: Below -6dB to prevent clipping
- **Noise Floor**: Below -50dB
- **Normalization**: Consistent levels within categories

### Content Requirements
- **No Mud**: Clean below 100Hz unless specifically needed
- **Appropriate Fades**: Quick attack for alerts, gradual for emotional accents
- **Mono Compatibility**: Must sound good in mono
- **Voice Space**: Minimal energy in speech frequencies (300-3kHz)

## Category Guidelines

### 🔔 Notification
**Purpose**: Draw attention without startling
- **Duration**: 0.2-1.0 seconds
- **Volume**: 30-50% of speech level
- **Frequency**: 800-4000Hz focus
- **Examples**: gentle_chime.wav, soft_bell.wav, notification_pop.wav

**Subcategories**:
- `gentle/` - Soft, non-intrusive (0.3-0.8s)
- `urgent/` - Attention-getting but not harsh (0.2-0.6s)
- `subtle/` - Very quiet for sensitive content (0.4-1.0s)

### ↔️ Transition
**Purpose**: Smooth section bridging
- **Duration**: 0.5-2.0 seconds
- **Volume**: 20-40% of speech level
- **Characteristics**: Flowing, non-jarring
- **Examples**: whoosh_soft.wav, page_turn.wav, musical_bridge.wav

**Subcategories**:
- `whoosh/` - Air movement sounds (0.8-2.0s)
- `page_turn/` - Paper/book sounds (0.5-1.5s)
- `musical/` - Harmonic transitions (1.0-3.0s)

### 💝 Emotional Accent
**Purpose**: Enhance emotional impact subtly
- **Duration**: 1.0-5.0 seconds
- **Volume**: 10-25% of speech level
- **Frequency**: 150-2000Hz focus (warm range)
- **Examples**: heart_warm.wav, gentle_swell.wav, touching_chord.wav

**Subcategories**:
- `touching/` - Warm, heart-touching (1.0-4.0s)
- `hopeful/` - Uplifting accents (1.5-3.0s)
- `contemplative/` - Thoughtful support (2.0-5.0s)

### 📝 Text Reveal
**Purpose**: Support text animations
- **Duration**: 0.1-0.6 seconds
- **Volume**: 25-45% of speech level
- **Characteristics**: Crisp, clear, brief
- **Examples**: typewriter_click.wav, text_pop.wav, digital_beep.wav

**Subcategories**:
- `typewriter/` - Mechanical sounds (0.1-0.3s)
- `digital/` - Modern interface sounds (0.1-0.4s)
- `organic/` - Natural, gentle sounds (0.2-0.6s)

### 🌬️ Ambient
**Purpose**: Background atmosphere
- **Duration**: 10-300 seconds (long loops)
- **Volume**: 5-15% of speech level
- **Characteristics**: Continuous, unobtrusive
- **Examples**: room_tone_warm.wav, gentle_birds.wav, cozy_space.wav

**Subcategories**:
- `room_tone/` - Neutral indoor ambience (10-120s)
- `nature_soft/` - Gentle outdoor sounds (30-300s)
- `warm_space/` - Comforting interior atmosphere (20-180s)

## Naming Convention

Format: `{category}_{subcategory}_{description}_{duration}ms_{source}.{ext}`

Examples:
- `notification_gentle_soft_bell_800ms_recorded.wav`
- `transition_whoosh_air_flow_1200ms_generated.wav`
- `emotional_accent_touching_warm_heart_3000ms_synthesized.wav`
- `text_reveal_digital_modern_pop_250ms_library.wav`
- `ambient_room_tone_warm_space_60000ms_recorded.wav`

## Content Type Usage

### Validation Content
- **Preferred**: emotional_accent (touching, contemplative), ambient (warm_space)
- **Avoid**: notification sounds
- **Volume**: 70% of normal levels (gentler)

### Confessions
- **Preferred**: emotional_accent (contemplative), ambient (room_tone), transition (musical)
- **Avoid**: notification sounds
- **Volume**: 60% of normal levels (intimate)

### Tips/Education
- **Preferred**: text_reveal (digital, organic), transition (page_turn), ambient (room_tone)
- **Limited**: emotional_accent
- **Volume**: 80% of normal levels

### Sandwich Generation
- **Preferred**: text_reveal, transition, notification (gentle)
- **Optional**: emotional_accent (hopeful)
- **Volume**: 100% of normal levels (energetic)

### Chaos Stories
- **Preferred**: notification (urgent, gentle), transition (whoosh), text_reveal
- **Optional**: emotional_accent (contemplative after resolution)
- **Volume**: 90% of normal levels

## Recommended Sources

### Free Sources
1. **Freesound.org** - Community-contributed, various licenses
2. **BBC Sound Effects Library** - Public domain archive
3. **YouTube Audio Library** - Limited SFX selection
4. **Pixabay** - Some SFX available

### Premium Sources
1. **Zapsplat** - Professional library, subscription required
2. **Adobe Audition** - Built-in SFX library with Creative Cloud
3. **Pro Sound Effects** - High-quality commercial library

### Procedural Generation
The system can generate basic SFX when files aren't available:
- Simple tones and chimes (notification)
- Whoosh and sweep sounds (transition)
- Harmonic pads (emotional accent)
- Click and pop sounds (text reveal)
- Basic ambient noise (ambient)

## Recording Your Own SFX

### Equipment
- **Recorder**: Zoom H1n, H4n, or smartphone with good mic
- **Environment**: Quiet space, minimal reverb for most SFX
- **Format**: Record at 48kHz/24-bit, convert to 44.1kHz/16-bit for final

### Techniques
- **Foley**: Record real actions (paper rustling, gentle taps)
- **Synthesis**: Create electronic sounds with DAW
- **Processing**: EQ, compress, and normalize appropriately
- **Fades**: Add smooth fades to prevent clicks

## Processing Guidelines

### Notification Sounds
1. High-pass filter at 200Hz
2. Gentle presence boost around 2kHz
3. Quick fade-in (10-50ms), natural decay
4. Light limiting to prevent peaks

### Transition Sounds
1. High-pass filter at 100Hz
2. Gentle high-frequency shelf for airiness
3. Smooth fade-in and fade-out (100-500ms)
4. Stereo width appropriate to movement

### Emotional Accents
1. Low-pass filter around 2kHz for warmth
2. Warm low-mid boost if needed
3. Very gradual fade-in (500ms+), long fade-out (1s+)
4. Gentle compression for consistency

### Text Reveals
1. High-pass filter at 300Hz for clarity
2. Clarity boost around 3kHz
3. Quick fade-in (5-20ms), quick fade-out (50-200ms)
4. Quick limiting to control transients

### Ambient Sounds
1. High-pass filter at 200Hz
2. Gentle high-cut around 6kHz
3. Seamless loops with crossfaded ends
4. Very gentle compression to even out levels

## Quality Testing

Before adding SFX to library:
1. **Technical**: Check levels, fades, frequency content
2. **Contextual**: Test with actual speech content
3. **Emotional**: Verify appropriate impact
4. **Mixing**: Ensure good blend with music and voice

## Usage in System

The SFX library will:
1. **Select** appropriate effects based on content type and emotional context
2. **Time** placement automatically based on content analysis
3. **Generate** procedural SFX when library files unavailable
4. **Balance** volumes relative to speech and music
5. **Avoid** overuse that could distract from content

## Adding New SFX

1. **Record or source** appropriate sound
2. **Process** according to category guidelines
3. **Name** using the convention
4. **Place** in correct category/subcategory folder
5. **Test** with system: `python src/sfx_library.py --validate path/to/effect.wav --category {category}`

---

**Goal**: Create a professional SFX library that enhances content without distracting from the message.