#!/usr/bin/env python3
"""
Kiin Content Factory - SEO Content Optimizer

Comprehensive SEO optimization tool for caregiving content.
Includes keyword density analysis, title optimization, meta descriptions,
header structure, internal linking, and readability scoring.
"""

import re
import json
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from pathlib import Path
import sqlite3
from collections import Counter
import math
import statistics

@dataclass 
class SEOScore:
    """SEO scoring results"""
    overall_score: float  # 0-100
    keyword_density: float
    title_score: float
    meta_description_score: float
    header_structure_score: float
    content_length_score: float
    readability_score: float
    internal_links_score: float
    recommendations: List[str]

@dataclass
class ContentAnalysis:
    """Complete content analysis results"""
    word_count: int
    character_count: int
    paragraph_count: int
    sentence_count: int
    average_sentence_length: float
    keyword_density: Dict[str, float]
    title_analysis: Dict
    meta_analysis: Dict
    header_analysis: Dict
    readability_metrics: Dict
    seo_score: SEOScore

class SEOContentOptimizer:
    """Main SEO content optimization tool"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Load caregiving keywords
        self.load_keywords()
        
        # SEO optimization rules
        self.seo_rules = self.load_seo_rules()
    
    def load_keywords(self):
        """Load caregiving keywords for optimization"""
        config_path = Path("config/seo_keywords.json")
        if config_path.exists():
            with open(config_path) as f:
                keyword_config = json.load(f)
                
            # Flatten all keywords
            self.keywords = []
            for category, keywords in keyword_config.items():
                if isinstance(keywords, list):
                    self.keywords.extend(keywords)
        else:
            self.keywords = []
    
    def load_seo_rules(self) -> Dict:
        """Load SEO optimization rules and targets"""
        return {
            'title': {
                'min_length': 30,
                'max_length': 60,
                'include_keyword': True,
                'avoid_keyword_stuffing': True
            },
            'meta_description': {
                'min_length': 120,
                'max_length': 160,
                'include_keyword': True,
                'call_to_action': True
            },
            'content': {
                'min_word_count': 300,
                'optimal_word_count': 1500,
                'max_word_count': 3000,
                'keyword_density_min': 0.5,  # %
                'keyword_density_max': 3.0,  # %
                'min_paragraphs': 3
            },
            'headers': {
                'h1_required': True,
                'h1_count': 1,
                'h2_min': 2,
                'include_keywords': True,
                'hierarchy_proper': True
            },
            'readability': {
                'max_sentence_length': 20,
                'min_paragraph_sentences': 2,
                'max_paragraph_sentences': 6,
                'flesch_kincaid_target': 60  # Grade 8-9 reading level
            },
            'internal_links': {
                'min_links': 2,
                'max_links_per_100_words': 1,
                'relevant_anchor_text': True
            }
        }
    
    def analyze_title(self, title: str, target_keyword: str = None) -> Dict:
        """Analyze title for SEO optimization"""
        analysis = {
            'length': len(title),
            'character_count': len(title),
            'word_count': len(title.split()),
            'has_target_keyword': False,
            'keyword_position': None,
            'capitalization_proper': self.check_title_capitalization(title),
            'emotional_words': self.find_emotional_words(title),
            'power_words': self.find_power_words(title),
            'score': 0
        }
        
        rules = self.seo_rules['title']
        score = 0
        
        # Length scoring
        if rules['min_length'] <= len(title) <= rules['max_length']:
            score += 25
        elif len(title) < rules['min_length']:
            score -= 10
        elif len(title) > rules['max_length']:
            score -= 15
        
        # Keyword analysis
        if target_keyword:
            title_lower = title.lower()
            keyword_lower = target_keyword.lower()
            
            if keyword_lower in title_lower:
                analysis['has_target_keyword'] = True
                analysis['keyword_position'] = title_lower.find(keyword_lower)
                score += 25
                
                # Bonus for keyword at beginning
                if analysis['keyword_position'] < 10:
                    score += 10
        
        # Emotional/power words bonus
        score += min(len(analysis['emotional_words']) * 5, 15)
        score += min(len(analysis['power_words']) * 3, 10)
        
        # Proper capitalization
        if analysis['capitalization_proper']:
            score += 10
        
        analysis['score'] = min(max(score, 0), 100)
        return analysis
    
    def check_title_capitalization(self, title: str) -> bool:
        """Check if title uses proper capitalization"""
        # Simple check for title case
        words = title.split()
        if not words:
            return False
        
        # First word should be capitalized
        if not words[0][0].isupper():
            return False
        
        # Check for common title case patterns
        minor_words = {'a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor', 'on', 'at', 'to', 'from', 'by', 'of', 'in'}
        
        for i, word in enumerate(words):
            if i == 0 or i == len(words) - 1:  # First and last words should be capitalized
                if not word[0].isupper():
                    return False
            elif word.lower() not in minor_words:  # Major words should be capitalized
                if not word[0].isupper():
                    return False
        
        return True
    
    def find_emotional_words(self, text: str) -> List[str]:
        """Find emotional trigger words in text"""
        emotional_words = [
            'amazing', 'incredible', 'stunning', 'breakthrough', 'revolutionary',
            'essential', 'crucial', 'vital', 'important', 'ultimate', 'complete',
            'comprehensive', 'definitive', 'proven', 'effective', 'powerful',
            'simple', 'easy', 'quick', 'instant', 'immediate', 'fast'
        ]
        
        found = []
        text_lower = text.lower()
        for word in emotional_words:
            if word in text_lower:
                found.append(word)
        
        return found
    
    def find_power_words(self, text: str) -> List[str]:
        """Find power words in text"""
        power_words = [
            'guide', 'tips', 'secrets', 'strategies', 'methods', 'techniques',
            'solutions', 'blueprint', 'roadmap', 'framework', 'system',
            'how to', 'why', 'what', 'when', 'where', 'best', 'top',
            'expert', 'professional', 'advanced', 'beginner', 'step-by-step'
        ]
        
        found = []
        text_lower = text.lower()
        for word in power_words:
            if word in text_lower:
                found.append(word)
        
        return found
    
    def analyze_meta_description(self, meta_description: str, target_keyword: str = None) -> Dict:
        """Analyze meta description for SEO"""
        analysis = {
            'length': len(meta_description),
            'word_count': len(meta_description.split()),
            'has_target_keyword': False,
            'has_call_to_action': False,
            'emotional_words': self.find_emotional_words(meta_description),
            'score': 0
        }
        
        rules = self.seo_rules['meta_description']
        score = 0
        
        # Length scoring
        if rules['min_length'] <= len(meta_description) <= rules['max_length']:
            score += 30
        elif len(meta_description) < rules['min_length']:
            score -= 15
        elif len(meta_description) > rules['max_length']:
            score -= 20
        
        # Keyword inclusion
        if target_keyword and target_keyword.lower() in meta_description.lower():
            analysis['has_target_keyword'] = True
            score += 25
        
        # Call-to-action detection
        cta_words = ['learn', 'discover', 'find out', 'get', 'download', 'read', 'explore', 'see how']
        if any(cta in meta_description.lower() for cta in cta_words):
            analysis['has_call_to_action'] = True
            score += 20
        
        # Emotional words bonus
        score += min(len(analysis['emotional_words']) * 3, 15)
        
        analysis['score'] = min(max(score, 0), 100)
        return analysis
    
    def analyze_header_structure(self, content: str) -> Dict:
        """Analyze header structure and hierarchy"""
        # Extract headers using regex
        h1_pattern = r'<h1[^>]*>(.*?)</h1>'
        h2_pattern = r'<h2[^>]*>(.*?)</h2>'
        h3_pattern = r'<h3[^>]*>(.*?)</h3>'
        h4_pattern = r'<h4[^>]*>(.*?)</h4>'
        
        h1_headers = re.findall(h1_pattern, content, re.IGNORECASE | re.DOTALL)
        h2_headers = re.findall(h2_pattern, content, re.IGNORECASE | re.DOTALL)
        h3_headers = re.findall(h3_pattern, content, re.IGNORECASE | re.DOTALL)
        h4_headers = re.findall(h4_pattern, content, re.IGNORECASE | re.DOTALL)
        
        analysis = {
            'h1_count': len(h1_headers),
            'h2_count': len(h2_headers),
            'h3_count': len(h3_headers),
            'h4_count': len(h4_headers),
            'h1_text': h1_headers,
            'h2_text': h2_headers,
            'total_headers': len(h1_headers) + len(h2_headers) + len(h3_headers) + len(h4_headers),
            'hierarchy_proper': True,
            'headers_with_keywords': [],
            'score': 0
        }
        
        rules = self.seo_rules['headers']
        score = 0
        
        # H1 requirements
        if analysis['h1_count'] == 1:
            score += 20
        elif analysis['h1_count'] == 0:
            score -= 30
        elif analysis['h1_count'] > 1:
            score -= 15
        
        # H2 requirements
        if analysis['h2_count'] >= rules['h2_min']:
            score += 20
        elif analysis['h2_count'] > 0:
            score += 10
        
        # Check for keywords in headers
        all_headers = h1_headers + h2_headers + h3_headers
        keyword_headers = 0
        for header in all_headers:
            header_lower = header.lower()
            for keyword in self.keywords[:10]:  # Check top keywords
                if keyword.lower() in header_lower:
                    analysis['headers_with_keywords'].append({
                        'header': header,
                        'keyword': keyword
                    })
                    keyword_headers += 1
                    break
        
        if keyword_headers > 0:
            score += min(keyword_headers * 10, 30)
        
        analysis['score'] = min(max(score, 0), 100)
        return analysis
    
    def calculate_keyword_density(self, content: str, target_keyword: str) -> float:
        """Calculate keyword density percentage"""
        # Clean content
        content_clean = re.sub(r'<[^>]+>', ' ', content)  # Remove HTML
        content_clean = re.sub(r'[^\w\s]', ' ', content_clean)  # Remove punctuation
        words = content_clean.lower().split()
        
        if not words:
            return 0.0
        
        keyword_words = target_keyword.lower().split()
        keyword_count = 0
        
        # Count exact phrase occurrences
        content_text = ' '.join(words)
        keyword_phrase = ' '.join(keyword_words)
        keyword_count = content_text.count(keyword_phrase)
        
        # Calculate density
        total_words = len(words)
        density = (keyword_count / total_words) * 100 if total_words > 0 else 0
        
        return density
    
    def analyze_readability(self, content: str) -> Dict:
        """Analyze content readability using multiple metrics"""
        # Clean content
        content_clean = re.sub(r'<[^>]+>', ' ', content)  # Remove HTML
        content_clean = re.sub(r'\s+', ' ', content_clean).strip()
        
        # Basic counts
        sentences = re.split(r'[.!?]+', content_clean)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        words = content_clean.split()
        syllables = sum(self.count_syllables(word) for word in words)
        
        paragraphs = content_clean.split('\n\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        if not sentences or not words:
            return {
                'flesch_kincaid_grade': 0,
                'flesch_reading_ease': 0,
                'average_sentence_length': 0,
                'average_syllables_per_word': 0,
                'paragraph_count': len(paragraphs),
                'score': 0
            }
        
        # Calculate metrics
        avg_sentence_length = len(words) / len(sentences)
        avg_syllables_per_word = syllables / len(words)
        
        # Flesch-Kincaid Grade Level
        fk_grade = 0.39 * avg_sentence_length + 11.8 * avg_syllables_per_word - 15.59
        
        # Flesch Reading Ease
        flesch_ease = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables_per_word
        
        # Scoring based on readability rules
        rules = self.seo_rules['readability']
        score = 50  # Base score
        
        # Grade level scoring (target: 8-9th grade)
        if 8 <= fk_grade <= 9:
            score += 30
        elif 6 <= fk_grade <= 11:
            score += 20
        elif fk_grade < 6:
            score += 10  # Too easy is okay
        else:
            score -= 20  # Too difficult
        
        # Sentence length scoring
        if avg_sentence_length <= rules['max_sentence_length']:
            score += 20
        else:
            score -= 15
        
        analysis = {
            'flesch_kincaid_grade': round(fk_grade, 1),
            'flesch_reading_ease': round(flesch_ease, 1),
            'average_sentence_length': round(avg_sentence_length, 1),
            'average_syllables_per_word': round(avg_syllables_per_word, 2),
            'paragraph_count': len(paragraphs),
            'sentence_count': len(sentences),
            'word_count': len(words),
            'score': min(max(score, 0), 100)
        }
        
        return analysis
    
    def count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified algorithm)"""
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        # Handle silent 'e'
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        return max(syllable_count, 1)
    
    def analyze_internal_links(self, content: str) -> Dict:
        """Analyze internal linking structure"""
        # Extract internal links (assuming domain patterns)
        link_pattern = r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>'
        links = re.findall(link_pattern, content, re.IGNORECASE | re.DOTALL)
        
        internal_links = []
        external_links = []
        
        for url, anchor_text in links:
            # Simple heuristic for internal vs external
            if url.startswith('/') or 'kiin.com' in url or url.startswith('#'):
                internal_links.append({
                    'url': url,
                    'anchor_text': anchor_text.strip(),
                    'relevant': self.is_relevant_anchor_text(anchor_text)
                })
            else:
                external_links.append({
                    'url': url,
                    'anchor_text': anchor_text.strip()
                })
        
        # Calculate score
        rules = self.seo_rules['internal_links']
        score = 0
        
        # Minimum links check
        if len(internal_links) >= rules['min_links']:
            score += 30
        elif len(internal_links) > 0:
            score += 15
        
        # Links density check (words per link)
        word_count = len(content.split())
        if word_count > 0:
            links_per_100_words = (len(internal_links) / word_count) * 100
            if links_per_100_words <= rules['max_links_per_100_words']:
                score += 20
            else:
                score -= 10
        
        # Relevant anchor text
        relevant_links = sum(1 for link in internal_links if link['relevant'])
        if relevant_links > 0:
            score += min(relevant_links * 10, 30)
        
        analysis = {
            'internal_link_count': len(internal_links),
            'external_link_count': len(external_links),
            'internal_links': internal_links,
            'relevant_anchor_count': relevant_links,
            'score': min(max(score, 0), 100)
        }
        
        return analysis
    
    def is_relevant_anchor_text(self, anchor_text: str) -> bool:
        """Check if anchor text is relevant and descriptive"""
        anchor_lower = anchor_text.lower().strip()
        
        # Avoid generic anchor text
        generic_terms = ['click here', 'read more', 'learn more', 'here', 'link', 'this']
        if anchor_lower in generic_terms:
            return False
        
        # Check for keyword relevance
        for keyword in self.keywords[:20]:  # Check top keywords
            if keyword.lower() in anchor_lower:
                return True
        
        # Check if descriptive (more than 2 words)
        return len(anchor_text.split()) > 2
    
    def generate_optimization_recommendations(self, analysis: ContentAnalysis, 
                                           target_keyword: str = None) -> List[str]:
        """Generate specific optimization recommendations"""
        recommendations = []
        
        # Title recommendations
        if analysis.title_analysis['score'] < 80:
            if analysis.title_analysis['length'] < self.seo_rules['title']['min_length']:
                recommendations.append("Lengthen title to 30-60 characters for better SEO")
            elif analysis.title_analysis['length'] > self.seo_rules['title']['max_length']:
                recommendations.append("Shorten title to under 60 characters to avoid truncation")
            
            if target_keyword and not analysis.title_analysis['has_target_keyword']:
                recommendations.append(f"Include target keyword '{target_keyword}' in title")
        
        # Meta description recommendations
        if analysis.meta_analysis['score'] < 80:
            if analysis.meta_analysis['length'] < self.seo_rules['meta_description']['min_length']:
                recommendations.append("Expand meta description to 120-160 characters")
            elif analysis.meta_analysis['length'] > self.seo_rules['meta_description']['max_length']:
                recommendations.append("Trim meta description to under 160 characters")
            
            if not analysis.meta_analysis['has_call_to_action']:
                recommendations.append("Add a call-to-action to meta description")
        
        # Content length recommendations
        if analysis.word_count < self.seo_rules['content']['min_word_count']:
            recommendations.append("Increase content length to at least 300 words")
        elif analysis.word_count > self.seo_rules['content']['max_word_count']:
            recommendations.append("Consider breaking content into multiple pages")
        
        # Keyword density recommendations
        if target_keyword:
            density = analysis.keyword_density.get(target_keyword, 0)
            if density < self.seo_rules['content']['keyword_density_min']:
                recommendations.append(f"Increase '{target_keyword}' usage (current density: {density:.1f}%)")
            elif density > self.seo_rules['content']['keyword_density_max']:
                recommendations.append(f"Reduce '{target_keyword}' usage to avoid keyword stuffing")
        
        # Header recommendations
        if analysis.header_analysis['score'] < 70:
            if analysis.header_analysis['h1_count'] == 0:
                recommendations.append("Add an H1 header to structure content")
            elif analysis.header_analysis['h1_count'] > 1:
                recommendations.append("Use only one H1 header per page")
            
            if analysis.header_analysis['h2_count'] < 2:
                recommendations.append("Add more H2 headers to improve content structure")
        
        # Readability recommendations
        if analysis.readability_metrics['score'] < 70:
            if analysis.readability_metrics['average_sentence_length'] > 20:
                recommendations.append("Break up long sentences to improve readability")
            
            if analysis.readability_metrics['flesch_kincaid_grade'] > 12:
                recommendations.append("Simplify language to improve readability (target 8th-9th grade)")
        
        # Internal linking recommendations
        if analysis.seo_score.internal_links_score < 60:
            if analysis.header_analysis.get('internal_link_count', 0) < 2:
                recommendations.append("Add more internal links to related content")
        
        return recommendations
    
    def optimize_content(self, content: str, title: str = "", meta_description: str = "", 
                        target_keyword: str = None) -> ContentAnalysis:
        """Perform complete content optimization analysis"""
        
        # Basic content metrics
        content_clean = re.sub(r'<[^>]+>', ' ', content)
        words = content_clean.split()
        sentences = re.split(r'[.!?]+', content_clean)
        sentences = [s.strip() for s in sentences if s.strip()]
        paragraphs = content.split('\n\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        word_count = len(words)
        character_count = len(content_clean)
        paragraph_count = len(paragraphs)
        sentence_count = len(sentences)
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        
        # Keyword density analysis
        keyword_density = {}
        if target_keyword:
            keyword_density[target_keyword] = self.calculate_keyword_density(content, target_keyword)
        
        # Component analyses
        title_analysis = self.analyze_title(title, target_keyword)
        meta_analysis = self.analyze_meta_description(meta_description, target_keyword)
        header_analysis = self.analyze_header_structure(content)
        readability_metrics = self.analyze_readability(content)
        internal_links_analysis = self.analyze_internal_links(content)
        
        # Calculate overall SEO score
        seo_score = self.calculate_overall_seo_score(
            title_analysis, meta_analysis, header_analysis,
            readability_metrics, internal_links_analysis, word_count, keyword_density
        )
        
        # Create complete analysis
        analysis = ContentAnalysis(
            word_count=word_count,
            character_count=character_count,
            paragraph_count=paragraph_count,
            sentence_count=sentence_count,
            average_sentence_length=avg_sentence_length,
            keyword_density=keyword_density,
            title_analysis=title_analysis,
            meta_analysis=meta_analysis,
            header_analysis=header_analysis,
            readability_metrics=readability_metrics,
            seo_score=seo_score
        )
        
        # Generate recommendations
        recommendations = self.generate_optimization_recommendations(analysis, target_keyword)
        analysis.seo_score.recommendations = recommendations
        
        return analysis
    
    def calculate_overall_seo_score(self, title_analysis: Dict, meta_analysis: Dict,
                                  header_analysis: Dict, readability_metrics: Dict,
                                  internal_links_analysis: Dict, word_count: int,
                                  keyword_density: Dict) -> SEOScore:
        """Calculate overall SEO score with component breakdown"""
        
        # Individual component scores
        title_score = title_analysis['score']
        meta_score = meta_analysis['score']
        header_score = header_analysis['score']
        readability_score = readability_metrics['score']
        internal_links_score = internal_links_analysis['score']
        
        # Content length score
        content_rules = self.seo_rules['content']
        if content_rules['min_word_count'] <= word_count <= content_rules['optimal_word_count']:
            content_length_score = 100
        elif word_count >= content_rules['optimal_word_count']:
            content_length_score = 90
        elif word_count >= content_rules['min_word_count']:
            content_length_score = 70
        else:
            content_length_score = 30
        
        # Keyword density score
        keyword_density_score = 50  # Default if no target keyword
        if keyword_density:
            main_density = list(keyword_density.values())[0]
            if content_rules['keyword_density_min'] <= main_density <= content_rules['keyword_density_max']:
                keyword_density_score = 100
            elif main_density < content_rules['keyword_density_min']:
                keyword_density_score = 60
            else:  # Over-optimization
                keyword_density_score = 30
        
        # Weighted overall score
        weights = {
            'title': 0.20,
            'meta': 0.15,
            'headers': 0.15,
            'content_length': 0.15,
            'keyword_density': 0.15,
            'readability': 0.10,
            'internal_links': 0.10
        }
        
        overall_score = (
            title_score * weights['title'] +
            meta_score * weights['meta'] +
            header_score * weights['headers'] +
            content_length_score * weights['content_length'] +
            keyword_density_score * weights['keyword_density'] +
            readability_score * weights['readability'] +
            internal_links_score * weights['internal_links']
        )
        
        return SEOScore(
            overall_score=round(overall_score, 1),
            keyword_density=list(keyword_density.values())[0] if keyword_density else 0,
            title_score=title_score,
            meta_description_score=meta_score,
            header_structure_score=header_score,
            content_length_score=content_length_score,
            readability_score=readability_score,
            internal_links_score=internal_links_score,
            recommendations=[]
        )
    
    def generate_title_suggestions(self, target_keyword: str, content_type: str = "article") -> List[str]:
        """Generate SEO-optimized title suggestions"""
        suggestions = []
        
        # Template-based title generation
        templates = {
            "article": [
                f"Complete Guide to {target_keyword}",
                f"How to {target_keyword}: Step-by-Step Guide",
                f"{target_keyword}: Everything You Need to Know",
                f"10 Essential Tips for {target_keyword}",
                f"The Ultimate {target_keyword} Guide for 2024"
            ],
            "guide": [
                f"{target_keyword}: Complete Beginner's Guide",
                f"Mastering {target_keyword}: A Comprehensive Guide",
                f"Your Complete {target_keyword} Handbook"
            ],
            "tips": [
                f"15 Proven {target_keyword} Tips That Actually Work",
                f"Expert {target_keyword} Tips for Better Results",
                f"Simple {target_keyword} Tips to Get Started"
            ]
        }
        
        suggestions.extend(templates.get(content_type, templates["article"]))
        return suggestions[:5]
    
    def generate_meta_description_suggestions(self, target_keyword: str, title: str) -> List[str]:
        """Generate SEO-optimized meta description suggestions"""
        suggestions = [
            f"Learn everything about {target_keyword} with our comprehensive guide. Discover expert tips, strategies, and practical advice to get started today.",
            f"Master {target_keyword} with proven strategies and expert guidance. Get actionable tips and step-by-step instructions in our complete guide.",
            f"Discover the complete guide to {target_keyword}. Learn expert techniques, best practices, and proven methods to achieve your goals.",
            f"Everything you need to know about {target_keyword} in one place. Expert advice, practical tips, and actionable strategies to help you succeed."
        ]
        
        return suggestions

if __name__ == "__main__":
    optimizer = SEOContentOptimizer()
    
    # Example usage
    sample_content = """
    <h1>Complete Guide to Caregiver Burnout Prevention</h1>
    
    <p>Caregiver burnout is a serious issue affecting millions of family caregivers across the country. This comprehensive guide will help you understand, prevent, and manage burnout while caring for your loved ones.</p>
    
    <h2>What is Caregiver Burnout?</h2>
    <p>Caregiver burnout is a state of physical, emotional, and mental exhaustion. It occurs when caregivers don't get the help they need, or if they try to do more than they are able.</p>
    
    <h2>Signs of Caregiver Burnout</h2>
    <p>Recognizing the signs early is crucial for prevention. Common symptoms include chronic fatigue, increased illness, and emotional withdrawal.</p>
    """
    
    analysis = optimizer.optimize_content(
        content=sample_content,
        title="Complete Guide to Caregiver Burnout Prevention",
        meta_description="Learn how to prevent and manage caregiver burnout with expert tips and strategies. Comprehensive guide for family caregivers.",
        target_keyword="caregiver burnout"
    )
    
    print(f"Overall SEO Score: {analysis.seo_score.overall_score}/100")
    print(f"Word Count: {analysis.word_count}")
    print(f"Keyword Density: {analysis.seo_score.keyword_density:.1f}%")
    print("\nRecommendations:")
    for rec in analysis.seo_score.recommendations:
        print(f"- {rec}")