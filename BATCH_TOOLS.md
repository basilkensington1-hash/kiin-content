# Batch Content Generation & Calendar Tools

Two powerful new tools for bulk content creation and strategic scheduling.

## 🚀 Batch Content Generator

**Location:** `src/batch_generator.py`

Generate multiple videos efficiently with parallel processing, progress tracking, and automatic caption generation.

### Quick Examples

```bash
# Generate a week of content (one of each type per day)
python3 src/batch_generator.py --days 7 --output-dir ./output/week1/

# Generate specific content type in bulk
python3 src/batch_generator.py --type validation --count 10

# Generate full content library
python3 src/batch_generator.py --all --count 5  # 5 of each type = 25 videos
```

### Features

✅ **Parallel Processing** - Uses ThreadPoolExecutor for speed  
✅ **Progress Tracking** - Real-time progress with ETAs  
✅ **Smart Organization** - Output organized by date/type  
✅ **Auto Captions** - Platform-specific captions (TikTok/Instagram)  
✅ **Manifest Generation** - JSON manifest with all video metadata  
✅ **Error Handling** - Continues on failures, reports at end

### Options

- `--days N` - Generate daily content for N days
- `--type TYPE` - Generate specific content type in bulk
- `--all` - Generate all content types in bulk  
- `--count N` - Number of videos per type/day (default: 5)
- `--output-dir PATH` - Output directory (default: ./output)
- `--workers N` - Parallel workers (default: 3)
- `--start-date YYYY-MM-DD` - Start date for daily generation

### Output Structure

```
output/
├── manifest.json                # Complete metadata
├── 2026-01-29/                 # Daily content
│   ├── 2026-01-29_validation_01.mp4
│   ├── 2026-01-29_tips_02.mp4
│   └── ...
├── validation/                  # Bulk content
│   ├── validation_001_20260128_223045.mp4
│   └── ...
└── tips/
    ├── tips_001_20260128_223045.mp4
    └── ...
```

### Manifest File

The generated `manifest.json` contains:

```json
{
  "generated_at": "2026-01-28T22:30:00",
  "total_videos": 25,
  "successful": 23,
  "failed": 2,
  "total_size_mb": 456.7,
  "videos": [
    {
      "id": "validation_1",
      "type": "validation",
      "filename": "validation_001.mp4",
      "file_size_mb": 18.5,
      "success": true,
      "captions": {
        "tiktok": "💜 You are enough just as you are...",
        "instagram": "💜 Reminder for caregivers..."
      },
      "metadata": {...}
    }
  ]
}
```

## 📅 Content Calendar Generator

**Location:** `src/content_calendar.py`

Generate research-based posting schedules optimized for engagement.

### Quick Examples

```bash
# Generate 4-week calendar
python3 src/content_calendar.py --weeks 4 --output calendar.json

# Generate calendar with markdown view
python3 src/content_calendar.py --weeks 2 --output calendar.json --markdown calendar.md

# Use existing content library
python3 src/content_calendar.py --weeks 1 --content-library ./output/manifest.json --output my_calendar.json
```

### Research-Based Scheduling

🎯 **Best Posting Times**: 10-11 AM and 6-8 PM  
📱 **TikTok Frequency**: 1-3 posts per day  
📸 **Instagram Frequency**: 3-4 posts per week  
🎨 **Content Mix**: 40% educational, 30% personal, 20% community, 10% awareness

### Features

✅ **Smart Distribution** - Balanced content mix following research  
✅ **Platform Optimization** - Different strategies for TikTok vs Instagram  
✅ **Time Optimization** - Posts scheduled at peak engagement times  
✅ **Content Mapping** - Maps video types to engagement categories  
✅ **Markdown Export** - Human-readable calendar view  
✅ **Statistics** - Detailed analytics on distribution and timing

### Options

- `--weeks N` - Number of weeks to generate
- `--output FILE` - Output JSON file (default: calendar.json)
- `--markdown FILE` - Also generate markdown calendar
- `--start-date YYYY-MM-DD` - Start date (default: tomorrow)
- `--content-library FILE` - Path to content manifest.json

### Calendar Output

```json
{
  "2026-01-29": [
    {
      "time": "10:00",
      "platform": "tiktok", 
      "content_type": "tips",
      "category": "educational",
      "video": "tips_001.mp4",
      "video_id": "tips_001_20260128_223045",
      "file_path": "./output/tips/tips_001.mp4"
    }
  ]
}
```

### Markdown Calendar

The markdown export provides:

- 📊 **Summary Statistics** - Posts, platform split, content distribution
- 📅 **Weekly View** - Week-by-week overview with emojis
- 📋 **Daily Schedule** - Detailed daily posting schedule
- 📈 **Analytics** - Distribution vs targets, most used times
- 🔬 **Research Notes** - Basis for scheduling decisions

## 🔄 Workflow Integration

### Complete Content Creation Pipeline

```bash
# 1. Generate content library
python3 src/batch_generator.py --all --count 20 --output-dir ./content-library/

# 2. Create posting calendar using the library
python3 src/content_calendar.py --weeks 4 --content-library ./content-library/manifest.json --output posting-schedule.json --markdown posting-schedule.md

# 3. Review the markdown calendar
open posting-schedule.md
```

### Continuous Content Creation

```bash
# Weekly content generation
python3 src/batch_generator.py --days 7 --start-date "2026-02-03" --output-dir ./output/week2/

# Update calendar with new content
python3 src/content_calendar.py --weeks 1 --start-date "2026-02-03" --content-library ./output/week2/manifest.json --output week2-calendar.json
```

## 📊 Analytics & Monitoring

### Batch Generation Metrics

- **Success Rate**: Track generation success vs failures
- **Speed**: Videos per minute, total processing time
- **File Sizes**: Monitor output sizes for platform optimization
- **Content Distribution**: Balance across content types

### Calendar Analytics

- **Platform Distribution**: TikTok vs Instagram posting frequency
- **Time Analysis**: Peak posting times vs engagement targets
- **Content Balance**: Educational/personal/community/awareness mix
- **Weekly Patterns**: Posting consistency and frequency

## 🛠️ Troubleshooting

### Common Issues

**Import Errors**: Ensure virtual environment is activated:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Generation Failures**: Check individual generator configs:
```bash
# Test individual generators
python3 src/validation_generator.py
python3 src/tips_generator.py
```

**Calendar Empty**: Verify content library path:
```bash
# Check manifest exists and has content
cat ./output/manifest.json | jq '.videos | length'
```

### Performance Optimization

**Increase Parallel Workers**:
```bash
python3 src/batch_generator.py --workers 6 --type validation --count 50
```

**Split Large Batches**:
```bash
# Instead of 100 videos at once, do 4 batches of 25
for i in {1..4}; do
  python3 src/batch_generator.py --type tips --count 25 --output-dir ./batch-$i/
done
```

## 🔗 Integration with Existing Tools

These batch tools integrate seamlessly with existing generators:

- **Validation Generator**: `src/validation_generator.py`
- **Tips Generator**: `src/tips_generator.py` 
- **Confession Generator**: `src/confession_generator.py`
- **Sandwich Generator**: `src/sandwich_generator.py`
- **Chaos Generator**: `src/chaos_generator.py`

Caption generation uses existing templates and platform-specific formatting.

---

**Next Steps**: 
1. Generate a content library with `batch_generator.py`
2. Create posting schedule with `content_calendar.py`  
3. Review markdown calendar for optimal timing
4. Execute posting schedule with your preferred scheduler