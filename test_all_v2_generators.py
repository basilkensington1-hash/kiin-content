#!/usr/bin/env python3
"""
Comprehensive test script for all V2 generators in Kiin Content Factory
"""

import asyncio
import os
import sys
import subprocess
import traceback
from pathlib import Path
from datetime import datetime

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

class V2GeneratorTester:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.output_dir = self.base_dir / "output" / "v2_tests"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results = {}
        
    def log_test_result(self, generator: str, test_name: str, success: bool, message: str = "", output_path: str = ""):
        """Log test results for later summary"""
        if generator not in self.results:
            self.results[generator] = []
        
        self.results[generator].append({
            'test': test_name,
            'success': success,
            'message': message,
            'output_path': output_path,
            'timestamp': datetime.now().isoformat()
        })
        
        status = "✅" if success else "❌"
        print(f"{status} {generator} - {test_name}: {message}")
        
    def check_video_output(self, path: str) -> bool:
        """Verify video file exists and is valid"""
        if not os.path.exists(path):
            return False
            
        try:
            # Use ffprobe to check video file
            result = subprocess.run([
                'ffprobe', '-v', 'quiet', '-print_format', 'json', 
                '-show_format', '-show_streams', path
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                # Basic check - has video stream
                import json
                data = json.loads(result.stdout)
                streams = data.get('streams', [])
                has_video = any(s.get('codec_type') == 'video' for s in streams)
                return has_video
            return False
        except Exception:
            return False

    async def test_validation_generator_v2(self):
        """Test validation_generator_v2.py with multiple scenarios"""
        print("\n🧪 Testing Validation Generator V2...")
        
        try:
            from validation_generator_v2 import EnhancedValidationGenerator
            generator = EnhancedValidationGenerator()
            
            # Test 1: Basic guilt relief validation
            test_output = str(self.output_dir / "validation_test1_guilt_relief.mp4")
            try:
                output_path = await generator.generate_validation_video(
                    category="guilt_relief",
                    output_path=test_output,
                    style="brand_professional"
                )
                
                if self.check_video_output(output_path):
                    self.log_test_result("validation_v2", "guilt_relief_basic", True, 
                                       "Generated guilt relief validation video", output_path)
                else:
                    self.log_test_result("validation_v2", "guilt_relief_basic", False, 
                                       "Video file invalid or missing")
                    
            except Exception as e:
                self.log_test_result("validation_v2", "guilt_relief_basic", False, 
                                   f"Exception: {str(e)}")
            
            # Test 2: Permission statements with nature soft style
            test_output = str(self.output_dir / "validation_test2_permission.mp4")
            try:
                output_path = await generator.generate_validation_video(
                    category="permission_statements",
                    output_path=test_output,
                    style="nature_soft"
                )
                
                if self.check_video_output(output_path):
                    self.log_test_result("validation_v2", "permission_nature", True, 
                                       "Generated permission statements with nature style", output_path)
                else:
                    self.log_test_result("validation_v2", "permission_nature", False, 
                                       "Video file invalid or missing")
                    
            except Exception as e:
                self.log_test_result("validation_v2", "permission_nature", False, 
                                   f"Exception: {str(e)}")
            
            # Test 3: Custom message with abstract warm style
            test_output = str(self.output_dir / "validation_test3_custom.mp4")
            try:
                output_path = await generator.generate_validation_video(
                    message_text="You are worthy of love and kindness just as you are.",
                    output_path=test_output,
                    style="abstract_warm"
                )
                
                if self.check_video_output(output_path):
                    self.log_test_result("validation_v2", "custom_message", True, 
                                       "Generated custom validation message", output_path)
                else:
                    self.log_test_result("validation_v2", "custom_message", False, 
                                       "Video file invalid or missing")
                    
            except Exception as e:
                self.log_test_result("validation_v2", "custom_message", False, 
                                   f"Exception: {str(e)}")
            
        except ImportError as e:
            self.log_test_result("validation_v2", "import_test", False, f"Import failed: {e}")
        except Exception as e:
            self.log_test_result("validation_v2", "general_error", False, f"Unexpected error: {e}")

    async def test_confession_generator_v2(self):
        """Test confession_generator_v2.py with multiple scenarios"""
        print("\n🧪 Testing Confession Generator V2...")
        
        try:
            from confession_generator_v2 import EnhancedConfessionGenerator
            generator = EnhancedConfessionGenerator()
            
            # Test 1: Basic confession - food category
            test_output = str(self.output_dir / "confession_test1_food.mp4")
            try:
                output_path = await generator.generate_confession_video(
                    category="food_secrets",
                    output_path=test_output,
                    style="cozy_kitchen"
                )
                
                if self.check_video_output(output_path):
                    self.log_test_result("confession_v2", "food_secrets", True, 
                                       "Generated food confession video", output_path)
                else:
                    self.log_test_result("confession_v2", "food_secrets", False, 
                                       "Video file invalid or missing")
                    
            except Exception as e:
                self.log_test_result("confession_v2", "food_secrets", False, 
                                   f"Exception: {str(e)}")
            
            # Test 2: Relationships category with moody aesthetic
            test_output = str(self.output_dir / "confession_test2_relationships.mp4")
            try:
                output_path = await generator.generate_confession_video(
                    category="relationship_secrets",
                    output_path=test_output,
                    style="moody_aesthetic"
                )
                
                if self.check_video_output(output_path):
                    self.log_test_result("confession_v2", "relationship_secrets", True, 
                                       "Generated relationship confession video", output_path)
                else:
                    self.log_test_result("confession_v2", "relationship_secrets", False, 
                                       "Video file invalid or missing")
                    
            except Exception as e:
                self.log_test_result("confession_v2", "relationship_secrets", False, 
                                   f"Exception: {str(e)}")
            
            # Test 3: Custom confession message
            test_output = str(self.output_dir / "confession_test3_custom.mp4")
            try:
                output_path = await generator.generate_confession_video(
                    message_text="I sometimes eat cereal for dinner and pretend it's a gourmet meal.",
                    output_path=test_output,
                    style="playful_bright"
                )
                
                if self.check_video_output(output_path):
                    self.log_test_result("confession_v2", "custom_confession", True, 
                                       "Generated custom confession message", output_path)
                else:
                    self.log_test_result("confession_v2", "custom_confession", False, 
                                       "Video file invalid or missing")
                    
            except Exception as e:
                self.log_test_result("confession_v2", "custom_confession", False, 
                                   f"Exception: {str(e)}")
            
        except ImportError as e:
            self.log_test_result("confession_v2", "import_test", False, f"Import failed: {e}")
        except Exception as e:
            self.log_test_result("confession_v2", "general_error", False, f"Unexpected error: {e}")

    async def test_tips_generator_v2(self):
        """Test tips_generator_v2.py with multiple scenarios"""
        print("\n🧪 Testing Tips Generator V2...")
        
        try:
            from tips_generator_v2 import EnhancedTipsGenerator
            generator = EnhancedTipsGenerator()
            
            # Test 1: Productivity tip
            test_output = str(self.output_dir / "tips_test1_productivity.mp4")
            try:
                output_path = await generator.generate_tips_video(
                    category="productivity_hacks",
                    output_path=test_output,
                    style="clean_minimal"
                )
                
                if self.check_video_output(output_path):
                    self.log_test_result("tips_v2", "productivity_hacks", True, 
                                       "Generated productivity tip video", output_path)
                else:
                    self.log_test_result("tips_v2", "productivity_hacks", False, 
                                       "Video file invalid or missing")
                    
            except Exception as e:
                self.log_test_result("tips_v2", "productivity_hacks", False, 
                                   f"Exception: {str(e)}")
            
            # Test 2: Wellness tip
            test_output = str(self.output_dir / "tips_test2_wellness.mp4")
            try:
                output_path = await generator.generate_tips_video(
                    category="wellness_daily",
                    output_path=test_output,
                    style="nature_zen"
                )
                
                if self.check_video_output(output_path):
                    self.log_test_result("tips_v2", "wellness_daily", True, 
                                       "Generated wellness tip video", output_path)
                else:
                    self.log_test_result("tips_v2", "wellness_daily", False, 
                                       "Video file invalid or missing")
                    
            except Exception as e:
                self.log_test_result("tips_v2", "wellness_daily", False, 
                                   f"Exception: {str(e)}")
            
            # Test 3: Custom tip message
            test_output = str(self.output_dir / "tips_test3_custom.mp4")
            try:
                output_path = await generator.generate_tips_video(
                    message_text="Try the 2-minute rule: If something takes less than 2 minutes, do it now.",
                    output_path=test_output,
                    style="vibrant_energy"
                )
                
                if self.check_video_output(output_path):
                    self.log_test_result("tips_v2", "custom_tip", True, 
                                       "Generated custom tip message", output_path)
                else:
                    self.log_test_result("tips_v2", "custom_tip", False, 
                                       "Video file invalid or missing")
                    
            except Exception as e:
                self.log_test_result("tips_v2", "custom_tip", False, 
                                   f"Exception: {str(e)}")
                
        except ImportError as e:
            self.log_test_result("tips_v2", "import_test", False, f"Import failed: {e}")
        except Exception as e:
            self.log_test_result("tips_v2", "general_error", False, f"Unexpected error: {e}")

    async def test_sandwich_generator_v2(self):
        """Test sandwich_generator_v2.py with multiple scenarios"""
        print("\n🧪 Testing Sandwich Generator V2...")
        
        try:
            from sandwich_generator_v2 import EnhancedSandwichGenerator
            generator = EnhancedSandwichGenerator()
            
            # Test 1: Basic compliment sandwich
            test_output = str(self.output_dir / "sandwich_test1_compliment.mp4")
            try:
                output_path = await generator.generate_sandwich_video(
                    category="daily_compliments",
                    output_path=test_output,
                    style="warm_encouraging"
                )
                
                if self.check_video_output(output_path):
                    self.log_test_result("sandwich_v2", "daily_compliments", True, 
                                       "Generated compliment sandwich video", output_path)
                else:
                    self.log_test_result("sandwich_v2", "daily_compliments", False, 
                                       "Video file invalid or missing")
                    
            except Exception as e:
                self.log_test_result("sandwich_v2", "daily_compliments", False, 
                                   f"Exception: {str(e)}")
            
            # Test 2: Motivational sandwich
            test_output = str(self.output_dir / "sandwich_test2_motivation.mp4")
            try:
                output_path = await generator.generate_sandwich_video(
                    category="motivation_boost",
                    output_path=test_output,
                    style="energetic_bold"
                )
                
                if self.check_video_output(output_path):
                    self.log_test_result("sandwich_v2", "motivation_boost", True, 
                                       "Generated motivational sandwich video", output_path)
                else:
                    self.log_test_result("sandwich_v2", "motivation_boost", False, 
                                       "Video file invalid or missing")
                    
            except Exception as e:
                self.log_test_result("sandwich_v2", "motivation_boost", False, 
                                   f"Exception: {str(e)}")
            
            # Test 3: Custom sandwich message
            test_output = str(self.output_dir / "sandwich_test3_custom.mp4")
            try:
                custom_messages = [
                    "You're doing amazing today!",
                    "Here's a gentle reminder:",
                    "You deserve all the good things coming your way!"
                ]
                
                output_path = await generator.generate_sandwich_video(
                    sandwich_messages=custom_messages,
                    output_path=test_output,
                    style="soft_pastel"
                )
                
                if self.check_video_output(output_path):
                    self.log_test_result("sandwich_v2", "custom_sandwich", True, 
                                       "Generated custom sandwich message", output_path)
                else:
                    self.log_test_result("sandwich_v2", "custom_sandwich", False, 
                                       "Video file invalid or missing")
                    
            except Exception as e:
                self.log_test_result("sandwich_v2", "custom_sandwich", False, 
                                   f"Exception: {str(e)}")
                
        except ImportError as e:
            self.log_test_result("sandwich_v2", "import_test", False, f"Import failed: {e}")
        except Exception as e:
            self.log_test_result("sandwich_v2", "general_error", False, f"Unexpected error: {e}")

    async def test_chaos_generator_v2(self):
        """Test chaos_generator_v2.py with multiple scenarios"""
        print("\n🧪 Testing Chaos Generator V2...")
        
        try:
            from chaos_generator_v2 import EnhancedChaosGenerator
            generator = EnhancedChaosGenerator()
            
            # Test 1: Random chaos mode
            test_output = str(self.output_dir / "chaos_test1_random.mp4")
            try:
                output_path = await generator.generate_chaos_video(
                    chaos_type="random_chaos",
                    output_path=test_output,
                    style="neon_glitch"
                )
                
                if self.check_video_output(output_path):
                    self.log_test_result("chaos_v2", "random_chaos", True, 
                                       "Generated random chaos video", output_path)
                else:
                    self.log_test_result("chaos_v2", "random_chaos", False, 
                                       "Video file invalid or missing")
                    
            except Exception as e:
                self.log_test_result("chaos_v2", "random_chaos", False, 
                                   f"Exception: {str(e)}")
            
            # Test 2: Text chaos mode
            test_output = str(self.output_dir / "chaos_test2_text.mp4")
            try:
                output_path = await generator.generate_chaos_video(
                    chaos_type="text_chaos",
                    output_path=test_output,
                    style="retro_vaporwave"
                )
                
                if self.check_video_output(output_path):
                    self.log_test_result("chaos_v2", "text_chaos", True, 
                                       "Generated text chaos video", output_path)
                else:
                    self.log_test_result("chaos_v2", "text_chaos", False, 
                                       "Video file invalid or missing")
                    
            except Exception as e:
                self.log_test_result("chaos_v2", "text_chaos", False, 
                                   f"Exception: {str(e)}")
            
            # Test 3: Visual chaos mode
            test_output = str(self.output_dir / "chaos_test3_visual.mp4")
            try:
                output_path = await generator.generate_chaos_video(
                    chaos_type="visual_chaos",
                    output_path=test_output,
                    style="psychedelic"
                )
                
                if self.check_video_output(output_path):
                    self.log_test_result("chaos_v2", "visual_chaos", True, 
                                       "Generated visual chaos video", output_path)
                else:
                    self.log_test_result("chaos_v2", "visual_chaos", False, 
                                       "Video file invalid or missing")
                    
            except Exception as e:
                self.log_test_result("chaos_v2", "visual_chaos", False, 
                                   f"Exception: {str(e)}")
                
        except ImportError as e:
            self.log_test_result("chaos_v2", "import_test", False, f"Import failed: {e}")
        except Exception as e:
            self.log_test_result("chaos_v2", "general_error", False, f"Unexpected error: {e}")

    def test_confession_simplified(self):
        """Test the simplified confession generator"""
        print("\n🧪 Testing Simplified Confession Generator...")
        
        try:
            from confession_generator_v2_simplified import SimplifiedConfessionGenerator
            generator = SimplifiedConfessionGenerator()
            
            # Test simplified version with basic confession
            test_output = str(self.output_dir / "confession_simplified_test.mp4")
            try:
                output_path = generator.generate_confession_video(
                    message_text="I actually like pineapple on pizza and I'm not sorry about it!",
                    output_path=test_output
                )
                
                if self.check_video_output(output_path):
                    self.log_test_result("confession_simplified", "basic_test", True, 
                                       "Generated simplified confession video", output_path)
                else:
                    self.log_test_result("confession_simplified", "basic_test", False, 
                                       "Video file invalid or missing")
                    
            except Exception as e:
                self.log_test_result("confession_simplified", "basic_test", False, 
                                   f"Exception: {str(e)}")
                
        except ImportError as e:
            self.log_test_result("confession_simplified", "import_test", False, f"Import failed: {e}")
        except Exception as e:
            self.log_test_result("confession_simplified", "general_error", False, f"Unexpected error: {e}")

    def generate_test_report(self):
        """Generate a comprehensive test report"""
        print("\n" + "="*80)
        print("🧪 V2 GENERATOR TEST RESULTS SUMMARY")
        print("="*80)
        
        total_tests = 0
        passed_tests = 0
        
        for generator, tests in self.results.items():
            print(f"\n📱 {generator.upper()}")
            print("-" * 40)
            
            for test in tests:
                total_tests += 1
                status = "✅ PASS" if test['success'] else "❌ FAIL"
                print(f"  {status}: {test['test']}")
                if test['message']:
                    print(f"    → {test['message']}")
                if test['output_path'] and test['success']:
                    print(f"    → Output: {test['output_path']}")
                    
                if test['success']:
                    passed_tests += 1
        
        print(f"\n" + "="*80)
        print(f"🎯 OVERALL RESULTS: {passed_tests}/{total_tests} tests passed")
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"📊 Success Rate: {success_rate:.1f}%")
        print("="*80)
        
        return success_rate > 75  # Consider 75%+ a passing grade

    async def run_all_tests(self):
        """Run all V2 generator tests"""
        print("🚀 Starting comprehensive V2 generator testing...")
        print(f"📁 Test outputs will be saved to: {self.output_dir}")
        
        # Test each generator
        await self.test_validation_generator_v2()
        await self.test_confession_generator_v2()
        await self.test_tips_generator_v2()
        await self.test_sandwich_generator_v2()
        await self.test_chaos_generator_v2()
        self.test_confession_simplified()
        
        # Generate final report
        success = self.generate_test_report()
        
        if success:
            print("\n🎉 Testing completed successfully! Most generators are working properly.")
        else:
            print("\n⚠️ Testing completed with issues. Some generators need attention.")
            
        return success

async def main():
    """Main test execution"""
    tester = V2GeneratorTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())