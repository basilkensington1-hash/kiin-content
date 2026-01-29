#!/usr/bin/env python3
"""
Blog Generator for Kiin Content Factory
Generates long-form blog posts optimized for caregiver audiences
"""

import json
import os
import random
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse

class BlogGenerator:
    def __init__(self):
        self.config_dir = Path(__file__).parent.parent / "config"
        self.output_dir = Path(__file__).parent.parent / "output" / "blog"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration files
        self.blog_topics = self._load_config("blog_topics.json")
        self.seo_keywords = self._load_config("seo_keywords.json")
        self.existing_confessions = self._load_config("confessions_v2.json")
        self.tips = self._load_config("expanded_caregiver_tips.json")
        
        self.tone_styles = {
            "supportive": {
                "intro_style": "warm and understanding",
                "voice": "empathetic friend who truly gets it",
                "sentence_structure": "conversational with gentle guidance",
                "emotional_approach": "validation and encouragement"
            },
            "educational": {
                "intro_style": "informative and structured",
                "voice": "knowledgeable guide with clear expertise",
                "sentence_structure": "clear, logical progression",
                "emotional_approach": "confidence through knowledge"
            },
            "personal": {
                "intro_style": "intimate and relatable",
                "voice": "fellow caregiver sharing real experience",
                "sentence_structure": "varied, with personal anecdotes",
                "emotional_approach": "authentic vulnerability and connection"
            },
            "compassionate": {
                "intro_style": "deeply understanding",
                "voice": "caring professional with heart",
                "sentence_structure": "gentle, thoughtful pacing",
                "emotional_approach": "profound empathy and wisdom"
            },
            "empowering": {
                "intro_style": "confident and motivating",
                "voice": "inspiring mentor and advocate",
                "sentence_structure": "strong, action-oriented",
                "emotional_approach": "strength-building and capability-focused"
            }
        }
        
    def _load_config(self, filename: str) -> Dict:
        """Load a configuration file"""
        config_path = self.config_dir / filename
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: {filename} not found")
            return {}
            
    def generate_blog_post(self, topic: str = None, content_type: str = "educational_guides", 
                          tone: str = "supportive", keywords: List[str] = None, 
                          target_words: int = 2500) -> Dict:
        """Generate a complete blog post"""
        
        # Select topic
        if topic:
            # Find topic in config or create custom
            selected_topic = self._find_topic_by_title(topic)
            if not selected_topic:
                selected_topic = self._create_custom_topic(topic, content_type, tone, target_words)
        else:
            selected_topic = self._select_topic(content_type)
            
        # Generate content
        blog_content = self._generate_content(selected_topic, tone, target_words)
        
        # Generate SEO metadata
        seo_data = self._generate_seo_metadata(selected_topic, blog_content)
        
        # Create internal linking suggestions
        internal_links = self._suggest_internal_links(selected_topic)
        
        # Generate image placement markers
        image_suggestions = self._generate_image_suggestions(selected_topic, blog_content)
        
        # Compile complete blog post
        complete_post = {
            "metadata": {
                "title": blog_content["title"],
                "slug": self._generate_slug(blog_content["title"]),
                "author": "Kiin Care Team",
                "date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "type": content_type,
                "tone": tone,
                "estimated_read_time": f"{target_words // 200} min read",
                "target_audience": selected_topic.get("target_audience", "family caregivers"),
                "difficulty": selected_topic.get("difficulty", "intermediate")
            },
            "seo": seo_data,
            "content": blog_content,
            "internal_links": internal_links,
            "images": image_suggestions,
            "call_to_action": self._generate_cta(content_type, selected_topic),
            "related_content": self._suggest_related_content(selected_topic)
        }
        
        return complete_post
        
    def _find_topic_by_title(self, title: str) -> Optional[Dict]:
        """Find a topic in the config by title"""
        for category in self.blog_topics.values():
            if isinstance(category, list):
                for topic in category:
                    if topic.get("title", "").lower() == title.lower():
                        return topic
        return None
        
    def _create_custom_topic(self, title: str, content_type: str, tone: str, target_words: int) -> Dict:
        """Create a custom topic structure"""
        return {
            "title": title,
            "keywords": [],
            "tone": tone,
            "estimated_words": target_words,
            "target_audience": "family caregivers",
            "difficulty": "intermediate",
            "content_type": content_type
        }
        
    def _select_topic(self, content_type: str) -> Dict:
        """Select a random topic from the specified type"""
        if content_type in self.blog_topics and self.blog_topics[content_type]:
            return random.choice(self.blog_topics[content_type])
        else:
            # Fallback to any topic
            all_topics = []
            for category in self.blog_topics.values():
                if isinstance(category, list):
                    all_topics.extend(category)
            return random.choice(all_topics) if all_topics else {}
            
    def _generate_content(self, topic: Dict, tone: str, target_words: int) -> Dict:
        """Generate the main blog content"""
        content_type = topic.get("content_type", "educational")
        
        if content_type == "personal_stories":
            return self._generate_personal_story(topic, tone, target_words)
        elif content_type == "how_to_guides":
            return self._generate_how_to_guide(topic, tone, target_words)
        elif content_type == "resource_lists":
            return self._generate_resource_list(topic, tone, target_words)
        elif content_type == "myth_busting":
            return self._generate_myth_busting_article(topic, tone, target_words)
        else:
            return self._generate_educational_article(topic, tone, target_words)
            
    def _generate_educational_article(self, topic: Dict, tone: str, target_words: int) -> Dict:
        """Generate an educational article"""
        title = topic.get("title", "Caregiver Guide")
        style = self.tone_styles.get(tone, self.tone_styles["supportive"])
        
        # Generate sections based on target word count
        sections = []
        
        # Introduction (10% of content)
        intro_words = int(target_words * 0.1)
        introduction = self._generate_introduction(topic, tone, intro_words)
        
        # Main content (70% of content)
        main_words = int(target_words * 0.7)
        main_sections = self._generate_main_sections(topic, tone, main_words)
        
        # Conclusion (10% of content)
        conclusion_words = int(target_words * 0.1)
        conclusion = self._generate_conclusion(topic, tone, conclusion_words)
        
        # Key takeaways (10% of content)
        takeaway_words = int(target_words * 0.1)
        key_takeaways = self._generate_key_takeaways(topic, takeaway_words)
        
        return {
            "title": title,
            "introduction": introduction,
            "main_content": main_sections,
            "key_takeaways": key_takeaways,
            "conclusion": conclusion,
            "word_count": target_words,
            "tone_used": tone,
            "content_type": "educational_article"
        }
        
    def _generate_personal_story(self, topic: Dict, tone: str, target_words: int) -> Dict:
        """Generate a personal story based on confessions or scenarios"""
        # Use existing confession as inspiration
        if self.existing_confessions:
            base_confession = random.choice(self.existing_confessions.get("confessions", []))
            scenario = base_confession.get("scenario", "A caregiving challenge")
        else:
            scenario = "A challenging caregiving moment"
            
        story_arc = topic.get("story_arc", "transformation")
        
        content_sections = []
        
        if story_arc == "realization":
            content_sections = [
                "The Setup: Life Before the Realization",
                "The Moment: When Everything Changed", 
                "The Impact: What This Meant",
                "The Learning: What I Wish I'd Known",
                "Moving Forward: What Comes Next"
            ]
        elif story_arc == "transformation":
            content_sections = [
                "Where I Started: The Struggle",
                "The Turning Point: What Had to Change",
                "The Journey: Taking Action",
                "The Outcome: Where I Am Now",
                "What I Learned: For Other Caregivers"
            ]
        else:
            content_sections = [
                "The Challenge: What We Faced",
                "The Struggle: Why It Was Hard",
                "Finding Solutions: What Worked",
                "The Result: How Things Changed",
                "Your Journey: What This Means for You"
            ]
            
        return {
            "title": topic.get("title", "My Caregiving Story"),
            "story_type": story_arc,
            "sections": content_sections,
            "base_scenario": scenario,
            "tone_used": tone,
            "estimated_words": target_words,
            "content_type": "personal_story"
        }
        
    def _generate_how_to_guide(self, topic: Dict, tone: str, target_words: int) -> Dict:
        """Generate a step-by-step how-to guide"""
        steps = topic.get("steps", 6)
        
        guide_sections = []
        words_per_section = target_words // (steps + 3)  # +3 for intro, overview, conclusion
        
        # Introduction
        guide_sections.append({
            "type": "introduction",
            "content": f"Complete guide to {topic.get('title', 'this caregiving task')}",
            "word_count": words_per_section
        })
        
        # Overview/what you'll need
        guide_sections.append({
            "type": "preparation",
            "content": "What you'll need to get started",
            "word_count": words_per_section
        })
        
        # Steps
        for i in range(1, steps + 1):
            guide_sections.append({
                "type": "step",
                "step_number": i,
                "content": f"Step {i}: [Specific action]",
                "word_count": words_per_section
            })
            
        # Conclusion/next steps
        guide_sections.append({
            "type": "conclusion",
            "content": "What to do next and common troubleshooting",
            "word_count": words_per_section
        })
        
        return {
            "title": topic.get("title", "How-to Guide"),
            "guide_type": "step_by_step",
            "total_steps": steps,
            "difficulty": topic.get("difficulty", "intermediate"),
            "sections": guide_sections,
            "estimated_time": f"{steps * 10} minutes to complete",
            "tone_used": tone,
            "content_type": "how_to_guide"
        }
        
    def _generate_resource_list(self, topic: Dict, tone: str, target_words: int) -> Dict:
        """Generate a resource list or roundup"""
        list_format = topic.get("format", "numbered_list")
        
        # Determine number of resources based on word count
        resources_count = max(10, target_words // 200)
        
        sections = [
            {
                "type": "introduction",
                "content": "Why these resources matter for caregivers",
                "word_count": int(target_words * 0.15)
            },
            {
                "type": "resource_list",
                "format": list_format,
                "resource_count": resources_count,
                "content": "Detailed resource descriptions with how to use each",
                "word_count": int(target_words * 0.70)
            },
            {
                "type": "action_steps",
                "content": "How to implement these resources",
                "word_count": int(target_words * 0.15)
            }
        ]
        
        return {
            "title": topic.get("title", "Resource List"),
            "list_format": list_format,
            "resource_count": resources_count,
            "sections": sections,
            "tone_used": tone,
            "content_type": "resource_list"
        }
        
    def _generate_myth_busting_article(self, topic: Dict, tone: str, target_words: int) -> Dict:
        """Generate a myth-busting article"""
        myths_count = topic.get("myths_covered", 8)
        words_per_myth = (target_words - 400) // myths_count  # Reserve 400 for intro/conclusion
        
        myth_structure = []
        for i in range(1, myths_count + 1):
            myth_structure.append({
                "myth_number": i,
                "myth_statement": f"Myth {i}: [Common misconception]",
                "reality": "The actual truth",
                "explanation": "Why this myth persists and what to do instead",
                "word_count": words_per_myth
            })
            
        return {
            "title": topic.get("title", "Myth-Busting Guide"),
            "myths_addressed": myths_count,
            "myth_structure": myth_structure,
            "introduction": "Why these myths are harmful and what we're covering",
            "conclusion": "Moving forward with the truth",
            "tone_used": tone,
            "content_type": "myth_busting"
        }
        
    def _generate_introduction(self, topic: Dict, tone: str, word_count: int) -> str:
        """Generate an engaging introduction"""
        style = self.tone_styles.get(tone, self.tone_styles["supportive"])
        
        intro_templates = {
            "supportive": [
                "You're not alone in feeling overwhelmed by...",
                "Every caregiver faces moments when...",
                "It's okay to admit that..."
            ],
            "educational": [
                "Understanding [topic] is crucial for...",
                "Research shows that caregivers who...",
                "This comprehensive guide will help you..."
            ],
            "personal": [
                "I remember the day when...",
                "Three years into my caregiving journey...",
                "Nobody prepared me for..."
            ]
        }
        
        templates = intro_templates.get(tone, intro_templates["supportive"])
        
        return f"[{word_count} word introduction using {style['intro_style']} approach. Start with: {random.choice(templates)}]"
        
    def _generate_main_sections(self, topic: Dict, tone: str, word_count: int) -> List[Dict]:
        """Generate main content sections"""
        # Determine number of sections based on content type and word count
        section_count = max(3, min(6, word_count // 400))
        words_per_section = word_count // section_count
        
        sections = []
        for i in range(section_count):
            sections.append({
                "section_number": i + 1,
                "heading": f"Section {i + 1}: [Relevant subtopic]",
                "content": f"[{words_per_section} words covering specific aspect of the topic]",
                "key_points": ["Point 1", "Point 2", "Point 3"],
                "word_count": words_per_section
            })
            
        return sections
        
    def _generate_conclusion(self, topic: Dict, tone: str, word_count: int) -> str:
        """Generate a compelling conclusion"""
        conclusion_templates = {
            "supportive": "Remember, caregiving is a journey, not a destination...",
            "educational": "By implementing these strategies...",
            "personal": "Looking back on this experience...",
            "empowering": "You have the strength to..."
        }
        
        template = conclusion_templates.get(tone, conclusion_templates["supportive"])
        
        return f"[{word_count} word conclusion starting with: {template}]"
        
    def _generate_key_takeaways(self, topic: Dict, word_count: int) -> List[str]:
        """Generate key takeaways"""
        takeaway_count = max(3, min(7, word_count // 50))
        
        takeaways = []
        for i in range(takeaway_count):
            takeaways.append(f"Key takeaway {i + 1}: [Actionable insight]")
            
        return takeaways
        
    def _generate_seo_metadata(self, topic: Dict, content: Dict) -> Dict:
        """Generate SEO metadata"""
        title = content.get("title", "Caregiver Guide")
        
        # Get relevant keywords
        topic_keywords = topic.get("keywords", [])
        primary_keywords = self.seo_keywords.get("primary_keywords", {}).get("high_volume", [])
        
        # Create meta description
        meta_description = f"Complete guide to {title.lower()}. Evidence-based advice for family caregivers with practical tips and emotional support."
        
        return {
            "meta_title": f"{title} | Kiin Care",
            "meta_description": meta_description[:160],  # SEO limit
            "focus_keyword": topic_keywords[0] if topic_keywords else "family caregiver",
            "keywords": topic_keywords + random.sample(primary_keywords, min(3, len(primary_keywords))),
            "canonical_url": f"https://kiin.care/blog/{self._generate_slug(title)}",
            "og_title": title,
            "og_description": meta_description[:300],
            "og_type": "article",
            "schema_type": "Article"
        }
        
    def _generate_slug(self, title: str) -> str:
        """Generate URL slug from title"""
        return title.lower().replace(" ", "-").replace(":", "").replace("?", "").replace("!", "")
        
    def _suggest_internal_links(self, topic: Dict) -> List[Dict]:
        """Suggest internal linking opportunities"""
        suggestions = []
        
        # Link to related content based on keywords
        keywords = topic.get("keywords", [])
        
        for keyword in keywords[:3]:  # Limit to top 3 keywords
            suggestions.append({
                "anchor_text": f"Learn more about {keyword}",
                "target_url": f"/blog/tag/{keyword.replace(' ', '-')}",
                "placement": "within relevant section",
                "link_type": "internal_topic"
            })
            
        # Always suggest linking to key resource pages
        suggestions.extend([
            {
                "anchor_text": "caregiver resources",
                "target_url": "/resources",
                "placement": "conclusion",
                "link_type": "resource_hub"
            },
            {
                "anchor_text": "join our community",
                "target_url": "/community",
                "placement": "after_key_takeaways",
                "link_type": "community_engagement"
            }
        ])
        
        return suggestions
        
    def _generate_image_suggestions(self, topic: Dict, content: Dict) -> List[Dict]:
        """Generate image placement suggestions"""
        images = []
        
        # Featured image
        images.append({
            "type": "featured_image",
            "placement": "top_of_post",
            "alt_text": f"Guide to {topic.get('title', 'caregiving topic')}",
            "description": "Hero image that captures the emotional tone and main topic",
            "suggested_style": "warm, authentic photo of caregiver scenario"
        })
        
        # Section break images
        if content.get("main_content"):
            section_count = len(content.get("main_content", []))
            for i in range(min(section_count, 3)):  # Max 3 section images
                images.append({
                    "type": "section_break",
                    "placement": f"before_section_{i + 1}",
                    "alt_text": f"Visual for section {i + 1}",
                    "description": "Supporting visual for section content",
                    "suggested_style": "relevant illustration or photo"
                })
                
        # Infographic opportunity
        if content.get("key_takeaways"):
            images.append({
                "type": "infographic",
                "placement": "with_key_takeaways",
                "alt_text": "Key takeaways infographic",
                "description": "Visual summary of main points",
                "suggested_style": "branded infographic with key points"
            })
            
        return images
        
    def _generate_cta(self, content_type: str, topic: Dict) -> Dict:
        """Generate appropriate call-to-action"""
        cta_options = {
            "educational_guides": {
                "text": "Get the complete caregiver resource guide",
                "type": "lead_magnet",
                "urgency": "low",
                "placement": "end_of_post"
            },
            "personal_stories": {
                "text": "Share your story with our community",
                "type": "community_engagement",
                "urgency": "medium",
                "placement": "after_story"
            },
            "how_to_guides": {
                "text": "Download the step-by-step checklist",
                "type": "lead_magnet",
                "urgency": "high",
                "placement": "after_steps"
            },
            "resource_lists": {
                "text": "Save this resource list for later",
                "type": "content_save",
                "urgency": "medium",
                "placement": "end_of_list"
            }
        }
        
        return cta_options.get(content_type, cta_options["educational_guides"])
        
    def _suggest_related_content(self, topic: Dict) -> List[Dict]:
        """Suggest related content"""
        related = []
        
        # Find related topics by keywords
        keywords = topic.get("keywords", [])
        
        # Look through all topics for keyword matches
        for category_name, category_topics in self.blog_topics.items():
            if isinstance(category_topics, list):
                for related_topic in category_topics:
                    related_keywords = related_topic.get("keywords", [])
                    
                    # Check for keyword overlap
                    if any(keyword in related_keywords for keyword in keywords):
                        related.append({
                            "title": related_topic.get("title", "Related Article"),
                            "type": category_name,
                            "relevance_score": len(set(keywords) & set(related_keywords)),
                            "url": f"/blog/{self._generate_slug(related_topic.get('title', ''))}"
                        })
                        
        # Sort by relevance and return top 3
        related.sort(key=lambda x: x["relevance_score"], reverse=True)
        return related[:3]
        
    def save_blog_post(self, blog_post: Dict, filename: str = None) -> str:
        """Save blog post to file"""
        if not filename:
            slug = blog_post["metadata"]["slug"]
            filename = f"{slug}_{datetime.datetime.now().strftime('%Y%m%d')}.md"
            
        # Convert to markdown format
        markdown_content = self._convert_to_markdown(blog_post)
        
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
            
        return str(filepath)
        
    def _convert_to_markdown(self, blog_post: Dict) -> str:
        """Convert blog post to markdown format"""
        md_content = []
        
        # Frontmatter
        md_content.append("---")
        md_content.append(f"title: \"{blog_post['metadata']['title']}\"")
        md_content.append(f"slug: {blog_post['metadata']['slug']}")
        md_content.append(f"date: {blog_post['metadata']['date']}")
        md_content.append(f"author: {blog_post['metadata']['author']}")
        md_content.append(f"type: {blog_post['metadata']['type']}")
        md_content.append(f"tone: {blog_post['metadata']['tone']}")
        md_content.append(f"readTime: {blog_post['metadata']['estimated_read_time']}")
        md_content.append(f"audience: {blog_post['metadata']['target_audience']}")
        md_content.append(f"difficulty: {blog_post['metadata']['difficulty']}")
        md_content.append(f"focusKeyword: {blog_post['seo']['focus_keyword']}")
        md_content.append(f"metaDescription: \"{blog_post['seo']['meta_description']}\"")
        md_content.append("---")
        md_content.append("")
        
        # Content
        content = blog_post["content"]
        
        md_content.append(f"# {content['title']}")
        md_content.append("")
        
        # Introduction
        if content.get("introduction"):
            md_content.append(content["introduction"])
            md_content.append("")
            
        # Main content sections
        if content.get("main_content"):
            for section in content["main_content"]:
                md_content.append(f"## {section.get('heading', 'Section')}")
                md_content.append("")
                md_content.append(section.get("content", "Section content here"))
                md_content.append("")
                
        # Key takeaways
        if content.get("key_takeaways"):
            md_content.append("## Key Takeaways")
            md_content.append("")
            for takeaway in content["key_takeaways"]:
                md_content.append(f"- {takeaway}")
            md_content.append("")
            
        # Conclusion
        if content.get("conclusion"):
            md_content.append("## Conclusion")
            md_content.append("")
            md_content.append(content["conclusion"])
            md_content.append("")
            
        # Internal links section
        md_content.append("<!-- Internal Links -->")
        for link in blog_post["internal_links"]:
            md_content.append(f"<!-- {link['anchor_text']}: {link['target_url']} -->")
            
        # Image suggestions
        md_content.append("")
        md_content.append("<!-- Image Suggestions -->")
        for img in blog_post["images"]:
            md_content.append(f"<!-- {img['type']}: {img['description']} -->")
            
        # CTA
        cta = blog_post["call_to_action"]
        md_content.append("")
        md_content.append("---")
        md_content.append("")
        md_content.append(f"**{cta['text']}**")
        md_content.append("")
        
        return "\n".join(md_content)

def main():
    parser = argparse.ArgumentParser(description="Generate blog posts for Kiin Content Factory")
    parser.add_argument("--topic", help="Specific topic title")
    parser.add_argument("--type", default="educational_guides", 
                       choices=["educational_guides", "personal_stories", "resource_lists", 
                               "how_to_guides", "myth_busting", "research_summaries"],
                       help="Type of blog post")
    parser.add_argument("--tone", default="supportive",
                       choices=["supportive", "educational", "personal", "compassionate", "empowering"],
                       help="Tone of the blog post")
    parser.add_argument("--words", type=int, default=2500, help="Target word count")
    parser.add_argument("--output", help="Output filename")
    
    args = parser.parse_args()
    
    generator = BlogGenerator()
    
    # Generate blog post
    blog_post = generator.generate_blog_post(
        topic=args.topic,
        content_type=args.type,
        tone=args.tone,
        target_words=args.words
    )
    
    # Save to file
    filepath = generator.save_blog_post(blog_post, args.output)
    
    print(f"Blog post generated successfully!")
    print(f"Title: {blog_post['metadata']['title']}")
    print(f"Type: {blog_post['metadata']['type']}")
    print(f"Tone: {blog_post['metadata']['tone']}")
    print(f"Target words: {args.words}")
    print(f"Saved to: {filepath}")
    
if __name__ == "__main__":
    main()