#!/usr/bin/env python3
"""
Analytics & Performance Tracking System for Kiin Content Factory

This system tracks content performance across platforms and generates
comprehensive analytics reports for caregiving niche content.

Usage Examples:
    python analytics.py --log --video validation_001.mp4 --platform tiktok --views 5000 --likes 300
    python analytics.py --report --period week
    python analytics.py --best-performing --metric saves --count 10
    python analytics.py --export --format csv --output analytics_export.csv
"""

import argparse
import json
import os
import sys
import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict
import statistics

class AnalyticsTracker:
    def __init__(self, data_file: str = None):
        """Initialize the analytics tracker with data file path."""
        if data_file is None:
            # Default to data directory relative to script location
            script_dir = Path(__file__).parent
            self.data_file = script_dir.parent / "data" / "performance.json"
        else:
            self.data_file = Path(data_file)
        
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self.performance_data = self._load_data()

    def _load_data(self) -> List[Dict[str, Any]]:
        """Load performance data from JSON file."""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                print(f"Warning: Could not load {self.data_file}. Starting with empty data.")
                return []
        return []

    def _save_data(self):
        """Save performance data to JSON file."""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.performance_data, f, indent=2, default=str)
        except IOError as e:
            print(f"Error saving data: {e}")
            sys.exit(1)

    def log_performance(self, video: str, platform: str, **metrics):
        """Log performance metrics for a video."""
        entry = {
            'video': video,
            'platform': platform,
            'timestamp': datetime.now().isoformat(),
            'metrics': {}
        }
        
        # Standard metrics with validation
        metric_fields = ['views', 'likes', 'saves', 'shares', 'comments', 'reach', 'impressions']
        for field in metric_fields:
            if field in metrics:
                try:
                    entry['metrics'][field] = int(metrics[field])
                except ValueError:
                    print(f"Warning: Invalid {field} value: {metrics[field]}")
        
        # Additional custom metrics
        for key, value in metrics.items():
            if key not in metric_fields and key != 'content_type':
                entry['metrics'][key] = value
        
        # Content type detection
        content_type = metrics.get('content_type', self._detect_content_type(video))
        entry['content_type'] = content_type
        
        # Calculate engagement rate
        views = entry['metrics'].get('views', 0)
        if views > 0:
            total_engagement = sum([
                entry['metrics'].get('likes', 0),
                entry['metrics'].get('saves', 0),
                entry['metrics'].get('shares', 0),
                entry['metrics'].get('comments', 0)
            ])
            entry['metrics']['engagement_rate'] = round((total_engagement / views) * 100, 2)
        
        self.performance_data.append(entry)
        self._save_data()
        
        print(f"✅ Logged performance for {video} on {platform}")
        print(f"   Views: {entry['metrics'].get('views', 0):,}")
        print(f"   Engagement Rate: {entry['metrics'].get('engagement_rate', 0)}%")

    def _detect_content_type(self, video: str) -> str:
        """Auto-detect content type from video filename."""
        video_lower = video.lower()
        
        type_keywords = {
            'validation': ['validation', 'affirm', 'support'],
            'tips': ['tips', 'tip', 'advice', 'how-to', 'guide'],
            'facts': ['facts', 'fact', 'did-you-know', 'education'],
            'confession': ['confession', 'confess', 'story', 'experience'],
            'mythbuster': ['myth', 'truth', 'debunk', 'reality'],
            'quickwin': ['quick', 'fast', 'easy', 'simple', 'win'],
            'intro': ['intro', 'introduction', 'welcome'],
            'outro': ['outro', 'ending', 'goodbye', 'thanks']
        }
        
        for content_type, keywords in type_keywords.items():
            if any(keyword in video_lower for keyword in keywords):
                return content_type
        
        return 'general'

    def generate_report(self, period: str = 'week'):
        """Generate performance report for specified period."""
        now = datetime.now()
        
        if period == 'week':
            start_date = now - timedelta(days=7)
            period_label = "Past 7 Days"
        elif period == 'month':
            start_date = now - timedelta(days=30)
            period_label = "Past 30 Days"
        elif period == 'all':
            start_date = datetime.min
            period_label = "All Time"
        else:
            print(f"Unknown period: {period}")
            return

        # Filter data by date
        period_data = []
        for entry in self.performance_data:
            entry_date = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00').split('+')[0])
            if entry_date >= start_date:
                period_data.append(entry)

        if not period_data:
            print(f"No data found for {period_label}")
            return

        print(f"\n📊 PERFORMANCE REPORT - {period_label}")
        print("=" * 50)
        
        # Overall metrics
        total_videos = len(period_data)
        total_views = sum(entry['metrics'].get('views', 0) for entry in period_data)
        total_likes = sum(entry['metrics'].get('likes', 0) for entry in period_data)
        total_saves = sum(entry['metrics'].get('saves', 0) for entry in period_data)
        total_shares = sum(entry['metrics'].get('shares', 0) for entry in period_data)
        total_comments = sum(entry['metrics'].get('comments', 0) for entry in period_data)
        
        engagement_rates = [entry['metrics'].get('engagement_rate', 0) for entry in period_data]
        avg_engagement_rate = statistics.mean(engagement_rates) if engagement_rates else 0
        
        print(f"📈 OVERVIEW:")
        print(f"   Total Videos: {total_videos}")
        print(f"   Total Views: {total_views:,}")
        print(f"   Total Likes: {total_likes:,}")
        print(f"   Total Saves: {total_saves:,}")
        print(f"   Total Shares: {total_shares:,}")
        print(f"   Total Comments: {total_comments:,}")
        print(f"   Average Engagement Rate: {avg_engagement_rate:.2f}%")
        
        # Platform breakdown
        platform_stats = defaultdict(lambda: {'videos': 0, 'views': 0, 'engagement': 0})
        for entry in period_data:
            platform = entry['platform']
            platform_stats[platform]['videos'] += 1
            platform_stats[platform]['views'] += entry['metrics'].get('views', 0)
            platform_stats[platform]['engagement'] += entry['metrics'].get('engagement_rate', 0)
        
        print(f"\n📱 BY PLATFORM:")
        for platform, stats in platform_stats.items():
            avg_engagement = stats['engagement'] / stats['videos'] if stats['videos'] > 0 else 0
            print(f"   {platform.upper()}: {stats['videos']} videos, {stats['views']:,} views, {avg_engagement:.2f}% avg engagement")
        
        # Content type breakdown
        content_stats = defaultdict(lambda: {'videos': 0, 'views': 0, 'engagement': 0})
        for entry in period_data:
            content_type = entry.get('content_type', 'general')
            content_stats[content_type]['videos'] += 1
            content_stats[content_type]['views'] += entry['metrics'].get('views', 0)
            content_stats[content_type]['engagement'] += entry['metrics'].get('engagement_rate', 0)
        
        print(f"\n🎬 BY CONTENT TYPE:")
        for content_type, stats in content_stats.items():
            avg_engagement = stats['engagement'] / stats['videos'] if stats['videos'] > 0 else 0
            print(f"   {content_type.title()}: {stats['videos']} videos, {stats['views']:,} views, {avg_engagement:.2f}% avg engagement")
        
        # Time analysis
        self._analyze_posting_times(period_data)

    def _analyze_posting_times(self, data: List[Dict[str, Any]]):
        """Analyze optimal posting times."""
        if not data:
            return
        
        hour_performance = defaultdict(list)
        weekday_performance = defaultdict(list)
        
        for entry in data:
            timestamp = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00').split('+')[0])
            hour = timestamp.hour
            weekday = timestamp.strftime('%A')
            
            engagement = entry['metrics'].get('engagement_rate', 0)
            hour_performance[hour].append(engagement)
            weekday_performance[weekday].append(engagement)
        
        print(f"\n⏰ OPTIMAL POSTING TIMES:")
        
        # Best hours
        hour_averages = {hour: statistics.mean(rates) for hour, rates in hour_performance.items()}
        best_hours = sorted(hour_averages.items(), key=lambda x: x[1], reverse=True)[:3]
        
        print(f"   Best Hours (by engagement):")
        for hour, avg_engagement in best_hours:
            print(f"     {hour:02d}:00 - {avg_engagement:.2f}% avg engagement")
        
        # Best days
        day_averages = {day: statistics.mean(rates) for day, rates in weekday_performance.items()}
        best_days = sorted(day_averages.items(), key=lambda x: x[1], reverse=True)[:3]
        
        print(f"   Best Days (by engagement):")
        for day, avg_engagement in best_days:
            print(f"     {day} - {avg_engagement:.2f}% avg engagement")

    def get_best_performing(self, metric: str = 'engagement_rate', count: int = 10):
        """Get best performing content by specified metric."""
        if not self.performance_data:
            print("No performance data available")
            return
        
        # Sort by metric (handle nested metrics)
        if metric in ['views', 'likes', 'saves', 'shares', 'comments', 'engagement_rate']:
            sorted_data = sorted(
                self.performance_data,
                key=lambda x: x['metrics'].get(metric, 0),
                reverse=True
            )
        else:
            print(f"Unknown metric: {metric}")
            return
        
        top_content = sorted_data[:count]
        
        print(f"\n🏆 TOP {count} PERFORMING CONTENT (by {metric.replace('_', ' ').title()})")
        print("=" * 60)
        
        for i, entry in enumerate(top_content, 1):
            metric_value = entry['metrics'].get(metric, 0)
            views = entry['metrics'].get('views', 0)
            engagement_rate = entry['metrics'].get('engagement_rate', 0)
            
            print(f"{i:2d}. {entry['video']}")
            print(f"    Platform: {entry['platform']} | Type: {entry.get('content_type', 'general')}")
            print(f"    {metric.replace('_', ' ').title()}: {metric_value:,} | Views: {views:,} | Engagement: {engagement_rate}%")
            print(f"    Posted: {entry['timestamp'][:10]}")
            print()

    def analyze_content_types(self):
        """Analyze performance by content type."""
        if not self.performance_data:
            print("No performance data available")
            return
        
        content_analysis = defaultdict(lambda: {
            'count': 0,
            'total_views': 0,
            'total_likes': 0,
            'total_saves': 0,
            'total_shares': 0,
            'total_comments': 0,
            'engagement_rates': []
        })
        
        for entry in self.performance_data:
            content_type = entry.get('content_type', 'general')
            stats = content_analysis[content_type]
            
            stats['count'] += 1
            stats['total_views'] += entry['metrics'].get('views', 0)
            stats['total_likes'] += entry['metrics'].get('likes', 0)
            stats['total_saves'] += entry['metrics'].get('saves', 0)
            stats['total_shares'] += entry['metrics'].get('shares', 0)
            stats['total_comments'] += entry['metrics'].get('comments', 0)
            stats['engagement_rates'].append(entry['metrics'].get('engagement_rate', 0))
        
        print(f"\n📊 CONTENT TYPE ANALYSIS")
        print("=" * 50)
        
        for content_type, stats in content_analysis.items():
            if stats['count'] == 0:
                continue
            
            avg_views = stats['total_views'] / stats['count']
            avg_engagement = statistics.mean(stats['engagement_rates']) if stats['engagement_rates'] else 0
            save_rate = (stats['total_saves'] / stats['total_views']) * 100 if stats['total_views'] > 0 else 0
            
            print(f"\n🎬 {content_type.upper()}")
            print(f"   Videos: {stats['count']}")
            print(f"   Total Views: {stats['total_views']:,}")
            print(f"   Avg Views/Video: {avg_views:,.0f}")
            print(f"   Avg Engagement Rate: {avg_engagement:.2f}%")
            print(f"   Save Rate: {save_rate:.2f}%")
            print(f"   Best Metric: ", end="")
            
            # Determine strongest metric
            metrics = {
                'likes': stats['total_likes'],
                'saves': stats['total_saves'],
                'shares': stats['total_shares'],
                'comments': stats['total_comments']
            }
            best_metric = max(metrics.items(), key=lambda x: x[1])
            print(f"{best_metric[0]} ({best_metric[1]:,} total)")

    def export_data(self, format_type: str = 'json', output_file: str = None, period: str = None):
        """Export performance data in specified format."""
        if not self.performance_data:
            print("No performance data to export")
            return
        
        # Filter by period if specified
        data_to_export = self.performance_data
        if period and period != 'all':
            now = datetime.now()
            if period == 'week':
                start_date = now - timedelta(days=7)
            elif period == 'month':
                start_date = now - timedelta(days=30)
            else:
                print(f"Unknown period: {period}")
                return
                
            data_to_export = [
                entry for entry in self.performance_data
                if datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00').split('+')[0]) >= start_date
            ]
        
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            period_suffix = f"_{period}" if period else ""
            output_file = f"analytics_export{period_suffix}_{timestamp}.{format_type}"
        
        export_path = Path(output_file)
        
        if format_type.lower() == 'csv':
            self._export_csv(data_to_export, export_path)
        elif format_type.lower() == 'json':
            self._export_json(data_to_export, export_path)
        else:
            print(f"Unsupported export format: {format_type}")
            return
        
        print(f"✅ Data exported to {export_path}")
        print(f"   Records: {len(data_to_export)}")

    def _export_csv(self, data: List[Dict[str, Any]], output_path: Path):
        """Export data to CSV format."""
        if not data:
            return
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'video', 'platform', 'content_type', 'timestamp',
                'views', 'likes', 'saves', 'shares', 'comments',
                'engagement_rate', 'reach', 'impressions'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for entry in data:
                row = {
                    'video': entry['video'],
                    'platform': entry['platform'],
                    'content_type': entry.get('content_type', 'general'),
                    'timestamp': entry['timestamp'],
                }
                
                # Add metrics
                for field in fieldnames[4:]:
                    row[field] = entry['metrics'].get(field, 0)
                
                writer.writerow(row)

    def _export_json(self, data: List[Dict[str, Any]], output_path: Path):
        """Export data to JSON format."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                'export_date': datetime.now().isoformat(),
                'total_records': len(data),
                'data': data
            }, f, indent=2, default=str)

    def show_dashboard_summary(self):
        """Show a quick dashboard summary."""
        if not self.performance_data:
            print("No performance data available")
            return
        
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        
        # Recent data
        recent_data = [
            entry for entry in self.performance_data
            if datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00').split('+')[0]) >= week_ago
        ]
        
        print(f"\n📊 DASHBOARD SUMMARY")
        print("=" * 30)
        print(f"Total Videos: {len(self.performance_data)}")
        print(f"This Week: {len(recent_data)}")
        
        if recent_data:
            total_views = sum(entry['metrics'].get('views', 0) for entry in recent_data)
            avg_engagement = statistics.mean([
                entry['metrics'].get('engagement_rate', 0) for entry in recent_data
            ])
            
            print(f"Week Views: {total_views:,}")
            print(f"Avg Engagement: {avg_engagement:.2f}%")
            
            # Top platform this week
            platform_views = defaultdict(int)
            for entry in recent_data:
                platform_views[entry['platform']] += entry['metrics'].get('views', 0)
            
            if platform_views:
                top_platform = max(platform_views.items(), key=lambda x: x[1])
                print(f"Top Platform: {top_platform[0]} ({top_platform[1]:,} views)")


def main():
    parser = argparse.ArgumentParser(
        description='Analytics & Performance Tracking System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Log performance:
    python analytics.py --log --video validation_001.mp4 --platform tiktok --views 5000 --likes 300
    
  Generate reports:
    python analytics.py --report --period week
    python analytics.py --report --period month
    
  Find best content:
    python analytics.py --best-performing --metric saves --count 10
    python analytics.py --best-performing --metric engagement_rate --count 5
    
  Export data:
    python analytics.py --export --format csv
    python analytics.py --export --format json --period week
    
  Quick dashboard:
    python analytics.py --dashboard
        """
    )
    
    # Main action groups
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument('--log', action='store_true', help='Log performance data')
    action_group.add_argument('--report', action='store_true', help='Generate performance report')
    action_group.add_argument('--best-performing', action='store_true', help='Show best performing content')
    action_group.add_argument('--content-type-analysis', action='store_true', help='Analyze content type performance')
    action_group.add_argument('--export', action='store_true', help='Export data')
    action_group.add_argument('--dashboard', action='store_true', help='Show dashboard summary')
    
    # Logging arguments
    parser.add_argument('--video', help='Video filename')
    parser.add_argument('--platform', help='Platform name (tiktok, instagram, youtube, etc.)')
    parser.add_argument('--content-type', help='Content type override')
    parser.add_argument('--views', type=int, help='View count')
    parser.add_argument('--likes', type=int, help='Like count')
    parser.add_argument('--saves', type=int, help='Save count')
    parser.add_argument('--shares', type=int, help='Share count')
    parser.add_argument('--comments', type=int, help='Comment count')
    parser.add_argument('--reach', type=int, help='Reach count')
    parser.add_argument('--impressions', type=int, help='Impression count')
    
    # Report arguments
    parser.add_argument('--period', choices=['week', 'month', 'all'], default='week', help='Report period')
    
    # Best performing arguments
    parser.add_argument('--metric', default='engagement_rate', 
                       choices=['views', 'likes', 'saves', 'shares', 'comments', 'engagement_rate'],
                       help='Metric to rank by')
    parser.add_argument('--count', type=int, default=10, help='Number of top items to show')
    
    # Export arguments
    parser.add_argument('--format', choices=['csv', 'json'], default='json', help='Export format')
    parser.add_argument('--output', help='Output filename')
    
    # Data file override
    parser.add_argument('--data-file', help='Custom data file path')
    
    args = parser.parse_args()
    
    # Initialize tracker
    tracker = AnalyticsTracker(args.data_file)
    
    try:
        if args.log:
            if not args.video or not args.platform:
                print("Error: --video and --platform are required for logging")
                sys.exit(1)
            
            metrics = {}
            for metric in ['views', 'likes', 'saves', 'shares', 'comments', 'reach', 'impressions']:
                value = getattr(args, metric)
                if value is not None:
                    metrics[metric] = value
            
            if args.content_type:
                metrics['content_type'] = args.content_type
            
            tracker.log_performance(args.video, args.platform, **metrics)
            
        elif args.report:
            tracker.generate_report(args.period)
            
        elif args.best_performing:
            tracker.get_best_performing(args.metric, args.count)
            
        elif args.content_type_analysis:
            tracker.analyze_content_types()
            
        elif args.export:
            tracker.export_data(args.format, args.output, args.period)
            
        elif args.dashboard:
            tracker.show_dashboard_summary()
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()