#!/usr/bin/env python3
"""
Demo script for Tips Generator V2 - Shows how to use the enhanced features
"""

import asyncio
from tips_generator_v2 import TipsGeneratorV2
from pathlib import Path

async def demo_enhanced_features():
    """Demonstrate the enhanced features of Tips Generator V2"""
    
    # Initialize the generator
    config_path = "/Users/nick/clawd/kiin-content/config/expanded_caregiver_tips.json"
    output_dir = "/Users/nick/clawd/kiin-content/output"
    
    generator = TipsGeneratorV2(config_path, output_dir)
    
    print("🚀 Kiin Tips Generator V2 - Enhanced Features Demo")
    print("=" * 60)
    
    # Show available series
    print("\n📚 Available Series:")
    for series in generator.data['metadata']['series']:
        print(f"   • {series['title']}: {series['description']}")
    
    # Show difficulty levels
    print(f"\n🎯 Difficulty Levels: {', '.join(generator.data['metadata']['difficulty_levels'])}")
    
    # Show tips by difficulty
    print(f"\n📊 Tips by Difficulty:")
    for difficulty in generator.data['metadata']['difficulty_levels']:
        tips = generator.get_tips_by_difficulty(difficulty)
        print(f"   • {difficulty.title()}: {len(tips)} tips")
    
    # Generate a video from each difficulty level
    print(f"\n🎬 Generating sample videos...")
    
    for difficulty in ['beginner', 'intermediate', 'advanced']:
        tips = generator.get_tips_by_difficulty(difficulty)
        if tips:
            tip = tips[0]  # Take first tip of this difficulty
            filename = f"demo_{difficulty}_{tip['id']:02d}.mp4"
            
            print(f"\n   🎥 Creating {difficulty} level video...")
            video_path = await generator.generate_tip_video_v2(tip, filename)
            
            file_size = Path(video_path).stat().st_size / (1024 * 1024)  # MB
            print(f"   ✅ Generated: {filename} ({file_size:.2f} MB)")
    
    # Show what makes V2 10x better
    print(f"\n🚀 V2 Enhancements - What Makes It 10x Better:")
    print(f"   🎨 Visual Upgrades:")
    print(f"      • Animated icons (checkmarks, X marks, lightbulbs)")
    print(f"      • Smooth transitions between sections")
    print(f"      • Data visualizations showing tip effectiveness")
    print(f"      • Progress indicators throughout video")
    print(f"      • Memory aids with emoji and visual cues")
    print(f"   ")
    print(f"   🎵 Audio Enhancements:")
    print(f"      • Background music integration (professional mood)")
    print(f"      • Optimized voice selection via voice manager")
    print(f"      • Better pacing and natural speech flow")
    print(f"   ")
    print(f"   📚 Content Improvements:")
    print(f"      • Expanded from 17 to {generator.data['metadata']['total_tips']} tips")
    print(f"      • 3 difficulty levels: beginner, intermediate, advanced")
    print(f"      • 4 organized series for targeted learning")
    print(f"      • Source citations for credibility")
    print(f"   ")
    print(f"   🎓 Educational Design:")
    print(f"      • Key takeaway summaries")
    print(f"      • 'Try this today' action prompts")
    print(f"      • Visual memory aids for better retention")
    print(f"      • Data-driven impact visualization")
    print(f"   ")
    print(f"   🏷️ Brand Integration:")
    print(f"      • Consistent brand colors and fonts")
    print(f"      • Automatic watermarking")
    print(f"      • Professional voice selection")
    print(f"      • Brand-aligned visual style")
    
    print(f"\n💡 How to Use Advanced Features:")
    print(f"   # Generate entire series")
    print(f"   videos = generator.generate_series_videos('communication_week')")
    print(f"   ")
    print(f"   # Filter by difficulty")
    print(f"   beginner_tips = generator.get_tips_by_difficulty('beginner')")
    print(f"   ")
    print(f"   # Custom voice selection")
    print(f"   video = await generator.generate_tip_video_v2(tip, voice_name='en-GB-SoniaNeural')")

async def demo_series_generation():
    """Demo generating a complete series"""
    config_path = "/Users/nick/clawd/kiin-content/config/expanded_caregiver_tips.json"
    output_dir = "/Users/nick/clawd/kiin-content/output"
    
    generator = TipsGeneratorV2(config_path, output_dir)
    
    print("\n🎬 Series Generation Demo")
    print("=" * 40)
    
    # Show available series
    for series in generator.data['metadata']['series']:
        print(f"\nSeries: {series['title']}")
        print(f"Description: {series['description']}")
        
        series_tips = generator.get_tips_by_series(series['name'])
        print(f"Tips in series: {len(series_tips)}")
        
        for tip in series_tips[:2]:  # Show first 2 tips
            print(f"   • Day {tip['id']}: {tip['hook'][:60]}...")
    
    print(f"\nTo generate a complete series:")
    print(f"videos = generator.generate_series_videos('communication_week')")

if __name__ == "__main__":
    # Run the demo
    asyncio.run(demo_enhanced_features())
    
    # Uncomment to demo series generation (will take longer)
    # asyncio.run(demo_series_generation())