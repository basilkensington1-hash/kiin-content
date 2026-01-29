#!/usr/bin/env python3
"""
Email Generator for Kiin Content Factory
Generates email campaigns for caregiver audiences
"""

import json
import os
import random
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse

class EmailGenerator:
    def __init__(self):
        self.config_dir = Path(__file__).parent.parent / "config"
        self.output_dir = Path(__file__).parent.parent / "output" / "email"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration files
        self.email_sequences = self._load_config("email_sequences.json")
        self.caregiver_tips = self._load_config("expanded_caregiver_tips.json")
        self.confessions = self._load_config("confessions_v2.json")
        self.blog_topics = self._load_config("blog_topics.json")
        
        # Email templates and styles
        self.html_template = self._load_html_template()
        self.personalization_engine = PersonalizationEngine()
        
    def _load_config(self, filename: str) -> Dict:
        """Load a configuration file"""
        config_path = self.config_dir / filename
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: {filename} not found")
            return {}
            
    def _load_html_template(self) -> str:
        """Load the base HTML email template"""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{email_title}}</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4; }
        .container { max-width: 600px; margin: 0 auto; background-color: #ffffff; }
        .header { background-color: #2C3E50; color: white; padding: 20px; text-align: center; }
        .content { padding: 30px; line-height: 1.6; }
        .cta-button { display: inline-block; background-color: #3498DB; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 20px 0; }
        .footer { background-color: #ecf0f1; padding: 20px; text-align: center; font-size: 12px; color: #7f8c8d; }
        .highlight { background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 10px; margin: 15px 0; }
        .tip-box { background-color: #d1ecf1; border: 1px solid #bee5eb; border-radius: 5px; padding: 15px; margin: 15px 0; }
        .story-box { background-color: #f8f9fa; border-left: 4px solid #6c757d; padding: 15px; margin: 15px 0; font-style: italic; }
        @media only screen and (max-width: 600px) {
            .container { width: 100%; }
            .content { padding: 20px; }
            .cta-button { display: block; text-align: center; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{header_title}}</h1>
            <p>{{header_subtitle}}</p>
        </div>
        <div class="content">
            {{content_body}}
        </div>
        <div class="footer">
            <p>You're receiving this email because you signed up for caregiver support from Kiin Care.</p>
            <p><a href="{{unsubscribe_link}}">Unsubscribe</a> | <a href="{{preferences_link}}">Manage Preferences</a></p>
            <p>&copy; 2024 Kiin Care. Supporting caregivers with love and understanding.</p>
        </div>
    </div>
</body>
</html>
        '''
        
    def generate_email_campaign(self, campaign_type: str, segment: str = "general", 
                               sequence_name: str = None, email_number: int = 1,
                               personalization_data: Dict = None) -> Dict:
        """Generate a complete email campaign"""
        
        # Get campaign configuration
        campaign_config = self._get_campaign_config(campaign_type, sequence_name, email_number)
        
        # Generate content based on campaign type
        if campaign_type == "welcome":
            email_content = self._generate_welcome_email(campaign_config, personalization_data)
        elif campaign_type == "newsletter":
            email_content = self._generate_newsletter(campaign_config, personalization_data)
        elif campaign_type == "drip":
            email_content = self._generate_drip_email(campaign_config, personalization_data)
        elif campaign_type == "re_engagement":
            email_content = self._generate_reengagement_email(campaign_config, personalization_data)
        elif campaign_type == "product_announcement":
            email_content = self._generate_announcement_email(campaign_config, personalization_data)
        elif campaign_type == "community_highlight":
            email_content = self._generate_community_email(campaign_config, personalization_data)
        else:
            email_content = self._generate_general_email(campaign_config, personalization_data)
            
        # Generate subject line variations for A/B testing
        subject_variations = self._generate_subject_variations(campaign_config, personalization_data)
        
        # Apply personalization
        if personalization_data:
            email_content = self.personalization_engine.apply_personalization(email_content, personalization_data)
            
        # Generate HTML and plain text versions
        html_version = self._generate_html_email(email_content)
        plain_text_version = self._generate_plain_text_email(email_content)
        
        # Compile complete campaign
        complete_campaign = {
            "metadata": {
                "campaign_type": campaign_type,
                "sequence_name": sequence_name or "standalone",
                "email_number": email_number,
                "segment": segment,
                "created_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "estimated_send_time": self._estimate_send_time(email_content)
            },
            "subject_lines": subject_variations,
            "content": email_content,
            "html_version": html_version,
            "plain_text_version": plain_text_version,
            "analytics_tracking": self._generate_tracking_params(campaign_type, sequence_name, email_number),
            "send_timing": self._get_optimal_send_time(segment),
            "mobile_optimization": self._generate_mobile_optimizations(email_content)
        }
        
        return complete_campaign
        
    def _get_campaign_config(self, campaign_type: str, sequence_name: str, email_number: int) -> Dict:
        """Get configuration for the specified campaign"""
        if campaign_type == "welcome" and sequence_name:
            sequences = self.email_sequences.get("welcome_sequences", {})
            if sequence_name in sequences:
                sequence = sequences[sequence_name]
                emails = sequence.get("emails", [])
                for email in emails:
                    if email.get("email_number") == email_number:
                        return email
                        
        elif campaign_type == "drip" and sequence_name:
            drip_campaigns = self.email_sequences.get("drip_campaigns", {})
            if sequence_name in drip_campaigns:
                return drip_campaigns[sequence_name]
                
        elif campaign_type == "newsletter":
            newsletters = self.email_sequences.get("weekly_newsletters", {})
            return newsletters.get("caregiver_weekly", {})
            
        elif campaign_type == "re_engagement":
            reengagement = self.email_sequences.get("re_engagement", {})
            return reengagement.get("dormant_subscribers", {})
            
        elif campaign_type == "community_highlight":
            community = self.email_sequences.get("community_highlights", {})
            return community.get("member_success", {})
            
        # Fallback to general configuration
        return {
            "tone": "supportive",
            "main_topic": "caregiver_support",
            "estimated_words": 300,
            "cta": "Learn more"
        }
        
    def _generate_welcome_email(self, config: Dict, personalization: Dict = None) -> Dict:
        """Generate a welcome email"""
        email_number = config.get("email_number", 1)
        tone = config.get("tone", "welcoming")
        main_topic = config.get("main_topic", "welcome_and_validation")
        
        content_generators = {
            "welcome_and_validation": self._generate_welcome_content,
            "first_steps": self._generate_first_steps_content,
            "emergency_awareness": self._generate_welcome_content,  # Use welcome content for now
            "self_care_foundation": self._generate_self_care_content,
            "building_support": self._generate_welcome_content,  # Use welcome content for now
            "family_communication": self._generate_welcome_content,  # Use welcome content for now
            "milestone_celebration": self._generate_welcome_content  # Use welcome content for now
        }
        
        generator = content_generators.get(main_topic, self._generate_welcome_content)
        content = generator(config, personalization)
        
        return {
            "type": "welcome",
            "email_number": email_number,
            "tone": tone,
            "subject_line": random.choice(config.get("subject_lines", ["Welcome to your caregiving support"])),
            "main_content": content,
            "cta": {
                "text": config.get("cta", "Get started"),
                "url": "{{cta_url}}",
                "style": "primary"
            },
            "estimated_words": config.get("estimated_words", 300)
        }
        
    def _generate_welcome_content(self, config: Dict, personalization: Dict = None) -> Dict:
        """Generate welcome email content"""
        first_name = personalization.get("first_name", "there") if personalization else "there"
        
        return {
            "greeting": f"Hi {first_name},",
            "opening": "Welcome to a community that truly understands what you're going through.",
            "main_message": """
            Becoming a caregiver can feel overwhelming, isolating, and emotionally exhausting. 
            You might be wondering if you're doing enough, if you're making the right decisions, 
            or if it's normal to feel this way. Let me be the first to tell you: everything 
            you're feeling is valid, and you're not alone in this journey.
            """,
            "validation": """
            Thousands of caregivers just like you have found support, guidance, and community here. 
            We're not just another resource website – we're fellow caregivers who've been in your 
            shoes and understand the unique challenges you face.
            """,
            "what_to_expect": """
            Over the next few weeks, I'll be sharing practical tips, emotional support, and 
            real stories from other caregivers. You'll get resources that actually work, 
            not just generic advice that doesn't fit your situation.
            """,
            "immediate_action": "Your first step is simple: download our 'Getting Started as a Caregiver' guide. It's designed specifically for people just beginning this journey.",
            "closing": "Remember, asking for help isn't a sign of weakness – it's a sign of strength. You've taken the first step by joining us.",
            "signature": "With understanding and support,<br>The Kiin Care Team"
        }
        
    def _generate_first_steps_content(self, config: Dict, personalization: Dict = None) -> Dict:
        """Generate first steps guidance content"""
        return {
            "greeting": f"Hi {personalization.get('first_name', 'there') if personalization else 'there'},",
            "opening": "You've been caring for someone for a few days now. How are you feeling?",
            "main_message": """
            If you're feeling overwhelmed, uncertain, or even a bit lost – that's completely normal. 
            Every caregiver starts here, wondering if they're doing the right things.
            """,
            "key_insight": """
            Here's what I wish someone had told me on day one: You don't have to figure it all out at once. 
            Caregiving is learned through experience, compassion, and gradual understanding of what your 
            loved one needs.
            """,
            "practical_steps": [
                "Start with safety: Make sure their immediate environment is secure",
                "Organize medical information: Create a simple file with medications, doctors, and emergency contacts", 
                "Establish routines: Both you and your loved one will benefit from predictable patterns",
                "Connect with their healthcare team: Introduce yourself as the primary caregiver"
            ],
            "encouragement": """
            You're already doing better than you think. The fact that you're here, learning and seeking 
            support, shows your loved one is in caring hands.
            """,
            "closing": "Take it one day at a time. You've got this.",
            "signature": "Cheering you on,<br>The Kiin Care Team"
        }
        
    def _generate_self_care_content(self, config: Dict, personalization: Dict = None) -> Dict:
        """Generate self-care focused content"""
        return {
            "greeting": f"Hi {personalization.get('first_name', 'there') if personalization else 'there'},",
            "opening": "Let's talk about something that might make you uncomfortable: taking care of yourself.",
            "main_message": """
            I know, I know. You're probably thinking, 'I don't have time for self-care. My loved one needs me.'
            But here's the truth: you can't pour from an empty cup. Burned-out caregivers can't provide good care.
            """,
            "key_insight": """
            Self-care isn't selfish – it's essential. When you take care of yourself, you're ensuring your 
            loved one continues to have a capable, present, and emotionally available caregiver.
            """,
            "practical_steps": [
                "Schedule 15 minutes daily for something you enjoy",
                "Accept help when it's offered", 
                "Take breaks without feeling guilty",
                "Maintain your own medical appointments",
                "Connect with friends or family regularly"
            ],
            "encouragement": """
            Starting small is perfectly okay. Even five minutes of deep breathing or a quick walk around 
            the block can make a difference. You matter, and your wellbeing matters.
            """,
            "closing": "You're doing an incredible job. Don't forget to care for the caregiver – you.",
            "signature": "With care for you,<br>The Kiin Care Team"
        }
        
    def _generate_newsletter(self, config: Dict, personalization: Dict = None) -> Dict:
        """Generate newsletter content"""
        sections = config.get("sections", [])
        
        # Generate content for each section
        section_content = {}
        
        for section in sections:
            section_name = section.get("section_name", "")
            content_type = section.get("content_type", "")
            word_count = section.get("word_count", 100)
            
            if content_type == "featured_topic":
                section_content[section_name] = self._generate_featured_topic(word_count)
            elif content_type == "community_story":
                section_content[section_name] = self._generate_community_story(word_count)
            elif content_type == "actionable_tip":
                section_content[section_name] = self._generate_actionable_tip(word_count)
            elif content_type == "curated_links":
                section_content[section_name] = self._generate_curated_links(word_count)
            elif content_type == "user_generated_content":
                section_content[section_name] = self._generate_ugc_section(word_count)
            elif content_type == "wellness_reminder":
                section_content[section_name] = self._generate_wellness_reminder(word_count)
        
        return {
            "type": "newsletter",
            "issue_date": datetime.datetime.now().strftime("%B %d, %Y"),
            "sections": section_content,
            "tone": config.get("tone", "conversational_and_supportive"),
            "total_estimated_words": config.get("total_estimated_words", 775)
        }
        
    def _generate_featured_topic(self, word_count: int) -> Dict:
        """Generate featured topic content"""
        # Select a relevant topic from blog topics
        educational_topics = self.blog_topics.get("educational_guides", [])
        if educational_topics:
            topic = random.choice(educational_topics)
            return {
                "headline": topic.get("title", "This Week's Focus"),
                "summary": f"[{word_count} word summary of {topic.get('title')} with key insights for caregivers]",
                "key_points": ["Point 1", "Point 2", "Point 3"],
                "read_more_link": "/blog/" + topic.get("title", "").lower().replace(" ", "-")
            }
        else:
            return {
                "headline": "Managing Caregiver Stress During Difficult Times",
                "summary": f"[{word_count} word featured article about stress management techniques]",
                "key_points": ["Recognize early warning signs", "Build daily coping strategies", "Know when to seek help"],
                "read_more_link": "/blog/managing-caregiver-stress"
            }
            
    def _generate_community_story(self, word_count: int) -> Dict:
        """Generate community story content"""
        # Use existing confessions as inspiration
        if self.confessions and "confessions" in self.confessions:
            confession = random.choice(self.confessions["confessions"])
            return {
                "story_type": "member_highlight",
                "member_name": "Sarah M.",  # Always anonymized
                "challenge": confession.get("scenario", "A caregiving challenge"),
                "solution": f"[{word_count} word story about how they overcame this challenge]",
                "lesson": "What other caregivers can learn from this experience",
                "engagement_prompt": "Have you faced something similar? Share your experience in our community."
            }
        else:
            return {
                "story_type": "inspiration",
                "headline": "How One Caregiver Found Balance",
                "content": f"[{word_count} word inspiring story about caregiver success]",
                "lesson": "Key takeaway for readers",
                "engagement_prompt": "What's your caregiver success story?"
            }
            
    def _generate_actionable_tip(self, word_count: int) -> Dict:
        """Generate actionable tip content"""
        # Use existing tips
        if self.caregiver_tips and "tips" in self.caregiver_tips:
            tip = random.choice(self.caregiver_tips["tips"])
            return {
                "tip_title": "Quick Tip Tuesday",
                "tip_content": tip.get("tip_content", "Practical caregiving advice"),
                "how_to_implement": f"[{word_count} word explanation of how to implement this tip]",
                "why_it_works": "The science or reasoning behind this tip",
                "time_to_implement": "5 minutes"
            }
        else:
            return {
                "tip_title": "Quick Tip Tuesday",
                "tip_content": "Create a daily check-in routine with your loved one",
                "how_to_implement": f"[{word_count} word step-by-step implementation guide]",
                "why_it_works": "Regular check-ins build trust and catch issues early",
                "time_to_implement": "5 minutes daily"
            }
            
    def _generate_reengagement_email(self, config: Dict, personalization: Dict = None) -> Dict:
        """Generate re-engagement email"""
        emails = config.get("emails", [])
        email_data = emails[0] if emails else {}
        
        return {
            "type": "re_engagement",
            "tone": email_data.get("tone", "caring_check_in"),
            "subject_line": random.choice(email_data.get("subject_lines", ["We miss you"])),
            "main_content": {
                "greeting": f"Hi {personalization.get('first_name', 'there') if personalization else 'there'},",
                "check_in": """
                I noticed you haven't opened our emails lately, and I wanted to check in. 
                Caregiving is exhausting, and sometimes even helpful resources can feel like 
                too much to handle.
                """,
                "understanding": """
                If you're taking a break from emails because you're overwhelmed, that's okay. 
                Your mental health comes first, always.
                """,
                "value_reminder": """
                But if you've just been busy and want to stay connected, I wanted to remind you 
                what's here for you: practical tips, emotional support, and a community that 
                truly understands your journey.
                """,
                "choice": """
                The choice is yours: stay connected with us, update your email preferences, 
                or if it's time to say goodbye, we understand that too.
                """,
                "closing": "Whatever you choose, know that you're thought of and cared for."
            },
            "cta": {
                "text": "Update my preferences",
                "url": "{{preferences_url}}",
                "style": "secondary"
            }
        }
        
    def _generate_subject_variations(self, config: Dict, personalization: Dict = None) -> List[Dict]:
        """Generate A/B test subject line variations"""
        base_subjects = config.get("subject_lines", ["Your caregiver support"])
        
        variations = []
        
        for i, subject in enumerate(base_subjects[:3]):  # Max 3 variations
            # Apply personalization if available
            if personalization and "{{first_name}}" in subject:
                subject = subject.replace("{{first_name}}", personalization.get("first_name", ""))
                
            variations.append({
                "variation": chr(65 + i),  # A, B, C
                "subject_line": subject,
                "predicted_open_rate": self._predict_open_rate(subject),
                "personalized": "{{first_name}}" in subject
            })
            
        return variations
        
    def _predict_open_rate(self, subject_line: str) -> str:
        """Predict open rate based on subject line characteristics"""
        score = 0
        
        # Length optimization (30-50 characters is ideal)
        length = len(subject_line)
        if 30 <= length <= 50:
            score += 2
        elif 20 <= length <= 60:
            score += 1
            
        # Personalization boost
        if "{{first_name}}" in subject_line or "you" in subject_line.lower():
            score += 2
            
        # Urgency indicators
        urgent_words = ["now", "today", "urgent", "important", "don't miss"]
        if any(word in subject_line.lower() for word in urgent_words):
            score += 1
            
        # Emotional words
        emotional_words = ["support", "help", "care", "love", "understand", "together"]
        if any(word in subject_line.lower() for word in emotional_words):
            score += 2
            
        # Questions
        if "?" in subject_line:
            score += 1
            
        # Predict range based on score
        if score >= 6:
            return "25-30%"
        elif score >= 4:
            return "20-25%"
        elif score >= 2:
            return "15-20%"
        else:
            return "10-15%"
            
    def _generate_html_email(self, content: Dict) -> str:
        """Generate HTML email from content"""
        content_html = self._convert_content_to_html(content)
        
        # Replace template variables
        html = self.html_template
        html = html.replace("{{email_title}}", content.get("subject_line", "Caregiver Support"))
        html = html.replace("{{header_title}}", "Kiin Care")
        html = html.replace("{{header_subtitle}}", "Supporting caregivers with understanding")
        html = html.replace("{{content_body}}", content_html)
        html = html.replace("{{unsubscribe_link}}", "{{unsubscribe_url}}")
        html = html.replace("{{preferences_link}}", "{{preferences_url}}")
        
        return html
        
    def _convert_content_to_html(self, content: Dict) -> str:
        """Convert content structure to HTML"""
        html_parts = []
        
        email_type = content.get("type", "general")
        
        if email_type == "welcome":
            main_content = content.get("main_content", {})
            
            # Greeting
            if main_content.get("greeting"):
                html_parts.append(f"<p><strong>{main_content['greeting']}</strong></p>")
                
            # Opening
            if main_content.get("opening"):
                html_parts.append(f"<p>{main_content['opening']}</p>")
                
            # Main message
            if main_content.get("main_message"):
                html_parts.append(f"<p>{main_content['main_message'].strip()}</p>")
                
            # Validation
            if main_content.get("validation"):
                html_parts.append(f'<div class="highlight">{main_content["validation"].strip()}</div>')
                
            # What to expect
            if main_content.get("what_to_expect"):
                html_parts.append(f"<p>{main_content['what_to_expect'].strip()}</p>")
                
            # Practical steps
            if main_content.get("practical_steps"):
                html_parts.append("<h3>Your First Steps:</h3><ul>")
                for step in main_content["practical_steps"]:
                    html_parts.append(f"<li>{step}</li>")
                html_parts.append("</ul>")
                
            # Immediate action
            if main_content.get("immediate_action"):
                html_parts.append(f'<div class="tip-box">{main_content["immediate_action"]}</div>')
                
        elif email_type == "newsletter":
            sections = content.get("sections", {})
            
            # Issue date
            html_parts.append(f"<p><em>Issue for {content.get('issue_date', 'This Week')}</em></p>")
            
            # Generate each section
            for section_name, section_data in sections.items():
                html_parts.append(f"<h2>{section_name}</h2>")
                
                if isinstance(section_data, dict):
                    if section_data.get("headline"):
                        html_parts.append(f"<h3>{section_data['headline']}</h3>")
                    if section_data.get("summary"):
                        html_parts.append(f"<p>{section_data['summary']}</p>")
                    if section_data.get("content"):
                        html_parts.append(f"<p>{section_data['content']}</p>")
                        
        # Add CTA
        cta = content.get("cta", {})
        if cta:
            cta_class = "cta-button" if cta.get("style") == "primary" else "cta-button secondary"
            html_parts.append(f'<p><a href="{cta.get("url", "#")}" class="{cta_class}">{cta.get("text", "Learn More")}</a></p>')
            
        return "\n".join(html_parts)
        
    def _generate_plain_text_email(self, content: Dict) -> str:
        """Generate plain text version of email"""
        text_parts = []
        
        # Subject line
        text_parts.append(f"Subject: {content.get('subject_line', 'Caregiver Support')}")
        text_parts.append("=" * 50)
        text_parts.append("")
        
        email_type = content.get("type", "general")
        
        if email_type == "welcome":
            main_content = content.get("main_content", {})
            
            # Greeting
            if main_content.get("greeting"):
                text_parts.append(main_content["greeting"])
                text_parts.append("")
                
            # Main content sections
            for key in ["opening", "main_message", "validation", "what_to_expect", "immediate_action"]:
                if main_content.get(key):
                    text_parts.append(main_content[key].strip())
                    text_parts.append("")
                    
            # Practical steps
            if main_content.get("practical_steps"):
                text_parts.append("Your First Steps:")
                for i, step in enumerate(main_content["practical_steps"], 1):
                    text_parts.append(f"{i}. {step}")
                text_parts.append("")
                
        elif email_type == "newsletter":
            sections = content.get("sections", {})
            text_parts.append(f"Newsletter for {content.get('issue_date', 'This Week')}")
            text_parts.append("-" * 30)
            text_parts.append("")
            
            for section_name, section_data in sections.items():
                text_parts.append(f"{section_name.upper()}")
                text_parts.append("-" * len(section_name))
                
                if isinstance(section_data, dict):
                    for key, value in section_data.items():
                        if isinstance(value, str) and value.strip():
                            text_parts.append(value.strip())
                            text_parts.append("")
                            
        # Add CTA
        cta = content.get("cta", {})
        if cta:
            text_parts.append(f">> {cta.get('text', 'Learn More')}: {cta.get('url', '#')}")
            text_parts.append("")
            
        # Footer
        text_parts.append("-" * 50)
        text_parts.append("Kiin Care - Supporting caregivers with understanding")
        text_parts.append("Unsubscribe: {{unsubscribe_url}}")
        text_parts.append("Manage Preferences: {{preferences_url}}")
        
        return "\n".join(text_parts)
        
    def _generate_tracking_params(self, campaign_type: str, sequence_name: str, email_number: int) -> Dict:
        """Generate analytics tracking parameters"""
        return {
            "utm_source": "kiin_email",
            "utm_medium": "email",
            "utm_campaign": f"{campaign_type}_{sequence_name or 'standalone'}",
            "utm_content": f"email_{email_number}",
            "email_id": f"{campaign_type}_{datetime.datetime.now().strftime('%Y%m%d')}_{email_number}",
            "tracking_pixel": "{{tracking_pixel_url}}",
            "click_tracking": True,
            "open_tracking": True
        }
        
    def _get_optimal_send_time(self, segment: str) -> Dict:
        """Get optimal send time based on segment"""
        send_times = {
            "general": {"day": "Tuesday", "time": "10:00 AM", "timezone": "EST"},
            "working_caregivers": {"day": "Sunday", "time": "7:00 PM", "timezone": "EST"},
            "new_caregivers": {"day": "Wednesday", "time": "2:00 PM", "timezone": "EST"},
            "dementia_caregivers": {"day": "Thursday", "time": "11:00 AM", "timezone": "EST"}
        }
        
        return send_times.get(segment, send_times["general"])
        
    def _estimate_send_time(self, content: Dict) -> str:
        """Estimate how long the email takes to read"""
        word_count = content.get("estimated_words", 300)
        read_time = max(1, word_count // 200)  # 200 words per minute
        return f"{read_time} min read"
        
    def _generate_mobile_optimizations(self, content: Dict) -> Dict:
        """Generate mobile optimization suggestions"""
        return {
            "subject_line_length": "Keep under 40 characters for mobile preview",
            "preview_text": "First 90 characters will show in mobile preview",
            "button_size": "Minimum 44px height for touch targets",
            "font_size": "Minimum 14px for readability",
            "image_width": "Maximum 600px width for container",
            "single_column": "Use single column layout for mobile",
            "spacing": "Add generous padding around tap targets"
        }
        
    def save_email_campaign(self, campaign: Dict, filename: str = None) -> str:
        """Save email campaign to files"""
        if not filename:
            campaign_type = campaign["metadata"]["campaign_type"]
            sequence = campaign["metadata"]["sequence_name"]
            email_num = campaign["metadata"]["email_number"]
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
            filename = f"{campaign_type}_{sequence}_email{email_num}_{timestamp}"
            
        # Save HTML version
        html_path = self.output_dir / f"{filename}.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(campaign["html_version"])
            
        # Save plain text version
        txt_path = self.output_dir / f"{filename}.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(campaign["plain_text_version"])
            
        # Save campaign metadata as JSON
        json_path = self.output_dir / f"{filename}_metadata.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(campaign, f, indent=2, ensure_ascii=False)
            
        return str(html_path)

class PersonalizationEngine:
    """Handle email personalization"""
    
    def apply_personalization(self, content: Dict, personalization_data: Dict) -> Dict:
        """Apply personalization tokens to content"""
        personalized_content = json.loads(json.dumps(content))  # Deep copy
        
        # Apply basic personalization tokens
        tokens = {
            "{{first_name}}": personalization_data.get("first_name", ""),
            "{{care_recipient_relationship}}": personalization_data.get("care_recipient_relationship", "loved one"),
            "{{primary_challenge}}": personalization_data.get("primary_challenge", "caregiving"),
            "{{location}}": personalization_data.get("location", ""),
            "{{care_stage}}": personalization_data.get("care_stage", "ongoing"),
            "{{caregiver_type}}": personalization_data.get("caregiver_type", "family caregiver")
        }
        
        # Replace tokens in content recursively
        personalized_content = self._replace_tokens_recursive(personalized_content, tokens)
        
        return personalized_content
        
    def _replace_tokens_recursive(self, obj, tokens: Dict):
        """Recursively replace tokens in any data structure"""
        if isinstance(obj, str):
            for token, value in tokens.items():
                obj = obj.replace(token, str(value))
            return obj
        elif isinstance(obj, dict):
            return {k: self._replace_tokens_recursive(v, tokens) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._replace_tokens_recursive(item, tokens) for item in obj]
        else:
            return obj

def main():
    parser = argparse.ArgumentParser(description="Generate email campaigns for Kiin Content Factory")
    parser.add_argument("--type", required=True,
                       choices=["welcome", "newsletter", "drip", "re_engagement", "product_announcement", "community_highlight"],
                       help="Type of email campaign")
    parser.add_argument("--sequence", help="Sequence name (for welcome/drip campaigns)")
    parser.add_argument("--email-number", type=int, default=1, help="Email number in sequence")
    parser.add_argument("--segment", default="general", help="Target segment")
    parser.add_argument("--personalization", help="JSON file with personalization data")
    parser.add_argument("--output", help="Output filename prefix")
    
    args = parser.parse_args()
    
    generator = EmailGenerator()
    
    # Load personalization data if provided
    personalization_data = None
    if args.personalization:
        with open(args.personalization, 'r') as f:
            personalization_data = json.load(f)
    
    # Generate email campaign
    campaign = generator.generate_email_campaign(
        campaign_type=args.type,
        segment=args.segment,
        sequence_name=args.sequence,
        email_number=args.email_number,
        personalization_data=personalization_data
    )
    
    # Save campaign
    filepath = generator.save_email_campaign(campaign, args.output)
    
    print(f"Email campaign generated successfully!")
    print(f"Type: {args.type}")
    print(f"Sequence: {args.sequence or 'standalone'}")
    print(f"Email number: {args.email_number}")
    print(f"Segment: {args.segment}")
    print(f"Subject variations: {len(campaign['subject_lines'])}")
    print(f"Saved to: {filepath}")
    
    # Print subject line variations
    print("\nSubject Line A/B Tests:")
    for variation in campaign["subject_lines"]:
        print(f"  {variation['variation']}: {variation['subject_line']} (Est. open rate: {variation['predicted_open_rate']})")

if __name__ == "__main__":
    main()