"""
Timing Optimizer - Optimal posting times for different platforms and audiences.
"""

import json
import sqlite3
import pytz
from datetime import datetime, timedelta, time
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class TimingOptimizer:
    """Optimize posting times for maximum engagement"""
    
    def __init__(self, config_path: str = "config/posting_schedule.json"):
        self.config_path = config_path
        self.db_path = "data/timing_analytics.db"
        self.config = self._load_config()
        self._init_database()
        
        # Default optimal times by platform (EST timezone)
        self.default_optimal_times = {
            'instagram': [
                {'day': 'monday', 'time': '11:00', 'score': 0.8},
                {'day': 'monday', 'time': '14:00', 'score': 0.7},
                {'day': 'tuesday', 'time': '11:00', 'score': 0.9},
                {'day': 'tuesday', 'time': '14:00', 'score': 0.8},
                {'day': 'wednesday', 'time': '11:00', 'score': 0.8},
                {'day': 'wednesday', 'time': '15:00', 'score': 0.7},
                {'day': 'thursday', 'time': '11:00', 'score': 0.8},
                {'day': 'thursday', 'time': '14:00', 'score': 0.8},
                {'day': 'friday', 'time': '10:00', 'score': 0.7},
                {'day': 'friday', 'time': '13:00', 'score': 0.6},
                {'day': 'saturday', 'time': '10:00', 'score': 0.6},
                {'day': 'saturday', 'time': '14:00', 'score': 0.7},
                {'day': 'sunday', 'time': '12:00', 'score': 0.8},
                {'day': 'sunday', 'time': '15:00', 'score': 0.7}
            ],
            'tiktok': [
                {'day': 'tuesday', 'time': '09:00', 'score': 0.9},
                {'day': 'thursday', 'time': '12:00', 'score': 0.8},
                {'day': 'friday', 'time': '15:00', 'score': 0.8},
                {'day': 'saturday', 'time': '11:00', 'score': 0.7},
                {'day': 'sunday', 'time': '19:00', 'score': 0.8}
            ],
            'youtube': [
                {'day': 'tuesday', 'time': '14:00', 'score': 0.8},
                {'day': 'wednesday', 'time': '15:00', 'score': 0.9},
                {'day': 'thursday', 'time': '14:00', 'score': 0.8},
                {'day': 'saturday', 'time': '10:00', 'score': 0.7},
                {'day': 'sunday', 'time': '11:00', 'score': 0.8}
            ],
            'twitter': [
                {'day': 'monday', 'time': '09:00', 'score': 0.7},
                {'day': 'tuesday', 'time': '10:00', 'score': 0.8},
                {'day': 'wednesday', 'time': '09:00', 'score': 0.8},
                {'day': 'wednesday', 'time': '15:00', 'score': 0.7},
                {'day': 'thursday', 'time': '10:00', 'score': 0.8},
                {'day': 'friday', 'time': '09:00', 'score': 0.6}
            ],
            'linkedin': [
                {'day': 'tuesday', 'time': '10:00', 'score': 0.9},
                {'day': 'wednesday', 'time': '11:00', 'score': 0.8},
                {'day': 'thursday', 'time': '09:00', 'score': 0.8},
                {'day': 'thursday', 'time': '14:00', 'score': 0.7}
            ],
            'pinterest': [
                {'day': 'saturday', 'time': '20:00', 'score': 0.8},
                {'day': 'sunday', 'time': '19:00', 'score': 0.9},
                {'day': 'tuesday', 'time': '14:00', 'score': 0.7},
                {'day': 'friday', 'time': '15:00', 'score': 0.7}
            ],
            'facebook': [
                {'day': 'tuesday', 'time': '15:00', 'score': 0.8},
                {'day': 'wednesday', 'time': '15:00', 'score': 0.9},
                {'day': 'thursday', 'time': '15:00', 'score': 0.8},
                {'day': 'saturday', 'time': '12:00', 'score': 0.7}
            ]
        }
        
        # Caregiver audience patterns (when caregivers are most active)
        self.caregiver_patterns = {
            'morning_routine': {  # Early morning during care routines
                'time_range': ('06:00', '08:00'),
                'days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
                'score_modifier': 0.6  # Lower engagement but high relatability
            },
            'lunch_break': {  # Midday break
                'time_range': ('11:00', '13:00'),
                'days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
                'score_modifier': 0.9  # High engagement
            },
            'evening_wind_down': {  # Evening after care duties
                'time_range': ('19:00', '21:00'),
                'days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'],
                'score_modifier': 0.8  # Good engagement
            },
            'weekend_rest': {  # Weekend relaxation time
                'time_range': ('10:00', '15:00'),
                'days': ['saturday', 'sunday'],
                'score_modifier': 0.7  # Moderate engagement
            },
            'late_night_reflection': {  # Late night when caregivers reflect
                'time_range': ('21:00', '23:00'),
                'days': ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday'],
                'score_modifier': 0.6  # Lower volume but high emotional connection
            }
        }
        
        # Holiday and special event considerations
        self.special_events = {
            'national_caregivers_month': {'month': 11, 'boost': 0.2},  # November
            'mothers_day': {'month': 5, 'week': 2, 'boost': 0.3},
            'fathers_day': {'month': 6, 'week': 3, 'boost': 0.3},
            'world_alzheimers_day': {'month': 9, 'day': 21, 'boost': 0.4},
            'mental_health_awareness_month': {'month': 5, 'boost': 0.2},
            'thanksgiving': {'month': 11, 'week': -1, 'avoid': True},  # Family time
            'christmas': {'month': 12, 'day': 25, 'avoid': True},
            'new_years': {'month': 1, 'day': 1, 'avoid': True}
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """Load timing configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._get_default_config()
        except Exception as e:
            logger.error(f"Error loading timing config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default timing configuration"""
        return {
            "timezone": "America/New_York",  # EST - where many caregivers are
            "posting_frequency": {
                "instagram": {"daily": 1, "weekly": 7},
                "tiktok": {"daily": 1, "weekly": 5},
                "youtube": {"weekly": 2},
                "twitter": {"daily": 2, "weekly": 10},
                "linkedin": {"weekly": 3},
                "pinterest": {"weekly": 3},
                "facebook": {"weekly": 4}
            },
            "minimum_gap_hours": 2,  # Minimum time between posts on same platform
            "cross_platform_gap_minutes": 15,  # Gap between posting to different platforms
            "avoid_holidays": True,
            "audience_timezone_distribution": {
                "America/New_York": 0.4,    # EST - 40%
                "America/Chicago": 0.25,    # CST - 25%
                "America/Denver": 0.15,     # MST - 15%
                "America/Los_Angeles": 0.2  # PST - 20%
            }
        }
    
    def _init_database(self):
        """Initialize database for timing analytics"""
        Path(self.db_path).parent.mkdir(exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS posting_performance (
                    post_id TEXT PRIMARY KEY,
                    platform TEXT NOT NULL,
                    posted_at TEXT NOT NULL,
                    day_of_week TEXT NOT NULL,
                    hour INTEGER NOT NULL,
                    timezone TEXT NOT NULL,
                    impressions INTEGER DEFAULT 0,
                    engagement INTEGER DEFAULT 0,
                    engagement_rate REAL DEFAULT 0.0,
                    created_at TEXT NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS optimal_times (
                    platform TEXT NOT NULL,
                    day_of_week TEXT NOT NULL,
                    hour INTEGER NOT NULL,
                    engagement_score REAL DEFAULT 0.0,
                    post_count INTEGER DEFAULT 0,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (platform, day_of_week, hour)
                )
            """)
    
    def get_optimal_posting_time(self, platform: str, content_type: str = 'video',
                                target_timezone: Optional[str] = None) -> datetime:
        """Get the next optimal posting time for a platform"""
        
        # Use configured timezone or default
        tz_name = target_timezone or self.config.get('timezone', 'America/New_York')
        tz = pytz.timezone(tz_name)
        now = datetime.now(tz)
        
        # Get optimal times for platform
        optimal_times = self._get_platform_optimal_times(platform)
        
        # Find next optimal time
        next_times = []
        
        for i in range(7):  # Check next 7 days
            check_date = now.date() + timedelta(days=i)
            day_name = check_date.strftime('%A').lower()
            
            for time_slot in optimal_times:
                if time_slot['day'] == day_name:
                    time_obj = datetime.strptime(time_slot['time'], '%H:%M').time()
                    candidate_datetime = tz.localize(datetime.combine(check_date, time_obj))
                    
                    # Must be in the future
                    if candidate_datetime > now:
                        # Check if this time conflicts with existing posts
                        if not self._has_posting_conflict(candidate_datetime, platform):
                            # Apply caregiver audience adjustments
                            adjusted_score = self._adjust_for_caregiver_audience(
                                time_slot['score'], candidate_datetime
                            )
                            
                            # Check for special events
                            adjusted_score = self._adjust_for_special_events(
                                adjusted_score, candidate_datetime
                            )
                            
                            next_times.append({
                                'datetime': candidate_datetime,
                                'score': adjusted_score,
                                'original_score': time_slot['score']
                            })
        
        if not next_times:
            # Fallback: return next business hour
            return self._get_fallback_time(now, platform)
        
        # Sort by score and return best time
        next_times.sort(key=lambda x: x['score'], reverse=True)
        best_time = next_times[0]['datetime']
        
        logger.info(f"Optimal posting time for {platform}: {best_time} (score: {next_times[0]['score']:.2f})")
        return best_time
    
    def _get_platform_optimal_times(self, platform: str) -> List[Dict[str, Any]]:
        """Get optimal times for a platform from database or defaults"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT day_of_week, hour, engagement_score, post_count
                FROM optimal_times 
                WHERE platform = ? AND post_count >= 3
                ORDER BY engagement_score DESC
            """, (platform,))
            
            db_times = cursor.fetchall()
        
        if db_times:
            # Convert database results to expected format
            return [
                {
                    'day': row[0],
                    'time': f"{row[1]:02d}:00",
                    'score': row[2]
                }
                for row in db_times
            ]
        else:
            # Use default times
            return self.default_optimal_times.get(platform, [])
    
    def _has_posting_conflict(self, candidate_time: datetime, platform: str) -> bool:
        """Check if posting time conflicts with recent posts"""
        
        min_gap_hours = self.config.get('minimum_gap_hours', 2)
        
        with sqlite3.connect(self.db_path) as conn:
            # Check for posts within minimum gap
            cursor = conn.execute("""
                SELECT COUNT(*) FROM posting_performance 
                WHERE platform = ? 
                AND posted_at BETWEEN ? AND ?
            """, (
                platform,
                (candidate_time - timedelta(hours=min_gap_hours)).isoformat(),
                (candidate_time + timedelta(hours=min_gap_hours)).isoformat()
            ))
            
            conflict_count = cursor.fetchone()[0]
            return conflict_count > 0
    
    def _adjust_for_caregiver_audience(self, base_score: float, post_time: datetime) -> float:
        """Adjust score based on caregiver audience patterns"""
        
        day_name = post_time.strftime('%A').lower()
        time_str = post_time.strftime('%H:%M')
        hour = post_time.hour
        
        # Check each caregiver pattern
        for pattern_name, pattern_data in self.caregiver_patterns.items():
            if day_name in pattern_data['days']:
                start_time, end_time = pattern_data['time_range']
                start_hour = int(start_time.split(':')[0])
                end_hour = int(end_time.split(':')[0])
                
                if start_hour <= hour <= end_hour:
                    modifier = pattern_data['score_modifier']
                    adjusted_score = base_score * modifier
                    logger.debug(f"Applied {pattern_name} modifier {modifier} to score")
                    return adjusted_score
        
        return base_score
    
    def _adjust_for_special_events(self, base_score: float, post_time: datetime) -> float:
        """Adjust score for special events and holidays"""
        
        month = post_time.month
        day = post_time.day
        
        for event_name, event_data in self.special_events.items():
            # Check if date matches event
            if 'month' in event_data and event_data['month'] == month:
                
                # Specific day events
                if 'day' in event_data and event_data['day'] == day:
                    if event_data.get('avoid', False):
                        return base_score * 0.2  # Significantly reduce score
                    elif 'boost' in event_data:
                        return base_score * (1 + event_data['boost'])
                
                # Month-long events
                elif 'boost' in event_data and 'day' not in event_data:
                    return base_score * (1 + event_data['boost'])
        
        return base_score
    
    def _get_fallback_time(self, now: datetime, platform: str) -> datetime:
        """Get fallback time when no optimal times are available"""
        
        # Default to next business day at 2 PM
        next_weekday = now
        while next_weekday.weekday() >= 5:  # Weekend
            next_weekday += timedelta(days=1)
        
        # Set to 2 PM
        fallback_time = next_weekday.replace(hour=14, minute=0, second=0, microsecond=0)
        
        # If it's already past 2 PM today, move to tomorrow
        if fallback_time <= now:
            fallback_time += timedelta(days=1)
        
        return fallback_time
    
    def schedule_bulk_posting(self, platforms: List[str], content_count: int = 1,
                             start_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Schedule multiple posts across platforms optimally"""
        
        if not start_date:
            start_date = datetime.now(pytz.timezone(self.config.get('timezone', 'America/New_York')))
        
        schedule = []
        platform_last_post = {}  # Track last post time per platform
        
        for i in range(content_count):
            for platform in platforms:
                
                # Get optimal time for this platform
                if platform in platform_last_post:
                    # Ensure minimum gap from last post
                    min_gap = timedelta(hours=self.config.get('minimum_gap_hours', 2))
                    earliest_time = platform_last_post[platform] + min_gap
                else:
                    earliest_time = start_date
                
                # Find optimal time after earliest_time
                optimal_time = self._find_next_optimal_time(platform, earliest_time)
                
                schedule.append({
                    'platform': platform,
                    'content_index': i,
                    'scheduled_time': optimal_time,
                    'day_of_week': optimal_time.strftime('%A'),
                    'time_slot': optimal_time.strftime('%H:%M'),
                    'timezone': optimal_time.tzinfo.zone
                })
                
                platform_last_post[platform] = optimal_time
        
        # Sort by scheduled time
        schedule.sort(key=lambda x: x['scheduled_time'])
        
        logger.info(f"Scheduled {len(schedule)} posts across {len(platforms)} platforms")
        return schedule
    
    def _find_next_optimal_time(self, platform: str, after_time: datetime) -> datetime:
        """Find next optimal time for platform after given time"""
        
        optimal_times = self._get_platform_optimal_times(platform)
        
        # Look for optimal times in the next 14 days
        for i in range(14):
            check_date = after_time.date() + timedelta(days=i)
            day_name = check_date.strftime('%A').lower()
            
            for time_slot in optimal_times:
                if time_slot['day'] == day_name:
                    time_obj = datetime.strptime(time_slot['time'], '%H:%M').time()
                    candidate_datetime = after_time.tzinfo.localize(
                        datetime.combine(check_date, time_obj)
                    )
                    
                    if candidate_datetime > after_time:
                        return candidate_datetime
        
        # Fallback
        return self._get_fallback_time(after_time, platform)
    
    def track_posting_performance(self, post_id: str, platform: str, posted_at: datetime,
                                 impressions: int, engagement: int):
        """Track posting performance to improve timing optimization"""
        
        engagement_rate = (engagement / impressions * 100) if impressions > 0 else 0
        
        with sqlite3.connect(self.db_path) as conn:
            # Store individual post performance
            conn.execute("""
                INSERT OR REPLACE INTO posting_performance 
                (post_id, platform, posted_at, day_of_week, hour, timezone, 
                 impressions, engagement, engagement_rate, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                post_id, platform, posted_at.isoformat(),
                posted_at.strftime('%A').lower(), posted_at.hour,
                str(posted_at.tzinfo), impressions, engagement,
                engagement_rate, datetime.now().isoformat()
            ))
            
            # Update optimal times aggregation
            self._update_optimal_times(platform, posted_at, engagement_rate)
    
    def _update_optimal_times(self, platform: str, posted_at: datetime, engagement_rate: float):
        """Update optimal times based on performance data"""
        
        day_of_week = posted_at.strftime('%A').lower()
        hour = posted_at.hour
        
        with sqlite3.connect(self.db_path) as conn:
            # Get existing data
            cursor = conn.execute("""
                SELECT engagement_score, post_count FROM optimal_times
                WHERE platform = ? AND day_of_week = ? AND hour = ?
            """, (platform, day_of_week, hour))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing record with weighted average
                old_score, old_count = existing
                new_count = old_count + 1
                new_score = ((old_score * old_count) + engagement_rate) / new_count
                
                conn.execute("""
                    UPDATE optimal_times 
                    SET engagement_score = ?, post_count = ?, updated_at = ?
                    WHERE platform = ? AND day_of_week = ? AND hour = ?
                """, (
                    new_score, new_count, datetime.now().isoformat(),
                    platform, day_of_week, hour
                ))
            else:
                # Insert new record
                conn.execute("""
                    INSERT INTO optimal_times 
                    (platform, day_of_week, hour, engagement_score, post_count, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    platform, day_of_week, hour, engagement_rate, 1,
                    datetime.now().isoformat()
                ))
    
    def get_timing_analytics(self, platform: Optional[str] = None, 
                            days: int = 30) -> Dict[str, Any]:
        """Get timing performance analytics"""
        
        with sqlite3.connect(self.db_path) as conn:
            # Base query
            query = """
                SELECT platform, day_of_week, hour,
                       AVG(engagement_rate) as avg_engagement,
                       COUNT(*) as post_count,
                       AVG(impressions) as avg_impressions
                FROM posting_performance 
                WHERE posted_at > ?
            """
            params = [(datetime.now() - timedelta(days=days)).isoformat()]
            
            if platform:
                query += " AND platform = ?"
                params.append(platform)
            
            query += " GROUP BY platform, day_of_week, hour"
            
            cursor = conn.execute(query, params)
            results = cursor.fetchall()
        
        # Process results
        analytics = {
            'best_times': [],
            'platform_analysis': {},
            'day_analysis': {},
            'hour_analysis': {}
        }
        
        for row in results:
            plt, day, hour, engagement, count, impressions = row
            
            analytics['best_times'].append({
                'platform': plt,
                'day_of_week': day,
                'hour': hour,
                'engagement_rate': engagement,
                'post_count': count,
                'avg_impressions': impressions
            })
            
            # Platform analysis
            if plt not in analytics['platform_analysis']:
                analytics['platform_analysis'][plt] = {
                    'avg_engagement': 0,
                    'total_posts': 0,
                    'best_day': '',
                    'best_hour': 0
                }
            
            platform_data = analytics['platform_analysis'][plt]
            platform_data['avg_engagement'] = max(platform_data['avg_engagement'], engagement)
            platform_data['total_posts'] += count
            
            if engagement > platform_data['avg_engagement']:
                platform_data['best_day'] = day
                platform_data['best_hour'] = hour
        
        # Sort best times by engagement
        analytics['best_times'].sort(key=lambda x: x['engagement_rate'], reverse=True)
        
        return analytics
    
    def suggest_posting_schedule(self, platforms: List[str], posts_per_week: int = 7) -> Dict[str, Any]:
        """Suggest an optimized weekly posting schedule"""
        
        schedule = {}
        daily_posts = posts_per_week / 7
        
        for platform in platforms:
            platform_frequency = self.config.get('posting_frequency', {}).get(platform, {})
            weekly_posts = platform_frequency.get('weekly', 3)
            
            # Get best times for this platform
            optimal_times = self._get_platform_optimal_times(platform)
            
            # Select best times up to weekly limit
            selected_times = optimal_times[:weekly_posts]
            
            schedule[platform] = {
                'weekly_posts': weekly_posts,
                'optimal_slots': selected_times,
                'recommended_gaps': f"{24 // len(selected_times) if selected_times else 24} hours"
            }
        
        return {
            'weekly_schedule': schedule,
            'total_weekly_posts': sum(s['weekly_posts'] for s in schedule.values()),
            'timezone': self.config.get('timezone'),
            'notes': [
                "Times are optimized for caregiver audience",
                "Avoid posting during major holidays",
                f"Maintain {self.config.get('minimum_gap_hours', 2)}+ hour gaps between posts on same platform"
            ]
        }
    
    def check_holiday_conflicts(self, date: datetime) -> Dict[str, Any]:
        """Check if date conflicts with holidays or special events"""
        
        conflicts = {
            'should_avoid': False,
            'has_boost': False,
            'events': [],
            'recommendations': []
        }
        
        month = date.month
        day = date.day
        
        for event_name, event_data in self.special_events.items():
            if 'month' in event_data and event_data['month'] == month:
                
                # Check specific day events
                if 'day' in event_data and event_data['day'] == day:
                    conflicts['events'].append(event_name)
                    
                    if event_data.get('avoid', False):
                        conflicts['should_avoid'] = True
                        conflicts['recommendations'].append(f"Avoid posting on {event_name}")
                    elif 'boost' in event_data:
                        conflicts['has_boost'] = True
                        conflicts['recommendations'].append(
                            f"Good time to post - {event_name} boost available"
                        )
                
                # Check month-long events
                elif 'boost' in event_data and 'day' not in event_data:
                    conflicts['events'].append(f"{event_name} (month-long)")
                    conflicts['has_boost'] = True
                    conflicts['recommendations'].append(
                        f"Consider {event_name}-themed content this month"
                    )
        
        return conflicts