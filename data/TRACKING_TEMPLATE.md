# Content Performance Tracking Template

## Manual Entry Format

### Quick Entry Template
Copy this template for manual tracking:

```
Video: [filename]
Platform: [tiktok/instagram/youtube/etc.]
Content Type: [validation/tips/facts/confession/mythbuster/quickwin/intro/outro]
Date Posted: [YYYY-MM-DD]
Time Posted: [HH:MM] (24hr format)

METRICS:
- Views: [number]
- Likes: [number]
- Saves: [number]
- Shares: [number]
- Comments: [number]
- Reach: [number] (if available)
- Impressions: [number] (if available)

NOTES:
[Any observations, trending factors, etc.]
```

### Analytics Command
Convert manual entry to database:
```bash
python analytics.py --log --video [filename] --platform [platform] --content-type [type] --views [#] --likes [#] --saves [#] --shares [#] --comments [#]
```

## KPI Definitions for Caregiving Niche

### Primary Metrics

**Views**: Total number of times content was watched
- Measures reach and discoverability
- Platform-specific counting methods apply

**Engagement Rate**: (Likes + Saves + Shares + Comments) / Views × 100
- Key performance indicator for content quality
- Shows how compelling content is to audience

**Save Rate**: Saves / Views × 100
- Critical metric for caregiving content
- Indicates practical value and reference potential

### Secondary Metrics

**Like Rate**: Likes / Views × 100
- Shows emotional resonance
- Caregiving content often sees higher like rates due to relatability

**Comment Rate**: Comments / Views × 100
- Indicates community engagement
- Valuable for building support networks

**Share Rate**: Shares / Views × 100
- Shows content value for wider distribution
- Important for reaching isolated caregivers

### Platform-Specific Considerations

**TikTok**:
- Views: Counted after 3+ seconds
- Saves: "Add to Favorites" button
- Algorithm favors completion rate and rewatches

**Instagram Reels**:
- Views: Counted immediately
- Saves: "Save to Collection" feature
- Stories vs. Reels have different metrics

**YouTube Shorts**:
- Views: Counted after 30 seconds for longer content
- Saves: "Save to Playlist" 
- Watch time is crucial metric

## Benchmark Targets for Caregiving Niche

### Content Type Benchmarks

**Validation Content** (Emotional Support)
- Target Engagement Rate: 8-12%
- Target Save Rate: 2-4%
- Expected Performance: High emotional engagement, moderate shares
- Best Times: Evening (7-9 PM) when caregivers wind down

**Tips & Advice** (Practical Help)
- Target Engagement Rate: 6-10%
- Target Save Rate: 3-6%
- Expected Performance: High saves, moderate likes
- Best Times: Early morning (6-8 AM) or lunch (12-1 PM)

**Facts & Education** (Information)
- Target Engagement Rate: 5-8%
- Target Save Rate: 2-4%
- Expected Performance: Steady, educational value
- Best Times: Mid-morning (9-11 AM)

**Confessions & Stories** (Community Building)
- Target Engagement Rate: 10-15%
- Target Save Rate: 1-3%
- Expected Performance: High comments, strong community response
- Best Times: Weekend evenings (7-10 PM)

**Quick Wins** (Actionable Content)
- Target Engagement Rate: 7-11%
- Target Save Rate: 4-7%
- Expected Performance: High saves and shares
- Best Times: Weekday mornings (7-9 AM)

### Platform Benchmarks

**TikTok** (Primary Platform for Caregiving Content)
- Good Engagement Rate: 6-12%
- Excellent Engagement Rate: 12%+
- Typical View Range: 500-50,000 (depending on follower count)
- Save Rate Target: 2-5%

**Instagram Reels**
- Good Engagement Rate: 4-8%
- Excellent Engagement Rate: 8%+
- Reach Rate Target: 150-300% of follower count
- Story Completion Rate: 70%+

**YouTube Shorts**
- Good Engagement Rate: 3-7%
- Excellent Engagement Rate: 7%+
- Click-through Rate Target: 8-12%
- Watch Time Target: 60%+

## Performance Indicators

### Green Flags (Excellent Performance)
- Engagement Rate > 10%
- Save Rate > 4%
- Comments show personal stories/gratitude
- Shares to private groups/DMs
- Organic reach > 200% of follower count

### Yellow Flags (Needs Improvement)
- Engagement Rate 3-6%
- Save Rate < 2%
- Comments are generic or sparse
- Low completion rate on videos
- Reach plateauing at follower count

### Red Flags (Content Issues)
- Engagement Rate < 3%
- Save Rate < 1%
- Negative or critical comments
- High drop-off rate in first 3 seconds
- Consistent underperformance across platforms

## Weekly Tracking Checklist

### Content Planning Review
- [ ] Review last week's top 3 performers
- [ ] Identify content types that resonated
- [ ] Note optimal posting times discovered
- [ ] Plan content mix for coming week

### Metric Collection
- [ ] Update analytics.py with new performance data
- [ ] Generate weekly report: `python analytics.py --report --period week`
- [ ] Export data for visualization: `python analytics.py --export --format csv --period week`
- [ ] Check best performers: `python analytics.py --best-performing --metric engagement_rate --count 5`

### Analysis Tasks
- [ ] Compare content type performance
- [ ] Identify trending topics/formats
- [ ] Review comment themes for content ideas
- [ ] Assess posting time effectiveness

### Planning Adjustments
- [ ] Adjust content calendar based on insights
- [ ] Experiment with high-performing formats
- [ ] Plan A/B tests for underperforming content types
- [ ] Set targets for next week

## Monthly Deep Dive

### Comprehensive Analysis
```bash
# Generate full monthly report
python analytics.py --report --period month

# Analyze content type performance
python analytics.py --content-type-analysis

# Export comprehensive data
python analytics.py --export --format json --period month
```

### Strategic Review Points
1. **Content Mix Optimization**: Which content types drive best engagement?
2. **Platform Performance**: Are we optimizing for each platform's strengths?
3. **Audience Growth**: How does engagement correlate with follower growth?
4. **Community Building**: Are comments fostering supportive connections?
5. **Practical Impact**: Do saves indicate real-world application of advice?

## Success Metrics for Caregiving Niche

### Quantitative Goals
- **Monthly View Goal**: 100,000+ across all platforms
- **Engagement Rate Target**: 8%+ average
- **Community Growth**: 15%+ monthly follower growth
- **Content Consistency**: 5-7 posts per week

### Qualitative Indicators
- **Comment Quality**: Personal stories, gratitude, shared experiences
- **Message Impact**: DMs about content helping real situations
- **Community Support**: Users supporting each other in comments
- **Professional Recognition**: Healthcare providers sharing content

### Long-term KPIs (Quarterly)
- **Brand Recognition**: Mentions without tags
- **Authority Building**: Citations by healthcare organizations
- **Community Health**: Ratio of supportive vs. negative comments
- **Real-world Impact**: Success stories from followers

## Crisis Content Guidelines

### Red Alert Metrics
If content receives:
- Engagement Rate < 2% consistently
- Negative comment ratio > 20%
- Significant unfollows after posting
- Platform warning/restriction

### Response Protocol
1. **Immediate**: Remove or edit problematic content
2. **Analysis**: Identify what went wrong
3. **Community**: Address concerns transparently
4. **Prevention**: Update content guidelines
5. **Recovery**: Focus on proven successful content types

## Notes Section

### Content Insights
_Track recurring themes, successful hooks, and audience preferences here_

### Platform Updates
_Note algorithm changes, new features, or platform-specific trends_

### Competitive Analysis
_Track what similar accounts are doing successfully_

### Seasonal Patterns
_Note how content performance varies by time of year, holidays, etc._

---

**Remember**: Numbers tell the story, but the real impact is in the lives touched and the support provided to the caregiving community. Quality over quantity always wins in the long run.