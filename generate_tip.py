#!/usr/bin/env python3
"""
Simple interface for generating caregiver tip videos

Usage:
    python generate_tip.py                    # Generate example video
    python generate_tip.py --tip-id 5         # Generate specific tip
    python generate_tip.py --category communication  # Generate random tip from category
    python generate_tip.py --list             # List all tips
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
    parser = argparse.ArgumentParser(description="Generate Caregiver Tip Videos")
    parser.add_argument("--tip-id", type=int, help="Generate video for specific tip ID")
    parser.add_argument("--category", type=str, 
                       choices=['communication', 'self_care', 'coordination', 'emotional_management'],
                       help="Generate random tip from category")
    parser.add_argument("--list", action="store_true", help="List all available tips")
    parser.add_argument("--output", type=str, help="Output filename (without extension)")
    
    args = parser.parse_args()
    
    # Setup paths
    config_path = "config/caregiver_tips.json"
    output_dir = "output"
    
    # Create generator
    generator = CaregiverTipVideoGenerator(config_path, output_dir)
    
    if args.list:
        print("\n📝 Available Tips:")
        print("=" * 60)
        for tip in generator.list_tips():
            print(f"ID {tip['id']:2d} | {tip['category']:15s} | {tip['hook'][:40]}...")
        return
    
    # Select tip
    if args.tip_id:
        tips = [tip for tip in generator.list_tips() if tip['id'] == args.tip_id]
        if not tips:
            print(f"❌ Tip ID {args.tip_id} not found")
            return
        selected_tip = tips[0]
    elif args.category:
        category_tips = generator.get_tips_by_category(args.category)
        if not category_tips:
            print(f"❌ No tips found for category '{args.category}'")
            return
        selected_tip = random.choice(category_tips)
    else:
        # Generate example (first tip)
        selected_tip = generator.list_tips()[0]
    
    # Generate filename
    if args.output:
        filename = f"{args.output}.mp4"
    else:
        filename = f"tip_{selected_tip['id']:02d}_{selected_tip['category']}.mp4"
    
    print(f"\n🎬 Generating video for tip {selected_tip['id']}")
    print(f"📝 Hook: {selected_tip['hook']}")
    print(f"📁 Output: {filename}")
    print("\nProcessing...")
    
    try:
        video_path = await generator.generate_tip_video(selected_tip, filename)
        print(f"\n🎉 Success! Video generated: {video_path}")
        
        # Get file size
        file_size = Path(video_path).stat().st_size / (1024 * 1024)
        print(f"📁 File size: {file_size:.2f} MB")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    # Activate virtual environment programmatically
    venv_path = Path(__file__).parent / "venv"
    if venv_path.exists():
        import sys
        sys.path.insert(0, str(venv_path / "lib" / "python3.14" / "site-packages"))
    
    asyncio.run(main())