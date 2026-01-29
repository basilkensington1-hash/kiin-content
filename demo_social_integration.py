#!/usr/bin/env python3
"""
Kiin Content Factory - Social Media Integration Demo

This demo script shows how to use the social media integration system.
Run this to test the system with your content and credentials.
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from social.posting_manager import PostingManager
from social.hashtag_optimizer import HashtagOptimizer
from social.caption_generator import SocialCaptionGenerator
from social.timing_optimizer import TimingOptimizer
from social.repurpose_engine import RepurposeEngine
from social.base_adapter import VideoContent

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def demo_setup():
    """Setup demo environment"""
    print("🚀 Kiin Content Factory - Social Media Integration Demo")
    print("=" * 60)
    
    # Create necessary directories
    for dir_name in ['data', 'temp', 'logs']:
        os.makedirs(dir_name, exist_ok=True)
    
    print("✅ Created necessary directories")
    
    # Check if config files exist
    config_files = [
        'config/social_credentials.json',
        'config/hashtags.json',
        'config/posting_schedule.json',
        'config/platform_specs.json'
    ]
    
    missing_configs = []
    for config_file in config_files:
        if not os.path.exists(config_file):
            missing_configs.append(config_file)
    
    if missing_configs:
        print(f"⚠️  Missing config files: {missing_configs}")
        print("📝 Please ensure all config files are properly set up")
        return False
    
    print("✅ All config files found")
    return True

def demo_hashtag_optimization():
    """Demo hashtag optimization"""
    print("\n📊 HASHTAG OPTIMIZATION DEMO")
    print("-" * 40)
    
    try:
        optimizer = HashtagOptimizer()
        
        # Test content
        content_text = "Dealing with caregiver stress and burnout while caring for elderly parents"
        
        print(f"Content: '{content_text}'")
        print()
        
        # Test different platforms
        for platform in ['instagram', 'tiktok', 'youtube', 'linkedin']:
            print(f"📱 {platform.upper()}:")
            hashtags = optimizer.optimize_hashtags(content_text, platform)
            print(f"   Hashtags: {hashtags[:5]}...")  # Show first 5
            print(f"   Count: {len(hashtags)}")
        
        print("\n✅ Hashtag optimization demo completed")
        
    except Exception as e:
        print(f"❌ Hashtag optimization error: {e}")

def demo_caption_generation():
    """Demo caption generation"""
    print("\n✍️  CAPTION GENERATION DEMO")
    print("-" * 40)
    
    try:
        generator = SocialCaptionGenerator()
        
        content_data = {
            "title": "5 Self-Care Tips for Overwhelmed Caregivers",
            "description": "Quick practical tips to help you recharge and avoid burnout while caring for loved ones",
            "type": "tips"
        }
        
        print(f"Content: {content_data['title']}")
        print()
        
        # Generate captions for different platforms
        for platform in ['instagram', 'tiktok', 'linkedin']:
            print(f"📱 {platform.upper()}:")
            caption = generator.generate_caption(content_data, platform)
            # Show first 100 characters
            preview = caption[:100] + "..." if len(caption) > 100 else caption
            print(f"   '{preview}'")
            print(f"   Length: {len(caption)} characters")
            print()
        
        print("✅ Caption generation demo completed")
        
    except Exception as e:
        print(f"❌ Caption generation error: {e}")

def demo_timing_optimization():
    """Demo timing optimization"""
    print("\n⏰ TIMING OPTIMIZATION DEMO")
    print("-" * 40)
    
    try:
        optimizer = TimingOptimizer()
        
        # Get optimal times for different platforms
        for platform in ['instagram', 'tiktok', 'youtube']:
            optimal_time = optimizer.get_optimal_posting_time(platform)
            print(f"📱 {platform.upper()}: {optimal_time.strftime('%A, %B %d at %I:%M %p %Z')}")
        
        print()
        
        # Bulk scheduling demo
        schedule = optimizer.schedule_bulk_posting(
            platforms=['instagram', 'tiktok', 'youtube'],
            content_count=3
        )
        
        print("📅 SAMPLE POSTING SCHEDULE:")
        for i, item in enumerate(schedule[:6]):  # Show first 6
            time_str = item['scheduled_time'].strftime('%m/%d %I:%M %p')
            print(f"   {i+1}. {item['platform']} - {time_str}")
        
        print(f"\n   Total scheduled posts: {len(schedule)}")
        print("✅ Timing optimization demo completed")
        
    except Exception as e:
        print(f"❌ Timing optimization error: {e}")

def demo_video_repurposing():
    """Demo video repurposing (without actual video file)"""
    print("\n🎬 VIDEO REPURPOSING DEMO")
    print("-" * 40)
    
    try:
        engine = RepurposeEngine()
        
        # Show platform recommendations without actual file
        print("📊 PLATFORM COMPATIBILITY ANALYSIS:")
        
        # Simulate video specs
        simulated_video_specs = {
            'duration': 25,  # seconds
            'width': 1920,
            'height': 1080,
            'aspect_ratio': 1920/1080
        }
        
        print(f"Video specs: {simulated_video_specs['width']}x{simulated_video_specs['height']}, {simulated_video_specs['duration']}s")
        print()
        
        # Platform compatibility analysis
        platforms = ['instagram', 'tiktok', 'youtube', 'twitter', 'linkedin']
        
        for platform in platforms:
            spec = engine.video_specs.get(platform, {})
            if spec:
                duration_ok = simulated_video_specs['duration'] <= spec.get('max_duration', 60)
                aspect_ratios = spec.get('aspect_ratios', [])
                
                status = "✅ Compatible" if duration_ok else "⚠️  Needs trimming"
                print(f"📱 {platform.upper()}: {status}")
                print(f"   Max duration: {spec.get('max_duration')}s")
                print(f"   Supported ratios: {aspect_ratios}")
                print()
        
        print("✅ Video repurposing analysis completed")
        
    except Exception as e:
        print(f"❌ Video repurposing error: {e}")

def demo_posting_manager():
    """Demo posting manager (simulation mode)"""
    print("\n🎯 POSTING MANAGER DEMO")
    print("-" * 40)
    
    try:
        manager = PostingManager()
        
        # Check available adapters
        available_platforms = list(manager.adapters.keys())
        print(f"🔌 Available platforms: {available_platforms}")
        
        if not available_platforms:
            print("ℹ️  No platforms enabled. This is normal for demo mode.")
            print("   To enable platforms, update config/social_credentials.json")
        
        # Show queue status
        status = manager.get_queue_status()
        print(f"📋 Queue status: {status}")
        
        # Demo content creation
        print("\n📝 CREATING DEMO CONTENT:")
        demo_content = VideoContent(
            file_path="demo_video.mp4",  # This doesn't exist, just for demo
            title="Self-Care Sunday: 3 Quick Tips for Caregivers",
            description="Take care of yourself so you can take care of others",
            hashtags=["caregiver", "selfcare", "sunday", "tips", "wellness"]
        )
        
        print(f"   Title: {demo_content.title}")
        print(f"   Hashtags: {demo_content.hashtags}")
        
        print("\n✅ Posting manager demo completed")
        
    except Exception as e:
        print(f"❌ Posting manager error: {e}")

def demo_full_workflow():
    """Demo complete workflow"""
    print("\n🔄 COMPLETE WORKFLOW DEMO")
    print("-" * 40)
    
    try:
        # Initialize all components
        hashtag_optimizer = HashtagOptimizer()
        caption_generator = SocialCaptionGenerator()
        timing_optimizer = TimingOptimizer()
        posting_manager = PostingManager()
        
        # Content data
        content_data = {
            "title": "Caregiver Burnout: You're Not Alone",
            "description": "Feeling overwhelmed is normal. Here's how to cope.",
            "type": "validation"
        }
        
        platforms = ['instagram', 'tiktok', 'youtube']
        print(f"🎯 Target platforms: {platforms}")
        print()
        
        # Step 1: Optimize hashtags for each platform
        print("Step 1: Generating optimized hashtags...")
        platform_hashtags = {}
        for platform in platforms:
            hashtags = hashtag_optimizer.optimize_hashtags(
                content_data['description'], platform
            )
            platform_hashtags[platform] = hashtags
            print(f"   {platform}: {len(hashtags)} hashtags")
        
        # Step 2: Generate platform-specific captions
        print("\nStep 2: Generating platform-specific captions...")
        platform_captions = {}
        for platform in platforms:
            caption = caption_generator.generate_caption(content_data, platform)
            platform_captions[platform] = caption
            print(f"   {platform}: {len(caption)} characters")
        
        # Step 3: Determine optimal posting times
        print("\nStep 3: Finding optimal posting times...")
        posting_schedule = timing_optimizer.schedule_bulk_posting(
            platforms=platforms,
            content_count=1
        )
        
        for item in posting_schedule:
            time_str = item['scheduled_time'].strftime('%a %m/%d %I:%M %p')
            print(f"   {item['platform']}: {time_str}")
        
        # Step 4: Create VideoContent objects (simulation)
        print("\nStep 4: Creating content for posting...")
        for platform in platforms:
            content = VideoContent(
                file_path=f"repurposed_{platform}.mp4",  # Simulated
                title=content_data['title'],
                description=platform_captions[platform],
                hashtags=platform_hashtags[platform]
            )
            
            print(f"   {platform}: Ready for posting")
            # In real usage: job_id = posting_manager.queue_post(platform, content)
        
        print("\n🎉 Complete workflow demo finished!")
        print("    In production, videos would be automatically posted at optimal times")
        
    except Exception as e:
        print(f"❌ Workflow demo error: {e}")

def main():
    """Run the complete demo"""
    print("Starting Kiin Content Factory Social Media Integration Demo...\n")
    
    # Setup
    if not demo_setup():
        print("❌ Setup failed. Please check your configuration.")
        return
    
    # Run demos
    demo_hashtag_optimization()
    demo_caption_generation()
    demo_timing_optimization()
    demo_video_repurposing()
    demo_posting_manager()
    demo_full_workflow()
    
    # Summary
    print("\n" + "=" * 60)
    print("🎊 DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. 🔑 Add your real API credentials to config/social_credentials.json")
    print("2. 🎬 Add your video files to test actual posting")
    print("3. 🚀 Run posting_manager.start_processing() for automated posting")
    print("4. 📊 Monitor performance with analytics methods")
    print()
    print("📚 For more details, see:")
    print("   - docs/SOCIAL_MEDIA_INTEGRATION_README.md")
    print("   - docs/SECURITY_BEST_PRACTICES.md")
    print()
    print("Happy posting! 🎯")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        logger.exception("Demo failed")
        sys.exit(1)