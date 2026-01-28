#!/usr/bin/env python3
"""
Generate all coordination chaos videos

Usage:
    python generate_all.py [--limit N] [--scenarios scenario1,scenario2,...]
"""

import asyncio
import json
import argparse
from pathlib import Path
from src.chaos_generator import ChaosGenerator

async def main():
    parser = argparse.ArgumentParser(description='Generate all coordination chaos videos')
    parser.add_argument('--limit', type=int, help='Limit number of videos to generate')
    parser.add_argument('--scenarios', help='Comma-separated list of scenario IDs to generate')
    args = parser.parse_args()
    
    # Setup paths
    script_dir = Path(__file__).parent
    config_path = script_dir / 'config' / 'coordination_scenarios.json'
    output_dir = script_dir / 'output'
    
    # Load scenarios
    with open(config_path, 'r') as f:
        data = json.load(f)
    
    scenarios = data['scenarios']
    
    # Filter scenarios if specified
    if args.scenarios:
        scenario_ids = [s.strip() for s in args.scenarios.split(',')]
        scenarios = [s for s in scenarios if s['id'] in scenario_ids]
        
        # Check for missing scenarios
        found_ids = {s['id'] for s in scenarios}
        missing = set(scenario_ids) - found_ids
        if missing:
            print(f"⚠️  Warning: Scenarios not found: {', '.join(missing)}")
    
    # Limit if specified
    if args.limit:
        scenarios = scenarios[:args.limit]
    
    print(f"🎬 Generating {len(scenarios)} videos...")
    
    # Generate videos
    generator = ChaosGenerator(config_path, output_dir)
    
    try:
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n[{i}/{len(scenarios)}] Generating: {scenario['id']}")
            print(f"Hook: {scenario['hook']}")
            
            try:
                output_path = await generator.generate_video(scenario['id'])
                print(f"✅ Complete: {output_path}")
            except Exception as e:
                print(f"❌ Failed: {e}")
                
    finally:
        generator.cleanup()
    
    print(f"\n🎉 Batch generation complete!")
    print(f"📁 Check output directory: {output_dir}")

if __name__ == '__main__':
    asyncio.run(main())