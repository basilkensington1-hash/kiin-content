#!/usr/bin/env python3
"""
Kiin Content Factory - Content Strategy Planner

Comprehensive content planning tool that maps content pillars, generates topic clusters,
creates content calendars, and integrates seasonal themes with trending topics.
"""

import json
import datetime
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
import calendar
import random
from collections import defaultdict, Counter

class ContentType(Enum):
    BLOG_POST = "blog_post"
    VIDEO = "video"
    INFOGRAPHIC = "infographic"
    SOCIAL_POST = "social_post"
    GUIDE = "guide"
    CHECKLIST = "checklist"
    CASE_STUDY = "case_study"
    WEBINAR = "webinar"
    PODCAST = "podcast"
    EMAIL = "email"

class FunnelStage(Enum):
    AWARENESS = "awareness"
    CONSIDERATION = "consideration" 
    DECISION = "decision"
    RETENTION = "retention"

class Platform(Enum):
    BLOG = "blog"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    PINTEREST = "pinterest"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    TWITTER = "twitter"

@dataclass
class ContentIdea:
    """Single content idea with metadata"""
    title: str
    content_type: ContentType
    platform: Platform
    funnel_stage: FunnelStage
    pillar: str
    cluster: str
    target_keyword: str
    secondary_keywords: List[str]
    estimated_effort: int  # Hours
    priority_score: float  # 0-100
    seasonal_relevance: Optional[str] = None
    trending_factor: float = 0.0
    target_audience: str = "family caregivers"
    content_angle: str = "educational"
    suggested_cta: str = ""
    related_content: List[str] = None
    
    def __post_init__(self):
        if self.related_content is None:
            self.related_content = []
        if self.secondary_keywords is None:
            self.secondary_keywords = []

@dataclass
class ContentCalendarEntry:
    """Content calendar entry"""
    date: str
    content_idea: ContentIdea
    status: str = "planned"  # planned, in_progress, completed, published
    assigned_to: str = ""
    notes: str = ""

class ContentStrategyPlanner:
    """Main content strategy planning tool"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Load configurations
        self.load_strategy_config()
        self.load_keywords_config()
        
        # Content generation rules
        self.content_rules = self.load_content_rules()
        
        # Generated ideas storage
        self.content_ideas: List[ContentIdea] = []
        
    def load_strategy_config(self):
        """Load content strategy configuration"""
        config_path = Path("config/content_strategy.json")
        if config_path.exists():
            with open(config_path) as f:
                self.strategy = json.load(f)
        else:
            self.strategy = self.get_default_strategy()
    
    def load_keywords_config(self):
        """Load keyword configuration"""
        config_path = Path("config/seo_keywords.json")
        if config_path.exists():
            with open(config_path) as f:
                self.keywords = json.load(f)
        else:
            self.keywords = {}
    
    def get_default_strategy(self) -> Dict:
        """Get default strategy if config not found"""
        return {
            "pillars": [
                "Caregiver Self-Care",
                "Care Coordination",
                "Emotional Support", 
                "Practical Tips",
                "Family Dynamics"
            ],
            "clusters": {},
            "seasonal_themes": {},
            "platform_strategy": {}
        }
    
    def load_content_rules(self) -> Dict:
        """Load content generation rules and patterns"""
        return {
            "posting_frequency": {
                Platform.BLOG: 2,  # Posts per week
                Platform.TIKTOK: 5,
                Platform.INSTAGRAM: 7,
                Platform.YOUTUBE: 2,
                Platform.PINTEREST: 10
            },
            "content_mix": {
                # Percentage distribution
                "educational": 40,
                "inspirational": 25,
                "practical": 20,
                "personal": 10,
                "promotional": 5
            },
            "funnel_distribution": {
                FunnelStage.AWARENESS: 50,
                FunnelStage.CONSIDERATION: 30,
                FunnelStage.DECISION: 15,
                FunnelStage.RETENTION: 5
            },
            "effort_estimation": {
                ContentType.BLOG_POST: 4,  # Hours
                ContentType.VIDEO: 8,
                ContentType.INFOGRAPHIC: 6,
                ContentType.SOCIAL_POST: 1,
                ContentType.GUIDE: 12,
                ContentType.CHECKLIST: 3
            }
        }
    
    def generate_content_ideas_for_cluster(self, cluster_name: str, cluster_data: Dict, 
                                         count: int = 20) -> List[ContentIdea]:
        """Generate content ideas for a specific topic cluster"""
        ideas = []
        
        main_topic = cluster_data.get('main_topic', cluster_name)
        supporting_topics = cluster_data.get('supporting_topics', [])
        cluster_keywords = cluster_data.get('keywords', [])
        
        # Generate ideas for each supporting topic
        for topic in supporting_topics[:count]:
            # Determine content type and platform distribution
            content_combinations = [
                (ContentType.BLOG_POST, Platform.BLOG, FunnelStage.AWARENESS),
                (ContentType.VIDEO, Platform.YOUTUBE, FunnelStage.CONSIDERATION),
                (ContentType.SOCIAL_POST, Platform.INSTAGRAM, FunnelStage.AWARENESS),
                (ContentType.INFOGRAPHIC, Platform.PINTEREST, FunnelStage.CONSIDERATION),
                (ContentType.GUIDE, Platform.BLOG, FunnelStage.DECISION),
                (ContentType.CHECKLIST, Platform.BLOG, FunnelStage.DECISION)
            ]
            
            # Select appropriate combination
            content_type, platform, funnel_stage = random.choice(content_combinations)
            
            # Generate title variations
            titles = self.generate_title_variations(topic, content_type)
            
            for title in titles[:2]:  # Max 2 titles per topic
                # Select primary keyword
                primary_keyword = self.select_primary_keyword(topic, cluster_keywords)
                
                # Generate secondary keywords
                secondary_keywords = self.generate_secondary_keywords(primary_keyword, topic)
                
                # Calculate priority score
                priority_score = self.calculate_content_priority(
                    primary_keyword, content_type, funnel_stage, cluster_name
                )
                
                # Determine content angle
                content_angle = self.determine_content_angle(title, funnel_stage)
                
                # Generate CTA
                cta = self.generate_cta(funnel_stage, platform)
                
                idea = ContentIdea(
                    title=title,
                    content_type=content_type,
                    platform=platform,
                    funnel_stage=funnel_stage,
                    pillar=main_topic,
                    cluster=cluster_name,
                    target_keyword=primary_keyword,
                    secondary_keywords=secondary_keywords,
                    estimated_effort=self.content_rules['effort_estimation'].get(content_type, 4),
                    priority_score=priority_score,
                    content_angle=content_angle,
                    suggested_cta=cta
                )
                
                ideas.append(idea)
        
        return ideas
    
    def generate_title_variations(self, topic: str, content_type: ContentType) -> List[str]:
        """Generate title variations for a topic"""
        templates = {
            ContentType.BLOG_POST: [
                f"Complete Guide to {topic}",
                f"How to Master {topic}: Expert Tips",
                f"{topic}: Everything You Need to Know",
                f"10 Essential Tips for {topic}",
                f"The Ultimate {topic} Guide for Family Caregivers"
            ],
            ContentType.VIDEO: [
                f"{topic}: Step-by-Step Tutorial",
                f"How I Handle {topic} as a Caregiver",
                f"{topic} Explained in 5 Minutes",
                f"Real Talk: {topic} Challenges"
            ],
            ContentType.GUIDE: [
                f"{topic}: Comprehensive Guide",
                f"Your Complete {topic} Handbook",
                f"Mastering {topic}: From Beginner to Expert"
            ],
            ContentType.CHECKLIST: [
                f"{topic}: Essential Checklist",
                f"The Complete {topic} Checklist",
                f"Don't Forget: {topic} Checklist"
            ],
            ContentType.INFOGRAPHIC: [
                f"{topic}: Quick Reference Guide",
                f"The {topic} Infographic",
                f"{topic} at a Glance"
            ],
            ContentType.SOCIAL_POST: [
                f"Quick tip: {topic}",
                f"Let's talk about {topic}",
                f"Why {topic} matters"
            ]
        }
        
        return templates.get(content_type, [f"Guide to {topic}"])
    
    def select_primary_keyword(self, topic: str, cluster_keywords: List[str]) -> str:
        """Select the most appropriate primary keyword for content"""
        topic_lower = topic.lower()
        
        # Try to find exact match first
        for keyword in cluster_keywords:
            if keyword.lower() in topic_lower:
                return keyword
        
        # Find partial matches
        for keyword in cluster_keywords:
            keyword_words = keyword.lower().split()
            if any(word in topic_lower for word in keyword_words):
                return keyword
        
        # Fall back to first cluster keyword or topic itself
        return cluster_keywords[0] if cluster_keywords else topic.lower()
    
    def generate_secondary_keywords(self, primary_keyword: str, topic: str) -> List[str]:
        """Generate related secondary keywords"""
        secondary = []
        
        # Add topic itself if different from primary keyword
        if topic.lower() != primary_keyword.lower():
            secondary.append(topic.lower())
        
        # Add keyword variations
        if 'care' in primary_keyword:
            secondary.extend(['caregiving', 'caregiver', 'care tips'])
        
        if 'dementia' in primary_keyword:
            secondary.extend(['alzheimer', 'memory care', 'cognitive decline'])
        
        if 'burnout' in primary_keyword:
            secondary.extend(['caregiver stress', 'self-care', 'mental health'])
        
        # Add question variations
        question_starters = ['how to', 'what is', 'tips for', 'guide to']
        for starter in question_starters:
            secondary.append(f"{starter} {primary_keyword}")
        
        return secondary[:5]  # Limit to 5 secondary keywords
    
    def calculate_content_priority(self, keyword: str, content_type: ContentType, 
                                 funnel_stage: FunnelStage, cluster: str) -> float:
        """Calculate content priority score (0-100)"""
        score = 50  # Base score
        
        # Keyword-based scoring (simplified)
        high_priority_keywords = [
            'caregiver burnout', 'dementia care', 'aging parents',
            'family caregiver', 'eldercare', 'caregiver stress'
        ]
        
        if any(hpk in keyword.lower() for hpk in high_priority_keywords):
            score += 20
        
        # Content type scoring
        high_impact_types = [ContentType.GUIDE, ContentType.BLOG_POST, ContentType.VIDEO]
        if content_type in high_impact_types:
            score += 15
        
        # Funnel stage scoring
        if funnel_stage == FunnelStage.AWARENESS:
            score += 10  # High volume potential
        elif funnel_stage == FunnelStage.DECISION:
            score += 15  # High conversion potential
        
        # Cluster importance (simplified)
        important_clusters = ['caregiver_self_care', 'emotional_support']
        if cluster in important_clusters:
            score += 10
        
        return min(score, 100)
    
    def determine_content_angle(self, title: str, funnel_stage: FunnelStage) -> str:
        """Determine the content angle based on title and funnel stage"""
        title_lower = title.lower()
        
        if 'guide' in title_lower or 'how to' in title_lower:
            return 'instructional'
        elif 'tips' in title_lower:
            return 'actionable'
        elif 'complete' in title_lower or 'everything' in title_lower:
            return 'comprehensive'
        elif funnel_stage == FunnelStage.AWARENESS:
            return 'educational'
        elif funnel_stage == FunnelStage.CONSIDERATION:
            return 'solution-focused'
        elif funnel_stage == FunnelStage.DECISION:
            return 'product-focused'
        else:
            return 'informational'
    
    def generate_cta(self, funnel_stage: FunnelStage, platform: Platform) -> str:
        """Generate appropriate call-to-action"""
        ctas = {
            FunnelStage.AWARENESS: {
                Platform.BLOG: "Learn more about caregiving support",
                Platform.TIKTOK: "Share your caregiving story below",
                Platform.INSTAGRAM: "Share your caregiving story below",
                Platform.YOUTUBE: "Subscribe for more caregiving tips",
                Platform.PINTEREST: "Save this for later"
            },
            FunnelStage.CONSIDERATION: {
                Platform.BLOG: "Download our comprehensive care planning guide",
                Platform.TIKTOK: "Save this post for future reference",
                Platform.INSTAGRAM: "Save this post for future reference",
                Platform.YOUTUBE: "Check out our care coordination tools",
                Platform.PINTEREST: "Get the complete guide"
            },
            FunnelStage.DECISION: {
                Platform.BLOG: "Try Kiin free for 30 days",
                Platform.TIKTOK: "Download the Kiin app today",
                Platform.INSTAGRAM: "Download the Kiin app today", 
                Platform.YOUTUBE: "Start your free Kiin trial",
                Platform.PINTEREST: "Get started with Kiin"
            }
        }
        
        return ctas.get(funnel_stage, {}).get(platform, "Learn more")
    
    def generate_all_content_ideas(self, ideas_per_cluster: int = 15) -> List[ContentIdea]:
        """Generate content ideas for all clusters"""
        all_ideas = []
        
        if 'clusters' in self.strategy:
            for cluster_name, cluster_data in self.strategy['clusters'].items():
                cluster_ideas = self.generate_content_ideas_for_cluster(
                    cluster_name, cluster_data, ideas_per_cluster
                )
                all_ideas.extend(cluster_ideas)
        
        # Add seasonal content ideas
        seasonal_ideas = self.generate_seasonal_content_ideas()
        all_ideas.extend(seasonal_ideas)
        
        # Sort by priority score
        all_ideas.sort(key=lambda x: x.priority_score, reverse=True)
        
        self.content_ideas = all_ideas
        return all_ideas
    
    def generate_seasonal_content_ideas(self) -> List[ContentIdea]:
        """Generate seasonal content ideas"""
        seasonal_ideas = []
        
        if 'seasonal_themes' not in self.strategy:
            return seasonal_ideas
        
        current_month = datetime.datetime.now().month
        current_season = self.get_season_from_month(current_month)
        
        # Generate ideas for current and next season
        seasons_to_plan = [current_season]
        next_season = self.get_next_season(current_season)
        if next_season:
            seasons_to_plan.append(next_season)
        
        for season in seasons_to_plan:
            if season in self.strategy['seasonal_themes']:
                season_data = self.strategy['seasonal_themes'][season]
                themes = season_data.get('themes', [])
                season_keywords = season_data.get('keywords', [])
                
                for theme in themes:
                    # Create seasonal content ideas
                    idea = ContentIdea(
                        title=f"{theme}: Complete Guide for Caregivers",
                        content_type=ContentType.BLOG_POST,
                        platform=Platform.BLOG,
                        funnel_stage=FunnelStage.AWARENESS,
                        pillar="Seasonal Care",
                        cluster=f"{season}_themes",
                        target_keyword=season_keywords[0] if season_keywords else theme.lower(),
                        secondary_keywords=season_keywords[1:] if len(season_keywords) > 1 else [],
                        estimated_effort=4,
                        priority_score=75,  # High priority for seasonal content
                        seasonal_relevance=season,
                        content_angle="seasonal"
                    )
                    seasonal_ideas.append(idea)
        
        return seasonal_ideas
    
    def get_season_from_month(self, month: int) -> str:
        """Get season from month number"""
        if month in [12, 1, 2]:
            return 'winter'
        elif month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        elif month in [9, 10, 11]:
            return 'fall'
        return 'spring'
    
    def get_next_season(self, current_season: str) -> Optional[str]:
        """Get the next season"""
        seasons = ['spring', 'summer', 'fall', 'winter']
        try:
            current_index = seasons.index(current_season)
            next_index = (current_index + 1) % len(seasons)
            return seasons[next_index]
        except ValueError:
            return None
    
    def create_content_calendar(self, start_date: str = None, weeks: int = 12) -> Dict[str, List[ContentCalendarEntry]]:
        """Create a content calendar for specified period"""
        if start_date:
            start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        else:
            start = datetime.datetime.now()
        
        calendar_entries = defaultdict(list)
        
        # Get content ideas if not already generated
        if not self.content_ideas:
            self.generate_all_content_ideas()
        
        # Plan content for each week
        idea_index = 0
        
        for week in range(weeks):
            week_start = start + datetime.timedelta(weeks=week)
            week_key = f"week_{week + 1}_{week_start.strftime('%Y-%m-%d')}"
            
            # Determine content count for this week
            total_weekly_posts = sum(
                freq for freq in self.content_rules['posting_frequency'].values()
            )
            
            # Select and schedule content for each platform
            for platform, frequency in self.content_rules['posting_frequency'].items():
                for post_num in range(frequency):
                    if idea_index >= len(self.content_ideas):
                        break
                    
                    # Find next idea for this platform
                    idea = None
                    temp_index = idea_index
                    while temp_index < len(self.content_ideas):
                        if self.content_ideas[temp_index].platform == platform:
                            idea = self.content_ideas[temp_index]
                            idea_index = temp_index + 1
                            break
                        temp_index += 1
                    
                    if idea:
                        # Calculate posting date within the week
                        post_date = week_start + datetime.timedelta(
                            days=post_num * (7 // frequency)
                        )
                        
                        entry = ContentCalendarEntry(
                            date=post_date.strftime('%Y-%m-%d'),
                            content_idea=idea,
                            status="planned"
                        )
                        
                        calendar_entries[week_key].append(entry)
        
        return dict(calendar_entries)
    
    def analyze_content_balance(self, calendar: Dict) -> Dict:
        """Analyze content balance across different dimensions"""
        analysis = {
            'content_types': Counter(),
            'platforms': Counter(),
            'funnel_stages': Counter(),
            'pillars': Counter(),
            'content_angles': Counter(),
            'total_content': 0,
            'average_effort_per_week': 0
        }
        
        total_effort = 0
        week_count = len(calendar)
        
        for week_entries in calendar.values():
            for entry in week_entries:
                idea = entry.content_idea
                
                analysis['content_types'][idea.content_type.value] += 1
                analysis['platforms'][idea.platform.value] += 1
                analysis['funnel_stages'][idea.funnel_stage.value] += 1
                analysis['pillars'][idea.pillar] += 1
                analysis['content_angles'][idea.content_angle] += 1
                analysis['total_content'] += 1
                
                total_effort += idea.estimated_effort
        
        if week_count > 0:
            analysis['average_effort_per_week'] = total_effort / week_count
        
        return analysis
    
    def export_content_strategy(self, filename: str = "content_strategy_plan.json") -> Path:
        """Export complete content strategy plan"""
        # Generate ideas if not already done
        if not self.content_ideas:
            self.generate_all_content_ideas()
        
        # Create content calendar
        calendar = self.create_content_calendar(weeks=12)
        
        # Analyze balance
        balance_analysis = self.analyze_content_balance(calendar)
        
        # Prepare export data
        export_data = {
            'content_ideas': [
                {
                    'id': i,
                    'title': idea.title,
                    'content_type': idea.content_type.value,
                    'platform': idea.platform.value,
                    'funnel_stage': idea.funnel_stage.value,
                    'pillar': idea.pillar,
                    'cluster': idea.cluster,
                    'target_keyword': idea.target_keyword,
                    'secondary_keywords': idea.secondary_keywords,
                    'estimated_effort': idea.estimated_effort,
                    'priority_score': idea.priority_score,
                    'seasonal_relevance': idea.seasonal_relevance,
                    'content_angle': idea.content_angle,
                    'suggested_cta': idea.suggested_cta
                }
                for i, idea in enumerate(self.content_ideas[:100])  # Top 100 ideas
            ],
            'content_calendar': {
                week: [
                    {
                        'date': entry.date,
                        'title': entry.content_idea.title,
                        'content_type': entry.content_idea.content_type.value,
                        'platform': entry.content_idea.platform.value,
                        'pillar': entry.content_idea.pillar,
                        'target_keyword': entry.content_idea.target_keyword,
                        'estimated_effort': entry.content_idea.estimated_effort,
                        'priority_score': entry.content_idea.priority_score,
                        'status': entry.status
                    }
                    for entry in entries
                ]
                for week, entries in calendar.items()
            },
            'balance_analysis': {
                'content_types': dict(balance_analysis['content_types']),
                'platforms': dict(balance_analysis['platforms']),
                'funnel_stages': dict(balance_analysis['funnel_stages']),
                'pillars': dict(balance_analysis['pillars']),
                'content_angles': dict(balance_analysis['content_angles']),
                'total_content': balance_analysis['total_content'],
                'average_effort_per_week': balance_analysis['average_effort_per_week']
            },
            'strategy_summary': {
                'planning_period': '12 weeks',
                'total_ideas_generated': len(self.content_ideas),
                'pillars': len(self.strategy.get('pillars', [])),
                'clusters': len(self.strategy.get('clusters', {})),
                'platforms': [platform.value for platform in self.content_rules['posting_frequency'].keys()],
                'content_mix_target': self.content_rules['content_mix']
            }
        }
        
        output_path = self.data_dir / filename
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return output_path

if __name__ == "__main__":
    planner = ContentStrategyPlanner()
    
    # Generate content strategy
    ideas = planner.generate_all_content_ideas()
    print(f"Generated {len(ideas)} content ideas")
    
    # Export strategy plan
    output_path = planner.export_content_strategy()
    print(f"Content strategy exported to: {output_path}")
    
    # Print top 10 ideas
    print("\nTop 10 Content Ideas:")
    for i, idea in enumerate(ideas[:10]):
        print(f"{i+1}. {idea.title} ({idea.content_type.value}, {idea.priority_score:.1f})")