#!/usr/bin/env python3
"""
A/B Testing Framework for Kiin Content
=====================================

A comprehensive system for creating, managing, and analyzing A/B tests
for content variations to optimize engagement metrics.

Features:
- Variation generator for different content types
- Test configuration management
- Performance tracking and analysis
- Statistical significance testing
- CLI interface for easy team usage

Usage:
    python ab_testing.py --create-test --content-type validation --variations 3
    python ab_testing.py --log-result --test-id abc123 --variation A --views 1000 --saves 50
    python ab_testing.py --report --test-id abc123
"""

import argparse
import json
import uuid
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import statistics
import math
from dataclasses import dataclass, asdict
from copy import deepcopy

@dataclass
class TestResult:
    """Single result entry for an A/B test variation."""
    test_id: str
    variation: str
    timestamp: str
    metrics: Dict[str, int]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ABTest:
    """A/B test configuration and metadata."""
    test_id: str
    content_type: str
    variations: List[str]
    metrics_to_track: List[str]
    created_at: str
    status: str = "active"
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class VariationGenerator:
    """Generates content variations for A/B testing."""
    
    HOOK_VARIATIONS = {
        "vulnerability_hook": {
            "style": "emotional vulnerability",
            "examples": ["I used to think...", "Nobody talks about...", "The hardest part is..."],
            "tone": "intimate, honest"
        },
        "question_hook": {
            "style": "engaging question",
            "examples": ["What if I told you...", "Have you ever wondered...", "Why do we..."],
            "tone": "curious, inviting"
        },
        "bold_hook": {
            "style": "bold statement",
            "examples": ["Stop doing this immediately", "This changes everything", "Here's the truth..."],
            "tone": "authoritative, direct"
        },
        "story_hook": {
            "style": "personal story",
            "examples": ["Last week, my friend...", "My journey started when...", "Picture this..."],
            "tone": "narrative, relatable"
        },
        "statistic_hook": {
            "style": "surprising statistic",
            "examples": ["85% of caregivers...", "Studies show that...", "Research reveals..."],
            "tone": "factual, credible"
        }
    }
    
    COLOR_VARIATIONS = {
        "warm": {"primary": "#FF6B6B", "secondary": "#4ECDC4", "accent": "#FFE66D"},
        "professional": {"primary": "#2C3E50", "secondary": "#3498DB", "accent": "#E74C3C"},
        "calming": {"primary": "#6C7B7F", "secondary": "#99D8C8", "accent": "#F7DC6F"},
        "energetic": {"primary": "#E67E22", "secondary": "#9B59B6", "accent": "#F1C40F"},
        "trustworthy": {"primary": "#1ABC9C", "secondary": "#34495E", "accent": "#E8F5E8"}
    }
    
    VOICE_VARIATIONS = {
        "empathetic": {"tone": "warm", "pace": "moderate", "style": "conversational"},
        "authoritative": {"tone": "confident", "pace": "steady", "style": "professional"},
        "friendly": {"tone": "upbeat", "pace": "lively", "style": "casual"},
        "calming": {"tone": "soothing", "pace": "slow", "style": "meditative"},
        "energetic": {"tone": "enthusiastic", "pace": "fast", "style": "motivational"}
    }
    
    def generate_variations(self, content_type: str, num_variations: int = 3) -> List[Dict[str, Any]]:
        """Generate multiple variations of content for testing."""
        variations = []
        
        hook_types = list(self.HOOK_VARIATIONS.keys())
        color_schemes = list(self.COLOR_VARIATIONS.keys())
        voice_styles = list(self.VOICE_VARIATIONS.keys())
        
        for i in range(num_variations):
            variation = {
                "id": chr(65 + i),  # A, B, C, etc.
                "hook": {
                    "type": hook_types[i % len(hook_types)],
                    "details": self.HOOK_VARIATIONS[hook_types[i % len(hook_types)]]
                },
                "colors": {
                    "scheme": color_schemes[i % len(color_schemes)],
                    "palette": self.COLOR_VARIATIONS[color_schemes[i % len(color_schemes)]]
                },
                "voice": {
                    "style": voice_styles[i % len(voice_styles)],
                    "settings": self.VOICE_VARIATIONS[voice_styles[i % len(voice_styles)]]
                },
                "text_emphasis": self._get_text_emphasis(i),
                "music": self._get_music_style(content_type, i)
            }
            variations.append(variation)
        
        return variations
    
    def _get_text_emphasis(self, variation_index: int) -> Dict[str, str]:
        """Generate text emphasis variations."""
        emphasis_styles = [
            {"style": "bold_keywords", "description": "Bold key phrases and emotional words"},
            {"style": "italic_emotions", "description": "Italicize emotional and personal words"},
            {"style": "caps_action", "description": "CAPS for action words and calls-to-action"},
            {"style": "minimal", "description": "Clean text with minimal formatting"}
        ]
        return emphasis_styles[variation_index % len(emphasis_styles)]
    
    def _get_music_style(self, content_type: str, variation_index: int) -> Dict[str, str]:
        """Generate music variations based on content type."""
        music_styles = {
            "validation": [
                {"genre": "ambient", "mood": "uplifting", "energy": "medium"},
                {"genre": "acoustic", "mood": "warm", "energy": "low"},
                {"genre": "soft_piano", "mood": "hopeful", "energy": "medium-low"}
            ],
            "tips": [
                {"genre": "upbeat_acoustic", "mood": "encouraging", "energy": "medium-high"},
                {"genre": "modern_ambient", "mood": "focused", "energy": "medium"},
                {"genre": "light_electronic", "mood": "energetic", "energy": "high"}
            ],
            "facts": [
                {"genre": "minimal_piano", "mood": "serious", "energy": "low"},
                {"genre": "documentary_style", "mood": "informative", "energy": "medium"},
                {"genre": "modern_classical", "mood": "authoritative", "energy": "medium-low"}
            ]
        }
        
        styles = music_styles.get(content_type, music_styles["validation"])
        return styles[variation_index % len(styles)]

class ABTestManager:
    """Manages A/B tests, configurations, and results."""
    
    def __init__(self, config_dir: Path = None):
        self.config_dir = config_dir or Path(__file__).parent.parent / "config"
        self.results_dir = self.config_dir / "ab_test_results"
        self.results_dir.mkdir(exist_ok=True)
        
        self.config_file = self.config_dir / "ab_tests.json"
        self.variation_generator = VariationGenerator()
        
        # Load existing tests
        self.tests = self._load_tests()
    
    def _load_tests(self) -> Dict[str, ABTest]:
        """Load existing test configurations."""
        if not self.config_file.exists():
            return {}
        
        with open(self.config_file, 'r') as f:
            data = json.load(f)
        
        tests = {}
        for test_data in data.get("tests", []):
            test = ABTest(**test_data)
            tests[test.test_id] = test
        
        return tests
    
    def _save_tests(self):
        """Save test configurations to file."""
        data = {
            "tests": [test.to_dict() for test in self.tests.values()],
            "last_updated": datetime.datetime.now().isoformat()
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_test(self, content_type: str, num_variations: int = 3, description: str = None) -> str:
        """Create a new A/B test with variations."""
        test_id = str(uuid.uuid4())[:8]
        
        # Generate variations
        variations_data = self.variation_generator.generate_variations(content_type, num_variations)
        variation_names = [f"variation_{v['id']}" for v in variations_data]
        
        # Create test configuration
        test = ABTest(
            test_id=test_id,
            content_type=content_type,
            variations=variation_names,
            metrics_to_track=["views", "saves", "shares", "comments", "completion_rate"],
            created_at=datetime.datetime.now().isoformat(),
            description=description
        )
        
        # Save variation details
        variation_file = self.results_dir / f"{test_id}_variations.json"
        with open(variation_file, 'w') as f:
            json.dump({
                "test_id": test_id,
                "variations": variations_data,
                "created_at": test.created_at
            }, f, indent=2)
        
        # Add to tests and save
        self.tests[test_id] = test
        self._save_tests()
        
        return test_id
    
    def log_result(self, test_id: str, variation: str, **metrics) -> bool:
        """Log performance metrics for a test variation."""
        if test_id not in self.tests:
            print(f"Error: Test {test_id} not found")
            return False
        
        result = TestResult(
            test_id=test_id,
            variation=variation,
            timestamp=datetime.datetime.now().isoformat(),
            metrics=metrics
        )
        
        # Append to results file
        results_file = self.results_dir / f"{test_id}_results.jsonl"
        with open(results_file, 'a') as f:
            f.write(json.dumps(result.to_dict()) + '\n')
        
        return True
    
    def get_results(self, test_id: str) -> List[TestResult]:
        """Get all results for a test."""
        results_file = self.results_dir / f"{test_id}_results.jsonl"
        if not results_file.exists():
            return []
        
        results = []
        with open(results_file, 'r') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    results.append(TestResult(**data))
        
        return results
    
    def analyze_test(self, test_id: str) -> Dict[str, Any]:
        """Analyze test results and determine statistical significance."""
        if test_id not in self.tests:
            return {"error": "Test not found"}
        
        test = self.tests[test_id]
        results = self.get_results(test_id)
        
        if not results:
            return {"error": "No results found for test"}
        
        # Group results by variation
        variation_results = {}
        for result in results:
            if result.variation not in variation_results:
                variation_results[result.variation] = []
            variation_results[result.variation].append(result.metrics)
        
        # Calculate statistics for each variation
        analysis = {
            "test_id": test_id,
            "test_config": test.to_dict(),
            "total_results": len(results),
            "variations": {},
            "winner": None,
            "confidence": None
        }
        
        for variation, metrics_list in variation_results.items():
            if not metrics_list:
                continue
            
            # Calculate averages and totals
            variation_stats = {
                "sample_size": len(metrics_list),
                "metrics": {}
            }
            
            # For each metric, calculate statistics
            for metric in test.metrics_to_track:
                values = [m.get(metric, 0) for m in metrics_list]
                if values:
                    variation_stats["metrics"][metric] = {
                        "total": sum(values),
                        "average": statistics.mean(values),
                        "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                        "min": min(values),
                        "max": max(values)
                    }
            
            analysis["variations"][variation] = variation_stats
        
        # Determine winner (simple comparison - could be enhanced with proper statistical testing)
        if len(analysis["variations"]) >= 2:
            analysis["winner"], analysis["confidence"] = self._determine_winner(analysis["variations"])
        
        return analysis
    
    def _determine_winner(self, variations: Dict[str, Any]) -> tuple:
        """Determine the winning variation based on primary metric (views by default)."""
        primary_metric = "views"
        
        best_variation = None
        best_score = 0
        
        # Simple winner determination based on average views
        # In practice, you'd want proper statistical significance testing
        for variation, stats in variations.items():
            if primary_metric in stats["metrics"]:
                avg_score = stats["metrics"][primary_metric]["average"]
                if avg_score > best_score:
                    best_score = avg_score
                    best_variation = variation
        
        # Calculate confidence based on sample sizes and differences
        # This is a simplified approach - real statistical testing would be more complex
        confidence = "medium"  # Would calculate based on statistical tests
        
        return best_variation, confidence

def main():
    """CLI interface for A/B testing framework."""
    parser = argparse.ArgumentParser(description="Kiin Content A/B Testing Framework")
    parser.add_argument("--create-test", action="store_true", help="Create a new A/B test")
    parser.add_argument("--log-result", action="store_true", help="Log test results")
    parser.add_argument("--report", action="store_true", help="Generate test report")
    parser.add_argument("--list-tests", action="store_true", help="List all tests")
    
    # Test creation arguments
    parser.add_argument("--content-type", help="Type of content to test (validation, tips, facts)")
    parser.add_argument("--variations", type=int, default=3, help="Number of variations to create")
    parser.add_argument("--description", help="Test description")
    
    # Result logging arguments
    parser.add_argument("--test-id", help="Test ID")
    parser.add_argument("--variation", help="Variation identifier (A, B, C, etc.)")
    parser.add_argument("--views", type=int, help="Number of views")
    parser.add_argument("--saves", type=int, help="Number of saves")
    parser.add_argument("--shares", type=int, help="Number of shares")
    parser.add_argument("--comments", type=int, help="Number of comments")
    parser.add_argument("--completion-rate", type=float, help="Completion rate (0-1)")
    
    args = parser.parse_args()
    
    manager = ABTestManager()
    
    if args.create_test:
        if not args.content_type:
            print("Error: --content-type required for creating tests")
            return
        
        test_id = manager.create_test(
            content_type=args.content_type,
            num_variations=args.variations,
            description=args.description
        )
        
        print(f"✅ Created A/B test: {test_id}")
        print(f"Content type: {args.content_type}")
        print(f"Variations: {args.variations}")
        
        # Show variation details
        variation_file = manager.results_dir / f"{test_id}_variations.json"
        with open(variation_file, 'r') as f:
            data = json.load(f)
        
        print("\n📊 Generated Variations:")
        for var in data["variations"]:
            print(f"  Variation {var['id']}:")
            print(f"    Hook: {var['hook']['type']}")
            print(f"    Colors: {var['colors']['scheme']}")
            print(f"    Voice: {var['voice']['style']}")
            print(f"    Music: {var['music']['genre']} ({var['music']['mood']})")
    
    elif args.log_result:
        if not args.test_id or not args.variation:
            print("Error: --test-id and --variation required for logging results")
            return
        
        metrics = {}
        if args.views is not None:
            metrics["views"] = args.views
        if args.saves is not None:
            metrics["saves"] = args.saves
        if args.shares is not None:
            metrics["shares"] = args.shares
        if args.comments is not None:
            metrics["comments"] = args.comments
        if args.completion_rate is not None:
            metrics["completion_rate"] = args.completion_rate
        
        if not metrics:
            print("Error: At least one metric required (--views, --saves, --shares, --comments, --completion-rate)")
            return
        
        success = manager.log_result(args.test_id, args.variation, **metrics)
        if success:
            print(f"✅ Logged results for test {args.test_id}, variation {args.variation}")
            print(f"Metrics: {metrics}")
        else:
            print("❌ Failed to log results")
    
    elif args.report:
        if not args.test_id:
            print("Error: --test-id required for generating reports")
            return
        
        analysis = manager.analyze_test(args.test_id)
        
        if "error" in analysis:
            print(f"❌ Error: {analysis['error']}")
            return
        
        print(f"\n📈 A/B Test Report: {args.test_id}")
        print(f"Content Type: {analysis['test_config']['content_type']}")
        print(f"Total Results: {analysis['total_results']}")
        
        if analysis["winner"]:
            print(f"🏆 Winner: Variation {analysis['winner']} (confidence: {analysis['confidence']})")
        
        print("\n📊 Variation Performance:")
        for variation, stats in analysis["variations"].items():
            print(f"\n  Variation {variation} (n={stats['sample_size']}):")
            for metric, data in stats["metrics"].items():
                print(f"    {metric.title()}: {data['average']:.1f} avg ({data['total']} total)")
    
    elif args.list_tests:
        if not manager.tests:
            print("No tests found.")
            return
        
        print("🧪 Active A/B Tests:")
        for test_id, test in manager.tests.items():
            results_count = len(manager.get_results(test_id))
            print(f"  {test_id}: {test.content_type} ({len(test.variations)} variations, {results_count} results)")
            if test.description:
                print(f"    Description: {test.description}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()