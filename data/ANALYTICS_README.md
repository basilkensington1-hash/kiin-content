# Analytics & Performance Tracking System

## Quick Start

The analytics system is ready to use! Here's how to get started:

### 1. Log Performance Data
```bash
# Basic logging (required: --video and --platform)
python3 src/analytics.py --log --video validation_001.mp4 --platform tiktok --views 5000 --likes 300 --saves 150 --shares 50 --comments 25

# With content type override
python3 src/analytics.py --log --video custom_video.mp4 --platform instagram --content-type tips --views 2500 --likes 180 --saves 95
```

### 2. Generate Reports
```bash
# Weekly report (default)
python3 src/analytics.py --report --period week

# Monthly report
python3 src/analytics.py --report --period month

# All-time report
python3 src/analytics.py --report --period all
```

### 3. Find Best Performers
```bash
# Top 10 by engagement rate
python3 src/analytics.py --best-performing --metric engagement_rate --count 10

# Top 5 by saves
python3 src/analytics.py --best-performing --metric saves --count 5

# Top performers by any metric: views, likes, saves, shares, comments
```

### 4. Content Analysis
```bash
# Analyze performance by content type
python3 src/analytics.py --content-type-analysis
```

### 5. Export Data
```bash
# Export as CSV
python3 src/analytics.py --export --format csv

# Export as JSON with custom filename
python3 src/analytics.py --export --format json --output my_analytics.json

# Export specific period
python3 src/analytics.py --export --format csv --period week --output weekly_data.csv
```

### 6. Quick Dashboard
```bash
# View summary statistics
python3 src/analytics.py --dashboard
```

## File Structure

- **`src/analytics.py`** - Main analytics script
- **`data/performance.json`** - Database of all performance metrics
- **`data/TRACKING_TEMPLATE.md`** - Manual tracking guide and KPI benchmarks
- **`data/ANALYTICS_README.md`** - This file

## Features

✅ **Performance Logging** - Track views, likes, saves, shares, comments, reach, impressions  
✅ **Auto Content Type Detection** - Automatically categorizes content based on filename  
✅ **Engagement Rate Calculation** - Automatic calculation of key performance metrics  
✅ **Multi-Platform Support** - TikTok, Instagram, YouTube, and custom platforms  
✅ **Time-Series Analysis** - Track performance trends over time  
✅ **Best Content Identification** - Find top performers by any metric  
✅ **Content Type Analysis** - Compare performance across content categories  
✅ **Optimal Timing Analysis** - Discover best posting times and days  
✅ **Data Export** - CSV and JSON export for external visualization  
✅ **Dashboard Summary** - Quick performance overview

## Content Types Supported

The system automatically detects these content types from video filenames:
- **validation** - Emotional support content
- **tips** - Practical advice and how-to content
- **facts** - Educational and informational content
- **confession** - Personal stories and experiences
- **mythbuster** - Truth vs myth content
- **quickwin** - Quick, actionable advice
- **intro** - Introduction content
- **outro** - Closing/farewell content
- **general** - Default fallback category

## Sample Data

The system includes sample data for testing:
- validation_001.mp4 (TikTok): 5,000 views, 10.5% engagement
- tips_morning_routine.mp4 (Instagram): 3,200 views, 15.0% engagement  
- confession_burnout.mp4 (YouTube): 8,500 views, 12.29% engagement

## Integration with Content Factory

This analytics system integrates seamlessly with the existing content generation tools:

1. **Video Generation** - Automatically track performance of generated content
2. **Content Calendar** - Use analytics to inform future content planning
3. **Batch Processing** - Log multiple videos at once during batch generation
4. **Brand Optimization** - Identify which branding approaches perform best

## Manual Tracking

For manual entry, see `TRACKING_TEMPLATE.md` which includes:
- Copy-paste templates for quick data entry
- KPI definitions specific to caregiving niche
- Benchmark targets for different content types
- Weekly and monthly tracking checklists

## Next Steps

1. Start logging your content performance data
2. Review the tracking template for manual entry guidance
3. Set up weekly reporting routine
4. Use insights to optimize content strategy
5. Export data for visualization in external tools

## Support

The analytics system is designed to be self-contained and error-resistant. All data is stored locally in JSON format for easy backup and portability.