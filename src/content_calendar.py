#!/usr/bin/env python3
"""
Content Calendar Generator for Kiin Content

Based on research findings:
- Best posting times: 10-11 AM and 6-8 PM
- Optimal frequency: 1-3x per day TikTok, 3-4x week Instagram
- Content mix: 40% educational, 30% personal, 20% community, 10% awareness

Usage:
    python content_calendar.py --weeks 4 --output calendar.json
"""

import argparse
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
import calendar


class ContentCalendarGenerator:
    """Generate posting calendars based on research-backed best practices"""
    
    # Content type mappings based on research
    CONTENT_CATEGORIES = {
        'educational': ['tips'],                    # 40% - Educational content
        'personal': ['validation', 'confession'],   # 30% - Personal/emotional content  
        'community': ['sandwich', 'chaos'],         # 20% - Community/relatable content
        'awareness': ['tips']                       # 10% - Awareness content (tips can serve dual purpose)
    }
    
    # Platform-specific posting patterns based on research
    PLATFORM_SCHEDULES = {
        'tiktok': {
            'frequency_range': (1, 3),  # 1-3 posts per day
            'best_times': ['10:00', '10:30', '11:00', '18:00', '19:00', '20:00'],
            'active_days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        },
        'instagram': {
            'frequency_range': (3, 4),  # 3-4 posts per week  
            'best_times': ['10:00', '10:30', '11:00', '18:00', '18:30', '19:00', '19:30', '20:00'],
            'active_days': ['tuesday', 'wednesday', 'thursday', 'friday', 'saturday']  # Skip Monday/Sunday for lower frequency
        }
    }
    
    # Content type weights for distribution
    CONTENT_WEIGHTS = {
        'educational': 0.40,
        'personal': 0.30,
        'community': 0.20,
        'awareness': 0.10
    }
    
    def __init__(self, content_library_path: str = None):
        """Initialize calendar generator"""
        self.content_library_path = Path(content_library_path) if content_library_path else None
        self.content_library = self._load_content_library()
        
    def _load_content_library(self) -> Dict:
        """Load available content from manifest or create mock data"""
        if self.content_library_path and self.content_library_path.exists():
            with open(self.content_library_path, 'r') as f:
                manifest = json.load(f)
                return self._organize_content_by_type(manifest.get('videos', []))
        
        # Create mock content library for planning
        return self._create_mock_content_library()
    
    def _organize_content_by_type(self, videos: List[Dict]) -> Dict:
        """Organize videos by content type"""
        organized = {}
        for video in videos:
            if video.get('success', False):
                content_type = video.get('type')
                if content_type not in organized:
                    organized[content_type] = []
                organized[content_type].append(video)
        return organized
    
    def _create_mock_content_library(self) -> Dict:
        """Create mock content library for planning purposes"""
        mock_library = {}
        
        # Create mock entries for each content type
        content_types = ['validation', 'tips', 'confession', 'sandwich', 'chaos']
        
        for content_type in content_types:
            mock_library[content_type] = []
            for i in range(50):  # 50 mock videos per type
                mock_video = {
                    'id': f"mock_{content_type}_{i:03d}",
                    'type': content_type,
                    'filename': f"{content_type}_{i:03d}.mp4",
                    'file_path': f"./output/{content_type}/{content_type}_{i:03d}.mp4",
                    'success': True,
                    'metadata': {
                        'content_type': content_type,
                        'batch_number': i
                    }
                }
                mock_library[content_type].append(mock_video)
        
        return mock_library
    
    def _get_content_category(self, content_type: str) -> str:
        """Map content type to research-based category"""
        for category, types in self.CONTENT_CATEGORIES.items():
            if content_type in types:
                return category
        return 'educational'  # Default fallback
    
    def _select_content_for_slot(self, used_content: Dict, preferred_category: str = None) -> Tuple[str, Dict]:
        """Select content for a posting slot"""
        # If no preference, use weighted random selection
        if not preferred_category:
            categories = list(self.CONTENT_WEIGHTS.keys())
            weights = list(self.CONTENT_WEIGHTS.values())
            preferred_category = random.choices(categories, weights=weights)[0]
        
        # Get content types for the category
        content_types = self.CONTENT_CATEGORIES.get(preferred_category, ['tips'])
        
        # Try each content type until we find available content
        for content_type in content_types:
            if content_type in self.content_library:
                available_content = [
                    content for content in self.content_library[content_type]
                    if content['id'] not in used_content
                ]
                
                if available_content:
                    selected = random.choice(available_content)
                    used_content[selected['id']] = True
                    return content_type, selected
        
        # Fallback: select any available content
        for content_type, content_list in self.content_library.items():
            available_content = [
                content for content in content_list
                if content['id'] not in used_content
            ]
            
            if available_content:
                selected = random.choice(available_content)
                used_content[selected['id']] = True
                return content_type, selected
        
        # No content available - return mock
        return 'tips', {
            'id': f"fallback_{random.randint(1000, 9999)}",
            'filename': 'content_needed.mp4',
            'type': 'tips'
        }
    
    def _get_weekday_name(self, date: datetime) -> str:
        """Get weekday name in lowercase"""
        return date.strftime('%A').lower()
    
    def generate_calendar(self, start_date: datetime, weeks: int) -> Dict:
        """Generate posting calendar for specified period"""
        calendar_data = {}
        used_content = {}  # Track used content to avoid duplicates
        
        # Content category tracking for balanced distribution
        category_counts = {cat: 0 for cat in self.CONTENT_WEIGHTS.keys()}
        total_posts = 0
        
        current_date = start_date
        end_date = start_date + timedelta(weeks=weeks)
        
        while current_date < end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            weekday = self._get_weekday_name(current_date)
            calendar_data[date_str] = []
            
            # Generate posts for each platform
            for platform, schedule in self.PLATFORM_SCHEDULES.items():
                # Skip if not an active day for this platform
                if weekday not in schedule['active_days']:
                    continue
                
                # Determine number of posts for today
                min_posts, max_posts = schedule['frequency_range']
                
                # For weekly frequency platforms, distribute posts across the week
                if platform == 'instagram':
                    # 3-4 posts per week = roughly every other day with some variation
                    posts_today = 1 if random.random() < 0.6 else 0  # 60% chance of posting
                    if total_posts == 0 and current_date == start_date:
                        posts_today = 1  # Ensure at least one post on start date
                else:
                    # Daily posting platforms
                    posts_today = random.randint(min_posts, max_posts)
                
                # Generate posts for today
                used_times = set()
                
                for post_num in range(posts_today):
                    # Select posting time
                    available_times = [time for time in schedule['best_times'] if time not in used_times]
                    if not available_times:
                        available_times = schedule['best_times']  # Allow duplicates if needed
                    
                    post_time = random.choice(available_times)
                    used_times.add(post_time)
                    
                    # Determine content category for balanced distribution
                    target_category = self._get_balanced_category(category_counts, total_posts)
                    
                    # Select content
                    content_type, content = self._select_content_for_slot(used_content, target_category)
                    category = self._get_content_category(content_type)
                    
                    # Update category counts
                    category_counts[category] += 1
                    total_posts += 1
                    
                    # Create calendar entry
                    calendar_entry = {
                        'time': post_time,
                        'platform': platform,
                        'content_type': content_type,
                        'category': category,
                        'video': content.get('filename', f'{content_type}_placeholder.mp4'),
                        'video_id': content.get('id'),
                        'file_path': content.get('file_path'),
                        'metadata': {
                            'weekday': weekday,
                            'week_number': (current_date - start_date).days // 7 + 1,
                            'post_number_today': post_num + 1,
                            'total_post_number': total_posts
                        }
                    }
                    
                    calendar_data[date_str].append(calendar_entry)
            
            # Sort posts by time for each day
            calendar_data[date_str].sort(key=lambda x: x['time'])
            
            current_date += timedelta(days=1)
        
        return calendar_data, category_counts, total_posts
    
    def _get_balanced_category(self, category_counts: Dict, total_posts: int) -> str:
        """Select category to maintain balanced content distribution"""
        if total_posts == 0:
            return 'educational'  # Start with educational content
        
        # Calculate current distribution
        current_distribution = {
            cat: count / total_posts for cat, count in category_counts.items()
        }
        
        # Find category that's most under-represented
        target_category = None
        max_deficit = 0
        
        for category, target_weight in self.CONTENT_WEIGHTS.items():
            current_weight = current_distribution.get(category, 0)
            deficit = target_weight - current_weight
            
            if deficit > max_deficit:
                max_deficit = deficit
                target_category = category
        
        return target_category or 'educational'
    
    def generate_summary_stats(self, calendar_data: Dict, category_counts: Dict, total_posts: int) -> Dict:
        """Generate summary statistics for the calendar"""
        # Platform distribution
        platform_counts = {}
        time_distribution = {}
        weekday_distribution = {}
        
        for date, posts in calendar_data.items():
            weekday = datetime.strptime(date, '%Y-%m-%d').strftime('%A')
            
            for post in posts:
                # Platform counts
                platform = post['platform']
                platform_counts[platform] = platform_counts.get(platform, 0) + 1
                
                # Time distribution
                time = post['time']
                time_distribution[time] = time_distribution.get(time, 0) + 1
                
                # Weekday distribution
                weekday_distribution[weekday] = weekday_distribution.get(weekday, 0) + 1
        
        # Category distribution percentages
        category_percentages = {
            cat: (count / total_posts * 100) if total_posts > 0 else 0
            for cat, count in category_counts.items()
        }
        
        return {
            'total_posts': total_posts,
            'posts_per_week': total_posts / (len(calendar_data) / 7) if len(calendar_data) > 0 else 0,
            'platform_distribution': platform_counts,
            'category_distribution': category_counts,
            'category_percentages': category_percentages,
            'time_distribution': time_distribution,
            'weekday_distribution': weekday_distribution,
            'date_range': {
                'start': min(calendar_data.keys()) if calendar_data else None,
                'end': max(calendar_data.keys()) if calendar_data else None,
                'total_days': len(calendar_data)
            }
        }
    
    def save_calendar(self, calendar_data: Dict, output_path: Path, include_stats: bool = True):
        """Save calendar to JSON file"""
        calendar_obj, category_counts, total_posts = calendar_data
        
        output_data = {
            'generated_at': datetime.now().isoformat(),
            'calendar': calendar_obj
        }
        
        if include_stats:
            output_data['stats'] = self.generate_summary_stats(calendar_obj, category_counts, total_posts)
        
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        return output_path
    
    def generate_markdown_calendar(self, calendar_data: Dict, output_path: Path):
        """Generate human-readable markdown calendar"""
        calendar_obj, category_counts, total_posts = calendar_data
        stats = self.generate_summary_stats(calendar_obj, category_counts, total_posts)
        
        markdown_content = []
        
        # Header
        markdown_content.append("# Content Posting Calendar\n")
        markdown_content.append(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")
        
        # Summary statistics
        markdown_content.append("## Summary Statistics\n")
        markdown_content.append(f"- **Total Posts:** {stats['total_posts']}")
        markdown_content.append(f"- **Posts per Week:** {stats['posts_per_week']:.1f}")
        markdown_content.append(f"- **Date Range:** {stats['date_range']['start']} to {stats['date_range']['end']}")
        markdown_content.append(f"- **Total Days:** {stats['date_range']['total_days']}\n")
        
        # Platform distribution
        markdown_content.append("### Platform Distribution")
        for platform, count in stats['platform_distribution'].items():
            percentage = (count / stats['total_posts'] * 100) if stats['total_posts'] > 0 else 0
            markdown_content.append(f"- **{platform.title()}:** {count} posts ({percentage:.1f}%)")
        markdown_content.append("")
        
        # Content category distribution
        markdown_content.append("### Content Category Distribution")
        for category, count in stats['category_distribution'].items():
            percentage = stats['category_percentages'][category]
            target_percentage = self.CONTENT_WEIGHTS[category] * 100
            markdown_content.append(f"- **{category.title()}:** {count} posts ({percentage:.1f}% - target: {target_percentage:.0f}%)")
        markdown_content.append("")
        
        # Best posting times
        markdown_content.append("### Most Used Posting Times")
        sorted_times = sorted(stats['time_distribution'].items(), key=lambda x: x[1], reverse=True)
        for time, count in sorted_times[:5]:
            markdown_content.append(f"- **{time}:** {count} posts")
        markdown_content.append("")
        
        # Weekly calendar view
        markdown_content.append("## Weekly Calendar View\n")
        
        # Group dates by week
        dates = sorted(calendar_obj.keys())
        if dates:
            current_week = None
            week_number = 1
            
            for date_str in dates:
                date = datetime.strptime(date_str, '%Y-%m-%d')
                week_start = date - timedelta(days=date.weekday())
                
                if current_week != week_start:
                    if current_week is not None:
                        markdown_content.append("")  # End previous week
                    
                    current_week = week_start
                    week_end = week_start + timedelta(days=6)
                    markdown_content.append(f"### Week {week_number}: {week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}")
                    week_number += 1
                
                # Day header
                posts = calendar_obj[date_str]
                weekday = date.strftime('%A')
                if posts:
                    markdown_content.append(f"\n**{weekday}, {date.strftime('%B %d')}** ({len(posts)} posts)")
                    
                    # Group posts by time
                    for post in posts:
                        platform_emoji = "📱" if post['platform'] == 'tiktok' else "📸"
                        category_emoji = {
                            'educational': '📚',
                            'personal': '💝', 
                            'community': '🤝',
                            'awareness': '💡'
                        }.get(post['category'], '📝')
                        
                        markdown_content.append(
                            f"  - {post['time']} {platform_emoji} **{post['platform'].upper()}** "
                            f"{category_emoji} {post['content_type']} → `{post['video']}`"
                        )
        
        # Daily schedule view
        markdown_content.append("\n## Daily Schedule View\n")
        
        for date_str in sorted(calendar_obj.keys()):
            posts = calendar_obj[date_str]
            if not posts:
                continue
                
            date = datetime.strptime(date_str, '%Y-%m-%d')
            markdown_content.append(f"### {date.strftime('%A, %B %d, %Y')}")
            
            for post in posts:
                platform_emoji = "📱" if post['platform'] == 'tiktok' else "📸"
                category_emoji = {
                    'educational': '📚',
                    'personal': '💝', 
                    'community': '🤝',
                    'awareness': '💡'
                }.get(post['category'], '📝')
                
                markdown_content.append(f"- **{post['time']}** {platform_emoji} {post['platform'].upper()}")
                markdown_content.append(f"  - Content: {category_emoji} {post['content_type']} ({post['category']})")
                markdown_content.append(f"  - Video: `{post['video']}`")
                
                # Add file path if available and not mock
                if post.get('file_path') and not post['video_id'].startswith('mock_'):
                    markdown_content.append(f"  - Path: `{post['file_path']}`")
                
                markdown_content.append("")
        
        # Research notes
        markdown_content.append("\n## Research-Based Scheduling Notes\n")
        markdown_content.append("This calendar is based on research findings:")
        markdown_content.append("- **Best posting times:** 10-11 AM and 6-8 PM")
        markdown_content.append("- **TikTok frequency:** 1-3 posts per day")
        markdown_content.append("- **Instagram frequency:** 3-4 posts per week")
        markdown_content.append("- **Content mix:** 40% educational, 30% personal, 20% community, 10% awareness")
        markdown_content.append("\n*Adjust times based on your audience's timezone and engagement patterns.*")
        
        # Save markdown file
        with open(output_path, 'w') as f:
            f.write('\n'.join(markdown_content))
        
        return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate content posting calendar based on research best practices",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate 4-week calendar
  python content_calendar.py --weeks 4 --output calendar.json
  
  # Generate calendar using existing content library
  python content_calendar.py --weeks 2 --content-library ./output/manifest.json --output my_calendar.json
  
  # Generate calendar with markdown view
  python content_calendar.py --weeks 1 --output calendar.json --markdown calendar.md
        """
    )
    
    parser.add_argument('--weeks', type=int, required=True,
                       help='Number of weeks to generate calendar for')
    parser.add_argument('--output', default='calendar.json',
                       help='Output JSON file path (default: calendar.json)')
    parser.add_argument('--markdown', type=str,
                       help='Also generate human-readable markdown calendar')
    parser.add_argument('--start-date', type=str,
                       help='Start date (YYYY-MM-DD, default: tomorrow)')
    parser.add_argument('--content-library', type=str,
                       help='Path to content library manifest.json')
    
    args = parser.parse_args()
    
    # Determine start date
    if args.start_date:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
    else:
        # Default to tomorrow to allow time for content creation
        start_date = datetime.now() + timedelta(days=1)
    
    # Create generator
    generator = ContentCalendarGenerator(args.content_library)
    
    print(f"🗓️  Generating {args.weeks}-week content calendar...")
    print(f"📅 Start date: {start_date.strftime('%Y-%m-%d (%A)')}")
    
    # Generate calendar
    calendar_data = generator.generate_calendar(start_date, args.weeks)
    calendar_obj, category_counts, total_posts = calendar_data
    
    # Save JSON calendar
    output_path = Path(args.output)
    generator.save_calendar(calendar_data, output_path)
    
    print(f"✅ Calendar saved: {output_path}")
    print(f"📊 Total posts scheduled: {total_posts}")
    
    # Generate markdown if requested
    if args.markdown:
        markdown_path = Path(args.markdown)
        generator.generate_markdown_calendar(calendar_data, markdown_path)
        print(f"📝 Markdown calendar saved: {markdown_path}")
    
    # Print quick summary
    stats = generator.generate_summary_stats(calendar_obj, category_counts, total_posts)
    print(f"\n📈 Quick Summary:")
    print(f"   • Posts per week: {stats['posts_per_week']:.1f}")
    print(f"   • Platform split: TikTok {stats['platform_distribution'].get('tiktok', 0)}, Instagram {stats['platform_distribution'].get('instagram', 0)}")
    
    # Show category distribution vs targets
    print(f"\n📊 Content Mix (target in parentheses):")
    for category, percentage in stats['category_percentages'].items():
        target = generator.CONTENT_WEIGHTS[category] * 100
        status = "✅" if abs(percentage - target) <= 10 else "⚠️ "
        print(f"   • {category.title()}: {percentage:.1f}% ({target:.0f}%) {status}")


if __name__ == "__main__":
    main()