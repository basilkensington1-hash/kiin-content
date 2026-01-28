#!/usr/bin/env python3
"""
List all available coordination chaos scenarios
"""

import json
from pathlib import Path

def main():
    config_path = Path(__file__).parent / 'config' / 'coordination_scenarios.json'
    
    with open(config_path, 'r') as f:
        data = json.load(f)
    
    print("🎬 Coordination Chaos Scenarios\n")
    print("Available scenarios for video generation:\n")
    
    for i, scenario in enumerate(data['scenarios'], 1):
        print(f"{i:2}. ID: {scenario['id']}")
        print(f"    Hook: {scenario['hook']}")
        print(f"    CTA: {scenario['cta']}")
        print()
    
    print(f"Total scenarios: {len(data['scenarios'])}")
    print("\nTo generate a video:")
    print("python src/chaos_generator.py [scenario_id]")
    print("\nExample:")
    print("python src/chaos_generator.py medication_double_dose")

if __name__ == '__main__':
    main()