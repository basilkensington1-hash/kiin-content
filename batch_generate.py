#!/usr/bin/env python3
"""
Batch generate multiple caregiver tip videos

Usage:
    python batch_generate.py --category communication  # Generate all communication tips
    python batch_generate.py --all                     # Generate all tips
    python batch_generate.py --random 5                # Generate 5 random tips
"""

import argparse
import asyncio
import random
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))
from tips_generator import CaregiverTipVideoGenerator


async def main():
    parser = argparse.ArgumentParser(description="Batch Generate Caregiver Tip Videos")
    parser.add_argument("--category", type=str, 
                       choices=['communication', 'self_care', 'coordination', 'emotional_management'],
                       help="Generate all tips from specific category")
    parser.add_argument("--all", action="store_true", help="Generate all tips")
    parser.add_argument("--random", type=int, help="Generate N random tips")
    
    args = parser.parse_args()
    
    if not any([args.category, args.all, args.random]):
        parser.error("Must specify --category, --all, or --random")
    
    # Setup paths
    config_path = "config/caregiver_tips.json"
    output_dir = "output"
    
    # Create generator
    generator = CaregiverTipVideoGenerator(config_path, output_dir)
    
    # Select tips to generate
    if args.all:
        tips_to_generate = generator.list_tips()
    elif args.category:
        tips_to_generate = generator.get_tips_by_category(args.category)
    else:  # random
        all_tips = generator.list_tips()
        tips_to_generate = random.sample(all_tips, min(args.random, len(all_tips)))
    
    if not tips_to_generate:
        print("❌ No tips selected for generation")
        return
    
    print(f"\n🎬 Batch generating {len(tips_to_generate)} videos...")
    print("=" * 60)
    
    successful = 0
    failed = 0
    
    for i, tip in enumerate(tips_to_generate, 1):
        filename = f"tip_{tip['id']:02d}_{tip['category']}.mp4"
        
        print(f"\n[{i}/{len(tips_to_generate)}] Generating: {filename}")
        print(f"Hook: {tip['hook'][:60]}...")
        
        try:
            video_path = await generator.generate_tip_video(tip, filename)
            file_size = Path(video_path).stat().st_size / (1024 * 1024)
            print(f"✅ Success! ({file_size:.2f} MB)")
            successful += 1
            
        except Exception as e:
            print(f"❌ Failed: {e}")
            failed += 1
    
    print(f"\n🎉 Batch complete!")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📁 Output directory: {output_dir}/")


if __name__ == "__main__":
    # Activate virtual environment programmatically
    venv_path = Path(__file__).parent / "venv"
    if venv_path.exists():
        import sys
        sys.path.insert(0, str(venv_path / "lib" / "python3.14" / "site-packages"))
    
    asyncio.run(main())