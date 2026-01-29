# Kiin Content Factory - Social Media Integration System

Complete automated social media posting and management system for caregiver content.

## 🚀 Quick Start

1. **Install Dependencies**
```bash
pip install requests pillow opencv-python numpy pytz sqlite3
# For video processing:
# Install ffmpeg: https://ffmpeg.org/download.html
```

2. **Configure Credentials**
```bash
cp config/social_credentials.json.example config/social_credentials.json
# Edit with your actual API credentials
```

3. **Test Setup**
```python
from src.social.posting_manager import PostingManager
from src.social.base_adapter import VideoContent

# Initialize manager
manager = PostingManager()

# Create test content
content = VideoContent(
    file_path="path/to/your/video.mp4",
    title="Test Caregiver Tip",
    description="A helpful tip for fellow caregivers",
    hashtags=["caregiver", "tips", "support"]
)

# Queue for Instagram (simulation mode)
job_id = manager.queue_post("instagram", content)
print(f"Queued job: {job_id}")
```

## 📁 System Components

### 1. Platform Adapters (`src/social/`)
- **instagram_adapter.py** - Instagram Reels via Facebook Graph API
- **tiktok_adapter.py** - TikTok videos (includes simulation mode)
- **youtube_adapter.py** - YouTube Shorts via YouTube Data API
- **twitter_adapter.py** - Twitter video posts via API v2
- **linkedin_adapter.py** - LinkedIn professional content
- **pinterest_adapter.py** - Pinterest video pins
- **facebook_adapter.py** - Facebook Reels via Graph API

### 2. Core Systems
- **posting_manager.py** - Unified posting orchestration
- **hashtag_optimizer.py** - Platform-specific hashtag research
- **caption_generator.py** - Automated caption creation
- **timing_optimizer.py** - Optimal posting time analysis
- **repurpose_engine.py** - Cross-platform content adaptation

### 3. Configuration Files (`config/`)
- **social_credentials.json** - API credentials (template)
- **posting_schedule.json** - Timing and frequency settings
- **platform_specs.json** - Platform-specific requirements
- **hashtags.json** - Hashtag optimization settings

## 🔧 Setup Guide

### API Credentials Setup

#### Instagram (Facebook Graph API)
1. Create Facebook Developer App
2. Add Instagram Basic Display product
3. Get Instagram Business Account access token
4. Update `social_credentials.json`:
```json
{
  "instagram": {
    "enabled": true,
    "access_token": "YOUR_ACCESS_TOKEN",
    "instagram_account_id": "YOUR_ACCOUNT_ID"
  }
}
```

#### TikTok
1. Apply for TikTok for Developers
2. Get API approval (may take time)
3. For testing, use simulation mode:
```json
{
  "tiktok": {
    "enabled": true,
    "simulation_mode": true
  }
}
```

#### YouTube
1. Create Google Cloud Project
2. Enable YouTube Data API v3
3. Create OAuth2 credentials
4. Get access/refresh tokens
```json
{
  "youtube": {
    "enabled": true,
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "access_token": "YOUR_ACCESS_TOKEN",
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }
}
```

#### Twitter
1. Apply for Twitter API access
2. Get API keys with video upload permissions
```json
{
  "twitter": {
    "enabled": true,
    "bearer_token": "YOUR_BEARER_TOKEN",
    "api_key": "YOUR_API_KEY",
    "api_secret": "YOUR_API_SECRET",
    "access_token": "YOUR_ACCESS_TOKEN",
    "access_token_secret": "YOUR_ACCESS_TOKEN_SECRET"
  }
}
```

### Video Processing Setup
```bash
# Install FFmpeg (required for video repurposing)
# macOS:
brew install ffmpeg

# Ubuntu/Debian:
sudo apt update && sudo apt install ffmpeg

# Windows:
# Download from https://ffmpeg.org/download.html
```

## 💡 Usage Examples

### Basic Posting
```python
from src.social import PostingManager, VideoContent

manager = PostingManager()

# Create content
content = VideoContent(
    file_path="videos/caregiver_tip_1.mp4",
    title="5 Self-Care Tips for Caregivers",
    description="Quick tips to help you recharge and avoid burnout",
    hashtags=["caregiver", "selfcare", "tips"],
    thumbnail_path="thumbnails/tip_1.jpg"
)

# Post to single platform
job_id = manager.queue_post("instagram", content)

# Post to multiple platforms
job_ids = manager.queue_bulk_post(
    platforms=["instagram", "tiktok", "youtube"],
    content=content,
    delay_between_posts=300  # 5 minutes between posts
)
```

### Hashtag Optimization
```python
from src.social.hashtag_optimizer import HashtagOptimizer

optimizer = HashtagOptimizer()

# Generate optimized hashtags
hashtags = optimizer.optimize_hashtags(
    content_text="Tips for managing caregiver stress and burnout",
    platform="instagram",
    content_type="video"
)

print(f"Optimized hashtags: {hashtags}")

# Get cross-platform strategy
strategy = optimizer.suggest_hashtag_strategy(
    content_theme="caregiver stress",
    platforms=["instagram", "tiktok", "youtube"]
)
```

### Caption Generation
```python
from src.social.caption_generator import SocialCaptionGenerator

generator = SocialCaptionGenerator()

content_data = {
    "title": "Dealing with Caregiver Guilt",
    "description": "It's normal to feel guilty as a caregiver",
    "type": "validation"
}

# Generate platform-specific captions
instagram_caption = generator.generate_caption(content_data, "instagram")
tiktok_caption = generator.generate_caption(content_data, "tiktok")

# Generate A/B test variations
ab_test = generator.generate_ab_test_captions(content_data, "instagram")
```

### Video Repurposing
```python
from src.social.repurpose_engine import RepurposeEngine

engine = RepurposeEngine()

# Repurpose for single platform
result = engine.repurpose_video(
    source_video_path="videos/original.mp4",
    target_platform="instagram",
    aspect_ratio="9:16"
)

# Bulk repurpose for multiple platforms
bulk_result = engine.bulk_repurpose(
    source_video_path="videos/original.mp4",
    target_platforms=["instagram", "tiktok", "youtube"]
)
```

### Timing Optimization
```python
from src.social.timing_optimizer import TimingOptimizer

optimizer = TimingOptimizer()

# Get next optimal posting time
optimal_time = optimizer.get_optimal_posting_time("instagram")

# Schedule multiple posts
schedule = optimizer.schedule_bulk_posting(
    platforms=["instagram", "tiktok", "youtube"],
    content_count=5
)

# Check for holiday conflicts
conflicts = optimizer.check_holiday_conflicts(datetime.now())
```

## 🔄 Automated Workflow

### 1. Start Processing Manager
```python
manager = PostingManager()
manager.start_processing()  # Starts background worker

# Queue posts throughout the day
# Manager automatically posts at optimal times

# Stop when done
manager.stop_processing()
```

### 2. Monitor Queue Status
```python
# Check queue status
status = manager.get_queue_status()
print(f"Total jobs: {status['total_jobs']}")
print(f"Published: {status['by_status']['published']}")

# Get job details
job = manager.get_job_status(job_id)
print(f"Job status: {job.status}")
```

### 3. Collect Analytics
```python
# Collect performance data
analytics = manager.collect_analytics()

# Get performance summary
summary = manager.get_performance_summary()
print(f"Success rate: {summary['success_rate']:.1f}%")
```

## 🔒 Security Best Practices

### 1. Credential Management
```bash
# Never commit real credentials
echo "config/social_credentials.json" >> .gitignore

# Use environment variables in production
export INSTAGRAM_ACCESS_TOKEN="your_token"
export YOUTUBE_CLIENT_SECRET="your_secret"
```

### 2. Access Control
```python
# Set up proper file permissions
import os
os.chmod("config/social_credentials.json", 0o600)  # Owner read/write only
```

### 3. Rate Limiting
```python
# All adapters include built-in rate limiting
# Configure in platform specs:
{
  "instagram": {
    "rate_limit": {
      "calls_per_hour": 200,
      "min_gap_seconds": 60
    }
  }
}
```

## 📊 Monitoring & Analytics

### Database Schema
The system automatically creates SQLite databases:
- `data/posting_manager.db` - Job queue and results
- `data/hashtag_analytics.db` - Hashtag performance
- `data/timing_analytics.db` - Optimal timing data

### Performance Tracking
```python
# Track posting performance
manager.track_posting_performance(
    post_id="12345",
    platform="instagram", 
    posted_at=datetime.now(),
    impressions=1000,
    engagement=50
)

# Get analytics
analytics = manager.get_performance_summary()
hashtag_analytics = optimizer.get_hashtag_analytics()
timing_analytics = timing_optimizer.get_timing_analytics()
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Video Processing Fails
```bash
# Check FFmpeg installation
ffmpeg -version

# Test video file
ffprobe your_video.mp4
```

#### 2. API Authentication Fails
```python
# Test credentials individually
from src.social.instagram_adapter import InstagramAdapter

adapter = InstagramAdapter(credentials)
if adapter.authenticate():
    print("✅ Authentication successful")
else:
    print("❌ Authentication failed")
```

#### 3. Database Permissions
```bash
# Fix database permissions
chmod 755 data/
chmod 644 data/*.db
```

### Debugging Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable detailed logging for all components
```

## 🔄 Content Workflow

### 1. Content Creation
```python
# Create video content
content = VideoContent(
    file_path="path/to/video.mp4",
    title="Your Title",
    description="Your description", 
    hashtags=optimizer.optimize_hashtags(description, platform)
)
```

### 2. Cross-Platform Repurposing
```python
# Generate versions for each platform
repurposed = engine.bulk_repurpose(
    source_video_path=content.file_path,
    target_platforms=["instagram", "tiktok", "youtube"]
)
```

### 3. Caption Generation
```python
# Generate platform-specific captions
for platform in platforms:
    caption = caption_generator.generate_caption(
        content_data, platform
    )
    content.description = caption
```

### 4. Optimal Scheduling
```python
# Schedule across platforms
schedule = timing_optimizer.schedule_bulk_posting(
    platforms=["instagram", "tiktok", "youtube"],
    content_count=1
)

for item in schedule:
    manager.queue_post(
        platform=item['platform'],
        content=content,
        scheduled_time=item['scheduled_time']
    )
```

### 5. Monitor & Analyze
```python
# Check performance after posting
time.sleep(3600)  # Wait 1 hour
analytics = manager.collect_analytics()
```

## 📈 Advanced Features

### A/B Testing
```python
# Test different captions
ab_captions = caption_generator.generate_ab_test_captions(
    content_data, "instagram"
)

# Post variation A
job_a = manager.queue_post("instagram", content_a)
# Post variation B later
job_b = manager.queue_post("instagram", content_b)

# Compare results after 24 hours
```

### Audience Targeting
```python
# Adjust timing for caregiver audience
optimal_time = timing_optimizer.get_optimal_posting_time(
    platform="instagram",
    content_type="support"  # Emotional support content
)
```

### Content Calendar Integration
```python
from datetime import datetime, timedelta

# Schedule week of content
for i in range(7):
    post_date = datetime.now() + timedelta(days=i)
    
    if not timing_optimizer.check_holiday_conflicts(post_date)['should_avoid']:
        optimal_time = timing_optimizer.get_optimal_posting_time("instagram")
        manager.queue_post("instagram", content, optimal_time)
```

## 🎯 Platform-Specific Tips

### Instagram
- Use 9:16 aspect ratio for Reels
- Keep captions under 150 characters for optimal engagement
- Post during lunch hours (11 AM - 1 PM EST) for caregivers

### TikTok  
- 15-30 second videos perform best
- Use trending hashtags but keep total under 100 characters
- Post early morning or evening for caregiver audience

### YouTube
- Add detailed descriptions for SEO
- Use 5 relevant hashtags maximum
- Schedule for weekday afternoons

### LinkedIn
- Professional tone, minimal hashtags
- Longer-form content performs well
- Post Tuesday-Thursday mornings

## 📞 Support

### Documentation
- API documentation in `docs/api/`
- Configuration examples in `config/`
- Troubleshooting guide in `docs/troubleshooting.md`

### Logging
All components include comprehensive logging:
```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Community
- Issues: GitHub Issues
- Discussions: GitHub Discussions
- Updates: Check releases for new features

---

## ⚠️ Legal Considerations

1. **API Terms of Service**: Ensure compliance with each platform's ToS
2. **Rate Limiting**: Respect API rate limits to avoid suspension
3. **Content Ownership**: Only post content you have rights to use
4. **Privacy**: Handle user data according to platform privacy policies
5. **Automation Disclosure**: Some platforms require disclosure of automated posting

## 🔮 Future Enhancements

- Real-time trending hashtag detection
- Advanced analytics dashboard
- Integration with content calendar tools
- Voice-to-text caption generation
- Automated thumbnail creation
- Multi-language support
- Advanced A/B testing framework

---

Built with ❤️ for the caregiver community.