"""
Hashtag Optimizer - Platform-specific hashtag research and optimization.
"""

import json
import requests
import logging
import re
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3

logger = logging.getLogger(__name__)

class HashtagOptimizer:
    """Optimize hashtags for different social media platforms"""
    
    def __init__(self, config_path: str = "config/hashtags.json"):
        self.config_path = config_path
        self.db_path = "data/hashtag_analytics.db"
        self.config = self._load_config()
        self._init_database()
        
        # Platform-specific hashtag limits and rules
        self.platform_specs = {
            'instagram': {
                'max_hashtags': 30,
                'optimal_count': 11,
                'style': 'separate_comment',  # Can be in post or comment
                'character_limit': None,
                'trending_weight': 0.3
            },
            'tiktok': {
                'max_hashtags': 100,  # Character limit matters more
                'optimal_count': 8,
                'style': 'integrated',  # Part of caption
                'character_limit': 100,  # Total hashtag characters
                'trending_weight': 0.5
            },
            'youtube': {
                'max_hashtags': 15,
                'optimal_count': 5,
                'style': 'description',  # In description
                'character_limit': None,
                'trending_weight': 0.2
            },
            'twitter': {
                'max_hashtags': 10,
                'optimal_count': 3,
                'style': 'integrated',
                'character_limit': 50,  # Reasonable limit for readability
                'trending_weight': 0.4
            },
            'linkedin': {
                'max_hashtags': 5,
                'optimal_count': 3,
                'style': 'professional',
                'character_limit': None,
                'trending_weight': 0.1
            },
            'pinterest': {
                'max_hashtags': 20,
                'optimal_count': 10,
                'style': 'descriptive',
                'character_limit': None,
                'trending_weight': 0.3
            },
            'facebook': {
                'max_hashtags': 10,
                'optimal_count': 5,
                'style': 'minimal',  # Less important on Facebook
                'character_limit': None,
                'trending_weight': 0.1
            }
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """Load hashtag configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Return default config if file doesn't exist
            return self._get_default_config()
        except Exception as e:
            logger.error(f"Error loading hashtag config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default hashtag configuration"""
        return {
            "core_hashtags": ["caregiver", "caregiving", "familycare"],
            "emotional_hashtags": ["caregiversupport", "yourenotalone", "caregiverstress"],
            "niche_hashtags": ["sandwichgeneration", "dementia", "eldercare", "alzheimers"],
            "trending_detection": True,
            "banned_hashtags": ["follow4follow", "like4like", "spam"],
            "platform_specific": {
                "instagram": ["instagramreels", "reelsinstagram"],
                "tiktok": ["fyp", "foryou", "viral"],
                "youtube": ["shorts", "youtubeshorts"],
                "linkedin": ["healthcare", "professionalcare"],
                "pinterest": ["selfcare", "wellness"],
                "facebook": ["familysupport", "community"]
            }
        }
    
    def _init_database(self):
        """Initialize database for hashtag analytics"""
        Path(self.db_path).parent.mkdir(exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS hashtag_performance (
                    hashtag TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    post_id TEXT NOT NULL,
                    impressions INTEGER DEFAULT 0,
                    engagement INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY (hashtag, platform, post_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS trending_hashtags (
                    hashtag TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    trend_score REAL DEFAULT 0,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (hashtag, platform)
                )
            """)
    
    def optimize_hashtags(self, content_text: str, platform: str, 
                         content_type: str = "video") -> List[str]:
        """Generate optimized hashtags for specific platform and content"""
        
        # Get platform specifications
        spec = self.platform_specs.get(platform, {})
        max_hashtags = spec.get('max_hashtags', 10)
        optimal_count = spec.get('optimal_count', 5)
        
        # Start with content-relevant hashtags
        content_hashtags = self._extract_content_hashtags(content_text, platform)
        
        # Add core hashtags
        core_hashtags = self._get_core_hashtags(platform)
        
        # Add trending hashtags
        trending_hashtags = self._get_trending_hashtags(platform)
        
        # Add niche hashtags
        niche_hashtags = self._get_niche_hashtags(content_text, platform)
        
        # Add platform-specific hashtags
        platform_hashtags = self._get_platform_specific_hashtags(platform, content_type)
        
        # Combine and score hashtags
        all_hashtags = self._combine_and_score_hashtags(
            content_hashtags, core_hashtags, trending_hashtags, 
            niche_hashtags, platform_hashtags, platform
        )
        
        # Filter and optimize
        optimized_hashtags = self._filter_and_optimize(
            all_hashtags, platform, optimal_count, max_hashtags
        )
        
        logger.info(f"Generated {len(optimized_hashtags)} hashtags for {platform}")
        return optimized_hashtags
    
    def _extract_content_hashtags(self, content_text: str, platform: str) -> List[tuple]:
        """Extract relevant hashtags based on content analysis"""
        hashtags = []
        
        # Define keyword mappings to hashtags
        keyword_mappings = {
            'stress': ['stress', 'caregiverstruggle', 'mentalhealth'],
            'support': ['support', 'caregiversupport', 'community'],
            'tips': ['tips', 'caregivertips', 'advice'],
            'family': ['family', 'familycare', 'familysupport'],
            'elderly': ['elderly', 'eldercare', 'seniors'],
            'dementia': ['dementia', 'alzheimers', 'memorycare'],
            'burnout': ['burnout', 'caregiverselfcare', 'wellness'],
            'help': ['help', 'caregiverhelp', 'resources'],
            'love': ['love', 'caregiverolve', 'compassion'],
            'difficult': ['difficult', 'hardtimes', 'struggle']
        }
        
        content_lower = content_text.lower()
        
        for keyword, related_hashtags in keyword_mappings.items():
            if keyword in content_lower:
                for hashtag in related_hashtags:
                    score = self._calculate_hashtag_score(hashtag, platform)
                    hashtags.append((hashtag, score))
        
        return hashtags
    
    def _get_core_hashtags(self, platform: str) -> List[tuple]:
        """Get core hashtags with scores"""
        core_hashtags = self.config.get('core_hashtags', [])
        return [(tag, self._calculate_hashtag_score(tag, platform)) for tag in core_hashtags]
    
    def _get_trending_hashtags(self, platform: str) -> List[tuple]:
        """Get trending hashtags for platform"""
        if not self.config.get('trending_detection', False):
            return []
        
        trending = []
        
        # Check database for stored trending hashtags
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT hashtag, trend_score FROM trending_hashtags 
                WHERE platform = ? AND updated_at > ?
                ORDER BY trend_score DESC LIMIT 10
            """, (platform, (datetime.now() - timedelta(days=1)).isoformat()))
            
            trending = [(row[0], row[1]) for row in cursor.fetchall()]
        
        # If no stored trending data, use default trending hashtags
        if not trending:
            trending = self._get_default_trending_hashtags(platform)
        
        return trending
    
    def _get_default_trending_hashtags(self, platform: str) -> List[tuple]:
        """Get default trending hashtags when API data isn't available"""
        default_trending = {
            'instagram': ['caregiverlife', 'caregivercommunity', 'eldercaretips'],
            'tiktok': ['caregivertiktok', 'sandwichgeneration', 'caregiversupport'],
            'youtube': ['caregivingjourney', 'caregiverolve', 'eldercare'],
            'twitter': ['CaregiverChat', 'ElderCare', 'CaregivingTips'],
            'linkedin': ['CaregivingProfessionals', 'HealthcareTips', 'FamilyCare'],
            'pinterest': ['CaregiverWellness', 'ElderCareTips', 'CaregiverSupport'],
            'facebook': ['CaregiverCommunity', 'FamilyCaregiving', 'ElderSupport']
        }
        
        hashtags = default_trending.get(platform, [])
        return [(tag, 0.7) for tag in hashtags]  # Default trending score
    
    def _get_niche_hashtags(self, content_text: str, platform: str) -> List[tuple]:
        """Get niche-specific hashtags"""
        niche_hashtags = self.config.get('niche_hashtags', [])
        content_lower = content_text.lower()
        
        relevant_niche = []
        for tag in niche_hashtags:
            # Check if hashtag is relevant to content
            if any(keyword in content_lower for keyword in [
                'dementia', 'alzheimer', 'memory', 'sandwich', 'elder', 
                'parent', 'aging', 'senior'
            ]):
                score = self._calculate_hashtag_score(tag, platform)
                relevant_niche.append((tag, score))
        
        return relevant_niche
    
    def _get_platform_specific_hashtags(self, platform: str, content_type: str) -> List[tuple]:
        """Get platform-specific hashtags"""
        platform_hashtags = self.config.get('platform_specific', {}).get(platform, [])
        
        # Add content type specific hashtags
        if content_type == 'video':
            video_hashtags = {
                'instagram': ['reels', 'instagramreels'],
                'tiktok': ['fyp', 'foryou'],
                'youtube': ['shorts', 'youtubeshorts'],
                'facebook': ['facebookreels', 'reels']
            }
            platform_hashtags.extend(video_hashtags.get(platform, []))
        
        return [(tag, self._calculate_hashtag_score(tag, platform)) for tag in platform_hashtags]
    
    def _calculate_hashtag_score(self, hashtag: str, platform: str) -> float:
        """Calculate hashtag score based on performance data and platform"""
        base_score = 0.5  # Base score for all hashtags
        
        # Get historical performance from database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT AVG(engagement), AVG(impressions), COUNT(*) 
                FROM hashtag_performance 
                WHERE hashtag = ? AND platform = ?
            """, (hashtag, platform))
            
            row = cursor.fetchone()
            if row and row[2] > 0:  # Have performance data
                avg_engagement = row[0] or 0
                avg_impressions = row[1] or 0
                post_count = row[2]
                
                # Calculate performance score
                performance_score = min((avg_engagement / 100 + avg_impressions / 1000) / post_count, 1.0)
                base_score = base_score * 0.3 + performance_score * 0.7
        
        # Apply platform-specific adjustments
        spec = self.platform_specs.get(platform, {})
        trending_weight = spec.get('trending_weight', 0.3)
        
        # Adjust for hashtag length (shorter usually better)
        length_penalty = max(0, (len(hashtag) - 10) * 0.05)
        base_score -= length_penalty
        
        # Boost core caregiver hashtags
        if hashtag in self.config.get('core_hashtags', []):
            base_score += 0.2
        
        # Boost emotional support hashtags
        if hashtag in self.config.get('emotional_hashtags', []):
            base_score += 0.1
        
        return max(0.0, min(1.0, base_score))
    
    def _combine_and_score_hashtags(self, *hashtag_lists, platform: str) -> List[tuple]:
        """Combine hashtag lists and remove duplicates"""
        all_hashtags = {}
        
        for hashtag_list in hashtag_lists:
            for hashtag, score in hashtag_list:
                # Clean hashtag
                clean_hashtag = self._clean_hashtag(hashtag)
                if self._is_valid_hashtag(clean_hashtag, platform):
                    # Take the highest score if duplicate
                    if clean_hashtag in all_hashtags:
                        all_hashtags[clean_hashtag] = max(all_hashtags[clean_hashtag], score)
                    else:
                        all_hashtags[clean_hashtag] = score
        
        # Convert back to list of tuples and sort by score
        hashtags = [(tag, score) for tag, score in all_hashtags.items()]
        hashtags.sort(key=lambda x: x[1], reverse=True)
        
        return hashtags
    
    def _clean_hashtag(self, hashtag: str) -> str:
        """Clean and normalize hashtag"""
        # Remove # if present
        hashtag = hashtag.lstrip('#')
        
        # Remove spaces and special characters
        hashtag = re.sub(r'[^a-zA-Z0-9]', '', hashtag)
        
        # Convert to lowercase
        hashtag = hashtag.lower()
        
        return hashtag
    
    def _is_valid_hashtag(self, hashtag: str, platform: str) -> bool:
        """Check if hashtag is valid for platform"""
        if not hashtag:
            return False
        
        # Check banned hashtags
        banned = self.config.get('banned_hashtags', [])
        if hashtag.lower() in [b.lower() for b in banned]:
            return False
        
        # Check length constraints
        if len(hashtag) < 3 or len(hashtag) > 30:
            return False
        
        # Platform-specific validation
        spec = self.platform_specs.get(platform, {})
        
        # LinkedIn should avoid too casual hashtags
        if platform == 'linkedin':
            casual_words = ['lol', 'omg', 'yolo', 'swag', 'viral', 'trending']
            if any(word in hashtag.lower() for word in casual_words):
                return False
        
        return True
    
    def _filter_and_optimize(self, hashtags: List[tuple], platform: str, 
                           optimal_count: int, max_hashtags: int) -> List[str]:
        """Filter and optimize hashtag selection"""
        
        # Ensure we don't exceed character limits for platforms that have them
        spec = self.platform_specs.get(platform, {})
        character_limit = spec.get('character_limit')
        
        selected_hashtags = []
        total_characters = 0
        
        for hashtag, score in hashtags:
            if len(selected_hashtags) >= max_hashtags:
                break
            
            hashtag_length = len(hashtag) + 1  # +1 for #
            
            if character_limit and (total_characters + hashtag_length) > character_limit:
                continue
            
            selected_hashtags.append(hashtag)
            total_characters += hashtag_length
            
            # Stop at optimal count if we have good scores
            if len(selected_hashtags) >= optimal_count and score < 0.6:
                break
        
        return selected_hashtags
    
    def track_hashtag_performance(self, hashtags: List[str], platform: str, 
                                 post_id: str, impressions: int, engagement: int):
        """Track hashtag performance for future optimization"""
        with sqlite3.connect(self.db_path) as conn:
            for hashtag in hashtags:
                clean_hashtag = self._clean_hashtag(hashtag)
                conn.execute("""
                    INSERT OR REPLACE INTO hashtag_performance 
                    (hashtag, platform, post_id, impressions, engagement, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    clean_hashtag, platform, post_id, 
                    impressions, engagement, datetime.now().isoformat()
                ))
    
    def update_trending_hashtags(self, platform: str, trending_data: Dict[str, float]):
        """Update trending hashtag data"""
        with sqlite3.connect(self.db_path) as conn:
            for hashtag, trend_score in trending_data.items():
                clean_hashtag = self._clean_hashtag(hashtag)
                conn.execute("""
                    INSERT OR REPLACE INTO trending_hashtags 
                    (hashtag, platform, trend_score, updated_at)
                    VALUES (?, ?, ?, ?)
                """, (
                    clean_hashtag, platform, trend_score, datetime.now().isoformat()
                ))
    
    def get_hashtag_analytics(self, platform: Optional[str] = None, 
                             days: int = 30) -> Dict[str, Any]:
        """Get hashtag performance analytics"""
        with sqlite3.connect(self.db_path) as conn:
            # Base query
            query = """
                SELECT hashtag, platform, 
                       AVG(impressions) as avg_impressions,
                       AVG(engagement) as avg_engagement,
                       COUNT(*) as usage_count
                FROM hashtag_performance 
                WHERE created_at > ?
            """
            params = [(datetime.now() - timedelta(days=days)).isoformat()]
            
            if platform:
                query += " AND platform = ?"
                params.append(platform)
            
            query += " GROUP BY hashtag, platform ORDER BY avg_engagement DESC"
            
            cursor = conn.execute(query, params)
            
            analytics = {
                "top_performing": [],
                "most_used": [],
                "platform_breakdown": {}
            }
            
            all_results = cursor.fetchall()
            
            # Top performing hashtags
            analytics["top_performing"] = [
                {
                    "hashtag": row[0],
                    "platform": row[1],
                    "avg_impressions": row[2],
                    "avg_engagement": row[3],
                    "usage_count": row[4]
                }
                for row in all_results[:20]
            ]
            
            # Most used hashtags
            most_used = sorted(all_results, key=lambda x: x[4], reverse=True)[:10]
            analytics["most_used"] = [
                {
                    "hashtag": row[0],
                    "platform": row[1],
                    "usage_count": row[4],
                    "avg_engagement": row[3]
                }
                for row in most_used
            ]
            
            # Platform breakdown
            for row in all_results:
                platform_name = row[1]
                if platform_name not in analytics["platform_breakdown"]:
                    analytics["platform_breakdown"][platform_name] = {
                        "total_hashtags": 0,
                        "avg_impressions": 0,
                        "avg_engagement": 0
                    }
                
                breakdown = analytics["platform_breakdown"][platform_name]
                breakdown["total_hashtags"] += row[4]
                breakdown["avg_impressions"] += row[2] * row[4]
                breakdown["avg_engagement"] += row[3] * row[4]
            
            # Calculate averages
            for platform_name, data in analytics["platform_breakdown"].items():
                if data["total_hashtags"] > 0:
                    data["avg_impressions"] /= data["total_hashtags"]
                    data["avg_engagement"] /= data["total_hashtags"]
        
        return analytics
    
    def suggest_hashtag_strategy(self, content_theme: str, platforms: List[str]) -> Dict[str, Any]:
        """Suggest hashtag strategy for content theme across platforms"""
        strategy = {
            "recommendations": {},
            "cross_platform_hashtags": [],
            "platform_specific_focus": {}
        }
        
        # Generate hashtags for each platform
        for platform in platforms:
            hashtags = self.optimize_hashtags(content_theme, platform)
            strategy["recommendations"][platform] = hashtags
        
        # Find cross-platform hashtags (appear in multiple platforms)
        all_hashtags = set()
        platform_hashtags = {}
        
        for platform, hashtags in strategy["recommendations"].items():
            platform_hashtags[platform] = set(hashtags)
            all_hashtags.update(hashtags)
        
        # Find hashtags that work across multiple platforms
        cross_platform = []
        for hashtag in all_hashtags:
            platforms_using = [p for p, tags in platform_hashtags.items() if hashtag in tags]
            if len(platforms_using) > 1:
                cross_platform.append({
                    "hashtag": hashtag,
                    "platforms": platforms_using,
                    "platform_count": len(platforms_using)
                })
        
        strategy["cross_platform_hashtags"] = sorted(
            cross_platform, 
            key=lambda x: x["platform_count"], 
            reverse=True
        )
        
        # Platform-specific focus recommendations
        for platform in platforms:
            spec = self.platform_specs.get(platform, {})
            strategy["platform_specific_focus"][platform] = {
                "style": spec.get("style", "integrated"),
                "optimal_count": spec.get("optimal_count", 5),
                "max_count": spec.get("max_hashtags", 10),
                "trending_importance": spec.get("trending_weight", 0.3)
            }
        
        return strategy