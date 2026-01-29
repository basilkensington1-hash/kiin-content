#!/usr/bin/env python3
"""
Kiin Content Factory - Keyword Research Tool

Comprehensive keyword research and analysis for caregiving content.
Includes search volume estimation, difficulty scoring, and keyword generation.
"""

import json
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import sqlite3
from pathlib import Path

class KeywordDifficulty(Enum):
    """Keyword difficulty levels"""
    VERY_EASY = 1
    EASY = 2
    MEDIUM = 3
    HARD = 4
    VERY_HARD = 5

class KeywordIntent(Enum):
    """Search intent classification"""
    INFORMATIONAL = "informational"
    NAVIGATIONAL = "navigational"
    TRANSACTIONAL = "transactional"
    COMMERCIAL = "commercial"

@dataclass
class Keyword:
    """Keyword data structure"""
    term: str
    search_volume: int
    difficulty: KeywordDifficulty
    intent: KeywordIntent
    category: str
    subcategory: Optional[str] = None
    cpc: float = 0.0
    competition: float = 0.0
    trending_score: float = 0.0
    related_terms: List[str] = None
    questions: List[str] = None
    
    def __post_init__(self):
        if self.related_terms is None:
            self.related_terms = []
        if self.questions is None:
            self.questions = []

class KeywordResearcher:
    """Main keyword research and analysis tool"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.db_path = self.data_dir / "keywords.db"
        self.init_database()
        
        # Load keyword seeds and patterns
        self.load_keyword_config()
    
    def init_database(self):
        """Initialize SQLite database for keyword storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS keywords (
                id INTEGER PRIMARY KEY,
                term TEXT UNIQUE,
                search_volume INTEGER,
                difficulty INTEGER,
                intent TEXT,
                category TEXT,
                subcategory TEXT,
                cpc REAL,
                competition REAL,
                trending_score REAL,
                related_terms TEXT,
                questions TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_keywords_category ON keywords(category);
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_keywords_difficulty ON keywords(difficulty);
        ''')
        
        conn.commit()
        conn.close()
    
    def load_keyword_config(self):
        """Load keyword configuration and seed data"""
        config_path = Path("config/seo_keywords.json")
        if config_path.exists():
            with open(config_path) as f:
                self.config = json.load(f)
        else:
            # Default configuration if file doesn't exist
            self.config = self.generate_default_config()
    
    def generate_default_config(self) -> Dict:
        """Generate default keyword configuration"""
        return {
            "primary_keywords": [
                "caregiver", "caregiving", "family care", "eldercare", "elder care",
                "home care", "senior care", "aging in place", "family caregiver"
            ],
            "condition_specific": [
                "dementia care", "alzheimer care", "stroke recovery", "diabetes management",
                "parkinson care", "cancer care", "heart disease care", "mobility issues",
                "chronic illness", "disability care", "memory care"
            ],
            "emotional_keywords": [
                "caregiver burnout", "caregiver stress", "caregiver guilt", 
                "caregiver support", "caregiver grief", "caregiver fatigue",
                "caregiver depression", "caregiver anxiety", "overwhelmed caregiver"
            ],
            "action_keywords": [
                "how to care for aging parents", "caring for elderly parents",
                "help aging parents", "elder care tips", "caregiver resources",
                "finding care", "care coordination", "medical appointments"
            ],
            "longtail_patterns": [
                "sandwich generation balancing work and caregiving",
                "long distance caregiving tips",
                "caring for parents while working full time",
                "how to talk to aging parents about care",
                "signs your parent needs help",
                "choosing between home care and assisted living"
            ]
        }
    
    def generate_longtail_keywords(self, seed_keyword: str, variations: int = 10) -> List[str]:
        """Generate long-tail keyword variations"""
        patterns = [
            f"how to {seed_keyword}",
            f"best {seed_keyword}",
            f"{seed_keyword} tips",
            f"{seed_keyword} guide",
            f"{seed_keyword} for beginners",
            f"{seed_keyword} checklist",
            f"{seed_keyword} resources",
            f"{seed_keyword} support",
            f"{seed_keyword} help",
            f"what is {seed_keyword}",
            f"signs of {seed_keyword}",
            f"dealing with {seed_keyword}",
            f"{seed_keyword} at home",
            f"{seed_keyword} for seniors",
            f"affordable {seed_keyword}"
        ]
        
        return patterns[:variations]
    
    def generate_question_keywords(self, topic: str) -> List[str]:
        """Generate question-based keywords"""
        question_starters = [
            f"How to {topic}",
            f"What is {topic}",
            f"Why does {topic}",
            f"When to {topic}",
            f"Where to find {topic}",
            f"Who can help with {topic}",
            f"How much does {topic} cost",
            f"Is {topic} covered by insurance",
            f"What are signs of {topic}",
            f"How long does {topic} take"
        ]
        
        return question_starters
    
    def estimate_search_volume(self, keyword: str) -> int:
        """Estimate search volume based on keyword characteristics"""
        # This is a simplified estimation model
        # In production, you'd use Google Keyword Planner API or similar
        
        base_volume = 1000
        
        # Adjust based on keyword length
        word_count = len(keyword.split())
        if word_count == 1:
            multiplier = 5.0
        elif word_count == 2:
            multiplier = 3.0
        elif word_count == 3:
            multiplier = 1.5
        else:
            multiplier = 0.5
        
        # Adjust based on keyword category
        high_volume_terms = ["caregiver", "caregiving", "dementia", "alzheimer"]
        if any(term in keyword.lower() for term in high_volume_terms):
            multiplier *= 2
        
        return int(base_volume * multiplier)
    
    def calculate_keyword_difficulty(self, keyword: str) -> KeywordDifficulty:
        """Calculate keyword difficulty based on various factors"""
        word_count = len(keyword.split())
        
        # More specific keywords tend to be easier
        if word_count >= 4:
            return KeywordDifficulty.EASY
        elif word_count == 3:
            return KeywordDifficulty.MEDIUM
        elif word_count == 2:
            return KeywordDifficulty.HARD
        else:
            return KeywordDifficulty.VERY_HARD
    
    def classify_search_intent(self, keyword: str) -> KeywordIntent:
        """Classify search intent of keyword"""
        keyword_lower = keyword.lower()
        
        # Informational intent patterns
        info_patterns = ["how to", "what is", "why", "guide", "tips", "help"]
        if any(pattern in keyword_lower for pattern in info_patterns):
            return KeywordIntent.INFORMATIONAL
        
        # Transactional intent patterns
        trans_patterns = ["buy", "purchase", "order", "hire", "book", "schedule"]
        if any(pattern in keyword_lower for pattern in trans_patterns):
            return KeywordIntent.TRANSACTIONAL
        
        # Commercial intent patterns
        commercial_patterns = ["best", "top", "review", "compare", "vs", "cost", "price"]
        if any(pattern in keyword_lower for pattern in commercial_patterns):
            return KeywordIntent.COMMERCIAL
        
        # Default to informational for caregiving content
        return KeywordIntent.INFORMATIONAL
    
    def add_keyword(self, keyword: Keyword):
        """Add keyword to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO keywords 
                (term, search_volume, difficulty, intent, category, subcategory, 
                 cpc, competition, trending_score, related_terms, questions)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                keyword.term,
                keyword.search_volume,
                keyword.difficulty.value,
                keyword.intent.value,
                keyword.category,
                keyword.subcategory,
                keyword.cpc,
                keyword.competition,
                keyword.trending_score,
                json.dumps(keyword.related_terms),
                json.dumps(keyword.questions)
            ))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error adding keyword {keyword.term}: {e}")
        finally:
            conn.close()
    
    def get_keywords_by_category(self, category: str) -> List[Keyword]:
        """Retrieve keywords by category"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM keywords WHERE category = ? ORDER BY search_volume DESC
        ''', (category,))
        
        keywords = []
        for row in cursor.fetchall():
            keyword = Keyword(
                term=row[1],
                search_volume=row[2],
                difficulty=KeywordDifficulty(row[3]),
                intent=KeywordIntent(row[4]),
                category=row[5],
                subcategory=row[6],
                cpc=row[7],
                competition=row[8],
                trending_score=row[9],
                related_terms=json.loads(row[10]) if row[10] else [],
                questions=json.loads(row[11]) if row[11] else []
            )
            keywords.append(keyword)
        
        conn.close()
        return keywords
    
    def research_keyword_set(self, seed_keywords: List[str], category: str):
        """Research a complete set of keywords for a category"""
        for seed in seed_keywords:
            # Main keyword
            main_keyword = Keyword(
                term=seed,
                search_volume=self.estimate_search_volume(seed),
                difficulty=self.calculate_keyword_difficulty(seed),
                intent=self.classify_search_intent(seed),
                category=category
            )
            
            # Generate related terms and questions
            main_keyword.related_terms = self.generate_longtail_keywords(seed, 5)
            main_keyword.questions = self.generate_question_keywords(seed)
            
            self.add_keyword(main_keyword)
            
            # Add long-tail variations
            for longtail in main_keyword.related_terms:
                longtail_keyword = Keyword(
                    term=longtail,
                    search_volume=self.estimate_search_volume(longtail),
                    difficulty=self.calculate_keyword_difficulty(longtail),
                    intent=self.classify_search_intent(longtail),
                    category=category,
                    subcategory="longtail"
                )
                self.add_keyword(longtail_keyword)
            
            # Add question variations
            for question in main_keyword.questions[:3]:  # Limit to top 3
                question_keyword = Keyword(
                    term=question,
                    search_volume=self.estimate_search_volume(question),
                    difficulty=self.calculate_keyword_difficulty(question),
                    intent=KeywordIntent.INFORMATIONAL,
                    category=category,
                    subcategory="questions"
                )
                self.add_keyword(question_keyword)
    
    def export_keywords_json(self, filename: str = "keyword_database.json"):
        """Export all keywords to JSON file"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM keywords ORDER BY category, search_volume DESC')
        
        keywords_data = {
            "keywords": [],
            "categories": {},
            "stats": {}
        }
        
        category_counts = {}
        
        for row in cursor.fetchall():
            keyword_data = {
                "term": row[1],
                "search_volume": row[2],
                "difficulty": row[3],
                "intent": row[4],
                "category": row[5],
                "subcategory": row[6],
                "cpc": row[7],
                "competition": row[8],
                "trending_score": row[9],
                "related_terms": json.loads(row[10]) if row[10] else [],
                "questions": json.loads(row[11]) if row[11] else []
            }
            keywords_data["keywords"].append(keyword_data)
            
            # Count by category
            category = row[5]
            category_counts[category] = category_counts.get(category, 0) + 1
        
        keywords_data["categories"] = category_counts
        keywords_data["stats"] = {
            "total_keywords": len(keywords_data["keywords"]),
            "categories": len(category_counts)
        }
        
        output_path = self.data_dir / filename
        with open(output_path, 'w') as f:
            json.dump(keywords_data, f, indent=2)
        
        conn.close()
        return output_path

    def build_complete_database(self):
        """Build the complete keyword database"""
        print("Building comprehensive keyword database...")
        
        # Research all keyword categories
        for category, keywords in self.config.items():
            if isinstance(keywords, list):
                print(f"Researching {category}...")
                self.research_keyword_set(keywords, category)
        
        print("Keyword database build complete!")
        return self.export_keywords_json()

if __name__ == "__main__":
    researcher = KeywordResearcher()
    db_path = researcher.build_complete_database()
    print(f"Keyword database exported to: {db_path}")