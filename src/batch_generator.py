#!/usr/bin/env python3
"""
Comprehensive Batch Content Generator for Kiin Content

Features:
- Generate multiple content types in parallel
- Progress tracking with rich console output
- Organize output by date/type
- Generate accompanying captions
- Create manifest files
- Support for various generation modes

Usage:
    # Generate a week of content (one of each type per day)
    python batch_generator.py --days 7 --output-dir ./output/week1/

    # Generate specific content type in bulk
    python batch_generator.py --type validation --count 10

    # Generate full content library
    python batch_generator.py --all --count 5  # 5 of each type = 25 videos
"""

import argparse
import asyncio
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import random

# Add src to path for imports
sys.path.append(str(Path(__file__).parent))

from validation_generator import ValidationVideoGenerator
from tips_generator import CaregiverTipVideoGenerator
from confession_generator import ConfessionGenerator
from sandwich_generator import SandwichGenerator
from chaos_generator import ChaosGenerator


class ProgressTracker:
    """Track and display generation progress"""

    def __init__(self, total_tasks: int):
        self.total_tasks = total_tasks
        self.completed = 0
        self.failed = 0
        self.start_time = time.time()
        self.current_tasks = {}

    def start_task(self, task_id: str, description: str):
        """Mark task as started"""
        self.current_tasks[task_id] = {
            'description': description,
            'start_time': time.time()
        }
        print(f"🟡 [{self.completed + self.failed + 1}/{self.total_tasks}] Starting: {description}")

    def complete_task(self, task_id: str, file_size_mb: float = None):
        """Mark task as completed"""
        if task_id in self.current_tasks:
            duration = time.time() - self.current_tasks[task_id]['start_time']
            size_info = f" ({file_size_mb:.2f} MB)" if file_size_mb else ""
            print(f"✅ [{self.completed + 1}/{self.total_tasks}] Completed in {duration:.1f}s{size_info}")
            del self.current_tasks[task_id]
        self.completed += 1
        self._print_status()

    def fail_task(self, task_id: str, error: str):
        """Mark task as failed"""
        if task_id in self.current_tasks:
            print(f"❌ [{self.completed + self.failed + 1}/{self.total_tasks}] Failed: {error}")
            del self.current_tasks[task_id]
        self.failed += 1
        self._print_status()

    def _print_status(self):
        """Print current progress status"""
        elapsed = time.time() - self.start_time
        rate = (self.completed + self.failed) / elapsed if elapsed > 0 else 0
        remaining = self.total_tasks - (self.completed + self.failed)
        eta = remaining / rate if rate > 0 else 0

        print(f"📊 Progress: {self.completed} completed, {self.failed} failed, {remaining} remaining")
        print(f"⏱️  Rate: {rate:.1f} videos/min, ETA: {eta/60:.1f} minutes")
        print("-" * 60)


class CaptionGenerator:
    """Generate captions for videos based on content type and metadata"""

    PLATFORM_LIMITS = {
        'tiktok': 2200,
        'instagram': 2200,
        'youtube_shorts': 1000
    }

    CAPTION_TEMPLATES = {
        'validation': {
            'tiktok': "💜 {title}\n\n{description}\n\n#caregiver #validation #selfcare #mentalhealth #support #healing #kindness #caregiving #love #strength",
            'instagram': "💜 {title}\n\n{description}\n\n•••\n#caregiver #validation #selfcare #mentalhealth #support #healing #kindness #caregiving #love #strength #caregiverstories #caregiverlife #compassion #worthy #enough"
        },
        'tips': {
            'tiktok': "💡 STOP doing this! → {hook}\n\n✅ Try this instead: {solution}\n\n#caregivertips #stopgettingangry #tips #caregiver #mentalhealth #selfcare #boundaries #communication",
            'instagram': "💡 {hook}\n\n❌ What NOT to do:\n{wrong_action}\n\n✅ What TO do:\n{right_action}\n\n•••\n#caregivertips #stopgettingangry #tips #caregiver #mentalhealth #selfcare #boundaries #communication #caregiverlife #wisdom"
        },
        'confession': {
            'tiktok': "🤫 Caregiver confession:\n\n{confession}\n\n#caregiverconfession #honest #raw #real #caregiver #mentalhealth #struggles #authentic #vulnerability",
            'instagram': "🤫 {confession}\n\nBeing honest about the hard parts of caregiving.\n\n•••\n#caregiverconfession #honest #raw #real #caregiver #mentalhealth #struggles #authentic #vulnerability #caregiverlife #truth #support"
        },
        'sandwich': {
            'tiktok': "🥪 The Sandwich Generation:\n\n{scenario}\n\n#sandwichgeneration #caregiving #family #balance #struggle #reallife #support #understanding",
            'instagram': "🥪 {scenario}\n\nNavigating life in the sandwich generation.\n\n•••\n#sandwichgeneration #caregiving #family #balance #struggle #reallife #support #understanding #familylife #caregivers #community"
        },
        'chaos': {
            'tiktok': "🌪️ Caregiver chaos:\n\n{scenario}\n\n#caregiverchaos #reallife #chaos #overwhelming #support #understanding #solidarity #caregiverlife",
            'instagram': "🌪️ {scenario}\n\nSometimes caregiving is pure chaos - and that's okay.\n\n•••\n#caregiverchaos #reallife #chaos #overwhelming #support #understanding #solidarity #caregiverlife #authentic #community #struggles"
        }
    }

    @classmethod
    def generate_caption(cls, content_type: str, platform: str, metadata: Dict) -> str:
        """Generate platform-specific caption"""
        if content_type not in cls.CAPTION_TEMPLATES:
            return f"New {content_type} content! #caregiver #content #support"

        if platform not in cls.CAPTION_TEMPLATES[content_type]:
            platform = 'tiktok'  # Default fallback

        template = cls.CAPTION_TEMPLATES[content_type][platform]
        caption = template.format(**metadata)

        # Truncate if needed
        limit = cls.PLATFORM_LIMITS.get(platform, 2200)
        if len(caption) > limit:
            caption = caption[:limit-3] + "..."

        return caption


class BatchContentGenerator:
    """Main batch generator class"""

    CONTENT_TYPES = {
        'validation': ValidationVideoGenerator,
        'tips': CaregiverTipVideoGenerator,
        'confession': ConfessionGenerator,
        'sandwich': SandwichGenerator,
        'chaos': ChaosGenerator
    }

    def __init__(self, output_dir: str = "./output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Initialize generators
        self.generators = {}
        self._init_generators()

    def _init_generators(self):
        """Initialize all content generators"""
        config_dir = Path(__file__).parent.parent / "config"

        try:
            # Validation generator
            self.generators['validation'] = ValidationVideoGenerator()

            # Tips generator
            tips_config = config_dir / "caregiver_tips.json"
            self.generators['tips'] = CaregiverTipVideoGenerator(str(tips_config), str(self.output_dir))

            # Confession generator
            confession_config = config_dir / "confessions.json"
            if confession_config.exists():
                self.generators['confession'] = ConfessionVideoGenerator(str(confession_config))

            # Sandwich generator
            sandwich_config = config_dir / "sandwich_scenarios.json"
            if sandwich_config.exists():
                self.generators['sandwich'] = SandwichGeneratorBot(str(sandwich_config))

            # Chaos generator
            chaos_config = config_dir / "chaos_scenarios.json"
            if chaos_config.exists():
                self.generators['chaos'] = ChaosVideoGenerator(str(chaos_config))

        except Exception as e:
            print(f"⚠️  Warning: Could not initialize some generators: {e}")

    async def generate_single_content(self, content_type: str, output_path: Path, 
                                    metadata: Dict = None) -> Tuple[bool, str, float]:
        """Generate a single piece of content"""
        if content_type not in self.generators:
            return False, f"No generator for type: {content_type}", 0

        try:
            generator = self.generators[content_type]
            
            # Generate based on content type
            if content_type == 'validation':
                # Generate random validation video
                video_path = await generator.generate_video(output_path=str(output_path))
                
            elif content_type == 'tips':
                # Get random tip and generate
                tips = generator.list_tips()
                if not tips:
                    return False, "No tips available", 0
                tip = random.choice(tips)
                video_path = await generator.generate_tip_video(tip, output_path.name)
                
            elif content_type == 'confession':
                # Generate random confession video
                video_path = await generator.generate_video(output_name=output_path.name)
                
            elif content_type == 'sandwich':
                # Generate random sandwich scenario video
                video_path = await generator.generate_video()
                
            elif content_type == 'chaos':
                # Generate random chaos scenario video  
                video_path = await generator.generate_video()
            
            # Get file size
            if Path(video_path).exists():
                file_size_mb = Path(video_path).stat().st_size / (1024 * 1024)
                return True, video_path, file_size_mb
            else:
                return False, "Video file not created", 0
                
        except Exception as e:
            return False, str(e), 0

    def generate_daily_content(self, date: datetime, output_dir: Path) -> List[Dict]:
        """Generate one piece of content of each type for a specific day"""
        date_str = date.strftime("%Y-%m-%d")
        day_dir = output_dir / date_str
        day_dir.mkdir(exist_ok=True)

        tasks = []

        for i, content_type in enumerate(self.generators.keys(), 1):
            filename = f"{date_str}_{content_type}_{i:02d}.mp4"
            output_path = day_dir / filename

            task = {
                'id': f"{date_str}_{content_type}",
                'type': content_type,
                'date': date_str,
                'output_path': output_path,
                'metadata': {
                    'date': date_str,
                    'content_type': content_type,
                    'filename': filename
                }
            }
            tasks.append(task)

        return tasks

    def generate_bulk_content(self, content_type: str, count: int,
                            output_dir: Path) -> List[Dict]:
        """Generate multiple pieces of the same content type"""
        type_dir = output_dir / content_type
        type_dir.mkdir(exist_ok=True)

        tasks = []

        for i in range(1, count + 1):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{content_type}_{i:03d}_{timestamp}.mp4"
            output_path = type_dir / filename

            task = {
                'id': f"{content_type}_{i}",
                'type': content_type,
                'date': datetime.now().strftime("%Y-%m-%d"),
                'output_path': output_path,
                'metadata': {
                    'content_type': content_type,
                    'filename': filename,
                    'batch_number': i
                }
            }
            tasks.append(task)

        return tasks

    def generate_all_content(self, count_per_type: int, output_dir: Path) -> List[Dict]:
        """Generate multiple pieces of all content types"""
        tasks = []

        for content_type in self.generators.keys():
            type_tasks = self.generate_bulk_content(content_type, count_per_type, output_dir)
            tasks.extend(type_tasks)

        return tasks

    async def execute_generation_task(self, task: Dict, progress: ProgressTracker) -> Dict:
        """Execute a single generation task with progress tracking"""
        task_id = task['id']
        content_type = task['type']
        output_path = task['output_path']

        # Start task
        description = f"{content_type} → {output_path.name}"
        progress.start_task(task_id, description)

        # Generate content
        success, result, file_size = await self.generate_single_content(
            content_type, output_path, task['metadata']
        )

        # Update progress
        if success:
            progress.complete_task(task_id, file_size)
            task['success'] = True
            task['video_path'] = result
            task['file_size_mb'] = file_size

            # Generate captions
            task['captions'] = self.generate_captions_for_task(task)

        else:
            progress.fail_task(task_id, result)
            task['success'] = False
            task['error'] = result

        return task

    def generate_captions_for_task(self, task: Dict) -> Dict:
        """Generate captions for different platforms"""
        metadata = task['metadata']
        content_type = task['type']

        captions = {}

        for platform in ['tiktok', 'instagram']:
            captions[platform] = CaptionGenerator.generate_caption(
                content_type, platform, metadata
            )

        return captions

    async def run_batch_generation(self, tasks: List[Dict], max_workers: int = 3) -> List[Dict]:
        """Run batch generation with parallel processing"""
        print(f"\n🚀 Starting batch generation of {len(tasks)} videos...")
        print(f"🔧 Using {max_workers} parallel workers")
        print("=" * 60)

        progress = ProgressTracker(len(tasks))
        completed_tasks = []

        # Use ThreadPoolExecutor for parallel generation
        semaphore = asyncio.Semaphore(max_workers)

        async def limited_task(task):
            async with semaphore:
                return await self.execute_generation_task(task, progress)

        # Run all tasks
        task_futures = [limited_task(task) for task in tasks]

        for future in asyncio.as_completed(task_futures):
            completed_task = await future
            completed_tasks.append(completed_task)

        return completed_tasks

    def create_manifest(self, completed_tasks: List[Dict], output_dir: Path):
        """Create manifest file with generation results"""
        manifest = {
            'generated_at': datetime.now().isoformat(),
            'total_videos': len(completed_tasks),
            'successful': len([t for t in completed_tasks if t.get('success', False)]),
            'failed': len([t for t in completed_tasks if not t.get('success', False)]),
            'total_size_mb': sum(t.get('file_size_mb', 0) for t in completed_tasks),
            'videos': []
        }

        for task in completed_tasks:
            video_info = {
                'id': task['id'],
                'type': task['type'],
                'date': task['date'],
                'filename': task['output_path'].name if task.get('success') else None,
                'file_path': str(task['output_path']) if task.get('success') else None,
                'file_size_mb': task.get('file_size_mb'),
                'success': task.get('success', False),
                'error': task.get('error'),
                'captions': task.get('captions', {}),
                'metadata': task['metadata']
            }
            manifest['videos'].append(video_info)

        # Save manifest
        manifest_path = output_dir / 'manifest.json'
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)

        print(f"\n📋 Manifest created: {manifest_path}")
        return manifest_path

    def print_summary(self, completed_tasks: List[Dict], output_dir: Path):
        """Print generation summary"""
        successful = [t for t in completed_tasks if t.get('success', False)]
        failed = [t for t in completed_tasks if not t.get('success', False)]
        total_size = sum(t.get('file_size_mb', 0) for t in successful)

        print(f"\n🎉 Batch Generation Complete!")
        print("=" * 60)
        print(f"✅ Successful: {len(successful)}")
        print(f"❌ Failed: {len(failed)}")
        print(f"💾 Total size: {total_size:.2f} MB")
        print(f"📁 Output directory: {output_dir}")

        if failed:
            print(f"\n❌ Failed videos:")
            for task in failed:
                print(f"   • {task['id']}: {task.get('error', 'Unknown error')}")


async def main():
    parser = argparse.ArgumentParser(
        description="Comprehensive Batch Content Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a week of content (one of each type per day)
  python batch_generator.py --days 7 --output-dir ./output/week1/

  # Generate specific content type in bulk
  python batch_generator.py --type validation --count 10

  # Generate full content library
  python batch_generator.py --all --count 5  # 5 of each type = 25 videos
        """
    )

    # Generation modes (mutually exclusive)
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--days', type=int,
                           help='Generate daily content for N days')
    mode_group.add_argument('--type', choices=['validation', 'tips', 'confession', 'sandwich', 'chaos'],
                           help='Generate specific content type in bulk')
    mode_group.add_argument('--all', action='store_true',
                           help='Generate all content types in bulk')

    # Additional options
    parser.add_argument('--count', type=int, default=5,
                       help='Number of videos per type/day (default: 5)')
    parser.add_argument('--output-dir', default='./output',
                       help='Output directory (default: ./output)')
    parser.add_argument('--workers', type=int, default=3,
                       help='Number of parallel workers (default: 3)')
    parser.add_argument('--start-date', type=str,
                       help='Start date for daily generation (YYYY-MM-DD, default: today)')

    args = parser.parse_args()

    # Create batch generator
    generator = BatchContentGenerator(args.output_dir)

    # Determine generation tasks
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    tasks = []

    if args.days:
        # Daily generation mode
        start_date = datetime.now()
        if args.start_date:
            start_date = datetime.strptime(args.start_date, '%Y-%m-%d')

        for i in range(args.days):
            date = start_date + timedelta(days=i)
            daily_tasks = generator.generate_daily_content(date, output_dir)
            tasks.extend(daily_tasks)

    elif args.type:
        # Single type bulk generation
        tasks = generator.generate_bulk_content(args.type, args.count, output_dir)

    elif args.all:
        # All types bulk generation
        tasks = generator.generate_all_content(args.count, output_dir)

    if not tasks:
        print("❌ No tasks generated!")
        return

    # Run batch generation
    completed_tasks = await generator.run_batch_generation(tasks, args.workers)

    # Create manifest and summary
    generator.create_manifest(completed_tasks, output_dir)
    generator.print_summary(completed_tasks, output_dir)


if __name__ == "__main__":
    asyncio.run(main())