# Free Music Sources for Kiin Content

A curated list of royalty-free music sources specifically suitable for caregiving and family content. All sources listed provide music that can be used in commercial projects with proper attribution (where required).

## 🎵 Primary Recommended Sources

### 1. YouTube Audio Library
- **Website**: [youtube.com/audiolibrary/music](https://www.youtube.com/audiolibrary/music)
- **License**: Creative Commons / YouTube Standard License
- **Cost**: Completely free
- **Attribution**: Some tracks require attribution, clearly marked
- **Quality**: Professional studio quality
- **Best Categories for Kiin**:
  - Ambient: Perfect for background music
  - Acoustic: Warm, human-centered tracks  
  - Cinematic: Emotional and storytelling music
- **Recommended Searches**: "ambient calm", "acoustic warm", "piano emotional", "strings gentle"
- **Download**: Direct MP3 download, various quality options

### 2. Freemusicarchive.org (FMA)
- **Website**: [freemusicarchive.org](https://freemusicarchive.org/)
- **License**: Various Creative Commons licenses
- **Cost**: Free
- **Attribution**: Required for most tracks
- **Quality**: Variable (check individual tracks)
- **Best Categories for Kiin**:
  - Ambient / Drone
  - Folk / Country (acoustic warmth)
  - Experimental (unique textures)
- **Pro Tip**: Filter by license type to find attribution-free options
- **Curated Collections**: Look for "Peaceful" and "Contemplative" collections

### 3. Incompetech (Kevin MacLeod)
- **Website**: [incompetech.com](https://incompetech.com/)
- **License**: Creative Commons Attribution 3.0
- **Cost**: Free with attribution, or $30/track for no attribution
- **Attribution**: "Music by Kevin MacLeod (incompetech.com)" required
- **Quality**: Consistently high, professionally mastered
- **Best Categories for Kiin**:
  - Ambient: "Drifting at 432 Hz", "Soothing Relaxation"
  - Corporate: Clean, professional backgrounds
  - Emotional: "Heartwarming", "Contemplative"
- **Search Tips**: Use mood-based searching ("warm", "gentle", "hopeful")

### 4. Pixabay Music
- **Website**: [pixabay.com/music](https://pixabay.com/music/)
- **License**: Pixabay Content License (commercial use OK)
- **Cost**: Free
- **Attribution**: Not required but appreciated
- **Quality**: Good to excellent
- **Best for**: Quick searches, no attribution needed
- **Categories**: Ambient, Acoustic, Piano, Cinematic

### 5. Uppbeat
- **Website**: [uppbeat.io](https://uppbeat.io/)
- **License**: Royalty-free for YouTube (free tier)
- **Cost**: Free tier available, paid plans for broader use
- **Attribution**: Required for free tier
- **Quality**: Professional, curated selection
- **Best for**: High-quality ambient and acoustic tracks

## 🎹 Specialized Sources by Mood

### Calm & Ambient
- **Chillhop Music**: [chillhop.com](https://chillhop.com/) - Lo-fi and chill beats
- **Ambient-Mixer**: [ambient-mixer.com](https://ambient-mixer.com/) - Nature sounds and ambient
- **Freesound**: [freesound.org](https://freesound.org/) - Individual sounds for custom ambient tracks

### Warm & Acoustic  
- **Josh Woodward**: [joshwoodward.com](https://joshwoodward.com/) - Beautiful acoustic music
- **Brad Sucks**: [bradsucks.net](http://bradsucks.net/) - Independent artist, warm sounds
- **NCS (NoCopyrightSounds)**: [ncs.io](https://ncs.io/) - Electronic but has ambient selections

### Professional & Corporate
- **Bensound**: [bensound.com](https://www.bensound.com/) - Professional background music
- **Purple Planet Music**: [purple-planet.com](https://www.purple-planet.com/) - Royalty-free professional tracks
- **Jamendo Music**: [jamendo.com](https://www.jamendo.com/) - Large library, various licenses

## 🎯 Kiin-Specific Recommendations

### For Validation Content (Warm & Nurturing)
**Recommended Tracks from Free Sources:**
- "Peaceful" by Kevin MacLeod (Incompetech)
- "Acoustic Breeze" by Bensound  
- "Warm Memories" by Josh Woodward
- "Gentle Piano" from YouTube Audio Library
- "Comfort Zone" from Pixabay

**Characteristics to Look For:**
- Acoustic guitar or piano lead
- Slow to medium tempo (60-90 BPM)
- Major keys or gentle minor
- Minimal percussion
- 3-5 minute duration for looping

### For Confessions Content (Intimate & Soft)
**Recommended Tracks:**
- "Meditation Impromptu 02" by Kevin MacLeod
- "Whispered Promises" from Freemusicarchive
- "Soft Piano" from YouTube Audio Library
- "Intimate Moments" from Uppbeat
- "Reflection" by Brad Sucks

**Characteristics:**
- Solo piano or minimal instrumentation  
- Very quiet dynamics
- Sustained notes, few sudden changes
- 2-4 minute loops
- Warm, analog-style recording

### For Tips Content (Professional & Clear)
**Recommended Tracks:**
- "Corporate Technology" by Kevin MacLeod
- "Clean Soul" by Bensound
- "Professional" from YouTube Audio Library
- "Minimal Corporate" from Pixabay
- "Clear Thinking" from Purple Planet

**Characteristics:**
- Clean, modern production
- Subtle rhythm without distraction
- Bright but not harsh tones
- Professional mixing quality
- 90-120 BPM tempo

### For Sandwich Generation Content (Energetic & Relatable)
**Recommended Tracks:**
- "Upbeat Corporate" from YouTube Audio Library
- "Happy Acoustic" by Bensound
- "Positive Energy" from Pixabay  
- "Family Time" by Josh Woodward
- "Together" from Incompetech

**Characteristics:**
- Acoustic instruments with light rhythm
- Uplifting major keys
- Medium tempo (100-130 BPM)
- Warm, friendly production
- Natural, organic sound

## 📋 License Quick Reference

| Source | Attribution Required | Commercial Use | Sublicense |
|--------|---------------------|----------------|------------|
| YouTube Audio Library | Some tracks | ✅ | ✅ |
| Freemusicarchive | Usually | ✅ | Varies |
| Incompetech | ✅ (or $30) | ✅ | ✅ |
| Pixabay Music | ❌ | ✅ | ✅ |
| Uppbeat | ✅ (free tier) | Limited | ❌ |

## 🔍 Search Strategy

### Effective Keywords for Caregiving Content
- **Emotional**: "warm", "gentle", "caring", "supportive", "nurturing"
- **Instrumental**: "acoustic", "piano", "strings", "ambient", "minimal"  
- **Mood**: "peaceful", "hopeful", "comforting", "intimate", "professional"
- **Tempo**: "slow", "medium", "contemplative", "relaxed"
- **Avoid**: "drums", "vocals", "electronic", "aggressive", "dark"

### Quality Checklist Before Download
- [ ] Consistent volume throughout track
- [ ] No sudden loud or jarring sounds  
- [ ] Appropriate length (2-10 minutes)
- [ ] Professional mixing quality
- [ ] Matches intended mood
- [ ] License allows commercial use
- [ ] Attribution requirements noted

## 🎬 Integration with Music Mixer

All sources listed are compatible with the Kiin music_mixer.py tool. To use:

```bash
# Download music to appropriate mood folder
python music_mixer.py --create-library ./music

# Test music with video
python music_mixer.py --video content.mp4 --music calm/peaceful.mp3 --output result.mp4

# Use mood presets
python music_mixer.py --video content.mp4 --mood calm --output result.mp4
```

## 📁 Recommended File Organization

```
/assets/music/
├── calm/
│   ├── ambient_peaceful.mp3
│   ├── nature_birds.mp3
│   └── strings_gentle.mp3
├── warm/  
│   ├── acoustic_guitar_warm.mp3
│   ├── piano_emotional.mp3
│   └── strings_hopeful.mp3
├── intimate/
│   ├── ambient_minimal.mp3
│   ├── piano_solo_soft.mp3
│   └── acoustic_fingerpicking.mp3
├── professional/
│   ├── corporate_soft.mp3
│   ├── piano_clean.mp3
│   └── ambient_professional.mp3
└── energetic/
    ├── acoustic_rhythmic.mp3
    ├── piano_lively.mp3
    └── folk_upbeat.mp3
```

## ⚖️ Legal Considerations

1. **Always verify licenses** before use in commercial projects
2. **Keep attribution records** for tracks that require it
3. **Check for updates** to licensing terms periodically
4. **Consider paid licensing** for high-volume commercial use
5. **Test audio quality** before final production use

## 🔄 Regular Updates

This list is maintained and updated quarterly. For the most current information:
- Check individual source websites for new content
- Verify license terms haven't changed
- Test new music against Kiin content guidelines
- Share discoveries with the content team

---

*Last updated: January 2024*  
*Next review: April 2024*

For questions about music licensing or to suggest new sources, contact the Kiin content team.