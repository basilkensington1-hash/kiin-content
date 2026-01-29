#!/usr/bin/env python3
"""
Kiin Content Factory - Funnel Content Mapper

Maps content to marketing funnel stages (awareness, consideration, decision, retention)
and optimizes content journey for Kiin app conversion.
"""

import json
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
import sqlite3
from collections import defaultdict

class FunnelStage(Enum):
    AWARENESS = "awareness"
    CONSIDERATION = "consideration" 
    DECISION = "decision"
    RETENTION = "retention"

class ContentIntent(Enum):
    EDUCATIONAL = "educational"
    INSPIRATIONAL = "inspirational"
    PRACTICAL = "practical"
    PROMOTIONAL = "promotional"
    COMMUNITY = "community"

class ConversionGoal(Enum):
    APP_DOWNLOAD = "app_download"
    TRIAL_SIGNUP = "trial_signup"
    FEATURE_ADOPTION = "feature_adoption"
    COMMUNITY_JOIN = "community_join"
    CONTENT_ENGAGEMENT = "content_engagement"

@dataclass
class FunnelContent:
    """Content piece mapped to funnel stage"""
    title: str
    content_type: str
    funnel_stage: FunnelStage
    content_intent: ContentIntent
    target_audience: str
    pain_points_addressed: List[str]
    conversion_goal: ConversionGoal
    kiin_features_highlighted: List[str]
    content_hooks: List[str]
    cta_primary: str
    cta_secondary: str
    success_metrics: List[str]
    content_outline: List[str]
    related_content: List[str] = None
    
    def __post_init__(self):
        if self.related_content is None:
            self.related_content = []

@dataclass
class ContentJourney:
    """Complete content journey mapping"""
    journey_name: str
    target_persona: str
    entry_point: str
    journey_stages: List[FunnelContent]
    conversion_path: List[str]
    expected_timeline: str
    success_metrics: Dict[str, float]

class FunnelContentMapper:
    """Main funnel content mapping tool"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.db_path = self.data_dir / "funnel_mapping.db"
        self.init_database()
        
        # Load Kiin-specific configuration
        self.load_kiin_config()
        
        # Content mapping rules
        self.funnel_rules = self.load_funnel_rules()
        
        # Generated content mappings
        self.funnel_content: Dict[FunnelStage, List[FunnelContent]] = defaultdict(list)
        self.content_journeys: List[ContentJourney] = []
        
    def init_database(self):
        """Initialize database for funnel mapping"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS funnel_content (
                id INTEGER PRIMARY KEY,
                title TEXT,
                content_type TEXT,
                funnel_stage TEXT,
                content_intent TEXT,
                target_audience TEXT,
                conversion_goal TEXT,
                kiin_features TEXT,
                content_hooks TEXT,
                cta_primary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content_journeys (
                id INTEGER PRIMARY KEY,
                journey_name TEXT,
                target_persona TEXT,
                entry_point TEXT,
                conversion_path TEXT,
                expected_timeline TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_kiin_config(self):
        """Load Kiin app-specific configuration"""
        self.kiin_config = {
            'app_features': [
                'Care coordination',
                'Family communication',
                'Care plan management', 
                'Resource directory',
                'Caregiver support community',
                'Emergency contacts',
                'Medical information storage',
                'Task management',
                'Appointment scheduling',
                'Medication tracking'
            ],
            'target_personas': {
                'sandwich_generation': {
                    'description': 'Adults caring for aging parents while raising children',
                    'age': '35-55',
                    'pain_points': [
                        'Time management',
                        'Coordination between family members',
                        'Balancing work and care',
                        'Financial stress',
                        'Guilt and overwhelm'
                    ],
                    'motivations': [
                        'Keep parents independent',
                        'Family harmony',
                        'Peace of mind',
                        'Better coordination',
                        'Professional support'
                    ]
                },
                'primary_caregiver': {
                    'description': 'Main caregiver for aging parent or spouse',
                    'age': '45-75',
                    'pain_points': [
                        'Caregiver burnout',
                        'Social isolation', 
                        'Health decline',
                        'Lack of respite',
                        'Decision overwhelm'
                    ],
                    'motivations': [
                        'Quality care for loved one',
                        'Support and resources',
                        'Connection with others',
                        'Self-care',
                        'Expert guidance'
                    ]
                },
                'long_distance_caregiver': {
                    'description': 'Adult children living far from aging parents',
                    'age': '40-65',
                    'pain_points': [
                        'Remote coordination',
                        'Finding local resources',
                        'Communication gaps',
                        'Crisis management',
                        'Guilt about distance'
                    ],
                    'motivations': [
                        'Remote monitoring',
                        'Local resource connections',
                        'Family coordination',
                        'Emergency preparedness',
                        'Peace of mind'
                    ]
                }
            },
            'value_propositions': [
                'Simplify family caregiving coordination',
                'Connect with trusted local resources',
                'Reduce caregiver stress and overwhelm',
                'Improve care quality and safety',
                'Build supportive caregiver community'
            ]
        }
    
    def load_funnel_rules(self) -> Dict:
        """Load funnel mapping rules"""
        return {
            'awareness': {
                'content_goals': [
                    'Educate about caregiving challenges',
                    'Build trust and credibility',
                    'Create emotional connection',
                    'Identify pain points',
                    'Establish thought leadership'
                ],
                'content_types': [
                    'Educational blog posts',
                    'Social media content',
                    'Infographics',
                    'Video content',
                    'Checklists and guides'
                ],
                'kiin_mentions': 'Minimal - focus on education',
                'cta_focus': 'Content engagement and email signup'
            },
            'consideration': {
                'content_goals': [
                    'Present solutions to problems',
                    'Compare options and approaches',
                    'Demonstrate expertise',
                    'Build confidence in solutions',
                    'Address objections'
                ],
                'content_types': [
                    'Solution-focused guides',
                    'Comparison content',
                    'Case studies',
                    'Expert interviews',
                    'Webinars and demos'
                ],
                'kiin_mentions': 'Moderate - position as solution',
                'cta_focus': 'Learn more about Kiin features'
            },
            'decision': {
                'content_goals': [
                    'Demonstrate product value',
                    'Remove barriers to adoption',
                    'Show ease of implementation',
                    'Provide social proof',
                    'Create urgency'
                ],
                'content_types': [
                    'Product tutorials',
                    'Success stories',
                    'Feature demonstrations',
                    'Getting started guides',
                    'Testimonials'
                ],
                'kiin_mentions': 'Heavy - product focused',
                'cta_focus': 'Try Kiin free or download app'
            },
            'retention': {
                'content_goals': [
                    'Maximize feature adoption',
                    'Build community engagement',
                    'Encourage referrals',
                    'Prevent churn',
                    'Drive expansion'
                ],
                'content_types': [
                    'Feature spotlights',
                    'Community content',
                    'Advanced tutorials',
                    'User stories',
                    'Tips and best practices'
                ],
                'kiin_mentions': 'Heavy - advanced usage',
                'cta_focus': 'Explore features or invite family'
            }
        }
    
    def generate_awareness_content(self) -> List[FunnelContent]:
        """Generate awareness stage content"""
        awareness_content = [
            FunnelContent(
                title="10 Warning Signs Your Aging Parent Needs Help",
                content_type="blog_post",
                funnel_stage=FunnelStage.AWARENESS,
                content_intent=ContentIntent.EDUCATIONAL,
                target_audience="sandwich_generation",
                pain_points_addressed=[
                    "Uncertainty about parent's safety",
                    "Not knowing when to intervene",
                    "Family disagreements about care"
                ],
                conversion_goal=ConversionGoal.CONTENT_ENGAGEMENT,
                kiin_features_highlighted=[],
                content_hooks=[
                    "Many families miss early warning signs",
                    "Recognizing these signs can prevent crises",
                    "Expert-backed checklist included"
                ],
                cta_primary="Download our complete care assessment checklist",
                cta_secondary="Share this with other family members",
                success_metrics=["page_views", "time_on_page", "email_signups", "social_shares"],
                content_outline=[
                    "Introduction: The difficulty of recognizing decline",
                    "Physical warning signs (5 signs)",
                    "Cognitive warning signs (3 signs)", 
                    "Safety warning signs (2 signs)",
                    "What to do when you notice these signs",
                    "How to start the conversation with family",
                    "Resources for professional assessment",
                    "CTA: Download complete assessment guide"
                ]
            ),
            
            FunnelContent(
                title="The Hidden Cost of Family Caregiving: What Nobody Tells You",
                content_type="blog_post",
                funnel_stage=FunnelStage.AWARENESS,
                content_intent=ContentIntent.EDUCATIONAL,
                target_audience="sandwich_generation",
                pain_points_addressed=[
                    "Underestimating caregiving costs",
                    "Financial planning for care",
                    "Work-life balance challenges"
                ],
                conversion_goal=ConversionGoal.CONTENT_ENGAGEMENT,
                kiin_features_highlighted=[],
                content_hooks=[
                    "The average family caregiver spends $1,986 annually",
                    "Hidden costs beyond money",
                    "How to protect your financial future"
                ],
                cta_primary="Get our free caregiving cost calculator",
                cta_secondary="Join our newsletter for financial tips",
                success_metrics=["page_views", "calculator_downloads", "email_signups"],
                content_outline=[
                    "The true scope of caregiving costs",
                    "Direct costs: medical, equipment, modifications",
                    "Indirect costs: lost income, benefits, career impact",
                    "Emotional costs: stress, relationships, health",
                    "Financial planning strategies",
                    "How to involve family in cost discussions",
                    "When to consider professional help",
                    "CTA: Download cost planning tools"
                ]
            ),
            
            FunnelContent(
                title="Why 73% of Family Caregivers Experience Burnout (And How to Prevent It)",
                content_type="video",
                funnel_stage=FunnelStage.AWARENESS,
                content_intent=ContentIntent.EDUCATIONAL,
                target_audience="primary_caregiver",
                pain_points_addressed=[
                    "Caregiver burnout",
                    "Feeling overwhelmed",
                    "Lack of support"
                ],
                conversion_goal=ConversionGoal.CONTENT_ENGAGEMENT,
                kiin_features_highlighted=[],
                content_hooks=[
                    "Shocking burnout statistics",
                    "Real caregiver stories",
                    "Actionable prevention strategies"
                ],
                cta_primary="Join our caregiver support community",
                cta_secondary="Download burnout prevention guide",
                success_metrics=["video_views", "watch_time", "community_joins"],
                content_outline=[
                    "Opening: Burnout statistics and real impact",
                    "What caregiver burnout looks like",
                    "Why it happens: common causes",
                    "Early warning signs to watch for",
                    "5 proven prevention strategies",
                    "Building your support network",
                    "When to ask for help",
                    "CTA: Connect with other caregivers"
                ]
            ),
            
            FunnelContent(
                title="Long-Distance Caregiving: A Complete Guide for Adult Children",
                content_type="guide",
                funnel_stage=FunnelStage.AWARENESS,
                content_intent=ContentIntent.EDUCATIONAL,
                target_audience="long_distance_caregiver",
                pain_points_addressed=[
                    "Managing care from a distance",
                    "Finding local resources",
                    "Coordinating with siblings"
                ],
                conversion_goal=ConversionGoal.CONTENT_ENGAGEMENT,
                kiin_features_highlighted=[],
                content_hooks=[
                    "7 million Americans provide long-distance care",
                    "Complete roadmap for remote caregiving",
                    "Expert strategies that actually work"
                ],
                cta_primary="Download the complete long-distance care toolkit",
                cta_secondary="Schedule a free consultation",
                success_metrics=["guide_downloads", "consultation_requests", "email_signups"],
                content_outline=[
                    "Understanding long-distance caregiving challenges",
                    "Setting up remote monitoring systems",
                    "Building a local support network",
                    "Coordinating with family members",
                    "Technology tools for remote care",
                    "Emergency planning from afar",
                    "Legal and financial considerations",
                    "CTA: Get complete toolkit"
                ]
            )
        ]
        
        return awareness_content
    
    def generate_consideration_content(self) -> List[FunnelContent]:
        """Generate consideration stage content"""
        consideration_content = [
            FunnelContent(
                title="How to Create a Family Care Plan That Actually Works",
                content_type="guide",
                funnel_stage=FunnelStage.CONSIDERATION,
                content_intent=ContentIntent.PRACTICAL,
                target_audience="sandwich_generation",
                pain_points_addressed=[
                    "Lack of coordination between family members",
                    "Unclear roles and responsibilities",
                    "Communication breakdowns"
                ],
                conversion_goal=ConversionGoal.TRIAL_SIGNUP,
                kiin_features_highlighted=[
                    "Care plan management",
                    "Family communication",
                    "Task coordination"
                ],
                content_hooks=[
                    "Step-by-step care plan template",
                    "Avoid common family conflicts",
                    "Technology tools that help"
                ],
                cta_primary="Try Kiin's care planning tools free for 30 days",
                cta_secondary="Download our care plan template",
                success_metrics=["guide_views", "template_downloads", "free_trial_signups"],
                content_outline=[
                    "Why family care plans fail",
                    "The 5 essential elements of effective care plans",
                    "How to involve all family members",
                    "Setting clear roles and responsibilities",
                    "Communication strategies that work",
                    "Using technology to coordinate care",
                    "Regular plan review and updates",
                    "CTA: Start your family's care plan with Kiin"
                ]
            ),
            
            FunnelContent(
                title="Technology vs. Traditional Methods: What Really Works for Caregiving",
                content_type="comparison_post",
                funnel_stage=FunnelStage.CONSIDERATION,
                content_intent=ContentIntent.EDUCATIONAL,
                target_audience="long_distance_caregiver",
                pain_points_addressed=[
                    "Uncertainty about technology adoption",
                    "Fear of complexity",
                    "Resistance from older family members"
                ],
                conversion_goal=ConversionGoal.APP_DOWNLOAD,
                kiin_features_highlighted=[
                    "Simple interface design",
                    "Family-friendly features",
                    "Emergency coordination"
                ],
                content_hooks=[
                    "Honest comparison of approaches",
                    "Real family success stories",
                    "When to use each method"
                ],
                cta_primary="See how Kiin simplifies family caregiving",
                cta_secondary="Read more success stories",
                success_metrics=["page_views", "app_downloads", "feature_demo_requests"],
                content_outline=[
                    "Traditional caregiving coordination methods",
                    "Pros and cons of phone calls and visits",
                    "How technology can enhance (not replace) care",
                    "Comparison: Manual vs. digital coordination",
                    "Real family case studies",
                    "When technology makes the biggest difference",
                    "Choosing the right tools for your family",
                    "CTA: Try technology that actually works"
                ]
            ),
            
            FunnelContent(
                title="5 Ways Successful Families Coordinate Care (Without the Drama)",
                content_type="case_study",
                funnel_stage=FunnelStage.CONSIDERATION,
                content_intent=ContentIntent.INSPIRATIONAL,
                target_audience="primary_caregiver",
                pain_points_addressed=[
                    "Family conflicts over care",
                    "Unequal sharing of responsibilities",
                    "Communication problems"
                ],
                conversion_goal=ConversionGoal.COMMUNITY_JOIN,
                kiin_features_highlighted=[
                    "Family communication tools",
                    "Task sharing features",
                    "Conflict resolution resources"
                ],
                content_hooks=[
                    "Real families, real solutions",
                    "Proven strategies that reduce conflict",
                    "How to get everyone involved"
                ],
                cta_primary="Join our family caregiver community",
                cta_secondary="Get our family coordination guide",
                success_metrics=["case_study_views", "community_joins", "guide_downloads"],
                content_outline=[
                    "Why family coordination is so challenging",
                    "Case study 1: The Johnson family's transformation",
                    "Case study 2: Long-distance coordination success",
                    "Case study 3: Sibling conflict resolution",
                    "Common patterns in successful families",
                    "Tools and strategies that made the difference", 
                    "How to implement these approaches",
                    "CTA: Connect with other successful families"
                ]
            )
        ]
        
        return consideration_content
    
    def generate_decision_content(self) -> List[FunnelContent]:
        """Generate decision stage content"""
        decision_content = [
            FunnelContent(
                title="Getting Started with Kiin: Your First 30 Days",
                content_type="tutorial",
                funnel_stage=FunnelStage.DECISION,
                content_intent=ContentIntent.PRACTICAL,
                target_audience="all_personas",
                pain_points_addressed=[
                    "Fear of technology complexity",
                    "Uncertainty about implementation",
                    "Need for quick wins"
                ],
                conversion_goal=ConversionGoal.APP_DOWNLOAD,
                kiin_features_highlighted=[
                    "Easy setup process",
                    "Family invitation system",
                    "Care plan templates"
                ],
                content_hooks=[
                    "Get results in your first week",
                    "Step-by-step setup guide",
                    "No tech expertise required"
                ],
                cta_primary="Download Kiin and start your free trial",
                cta_secondary="Watch the setup video",
                success_metrics=["tutorial_views", "app_downloads", "setup_completions"],
                content_outline=[
                    "Before you start: what you'll need",
                    "Week 1: Download and basic setup",
                    "Week 2: Invite family members",
                    "Week 3: Create your first care plan",
                    "Week 4: Explore advanced features",
                    "Quick wins you'll see immediately",
                    "Common questions and troubleshooting",
                    "CTA: Start your Kiin journey today"
                ]
            ),
            
            FunnelContent(
                title="Why the Martinez Family Chose Kiin (And Never Looked Back)",
                content_type="testimonial",
                funnel_stage=FunnelStage.DECISION,
                content_intent=ContentIntent.INSPIRATIONAL,
                target_audience="sandwich_generation",
                pain_points_addressed=[
                    "Proof that solution works",
                    "Overcoming family resistance",
                    "Value justification"
                ],
                conversion_goal=ConversionGoal.APP_DOWNLOAD,
                kiin_features_highlighted=[
                    "Family coordination",
                    "Emergency management",
                    "Local resource directory"
                ],
                content_hooks=[
                    "Real family transformation story",
                    "From chaos to coordination",
                    "Measurable improvements"
                ],
                cta_primary="Start your family's transformation with Kiin",
                cta_secondary="Read more success stories",
                success_metrics=["story_views", "app_downloads", "free_trial_starts"],
                content_outline=[
                    "The Martinez family's caregiving challenges",
                    "Why they decided to try Kiin",
                    "The setup process and early wins",
                    "How each family member uses Kiin",
                    "Specific problems Kiin solved",
                    "Measurable improvements after 6 months",
                    "Their advice for other families",
                    "CTA: Create your own success story"
                ]
            ),
            
            FunnelContent(
                title="Kiin vs. Other Solutions: An Honest Comparison",
                content_type="comparison",
                funnel_stage=FunnelStage.DECISION,
                content_intent=ContentIntent.EDUCATIONAL,
                target_audience="long_distance_caregiver", 
                pain_points_addressed=[
                    "Choice overwhelm",
                    "Feature comparison needs",
                    "Value for money concerns"
                ],
                conversion_goal=ConversionGoal.TRIAL_SIGNUP,
                kiin_features_highlighted=[
                    "All-in-one solution",
                    "Family-focused design",
                    "Local resource integration"
                ],
                content_hooks=[
                    "Unbiased feature comparison",
                    "Real pros and cons",
                    "Which solution fits your family"
                ],
                cta_primary="Try Kiin risk-free for 30 days",
                cta_secondary="Download detailed comparison chart",
                success_metrics=["comparison_views", "chart_downloads", "trial_signups"],
                content_outline=[
                    "How we evaluated each solution",
                    "Feature-by-feature comparison",
                    "Pricing and value analysis",
                    "Ease of use comparison",
                    "Family adoption rates",
                    "Customer support quality",
                    "When Kiin is the best choice",
                    "CTA: Experience the Kiin difference"
                ]
            )
        ]
        
        return decision_content
    
    def generate_retention_content(self) -> List[FunnelContent]:
        """Generate retention stage content"""
        retention_content = [
            FunnelContent(
                title="Advanced Kiin Tips: Getting More from Your Care Coordination",
                content_type="tutorial",
                funnel_stage=FunnelStage.RETENTION,
                content_intent=ContentIntent.PRACTICAL,
                target_audience="existing_users",
                pain_points_addressed=[
                    "Underutilizing features",
                    "Workflow optimization needs",
                    "Advanced coordination challenges"
                ],
                conversion_goal=ConversionGoal.FEATURE_ADOPTION,
                kiin_features_highlighted=[
                    "Advanced scheduling",
                    "Custom notifications",
                    "Report generation"
                ],
                content_hooks=[
                    "Hidden features most families miss",
                    "Power user strategies",
                    "Maximize your Kiin investment"
                ],
                cta_primary="Explore these advanced features in Kiin",
                cta_secondary="Join our power users community",
                success_metrics=["tutorial_engagement", "feature_adoption", "community_participation"],
                content_outline=[
                    "Taking your coordination to the next level",
                    "Advanced scheduling and calendar features",
                    "Custom notification strategies",
                    "Generating useful reports for healthcare providers",
                    "Integrating with other healthcare tools",
                    "Power user workflows and shortcuts",
                    "Getting family members more engaged",
                    "CTA: Master these advanced features"
                ]
            )
        ]
        
        return retention_content
    
    def create_content_journeys(self) -> List[ContentJourney]:
        """Create complete content journeys for each persona"""
        journeys = [
            ContentJourney(
                journey_name="Sandwich Generation Discovery to Adoption",
                target_persona="sandwich_generation",
                entry_point="Warning signs blog post",
                journey_stages=[
                    # Awareness
                    "10 Warning Signs Your Aging Parent Needs Help",
                    "The Hidden Cost of Family Caregiving",
                    # Consideration  
                    "How to Create a Family Care Plan That Actually Works",
                    "5 Ways Successful Families Coordinate Care",
                    # Decision
                    "Getting Started with Kiin: Your First 30 Days",
                    "Why the Martinez Family Chose Kiin"
                ],
                conversion_path=[
                    "Blog post → Email signup → Care plan guide → Free trial → App download"
                ],
                expected_timeline="4-8 weeks",
                success_metrics={
                    "email_conversion": 15.0,
                    "guide_download": 35.0, 
                    "trial_signup": 8.0,
                    "app_download": 65.0
                }
            ),
            
            ContentJourney(
                journey_name="Primary Caregiver Support to Community",
                target_persona="primary_caregiver",
                entry_point="Burnout prevention video",
                journey_stages=[
                    # Awareness
                    "Why 73% of Family Caregivers Experience Burnout",
                    # Consideration
                    "5 Ways Successful Families Coordinate Care",
                    # Decision
                    "Getting Started with Kiin: Your First 30 Days",
                    # Retention
                    "Advanced Kiin Tips"
                ],
                conversion_path=[
                    "Video → Community join → Care coordination guide → App trial → Feature adoption"
                ],
                expected_timeline="6-12 weeks",
                success_metrics={
                    "video_engagement": 25.0,
                    "community_join": 12.0,
                    "app_trial": 45.0,
                    "feature_adoption": 78.0
                }
            ),
            
            ContentJourney(
                journey_name="Long-Distance Caregiver Solution Journey",
                target_persona="long_distance_caregiver",
                entry_point="Long-distance caregiving guide",
                journey_stages=[
                    # Awareness
                    "Long-Distance Caregiving: A Complete Guide",
                    # Consideration
                    "Technology vs. Traditional Methods",
                    # Decision
                    "Kiin vs. Other Solutions: An Honest Comparison",
                    "Getting Started with Kiin: Your First 30 Days"
                ],
                conversion_path=[
                    "Guide → Comparison content → Solution trial → App adoption"
                ],
                expected_timeline="3-6 weeks",
                success_metrics={
                    "guide_download": 40.0,
                    "comparison_engagement": 60.0,
                    "trial_conversion": 22.0,
                    "app_adoption": 75.0
                }
            )
        ]
        
        self.content_journeys = journeys
        return journeys
    
    def generate_all_funnel_content(self):
        """Generate all funnel content"""
        awareness = self.generate_awareness_content()
        consideration = self.generate_consideration_content()
        decision = self.generate_decision_content()
        retention = self.generate_retention_content()
        
        self.funnel_content[FunnelStage.AWARENESS] = awareness
        self.funnel_content[FunnelStage.CONSIDERATION] = consideration
        self.funnel_content[FunnelStage.DECISION] = decision
        self.funnel_content[FunnelStage.RETENTION] = retention
        
        return self.funnel_content
    
    def export_funnel_mapping(self, filename: str = "funnel_content_mapping.json") -> Path:
        """Export complete funnel mapping"""
        
        # Generate all content if not already done
        if not self.funnel_content:
            self.generate_all_funnel_content()
        
        # Create content journeys
        journeys = self.create_content_journeys()
        
        # Prepare export data
        export_data = {
            'funnel_content': {
                stage.value: [
                    {
                        'title': content.title,
                        'content_type': content.content_type,
                        'funnel_stage': content.funnel_stage.value,
                        'content_intent': content.content_intent.value,
                        'target_audience': content.target_audience,
                        'pain_points_addressed': content.pain_points_addressed,
                        'conversion_goal': content.conversion_goal.value,
                        'kiin_features_highlighted': content.kiin_features_highlighted,
                        'content_hooks': content.content_hooks,
                        'cta_primary': content.cta_primary,
                        'cta_secondary': content.cta_secondary,
                        'success_metrics': content.success_metrics,
                        'content_outline': content.content_outline
                    }
                    for content in contents
                ]
                for stage, contents in self.funnel_content.items()
            },
            'content_journeys': [
                {
                    'journey_name': journey.journey_name,
                    'target_persona': journey.target_persona,
                    'entry_point': journey.entry_point,
                    'journey_stages': journey.journey_stages,
                    'conversion_path': journey.conversion_path,
                    'expected_timeline': journey.expected_timeline,
                    'success_metrics': journey.success_metrics
                }
                for journey in journeys
            ],
            'kiin_configuration': self.kiin_config,
            'funnel_strategy': {
                'awareness_focus': 'Education and problem identification',
                'consideration_focus': 'Solution presentation and comparison',
                'decision_focus': 'Product demonstration and social proof',
                'retention_focus': 'Feature adoption and community building'
            },
            'conversion_optimization': {
                'awareness_to_consideration': {
                    'tactics': ['Email capture', 'Content upgrades', 'Resource downloads'],
                    'target_rate': '15-25%'
                },
                'consideration_to_decision': {
                    'tactics': ['Free trials', 'Product demos', 'Comparison content'],
                    'target_rate': '8-15%'
                },
                'decision_to_customer': {
                    'tactics': ['Easy onboarding', 'Quick wins', 'Support'],
                    'target_rate': '60-80%'
                },
                'retention_optimization': {
                    'tactics': ['Feature education', 'Community engagement', 'Success tracking'],
                    'target_rate': '85-95%'
                }
            },
            'content_performance_metrics': {
                'awareness': ['page_views', 'time_on_page', 'email_signups', 'social_shares'],
                'consideration': ['guide_downloads', 'video_engagement', 'trial_requests'],
                'decision': ['app_downloads', 'trial_starts', 'demo_requests'],
                'retention': ['feature_adoption', 'community_participation', 'referrals']
            }
        }
        
        output_path = self.data_dir / filename
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return output_path

if __name__ == "__main__":
    mapper = FunnelContentMapper()
    
    # Generate funnel mapping
    funnel_content = mapper.generate_all_funnel_content()
    
    # Export mapping
    output_path = mapper.export_funnel_mapping()
    print(f"Funnel content mapping exported to: {output_path}")
    
    # Print summary
    total_content = sum(len(contents) for contents in funnel_content.values())
    print(f"\nGenerated {total_content} pieces of funnel-optimized content:")
    
    for stage, contents in funnel_content.items():
        print(f"- {stage.value.title()}: {len(contents)} pieces")
    
    print(f"\nCreated {len(mapper.content_journeys)} complete content journeys")