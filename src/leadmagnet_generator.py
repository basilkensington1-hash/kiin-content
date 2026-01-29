#!/usr/bin/env python3
"""
Lead Magnet Generator for Kiin Content Factory
Generates PDF-ready lead magnets for caregiver audiences
"""

import json
import os
import random
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse

class LeadMagnetGenerator:
    def __init__(self):
        self.config_dir = Path(__file__).parent.parent / "config"
        self.output_dir = Path(__file__).parent.parent / "output" / "leadmagnets"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration files
        self.leadmagnet_templates = self._load_config("leadmagnet_templates.json")
        self.caregiver_tips = self._load_config("expanded_caregiver_tips.json")
        self.blog_topics = self._load_config("blog_topics.json")
        self.seo_keywords = self._load_config("seo_keywords.json")
        
        # Branding and design
        self.brand_config = self._load_brand_config()
        
    def _load_config(self, filename: str) -> Dict:
        """Load a configuration file"""
        config_path = self.config_dir / filename
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: {filename} not found")
            return {}
            
    def _load_brand_config(self) -> Dict:
        """Load branding configuration"""
        brand_path = self.config_dir.parent / "brand"
        if brand_path.exists():
            # Use existing brand config if available
            return {
                "primary_color": "#2C3E50",
                "secondary_color": "#3498DB",
                "accent_color": "#E74C3C",
                "font_primary": "Open Sans",
                "font_secondary": "Lato",
                "logo_path": "assets/kiin-logo.png"
            }
        else:
            return self.leadmagnet_templates.get("design_specifications", {}).get("branding", {})
            
    def generate_lead_magnet(self, magnet_type: str, topic: str = None, 
                            target_audience: str = "family caregivers",
                            custom_config: Dict = None) -> Dict:
        """Generate a complete lead magnet"""
        
        # Get template configuration
        template_config = self._get_template_config(magnet_type, topic)
        
        # Override with custom config if provided
        if custom_config:
            template_config.update(custom_config)
            
        # Generate content based on type
        if magnet_type == "checklist":
            content = self._generate_checklist(template_config, target_audience)
        elif magnet_type == "resource_guide":
            content = self._generate_resource_guide(template_config, target_audience)
        elif magnet_type == "planner":
            content = self._generate_planner(template_config, target_audience)
        elif magnet_type == "tip_sheet":
            content = self._generate_tip_sheet(template_config, target_audience)
        elif magnet_type == "reference_card":
            content = self._generate_reference_card(template_config, target_audience)
        else:
            content = self._generate_generic_guide(template_config, target_audience)
            
        # Generate design specifications
        design_specs = self._generate_design_specifications(magnet_type, content)
        
        # Create distribution strategy
        distribution = self._create_distribution_strategy(magnet_type, content)
        
        # Generate tracking and analytics
        analytics = self._generate_analytics_config(magnet_type, content)
        
        # Compile complete lead magnet
        complete_magnet = {
            "metadata": {
                "name": content["title"],
                "type": magnet_type,
                "target_audience": target_audience,
                "created_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "pages": content.get("pages", 1),
                "estimated_completion_time": self._estimate_completion_time(content),
                "difficulty_level": template_config.get("difficulty", "beginner")
            },
            "content": content,
            "design_specifications": design_specs,
            "branding": self.brand_config,
            "distribution_strategy": distribution,
            "analytics": analytics,
            "pdf_generation_instructions": self._generate_pdf_instructions(content, design_specs),
            "follow_up_sequence": self._create_follow_up_sequence(magnet_type, content)
        }
        
        return complete_magnet
        
    def _get_template_config(self, magnet_type: str, topic: str = None) -> Dict:
        """Get template configuration for the specified type"""
        templates = self.leadmagnet_templates.get(f"{magnet_type}s", [])
        
        if topic:
            # Find template by name/topic
            for template in templates:
                if topic.lower() in template.get("name", "").lower():
                    return template
                    
        # Return first template of type or create default
        if templates:
            return templates[0]
        else:
            return self._create_default_template(magnet_type, topic)
            
    def _create_default_template(self, magnet_type: str, topic: str = None) -> Dict:
        """Create default template configuration"""
        return {
            "name": topic or f"Caregiver {magnet_type.title()}",
            "description": f"Essential {magnet_type} for family caregivers",
            "target_audience": "family caregivers",
            "format": "PDF",
            "pages": 3 if magnet_type == "reference_card" else 5
        }
        
    def _generate_checklist(self, config: Dict, target_audience: str) -> Dict:
        """Generate a checklist lead magnet"""
        name = config.get("name", "Caregiver Checklist")
        sections = config.get("sections", [])
        
        checklist_content = {
            "title": name,
            "subtitle": f"A comprehensive checklist for {target_audience}",
            "introduction": self._generate_checklist_intro(name, target_audience),
            "sections": [],
            "completion_tracking": True,
            "pages": config.get("pages", 5),
            "total_items": 0
        }
        
        # Generate sections
        for section_config in sections:
            section = self._generate_checklist_section(section_config)
            checklist_content["sections"].append(section)
            checklist_content["total_items"] += section["items_count"]
            
        # Add conclusion and next steps
        checklist_content["conclusion"] = self._generate_checklist_conclusion(name)
        checklist_content["next_steps"] = self._generate_next_steps(target_audience)
        
        return checklist_content
        
    def _generate_checklist_intro(self, name: str, target_audience: str) -> str:
        """Generate introduction for checklist"""
        return f"""
        Welcome to your {name}! This comprehensive checklist is designed specifically for {target_audience} 
        who want to ensure they're covering all the essential aspects of caregiving.
        
        Each item in this checklist has been carefully selected based on real caregiver experiences 
        and expert recommendations. Use this as your roadmap to confident, organized caregiving.
        
        How to use this checklist:
        • Work through one section at a time
        • Check off items as you complete them
        • Don't feel pressured to do everything at once
        • Return to this checklist regularly for reference
        
        Remember: This is a guide, not a test. Every caregiving situation is unique, so adapt 
        these recommendations to fit your specific needs.
        """
        
    def _generate_checklist_section(self, section_config: Dict) -> Dict:
        """Generate a single section of the checklist"""
        section_title = section_config.get("section_title", "Checklist Section")
        items_count = section_config.get("items_count", 10)
        priority_level = section_config.get("priority_level", "medium")
        estimated_time = section_config.get("estimated_time", "30 minutes")
        
        # Generate checklist items based on section type
        items = self._generate_checklist_items(section_title, items_count)
        
        return {
            "section_title": section_title,
            "priority_level": priority_level,
            "estimated_time": estimated_time,
            "items_count": items_count,
            "items": items,
            "tips": self._generate_section_tips(section_title),
            "common_mistakes": self._generate_common_mistakes(section_title)
        }
        
    def _generate_checklist_items(self, section_title: str, count: int) -> List[Dict]:
        """Generate checklist items for a section"""
        items = []
        
        # Define item templates based on section type
        if "safety" in section_title.lower():
            item_templates = [
                "Remove or secure loose rugs and carpets",
                "Install grab bars in bathroom",
                "Ensure adequate lighting in all areas",
                "Check that emergency numbers are easily accessible",
                "Verify smoke detector batteries are working",
                "Clear walkways of clutter",
                "Install non-slip mats in shower/tub",
                "Check that handrails are secure",
                "Remove or secure electrical cords",
                "Ensure emergency exits are clear"
            ]
        elif "medication" in section_title.lower():
            item_templates = [
                "Create a current medication list with dosages",
                "Organize medications with pill organizer",
                "Set up medication reminders/alarms",
                "Contact all prescribing doctors",
                "Review medications with pharmacist",
                "Check expiration dates on all medications",
                "Create emergency medication kit",
                "Understand drug interactions and side effects",
                "Establish routine for medication administration",
                "Keep backup supplies of essential medications"
            ]
        elif "medical" in section_title.lower():
            item_templates = [
                "Compile medical history and current conditions",
                "Gather insurance information and cards",
                "Create list of current healthcare providers",
                "Organize recent test results and reports",
                "Schedule overdue medical appointments",
                "Understand current treatment plans",
                "Identify nearest emergency room",
                "Create medical emergency action plan",
                "Discuss advance directives",
                "Set up patient portal access"
            ]
        else:
            # Generic caregiving items
            item_templates = [
                "Assess current care needs and challenges",
                "Create daily routine and schedule",
                "Establish communication with family members",
                "Research local support resources",
                "Set up emergency contact system",
                "Organize important documents",
                "Create care plan with specific goals",
                "Schedule regular check-ins with care recipient",
                "Identify respite care options",
                "Plan for care transitions"
            ]
            
        # Select and customize items
        selected_templates = random.sample(item_templates, min(count, len(item_templates)))
        
        for i, template in enumerate(selected_templates):
            items.append({
                "item_number": i + 1,
                "description": template,
                "priority": "high" if i < count // 3 else "medium" if i < 2 * count // 3 else "low",
                "estimated_time": "15-30 minutes",
                "notes_space": True
            })
            
        return items
        
    def _generate_checklist_conclusion(self, name: str) -> str:
        """Generate conclusion for checklist"""
        return f"""
        Congratulations on completing your {name}! By working through these items, you've taken 
        important steps toward providing safer, more organized care for your loved one.
        
        Remember:
        • This is an ongoing process, not a one-time task
        • Revisit this checklist regularly as needs change
        • Don't hesitate to seek professional help when needed
        • Celebrate the progress you've made
        
        Your dedication to providing quality care makes a real difference in your loved one's life.
        Keep up the excellent work, and remember that support is always available when you need it.
        """
        
    def _generate_next_steps(self, target_audience: str) -> List[str]:
        """Generate next steps after completing checklist"""
        return [
            "Review completed items weekly for any changes needed",
            "Share this checklist with other family members involved in care",
            "Schedule regular check-ins to reassess care needs",
            "Connect with local support resources in your community",
            "Consider joining a caregiver support group",
            "Schedule time for your own self-care and wellbeing"
        ]
        
    def _generate_section_tips(self, section_title: str) -> List[str]:
        """Generate tips for a checklist section"""
        tips = []
        if "safety" in section_title.lower():
            tips = [
                "Start with the most critical safety issues first",
                "Involve your loved one in safety decisions when possible",
                "Consider professional home safety assessments"
            ]
        elif "medication" in section_title.lower():
            tips = [
                "Review medications with pharmacist regularly",
                "Set up automated reminders for consistency",
                "Keep emergency medication information accessible"
            ]
        else:
            tips = [
                "Take your time working through this section",
                "Ask for help when needed",
                "Document what you've completed"
            ]
        return tips
        
    def _generate_common_mistakes(self, section_title: str) -> List[str]:
        """Generate common mistakes for a section"""
        mistakes = []
        if "safety" in section_title.lower():
            mistakes = [
                "Making changes without consulting your loved one",
                "Trying to do everything at once",
                "Ignoring smaller hazards that can add up"
            ]
        elif "medication" in section_title.lower():
            mistakes = [
                "Not checking for drug interactions",
                "Assuming all medications are still necessary",
                "Not having backup plans for missed doses"
            ]
        else:
            mistakes = [
                "Rushing through important decisions",
                "Not seeking professional guidance when needed",
                "Forgetting to include other family members"
            ]
        return mistakes
        
    def _generate_resource_guide(self, config: Dict, target_audience: str) -> Dict:
        """Generate a resource guide lead magnet"""
        name = config.get("name", "Caregiver Resource Guide")
        sections = config.get("sections", [])
        
        guide_content = {
            "title": name,
            "subtitle": f"Essential resources for {target_audience}",
            "introduction": self._generate_guide_intro(name, target_audience),
            "table_of_contents": [],
            "sections": [],
            "pages": config.get("pages", 15),
            "interactive_elements": config.get("interactive_elements", [])
        }
        
        # Generate sections
        for section_config in sections:
            section = self._generate_guide_section(section_config)
            guide_content["sections"].append(section)
            guide_content["table_of_contents"].append({
                "title": section["title"],
                "page": section.get("page_number", 1)
            })
            
        # Add resource directory
        guide_content["resource_directory"] = self._generate_resource_directory()
        guide_content["quick_reference"] = self._generate_quick_reference()
        
        return guide_content
        
    def _generate_curated_links(self, word_count: int) -> Dict:
        """Generate curated links section"""
        return {
            "headline": "This Week's Best Resources",
            "links": [
                {"title": "Essential Resource 1", "url": "#", "description": "Brief description"},
                {"title": "Essential Resource 2", "url": "#", "description": "Brief description"},
                {"title": "Essential Resource 3", "url": "#", "description": "Brief description"}
            ],
            "summary": f"[{word_count} word summary of curated resources]"
        }
        
    def _generate_ugc_section(self, word_count: int) -> Dict:
        """Generate user-generated content section"""
        return {
            "headline": "From Our Community",
            "content": f"[{word_count} word community highlights and shared experiences]",
            "engagement_prompt": "Share your experience in our Facebook group"
        }
        
    def _generate_wellness_reminder(self, word_count: int) -> Dict:
        """Generate wellness reminder section"""
        return {
            "headline": "Self-Care Reminder",
            "content": f"[{word_count} word gentle reminder about caregiver self-care]",
            "action_item": "One small thing you can do for yourself this week"
        }
        
    def _generate_practical_guidance(self, title: str) -> List[Dict]:
        """Generate practical guidance content"""
        return [
            {
                "guidance_type": "step_by_step",
                "title": f"How to handle {title}",
                "steps": ["Step 1", "Step 2", "Step 3"],
                "tips": ["Tip 1", "Tip 2", "Tip 3"]
            }
        ]
        
    def _generate_action_plans(self, title: str) -> List[Dict]:
        """Generate action plans"""
        return [
            {
                "plan_name": f"{title} Action Plan",
                "immediate_actions": ["Action 1", "Action 2"],
                "ongoing_actions": ["Action 3", "Action 4"],
                "emergency_actions": ["Emergency Action 1", "Emergency Action 2"]
            }
        ]
        
    def _generate_resource_directory(self) -> List[Dict]:
        """Generate comprehensive resource directory"""
        return [
            {
                "category": "Emergency Services",
                "resources": [
                    {"name": "911", "description": "Emergency services", "contact": "911"},
                    {"name": "Poison Control", "description": "24/7 poison help", "contact": "1-800-222-1222"}
                ]
            }
        ]
        
    def _generate_quick_reference(self) -> Dict:
        """Generate quick reference section"""
        return {
            "emergency_numbers": ["911", "Doctor: ___", "Pharmacy: ___"],
            "important_info": ["Insurance ID: ___", "Medical conditions: ___"],
            "quick_tips": ["Tip 1", "Tip 2", "Tip 3"]
        }
        
    def _generate_tracking_pages(self) -> List[Dict]:
        """Generate tracking pages for planners"""
        return [
            {
                "page_type": "medication_tracking",
                "layout": "weekly_grid",
                "fields": ["medication", "dosage", "time", "notes"]
            },
            {
                "page_type": "mood_tracking", 
                "layout": "daily_scale",
                "fields": ["date", "mood_rating", "observations"]
            }
        ]
        
    def _generate_reference_pages(self) -> List[Dict]:
        """Generate reference pages"""
        return [
            {
                "page_type": "emergency_contacts",
                "content": "Emergency contact information template"
            },
            {
                "page_type": "medical_information",
                "content": "Medical history and current conditions template"
            }
        ]
        
    def _generate_quick_actions(self) -> List[str]:
        """Generate quick action items"""
        return [
            "Create emergency contact list",
            "Schedule self-care time",
            "Connect with one support person",
            "Review safety checklist",
            "Take five deep breaths"
        ]
        
    def _generate_emergency_tips(self) -> List[Dict]:
        """Generate emergency tips"""
        return [
            {
                "situation": "Medical Emergency",
                "tip": "Call 911 immediately",
                "preparation": "Keep medical information easily accessible"
            },
            {
                "situation": "Behavior Crisis",
                "tip": "Stay calm and ensure safety first",
                "preparation": "Have crisis plan ready"
            }
        ]
        
    def _generate_social_copy(self, content: Dict) -> Dict:
        """Generate social media copy"""
        title = content.get("title", "Caregiver Resource")
        return {
            "facebook": f"Free download: {title} - everything you need in one place!",
            "twitter": f"Caregivers: get your free {title} 👇",
            "linkedin": f"Supporting family caregivers with our comprehensive {title}"
        }
        
    def _generate_planner_section(self, section_config: Dict) -> Dict:
        """Generate planner section"""
        title = section_config.get("section_title", "Planner Section")
        pages = section_config.get("pages", 3)
        content_type = section_config.get("content", "planning pages")
        
        return {
            "section_title": title,
            "pages": pages,
            "content_type": content_type,
            "layout": "weekly_grid" if "weekly" in title.lower() else "monthly_overview",
            "elements": ["date_fields", "task_lists", "notes_section"]
        }
        
    def _generate_educational_overview(self, title: str) -> str:
        """Generate educational overview content"""
        return f"""
        Understanding {title} is crucial for effective caregiving. This overview provides
        essential background information, key concepts, and foundational knowledge that
        will help you make informed decisions and provide better care.
        
        Key topics covered:
        • Fundamental principles
        • Common challenges and solutions
        • Best practices and recommendations
        • When to seek professional help
        • Resources for ongoing learning
        """
        
    def _generate_guide_intro(self, name: str, target_audience: str) -> str:
        """Generate introduction for resource guide"""
        return f"""
        Caregiving can feel overwhelming, especially when you're not sure where to find help. 
        This {name} brings together the most valuable resources for {target_audience} in one 
        convenient place.
        
        Inside this guide, you'll find:
        • Trusted organizations and support services
        • Online resources and helpful websites
        • Local services and how to find them
        • Financial assistance programs
        • Legal and planning resources
        • Emergency contacts and crisis support
        
        Each resource has been carefully vetted and includes specific information about:
        • Who they serve and how they can help
        • How to contact them
        • What to expect when you reach out
        • Any costs or eligibility requirements
        
        Keep this guide handy and don't hesitate to reach out for help. You don't have to 
        navigate caregiving alone.
        """
        
    def _generate_guide_section(self, section_config: Dict) -> Dict:
        """Generate a section of the resource guide"""
        title = section_config.get("section_title", "Resource Section")
        content_type = section_config.get("content_type", "resource_directory")
        pages = section_config.get("pages", 3)
        
        section = {
            "title": title,
            "content_type": content_type,
            "pages": pages,
            "page_number": 0  # Will be set during layout
        }
        
        if content_type == "educational_overview":
            section["content"] = self._generate_educational_overview(title)
            section["includes"] = section_config.get("includes", [])
        elif content_type == "resource_directory":
            section["resources"] = self._generate_resource_list(title)
        elif content_type == "practical_guidance":
            section["guidance"] = self._generate_practical_guidance(title)
        elif content_type == "action_plans":
            section["plans"] = self._generate_action_plans(title)
        else:
            section["content"] = f"[{content_type} content for {title}]"
            
        return section
        
    def _generate_resource_list(self, section_title: str) -> List[Dict]:
        """Generate a list of resources for a section"""
        resources = []
        
        if "dementia" in section_title.lower():
            resource_templates = [
                {
                    "name": "Alzheimer's Association",
                    "description": "Comprehensive support for Alzheimer's and dementia",
                    "contact": "1-800-272-3900",
                    "website": "alz.org",
                    "services": ["24/7 helpline", "Local support groups", "Educational resources"],
                    "cost": "Free"
                },
                {
                    "name": "Family Caregiver Alliance",
                    "description": "National center supporting family caregivers",
                    "contact": "1-800-445-8106",
                    "website": "caregiver.org",
                    "services": ["Information and guidance", "Caregiver support", "Policy advocacy"],
                    "cost": "Free"
                }
            ]
        elif "financial" in section_title.lower():
            resource_templates = [
                {
                    "name": "Medicare.gov",
                    "description": "Official Medicare information and enrollment",
                    "contact": "1-800-MEDICARE",
                    "website": "medicare.gov",
                    "services": ["Plan finder", "Coverage information", "Claims tracking"],
                    "cost": "Free"
                },
                {
                    "name": "Benefits Checkup",
                    "description": "Find benefit programs for seniors",
                    "contact": "Online tool",
                    "website": "benefitscheckup.org",
                    "services": ["Benefit screening", "Application assistance", "Program information"],
                    "cost": "Free"
                }
            ]
        else:
            resource_templates = [
                {
                    "name": "Eldercare Locator",
                    "description": "Find local aging and disability services",
                    "contact": "1-800-677-1116",
                    "website": "eldercare.acl.gov",
                    "services": ["Local resource finder", "Information and referral"],
                    "cost": "Free"
                },
                {
                    "name": "AARP Caregiving Resource Center",
                    "description": "Comprehensive caregiving support",
                    "contact": "Online resource",
                    "website": "aarp.org/caregiving",
                    "services": ["Guides and tools", "Expert advice", "Community support"],
                    "cost": "Free"
                }
            ]
            
        # Customize resources for section
        for template in resource_templates:
            resources.append({
                "organization": template["name"],
                "description": template["description"],
                "contact_info": template["contact"],
                "website": template["website"],
                "services_offered": template["services"],
                "cost_info": template["cost"],
                "notes_space": True
            })
            
        return resources
        
    def _generate_planner(self, config: Dict, target_audience: str) -> Dict:
        """Generate a planner lead magnet"""
        name = config.get("name", "Caregiver Planner")
        sections = config.get("sections", [])
        time_period = config.get("time_period", "monthly")
        
        planner_content = {
            "title": name,
            "subtitle": f"Organize your caregiving with this {time_period} planner",
            "introduction": self._generate_planner_intro(name, target_audience),
            "sections": [],
            "pages": config.get("pages", 20),
            "time_period": time_period,
            "features": config.get("features", [])
        }
        
        # Generate planner sections
        for section_config in sections:
            section = self._generate_planner_section(section_config)
            planner_content["sections"].append(section)
            
        # Add tracking pages
        planner_content["tracking_pages"] = self._generate_tracking_pages()
        planner_content["reference_pages"] = self._generate_reference_pages()
        
        return planner_content
        
    def _generate_planner_intro(self, name: str, target_audience: str) -> str:
        """Generate introduction for planner"""
        return f"""
        Effective caregiving requires organization, planning, and self-care. This {name} is 
        designed to help {target_audience} stay organized while maintaining balance in their lives.
        
        This planner includes:
        • Daily and weekly planning pages
        • Medical appointment tracking
        • Medication schedules and reminders
        • Self-care tracking and goals
        • Emergency contact information
        • Notes sections for observations and concerns
        
        How to use this planner effectively:
        1. Set aside 10 minutes each week for planning
        2. Use the daily pages to track activities and appointments
        3. Review weekly to identify patterns and adjust care plans
        4. Don't forget to schedule time for your own self-care
        5. Keep this planner easily accessible
        
        Remember: This planner is a tool to support you, not add pressure. Use what works 
        and adapt the rest to fit your unique situation.
        """
        
    def _generate_tip_sheet(self, config: Dict, target_audience: str) -> Dict:
        """Generate a tip sheet lead magnet"""
        name = config.get("name", "Caregiver Tips")
        topics = config.get("topics", [])
        
        tip_sheet_content = {
            "title": name,
            "subtitle": f"Quick reference guide for {target_audience}",
            "introduction": self._generate_tip_sheet_intro(name),
            "tip_sections": [],
            "pages": config.get("pages", 4),
            "format_style": "quick_reference"
        }
        
        # Generate tip sections
        for topic in topics[:10]:  # Limit to 10 topics for readability
            tip_section = self._generate_tip_section(topic)
            tip_sheet_content["tip_sections"].append(tip_section)
            
        # Add quick action items
        tip_sheet_content["quick_actions"] = self._generate_quick_actions()
        tip_sheet_content["emergency_tips"] = self._generate_emergency_tips()
        
        return tip_sheet_content
        
    def _generate_tip_section(self, topic: str) -> Dict:
        """Generate a section of tips for a specific topic"""
        # Use existing tips if available
        if self.caregiver_tips and "tips" in self.caregiver_tips:
            relevant_tips = [tip for tip in self.caregiver_tips["tips"] 
                           if topic.lower() in tip.get("scenario", "").lower() or
                              topic.lower() in tip.get("tip_content", "").lower()]
            
            if relevant_tips:
                selected_tip = random.choice(relevant_tips)
                return {
                    "topic": topic.title(),
                    "main_tip": selected_tip.get("tip_content", f"Key advice for {topic}"),
                    "quick_actions": [
                        "Immediate action 1",
                        "Immediate action 2", 
                        "Immediate action 3"
                    ],
                    "avoid_this": f"Common mistake to avoid with {topic}",
                    "when_to_seek_help": f"Warning signs that indicate you need professional help with {topic}"
                }
                
        # Generate generic tip section
        return {
            "topic": topic.title(),
            "main_tip": f"Essential guidance for managing {topic} in caregiving situations",
            "quick_actions": [
                f"Assess the {topic} situation",
                f"Create a plan for {topic}",
                f"Monitor progress with {topic}"
            ],
            "avoid_this": f"Don't ignore early warning signs related to {topic}",
            "when_to_seek_help": f"Contact professionals when {topic} becomes unmanageable"
        }
        
    def _generate_reference_card(self, config: Dict, target_audience: str) -> Dict:
        """Generate a reference card lead magnet"""
        name = config.get("name", "Quick Reference Card")
        size = config.get("size", "wallet_sized")
        
        card_content = {
            "title": name,
            "size": size,
            "front_side": self._generate_card_front(config),
            "back_side": self._generate_card_back(config),
            "pages": 1,
            "print_instructions": self._generate_print_instructions(size)
        }
        
        return card_content
        
    def _generate_card_front(self, config: Dict) -> Dict:
        """Generate front side content for reference card"""
        front_content = config.get("front_content", [])
        
        return {
            "header": "Emergency Caregiver Reference",
            "sections": [
                {
                    "title": "Emergency Contacts",
                    "content": ["911 - Emergency", "Doctor: ___________", "Pharmacy: ___________"]
                },
                {
                    "title": "Current Medications", 
                    "content": ["Medication 1: ___________", "Medication 2: ___________", "Allergies: ___________"]
                },
                {
                    "title": "Medical Info",
                    "content": ["Insurance: ___________", "ID #: ___________", "Preferred Hospital: ___________"]
                }
            ]
        }
        
    def _generate_design_specifications(self, magnet_type: str, content: Dict) -> Dict:
        """Generate design specifications for the lead magnet"""
        base_specs = self.leadmagnet_templates.get("design_specifications", {})
        
        # Customize based on type
        type_specific_specs = {
            "checklist": {
                "layout": "checkbox_list_format",
                "typography": "clear_hierarchy_with_checkboxes",
                "spacing": "generous_line_spacing",
                "colors": "high_contrast_for_readability"
            },
            "resource_guide": {
                "layout": "multi_column_directory",
                "typography": "easy_to_scan_headings",
                "spacing": "section_breaks_with_white_space",
                "colors": "professional_blue_and_gray_palette"
            },
            "planner": {
                "layout": "grid_based_calendar_style",
                "typography": "handwriting_friendly_fonts",
                "spacing": "ample_writing_space",
                "colors": "soft_colors_for_daily_use"
            },
            "tip_sheet": {
                "layout": "scannable_bullet_points",
                "typography": "bold_headers_clear_body_text",
                "spacing": "bite_sized_sections",
                "colors": "bright_accents_for_important_info"
            },
            "reference_card": {
                "layout": "compact_information_density",
                "typography": "small_but_readable_fonts",
                "spacing": "minimal_but_functional",
                "colors": "high_contrast_black_and_white"
            }
        }
        
        specs = base_specs.copy()
        specs.update(type_specific_specs.get(magnet_type, {}))
        
        # Add content-specific requirements
        specs["page_count"] = content.get("pages", 5)
        specs["print_format"] = "8.5x11 inches" if magnet_type != "reference_card" else "business_card_size"
        specs["color_mode"] = "CMYK for print, RGB for digital"
        specs["resolution"] = "300 DPI minimum"
        
        return specs
        
    def _create_distribution_strategy(self, magnet_type: str, content: Dict) -> Dict:
        """Create distribution strategy for the lead magnet"""
        base_strategy = self.leadmagnet_templates.get("distribution_strategy", {})
        
        # Customize based on content
        content_specific = {
            "landing_page_headline": f"Get Your Free {content.get('title', 'Caregiver Resource')}",
            "value_proposition": self._generate_value_proposition(magnet_type, content),
            "target_keywords": self._get_relevant_keywords(content),
            "social_media_copy": self._generate_social_copy(content),
            "email_signature_text": f"Download: {content.get('title', 'Free Caregiver Resource')}"
        }
        
        strategy = base_strategy.copy()
        strategy.update(content_specific)
        
        return strategy
        
    def _generate_value_proposition(self, magnet_type: str, content: Dict) -> str:
        """Generate value proposition for the lead magnet"""
        title = content.get("title", "Caregiver Resource")
        
        value_props = {
            "checklist": f"Get organized with our comprehensive {title}. Ensure you're covering all essential caregiving tasks without the overwhelm.",
            "resource_guide": f"Stop searching endlessly for caregiver help. Our {title} puts all the best resources at your fingertips.",
            "planner": f"Take control of your caregiving schedule with our {title}. Stay organized and reduce stress.",
            "tip_sheet": f"Get instant access to proven strategies with our {title}. Quick solutions for common caregiving challenges.",
            "reference_card": f"Keep essential information handy with our {title}. Perfect for emergencies and daily reference."
        }
        
        return value_props.get(magnet_type, f"Get valuable caregiving support with our {title}")
        
    def _generate_analytics_config(self, magnet_type: str, content: Dict) -> Dict:
        """Generate analytics configuration"""
        return {
            "tracking_events": [
                "lead_magnet_downloaded",
                "email_signup_completed",
                "pdf_opened",
                "follow_up_email_clicked"
            ],
            "conversion_goals": [
                {"goal": "download_completion", "value": 1},
                {"goal": "email_subscription", "value": 5},
                {"goal": "follow_up_engagement", "value": 3}
            ],
            "attribution_tracking": {
                "utm_source": "lead_magnet",
                "utm_medium": "pdf_download",
                "utm_campaign": f"{magnet_type}_{content.get('title', '').replace(' ', '_').lower()}"
            },
            "success_metrics": [
                "download_rate",
                "email_open_rate",
                "follow_up_click_rate",
                "conversion_to_paid"
            ]
        }
        
    def _generate_pdf_instructions(self, content: Dict, design_specs: Dict) -> Dict:
        """Generate instructions for PDF creation"""
        return {
            "page_setup": {
                "size": design_specs.get("print_format", "8.5x11 inches"),
                "margins": "0.75 inches all sides",
                "orientation": "portrait",
                "bleed": "0.125 inches if printing professionally"
            },
            "typography": {
                "primary_font": self.brand_config.get("font_primary", "Open Sans"),
                "secondary_font": self.brand_config.get("font_secondary", "Lato"),
                "body_size": "11pt minimum",
                "header_size": "16-24pt",
                "line_spacing": "1.3 for readability"
            },
            "colors": {
                "primary": self.brand_config.get("primary_color", "#2C3E50"),
                "secondary": self.brand_config.get("secondary_color", "#3498DB"),
                "accent": self.brand_config.get("accent_color", "#E74C3C"),
                "text": "#2C2C2C",
                "background": "#FFFFFF"
            },
            "layout_guidelines": [
                "Use consistent margins and spacing",
                "Include page numbers on multi-page documents",
                "Add Kiin Care branding to header/footer",
                "Ensure sufficient white space for readability",
                "Use bullet points and lists for easy scanning"
            ],
            "interactive_elements": self._generate_interactive_instructions(content),
            "printing_notes": [
                "Test print one page first to check formatting",
                "Use high-quality paper for professional appearance",
                "Consider spiral binding for planners",
                "Laminate reference cards for durability"
            ]
        }
        
    def _generate_interactive_instructions(self, content: Dict) -> List[str]:
        """Generate instructions for interactive PDF elements"""
        instructions = []
        
        if content.get("completion_tracking", False):
            instructions.append("Add fillable checkboxes for tracking completion")
            
        if "planner" in content.get("title", "").lower():
            instructions.append("Create fillable date fields and text areas")
            
        if "emergency" in content.get("title", "").lower():
            instructions.append("Include fillable fields for personal information")
            
        instructions.extend([
            "Make all form fields accessible and tab-navigable",
            "Include reset button for digital version",
            "Test fillable fields before finalizing"
        ])
        
        return instructions
        
    def _create_follow_up_sequence(self, magnet_type: str, content: Dict) -> Dict:
        """Create follow-up email sequence for lead magnet"""
        return {
            "sequence_name": f"{magnet_type}_follow_up",
            "total_emails": 3,
            "schedule": "days_1,7,14",
            "emails": [
                {
                    "email_number": 1,
                    "send_delay": "1 day",
                    "subject": f"How to get the most from your {content.get('title', 'resource')}",
                    "goal": "usage_guidance",
                    "content_type": "educational"
                },
                {
                    "email_number": 2, 
                    "send_delay": "7 days",
                    "subject": "Your caregiving journey: what comes next?",
                    "goal": "continued_engagement",
                    "content_type": "supportive"
                },
                {
                    "email_number": 3,
                    "send_delay": "14 days",
                    "subject": "Exclusive resource: advanced caregiving strategies",
                    "goal": "value_add_and_retention",
                    "content_type": "resource_sharing"
                }
            ]
        }
        
    def _estimate_completion_time(self, content: Dict) -> str:
        """Estimate time to complete the lead magnet"""
        magnet_type = content.get("title", "").lower()
        pages = content.get("pages", 5)
        
        if "checklist" in magnet_type:
            items = content.get("total_items", 20)
            return f"{items * 2} minutes to complete"
        elif "planner" in magnet_type:
            return "Ongoing - 10 minutes daily"
        elif "guide" in magnet_type:
            return f"{pages * 5} minutes to read"
        else:
            return f"{pages * 3} minutes to review"
            
    def _get_relevant_keywords(self, content: Dict) -> List[str]:
        """Get relevant SEO keywords for the lead magnet"""
        title = content.get("title", "").lower()
        keywords = []
        
        # Add base caregiver keywords
        base_keywords = self.seo_keywords.get("primary_keywords", {}).get("high_volume", [])
        keywords.extend(base_keywords[:3])
        
        # Add content-specific keywords
        if "dementia" in title:
            keywords.extend(["dementia care", "Alzheimer's support", "memory care"])
        elif "safety" in title:
            keywords.extend(["home safety", "fall prevention", "elder safety"])
        elif "medical" in title:
            keywords.extend(["medical management", "healthcare coordination", "medical advocacy"])
        elif "emergency" in title:
            keywords.extend(["emergency planning", "crisis management", "emergency preparedness"])
            
        return keywords[:8]  # Limit to 8 keywords
        
    def save_lead_magnet(self, lead_magnet: Dict, filename: str = None) -> str:
        """Save lead magnet to files"""
        if not filename:
            name = lead_magnet["metadata"]["name"]
            magnet_type = lead_magnet["metadata"]["type"]
            timestamp = datetime.datetime.now().strftime("%Y%m%d")
            filename = f"{magnet_type}_{name.replace(' ', '_').lower()}_{timestamp}"
            
        # Save content as JSON
        json_path = self.output_dir / f"{filename}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(lead_magnet, f, indent=2, ensure_ascii=False)
            
        # Generate markdown version for easier reading
        markdown_content = self._convert_to_markdown(lead_magnet)
        md_path = self.output_dir / f"{filename}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
            
        return str(json_path)
        
    def _convert_to_markdown(self, lead_magnet: Dict) -> str:
        """Convert lead magnet to markdown for review"""
        md_content = []
        
        metadata = lead_magnet["metadata"]
        content = lead_magnet["content"]
        
        # Header
        md_content.append(f"# {content.get('title', 'Lead Magnet')}")
        md_content.append("")
        md_content.append(f"**Type:** {metadata['type']}")
        md_content.append(f"**Target Audience:** {metadata['target_audience']}")
        md_content.append(f"**Pages:** {metadata['pages']}")
        md_content.append(f"**Completion Time:** {metadata['estimated_completion_time']}")
        md_content.append("")
        
        # Introduction
        if content.get("introduction"):
            md_content.append("## Introduction")
            md_content.append(content["introduction"].strip())
            md_content.append("")
            
        # Content sections based on type
        if metadata["type"] == "checklist":
            md_content.append("## Checklist Sections")
            for section in content.get("sections", []):
                md_content.append(f"### {section['section_title']}")
                md_content.append(f"*Priority: {section['priority_level']} | Time: {section['estimated_time']}*")
                md_content.append("")
                for item in section.get("items", []):
                    md_content.append(f"- [ ] {item['description']}")
                md_content.append("")
                
        elif metadata["type"] == "resource_guide":
            md_content.append("## Resource Sections")
            for section in content.get("sections", []):
                md_content.append(f"### {section['title']}")
                if section.get("resources"):
                    for resource in section["resources"]:
                        md_content.append(f"**{resource['organization']}**")
                        md_content.append(f"- {resource['description']}")
                        md_content.append(f"- Contact: {resource['contact_info']}")
                        md_content.append(f"- Website: {resource['website']}")
                        md_content.append("")
                        
        # Distribution strategy
        dist = lead_magnet.get("distribution_strategy", {})
        if dist:
            md_content.append("## Distribution Strategy")
            md_content.append(f"**Value Proposition:** {dist.get('value_proposition', 'N/A')}")
            md_content.append("")
            
        # Design specifications
        design = lead_magnet.get("design_specifications", {})
        if design:
            md_content.append("## Design Specifications")
            md_content.append(f"**Format:** {design.get('print_format', 'Standard')}")
            md_content.append(f"**Pages:** {design.get('page_count', 'Multiple')}")
            md_content.append("")
            
        return "\n".join(md_content)

def main():
    parser = argparse.ArgumentParser(description="Generate lead magnets for Kiin Content Factory")
    parser.add_argument("--type", required=True,
                       choices=["checklist", "resource_guide", "planner", "tip_sheet", "reference_card"],
                       help="Type of lead magnet")
    parser.add_argument("--topic", help="Specific topic or template name")
    parser.add_argument("--audience", default="family caregivers", help="Target audience")
    parser.add_argument("--output", help="Output filename prefix")
    parser.add_argument("--custom-config", help="JSON file with custom configuration")
    
    args = parser.parse_args()
    
    generator = LeadMagnetGenerator()
    
    # Load custom config if provided
    custom_config = None
    if args.custom_config:
        with open(args.custom_config, 'r') as f:
            custom_config = json.load(f)
    
    # Generate lead magnet
    lead_magnet = generator.generate_lead_magnet(
        magnet_type=args.type,
        topic=args.topic,
        target_audience=args.audience,
        custom_config=custom_config
    )
    
    # Save lead magnet
    filepath = generator.save_lead_magnet(lead_magnet, args.output)
    
    print(f"Lead magnet generated successfully!")
    print(f"Name: {lead_magnet['metadata']['name']}")
    print(f"Type: {args.type}")
    print(f"Target Audience: {args.audience}")
    print(f"Pages: {lead_magnet['metadata']['pages']}")
    print(f"Completion Time: {lead_magnet['metadata']['estimated_completion_time']}")
    print(f"Saved to: {filepath}")
    
    # Print distribution info
    dist = lead_magnet.get("distribution_strategy", {})
    if dist.get("value_proposition"):
        print(f"\nValue Proposition: {dist['value_proposition']}")

if __name__ == "__main__":
    main()