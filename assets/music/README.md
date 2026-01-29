# Music Library for Kiin Content Factory

This directory contains royalty-free background music organized by mood categories for intelligent content matching.

## Directory Structure

```
music/
├── supportive_gentle/     - Warm, nurturing music for validation content
├── hopeful_uplifting/     - Positive, encouraging music for tips and advice
├── tense_to_calm/         - Dynamic music for chaos stories (tension → resolution)
├── reflective_emotional/  - Intimate music for confessions and personal stories
└── energetic_motivating/  - Driving music for sandwich generation content
```

## File Requirements

### Audio Specifications
- **Format**: MP3 (128kbps+), WAV (preferred), or AAC
- **Duration**: 30 seconds to 10 minutes
- **Sample Rate**: 44.1kHz minimum
- **Quality**: Consistent volume, normalized to -23 LUFS
- **Fades**: Smooth 2-5 second fade-in, 3-6 second fade-out

### Content Requirements
- **No Vocals**: Instrumental only
- **Loop-Ready**: Should loop seamlessly if possible
- **Consistent Energy**: Avoid sudden volume or mood changes
- **Voice-Friendly**: Minimal content in speech frequencies (300-3000Hz)

## Naming Convention

Use this format: `{mood}_{tempo}bpm_{key}_{duration}s_{description}_{source}.{ext}`

Examples:
- `supportive_gentle_80bpm_Cmaj_180s_soft_piano_pixabay.mp3`
- `hopeful_uplifting_110bpm_Gmaj_240s_acoustic_guitar_incompetech.wav`
- `energetic_motivating_140bpm_Dmaj_300s_driving_strings_youtube.mp3`

## Recommended Sources

### Free Sources
1. **Pixabay Music** (https://pixabay.com/music/)
   - License: Pixabay Content License (Free for commercial use)
   - Search terms: ambient, peaceful, uplifting, acoustic

2. **YouTube Audio Library** (https://studio.youtube.com/channel/music)
   - License: Creative Commons / YouTube License
   - High quality, good search features

3. **Incompetech** (https://incompetech.com/)
   - License: Creative Commons Attribution 4.0
   - Professional quality, requires attribution
   - Attribution: "Music by Kevin MacLeod (incompetech.com)"

4. **Free Music Archive** (https://freemusicarchive.org/)
   - License: Various Creative Commons
   - Check individual track licenses

### Premium Sources (Optional)
- **Epidemic Sound** ($15-50/month) - No attribution required
- **Artlist** ($199/year) - Lifetime license per download

## Mood Guidelines

### Supportive Gentle
- **Use For**: Validation messages, comfort content
- **Tempo**: 60-100 BPM
- **Key**: Major keys, warm modes
- **Instruments**: Soft piano, gentle strings, acoustic guitar, ambient pads
- **Avoid**: Percussion, bass, dramatic changes

### Hopeful Uplifting  
- **Use For**: Tips, advice, positive messaging
- **Tempo**: 80-130 BPM
- **Key**: Bright major keys
- **Instruments**: Bright piano, uplifting strings, light percussion
- **Avoid**: Dark tones, minor progressions, sad melodies

### Tense to Calm
- **Use For**: Chaos stories, problem-to-solution content
- **Tempo**: 70-120 BPM (can vary within track)
- **Key**: Minor to major transitions preferred
- **Instruments**: Building strings, dynamic piano, resolution elements
- **Avoid**: Static mood, unchanging dynamics

### Reflective Emotional
- **Use For**: Confessions, personal stories, vulnerable content
- **Tempo**: 50-90 BPM
- **Key**: Minor keys, emotional modes
- **Instruments**: Solo piano, intimate strings, minimal arrangements
- **Avoid**: Busy arrangements, bright tones, complex harmonies

### Energetic Motivating
- **Use For**: Sandwich generation content, motivation, action items
- **Tempo**: 110-160 BPM
- **Key**: Confident major keys
- **Instruments**: Driving piano, strong strings, motivational builds
- **Avoid**: Slow tempos, subdued energy, overly busy textures

## Usage in System

The music system will:
1. **Analyze** audio properties (tempo, energy, emotional valence)
2. **Select** appropriate tracks based on content type and emotional context
3. **Mix** with intelligent volume ducking during speech
4. **Vary** selections to avoid repetition
5. **Loop** tracks seamlessly if content duration exceeds track length

## Adding New Music

1. **Download** appropriate track for the mood
2. **Process** according to audio specifications
3. **Name** using the convention above
4. **Place** in the correct mood directory
5. **Test** with the music system: `python src/music_system_v2.py --analyze path/to/track.mp3`

## Quality Control

Before adding tracks to the library:
- ✅ Check audio quality (no distortion, consistent levels)
- ✅ Verify appropriate mood match
- ✅ Ensure proper licensing for commercial use
- ✅ Test mix compatibility with speech content
- ✅ Confirm duration and fade requirements

## Legal Notes

- Always verify licensing terms for commercial use
- Keep attribution records for Creative Commons tracks
- Respect copyright - only use properly licensed music
- Consider purchasing premium licenses for high-volume usage

---

**Goal**: Create a professional music library that enhances emotional connection without competing with speech content.