#!/usr/bin/env python3
"""
Kiin Content Factory - Content Gap Analyzer

Analyzes existing content against keyword targets and identifies content opportunities.
Maps content to keywords and provides strategic recommendations.
"""

import json
import re
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import requests
from urllib.parse import urlparse, urljoin
from collections import defaultdict, Counter
import hashlib

class ContentType(Enum):
    BLOG_POST = "blog_post"
    VIDEO = "video"
    INFOGRAPHIC = "infographic"
    SOCIAL_POST = "social_post"
    GUIDE = "guide"
    CHECKLIST = "checklist"
    CASE_STUDY = "case_study"

class GapSeverity(Enum):
    CRITICAL = 1  # High volume keywords with no content
    HIGH = 2      # Important keywords with limited content
    MEDIUM = 3    # Moderate opportunity
    LOW = 4       # Nice to have

@dataclass
class ContentPiece:
    """Represents a piece of content"""
    url: str
    title: str
    content_type: ContentType
    word_count: int
    keywords: List[str] = None
    topic_clusters: List[str] = None
    performance_score: float = 0.0
    last_updated: Optional[str] = None
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []
        if self.topic_clusters is None:
            self.topic_clusters = []

@dataclass
class ContentGap:
    """Represents a content gap opportunity"""
    keyword: str
    search_volume: int
    difficulty: int
    current_content: List[ContentPiece]
    gap_severity: GapSeverity
    opportunity_score: float
    recommended_content_type: ContentType
    suggested_title: str
    content_angle: str
    target_funnel_stage: str

class ContentGapAnalyzer:
    """Main content gap analysis tool"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.db_path = self.data_dir / "content_analysis.db"
        self.init_database()
        
        # Load configurations
        self.load_keyword_data()
        self.load_content_strategy()
        
        # Content inventory
        self.content_inventory: List[ContentPiece] = []
        
    def init_database(self):
        """Initialize database for content analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Content pieces table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content_pieces (
                id INTEGER PRIMARY KEY,
                url TEXT UNIQUE,
                title TEXT,
                content_type TEXT,
                word_count INTEGER,
                keywords TEXT,
                topic_clusters TEXT,
                performance_score REAL,
                last_updated TEXT,
                content_hash TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Content gaps table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content_gaps (
                id INTEGER PRIMARY KEY,
                keyword TEXT,
                search_volume INTEGER,
                difficulty INTEGER,
                gap_severity INTEGER,
                opportunity_score REAL,
                recommended_content_type TEXT,
                suggested_title TEXT,
                content_angle TEXT,
                target_funnel_stage TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Keyword coverage table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS keyword_coverage (
                id INTEGER PRIMARY KEY,
                keyword TEXT,
                content_url TEXT,
                coverage_strength REAL,
                context TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_keyword_data(self):
        """Load keyword data from keyword research"""
        keyword_db_path = self.data_dir / "keywords.db"
        if keyword_db_path.exists():
            self.keyword_db = keyword_db_path
        else:
            print("Warning: Keyword database not found. Run keyword research first.")
            self.keyword_db = None
    
    def load_content_strategy(self):
        """Load content strategy configuration"""
        config_path = Path("config/content_strategy.json")
        if config_path.exists():
            with open(config_path) as f:
                self.strategy = json.load(f)
        else:
            self.strategy = {}
    
    def extract_keywords_from_content(self, text: str, title: str = "") -> List[str]:
        """Extract relevant keywords from content text"""
        # Load caregiving keywords
        config_path = Path("config/seo_keywords.json")
        if config_path.exists():
            with open(config_path) as f:
                keyword_config = json.load(f)
        else:
            return []
        
        # Combine all keywords
        all_keywords = []
        for category, keywords in keyword_config.items():
            if isinstance(keywords, list):
                all_keywords.extend(keywords)
        
        # Find keywords in content
        found_keywords = []
        content_lower = (text + " " + title).lower()
        
        for keyword in all_keywords:
            if keyword.lower() in content_lower:
                # Count occurrences to determine relevance
                count = content_lower.count(keyword.lower())
                if count > 0:
                    found_keywords.append(keyword)
        
        return found_keywords
    
    def calculate_keyword_coverage_strength(self, keyword: str, content: str, title: str = "") -> float:
        """Calculate how well content covers a keyword"""
        full_text = (content + " " + title).lower()
        keyword_lower = keyword.lower()
        
        # Base score from frequency
        frequency = full_text.count(keyword_lower)
        if frequency == 0:
            return 0.0
        
        # Calculate density (but cap it to avoid keyword stuffing)
        word_count = len(full_text.split())
        density = (frequency / word_count) * 100 if word_count > 0 else 0
        density_score = min(density / 2, 1.0)  # Cap at 2% density = 1.0 score
        
        # Bonus for keyword in title
        title_bonus = 0.3 if keyword_lower in title.lower() else 0
        
        # Bonus for keyword variations
        keyword_words = keyword_lower.split()
        variation_score = 0
        for word in keyword_words:
            if word in full_text:
                variation_score += 0.1
        
        total_score = min(density_score + title_bonus + variation_score, 1.0)
        return total_score
    
    def analyze_content_piece(self, url: str, title: str, content: str, content_type: ContentType) -> ContentPiece:
        """Analyze a single piece of content"""
        word_count = len(content.split()) if content else 0
        keywords = self.extract_keywords_from_content(content, title)
        
        # Determine topic clusters
        topic_clusters = []
        if 'clusters' in self.strategy:
            for cluster_key, cluster_data in self.strategy['clusters'].items():
                cluster_keywords = cluster_data.get('keywords', [])
                if any(kw in keywords for kw in cluster_keywords):
                    topic_clusters.append(cluster_data['main_topic'])
        
        piece = ContentPiece(
            url=url,
            title=title,
            content_type=content_type,
            word_count=word_count,
            keywords=keywords,
            topic_clusters=topic_clusters
        )
        
        return piece
    
    def add_content_to_inventory(self, content_piece: ContentPiece):
        """Add content piece to inventory and database"""
        self.content_inventory.append(content_piece)
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        content_hash = hashlib.md5(
            (content_piece.title + content_piece.url).encode()
        ).hexdigest()
        
        cursor.execute('''
            INSERT OR REPLACE INTO content_pieces 
            (url, title, content_type, word_count, keywords, topic_clusters, 
             performance_score, content_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            content_piece.url,
            content_piece.title,
            content_piece.content_type.value,
            content_piece.word_count,
            json.dumps(content_piece.keywords),
            json.dumps(content_piece.topic_clusters),
            content_piece.performance_score,
            content_hash
        ))
        
        # Store keyword coverage
        for keyword in content_piece.keywords:
            coverage_strength = self.calculate_keyword_coverage_strength(
                keyword, "", content_piece.title  # Simplified for now
            )
            
            cursor.execute('''
                INSERT OR REPLACE INTO keyword_coverage 
                (keyword, content_url, coverage_strength)
                VALUES (?, ?, ?)
            ''', (keyword, content_piece.url, coverage_strength))
        
        conn.commit()
        conn.close()
    
    def get_keyword_coverage(self, keyword: str) -> List[Tuple[ContentPiece, float]]:
        """Get all content covering a specific keyword with strength scores"""
        coverage = []
        
        for content in self.content_inventory:
            if keyword in content.keywords:
                strength = self.calculate_keyword_coverage_strength(
                    keyword, "", content.title  # Simplified
                )
                coverage.append((content, strength))
        
        # Sort by coverage strength
        coverage.sort(key=lambda x: x[1], reverse=True)
        return coverage
    
    def identify_content_gaps(self) -> List[ContentGap]:
        """Identify content gaps based on keyword analysis"""
        if not self.keyword_db:
            print("No keyword database available")
            return []
        
        gaps = []
        
        # Connect to keyword database
        conn = sqlite3.connect(self.keyword_db)
        cursor = conn.cursor()
        
        # Get all keywords with metrics
        cursor.execute('''
            SELECT term, search_volume, difficulty, category, intent 
            FROM keywords 
            ORDER BY search_volume DESC
        ''')
        
        for row in cursor.fetchall():
            keyword, search_volume, difficulty, category, intent = row
            
            # Get current content coverage
            coverage = self.get_keyword_coverage(keyword)
            current_content = [c[0] for c in coverage]
            
            # Calculate gap severity
            gap_severity = self.calculate_gap_severity(
                keyword, search_volume, difficulty, coverage
            )
            
            # Skip if gap is not significant
            if gap_severity == GapSeverity.LOW and len(current_content) > 0:
                continue
            
            # Calculate opportunity score
            opportunity_score = self.calculate_opportunity_score(
                search_volume, difficulty, len(coverage), gap_severity
            )
            
            # Generate content recommendations
            recommendations = self.generate_content_recommendations(
                keyword, category, intent, current_content
            )
            
            gap = ContentGap(
                keyword=keyword,
                search_volume=search_volume,
                difficulty=difficulty,
                current_content=current_content,
                gap_severity=gap_severity,
                opportunity_score=opportunity_score,
                recommended_content_type=recommendations['content_type'],
                suggested_title=recommendations['title'],
                content_angle=recommendations['angle'],
                target_funnel_stage=recommendations['funnel_stage']
            )
            
            gaps.append(gap)
        
        conn.close()
        
        # Sort by opportunity score
        gaps.sort(key=lambda x: x.opportunity_score, reverse=True)
        return gaps
    
    def calculate_gap_severity(self, keyword: str, search_volume: int, 
                             difficulty: int, coverage: List[Tuple]) -> GapSeverity:
        """Calculate the severity of a content gap"""
        coverage_count = len(coverage)
        max_coverage_strength = max([c[1] for c in coverage], default=0)
        
        # Critical gaps: high volume, no or very poor coverage
        if search_volume > 5000 and (coverage_count == 0 or max_coverage_strength < 0.3):
            return GapSeverity.CRITICAL
        
        # High priority: medium-high volume with poor coverage
        if search_volume > 1000 and (coverage_count <= 1 or max_coverage_strength < 0.5):
            return GapSeverity.HIGH
        
        # Medium priority: some volume, needs better coverage
        if search_volume > 500 and (coverage_count <= 2 or max_coverage_strength < 0.7):
            return GapSeverity.MEDIUM
        
        return GapSeverity.LOW
    
    def calculate_opportunity_score(self, search_volume: int, difficulty: int, 
                                  current_coverage: int, severity: GapSeverity) -> float:
        """Calculate content opportunity score (0-100)"""
        # Base score from search volume (normalized)
        volume_score = min(search_volume / 10000 * 50, 50)
        
        # Difficulty penalty (easier keywords score higher)
        difficulty_score = (6 - difficulty) * 10
        
        # Coverage gap bonus
        coverage_bonus = max(20 - current_coverage * 5, 0)
        
        # Severity multiplier
        severity_multiplier = {
            GapSeverity.CRITICAL: 1.5,
            GapSeverity.HIGH: 1.2,
            GapSeverity.MEDIUM: 1.0,
            GapSeverity.LOW: 0.7
        }[severity]
        
        total_score = (volume_score + difficulty_score + coverage_bonus) * severity_multiplier
        return min(total_score, 100)
    
    def generate_content_recommendations(self, keyword: str, category: str, 
                                       intent: str, existing_content: List[ContentPiece]) -> Dict:
        """Generate content recommendations for a keyword gap"""
        
        # Default recommendations
        recommendations = {
            'content_type': ContentType.BLOG_POST,
            'title': f"Complete Guide to {keyword.title()}",
            'angle': "comprehensive overview",
            'funnel_stage': "awareness"
        }
        
        # Customize based on keyword pattern and intent
        keyword_lower = keyword.lower()
        
        # Question keywords
        if keyword_lower.startswith(('how to', 'what is', 'why', 'when')):
            recommendations.update({
                'content_type': ContentType.GUIDE,
                'title': f"{keyword.title()}: Complete Step-by-Step Guide",
                'angle': "instructional how-to",
                'funnel_stage': "consideration"
            })
        
        # List/tip keywords
        elif 'tips' in keyword_lower or 'best' in keyword_lower:
            recommendations.update({
                'content_type': ContentType.BLOG_POST,
                'title': f"10 Essential Tips for {keyword.title()}",
                'angle': "actionable tips list",
                'funnel_stage': "consideration"
            })
        
        # Problem/solution keywords
        elif any(word in keyword_lower for word in ['burnout', 'stress', 'help', 'support']):
            recommendations.update({
                'content_type': ContentType.GUIDE,
                'title': f"How to Overcome {keyword.title()}: A Complete Guide",
                'angle': "problem-solving guide",
                'funnel_stage': "awareness"
            })
        
        # Checklist keywords
        elif any(word in keyword_lower for word in ['checklist', 'plan', 'prepare']):
            recommendations.update({
                'content_type': ContentType.CHECKLIST,
                'title': f"Ultimate {keyword.title()} Checklist",
                'angle': "practical checklist",
                'funnel_stage': "decision"
            })
        
        # App/product related keywords (Kiin specific)
        elif any(word in keyword_lower for word in ['app', 'technology', 'digital', 'online']):
            recommendations.update({
                'content_type': ContentType.GUIDE,
                'title': f"How Kiin Helps with {keyword.title()}",
                'angle': "product-focused solution",
                'funnel_stage': "decision"
            })
        
        return recommendations
    
    def generate_content_calendar_from_gaps(self, gaps: List[ContentGap], 
                                          weeks: int = 12) -> Dict:
        """Generate a content calendar based on identified gaps"""
        calendar = defaultdict(list)
        
        # Sort gaps by opportunity score and select top ones
        priority_gaps = sorted(gaps, key=lambda x: x.opportunity_score, reverse=True)
        
        # Distribute content across weeks
        week = 0
        for i, gap in enumerate(priority_gaps[:weeks * 2]):  # 2 pieces per week max
            week_key = f"week_{(i // 2) + 1}"
            
            calendar_entry = {
                'keyword': gap.keyword,
                'title': gap.suggested_title,
                'content_type': gap.recommended_content_type.value,
                'angle': gap.content_angle,
                'funnel_stage': gap.target_funnel_stage,
                'opportunity_score': gap.opportunity_score,
                'search_volume': gap.search_volume,
                'priority': gap.gap_severity.name
            }
            
            calendar[week_key].append(calendar_entry)
        
        return dict(calendar)
    
    def export_gap_analysis(self, filename: str = "content_gap_analysis.json") -> Path:
        """Export complete gap analysis to JSON"""
        gaps = self.identify_content_gaps()
        content_calendar = self.generate_content_calendar_from_gaps(gaps)
        
        # Prepare coverage summary
        keyword_coverage_summary = {}
        for content in self.content_inventory:
            for keyword in content.keywords:
                if keyword not in keyword_coverage_summary:
                    keyword_coverage_summary[keyword] = []
                keyword_coverage_summary[keyword].append({
                    'url': content.url,
                    'title': content.title,
                    'type': content.content_type.value
                })
        
        analysis_data = {
            'content_gaps': [
                {
                    'keyword': gap.keyword,
                    'search_volume': gap.search_volume,
                    'difficulty': gap.difficulty,
                    'gap_severity': gap.gap_severity.name,
                    'opportunity_score': gap.opportunity_score,
                    'current_content_count': len(gap.current_content),
                    'recommended_content_type': gap.recommended_content_type.value,
                    'suggested_title': gap.suggested_title,
                    'content_angle': gap.content_angle,
                    'target_funnel_stage': gap.target_funnel_stage
                }
                for gap in gaps[:50]  # Top 50 gaps
            ],
            'content_calendar': content_calendar,
            'keyword_coverage': keyword_coverage_summary,
            'summary_stats': {
                'total_gaps_identified': len(gaps),
                'critical_gaps': len([g for g in gaps if g.gap_severity == GapSeverity.CRITICAL]),
                'high_priority_gaps': len([g for g in gaps if g.gap_severity == GapSeverity.HIGH]),
                'total_content_pieces': len(self.content_inventory),
                'average_opportunity_score': sum(g.opportunity_score for g in gaps) / len(gaps) if gaps else 0
            }
        }
        
        output_path = self.data_dir / filename
        with open(output_path, 'w') as f:
            json.dump(analysis_data, f, indent=2)
        
        return output_path
    
    def load_sample_content(self):
        """Load sample content for demonstration"""
        sample_content = [
            {
                'url': 'https://kiin.com/blog/caregiver-burnout-prevention',
                'title': 'How to Prevent Caregiver Burnout: 10 Essential Strategies',
                'content': 'Caregiver burnout is a serious issue affecting millions of family caregivers. This comprehensive guide covers stress management, self-care routines, and support systems.',
                'type': ContentType.BLOG_POST
            },
            {
                'url': 'https://kiin.com/blog/dementia-care-guide',
                'title': 'Complete Guide to Dementia Care at Home',
                'content': 'Caring for someone with dementia requires specialized knowledge and techniques. Learn about creating safe environments, managing behaviors, and supporting cognitive function.',
                'type': ContentType.GUIDE
            },
            {
                'url': 'https://kiin.com/blog/family-care-meetings',
                'title': 'How to Run Effective Family Care Meetings',
                'content': 'Family care meetings are essential for coordinating care responsibilities. This article covers meeting structure, communication strategies, and conflict resolution.',
                'type': ContentType.BLOG_POST
            }
        ]
        
        for item in sample_content:
            content_piece = self.analyze_content_piece(
                item['url'], item['title'], item['content'], item['type']
            )
            self.add_content_to_inventory(content_piece)

if __name__ == "__main__":
    analyzer = ContentGapAnalyzer()
    
    # Load sample content for demo
    analyzer.load_sample_content()
    
    # Run gap analysis
    output_path = analyzer.export_gap_analysis()
    print(f"Content gap analysis exported to: {output_path}")