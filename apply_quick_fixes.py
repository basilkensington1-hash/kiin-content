#!/usr/bin/env python3
"""
Quick fix script to apply essential patches to V2 generators
Based on successful fixes from validation_generator_v2_fixed.py
"""

import os
import re
import shutil
from pathlib import Path

class QuickV2Fixer:
    """Apply quick fixes to V2 generators"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.src_dir = self.base_dir / "src"
        self.backup_dir = self.base_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
    def backup_file(self, filepath: Path) -> Path:
        """Create backup before modifying"""
        backup_path = self.backup_dir / f"{filepath.name}.backup"
        shutil.copy2(filepath, backup_path)
        print(f"📁 Backed up {filepath.name} to {backup_path}")
        return backup_path
    
    def add_directory_creation_fix(self, content: str) -> str:
        """Add directory creation before FFmpeg calls"""
        
        # Pattern 1: Look for subprocess.run with ffmpeg
        pattern1 = r'(\s*)(result\s*=\s*subprocess\.run\(\s*\[)'
        replacement1 = r'\1# Ensure output directory exists\n\1output_dir = Path(output_path).parent\n\1output_dir.mkdir(parents=True, exist_ok=True)\n\1\n\1\2'
        
        content = re.sub(pattern1, replacement1, content, flags=re.MULTILINE)
        
        # Pattern 2: Look for direct ffmpeg command construction
        pattern2 = r'(\s*)(cmd\s*=\s*\[\s*[\'"]ffmpeg[\'"])'
        replacement2 = r'\1# Ensure output directory exists\n\1if "output_path" in locals():\n\1    output_dir = Path(output_path).parent\n\1    output_dir.mkdir(parents=True, exist_ok=True)\n\1\n\1\2'
        
        content = re.sub(pattern2, replacement2, content, flags=re.MULTILINE)
        
        return content
    
    def add_error_handling(self, content: str) -> str:
        """Add basic error handling around complex operations"""
        
        # Add try-catch around video generation methods
        pattern = r'(def create_.*video.*\([^)]*\):)(.*?)(\n\s*return)'
        
        def add_try_catch(match):
            method_def = match.group(1)
            method_body = match.group(2)
            return_stmt = match.group(3)
            
            # Indent the method body
            indented_body = '\n'.join('        ' + line if line.strip() else line 
                                    for line in method_body.split('\n'))
            
            return f'''{method_def}
        try:{indented_body}
        except Exception as e:
            print(f"❌ Error in video generation: {{e}}")
            traceback.print_exc()
            raise{return_stmt}'''
        
        content = re.sub(pattern, add_try_catch, content, flags=re.DOTALL)
        
        return content
    
    def add_import_fixes(self, content: str) -> str:
        """Add missing imports that might be needed"""
        
        # Check if traceback import exists
        if 'import traceback' not in content:
            # Find the import section and add traceback
            import_pattern = r'(import\s+(?:os|sys|json|random).*?\n)'
            replacement = r'\1import traceback\n'
            content = re.sub(import_pattern, replacement, content, count=1)
        
        # Ensure Path import exists
        if 'from pathlib import Path' not in content and 'import Path' not in content:
            # Add to existing pathlib import if exists
            if 'from pathlib import' in content:
                content = content.replace(
                    'from pathlib import',
                    'from pathlib import Path,'
                ).replace('Path,', 'Path, ')
            else:
                # Add new import after other imports
                import_pattern = r'(import\s+(?:os|sys|json).*?\n)'
                replacement = r'\1from pathlib import Path\n'
                content = re.sub(import_pattern, replacement, content, count=1)
        
        return content
    
    def apply_fixes_to_generator(self, generator_file: str) -> bool:
        """Apply all fixes to a specific generator"""
        try:
            filepath = self.src_dir / generator_file
            
            if not filepath.exists():
                print(f"⚠️ File not found: {generator_file}")
                return False
            
            print(f"🔧 Applying fixes to {generator_file}...")
            
            # Backup original
            self.backup_file(filepath)
            
            # Read content
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Apply fixes
            print("   → Adding import fixes...")
            content = self.add_import_fixes(content)
            
            print("   → Adding directory creation fixes...")
            content = self.add_directory_creation_fix(content)
            
            print("   → Adding error handling...")
            content = self.add_error_handling(content)
            
            # Write back
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Fixes applied to {generator_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error applying fixes to {generator_file}: {e}")
            return False
    
    def apply_quick_fixes_to_all(self):
        """Apply quick fixes to all V2 generators"""
        
        generators_to_fix = [
            'confession_generator_v2.py',
            'tips_generator_v2.py',
            'sandwich_generator_v2.py', 
            'chaos_generator_v2.py',
            'validation_generator_v2.py'  # Original version
        ]
        
        print("🚀 Applying quick fixes to all V2 generators...")
        print(f"📁 Backups will be saved to: {self.backup_dir}")
        
        results = []
        
        for generator in generators_to_fix:
            success = self.apply_fixes_to_generator(generator)
            results.append((generator, success))
        
        # Summary
        print("\n" + "="*60)
        print("📊 QUICK FIX RESULTS")
        print("="*60)
        
        successful = 0
        for generator, success in results:
            status = "✅ FIXED" if success else "❌ FAILED"
            print(f"{status} {generator}")
            if success:
                successful += 1
        
        print(f"\n🎯 Results: {successful}/{len(results)} generators fixed")
        
        if successful > 0:
            print("\n⚠️ IMPORTANT:")
            print("1. Test each fixed generator individually")
            print("2. The fixes are basic - some generators may need manual tuning")
            print("3. Use validation_generator_v2_fixed.py as the gold standard")
            print("4. Restore from backups if issues occur")
            print(f"5. Backups available in: {self.backup_dir}")
        
        return successful == len(results)
    
    def create_test_script_for_fixed_generators(self):
        """Create a test script for the newly fixed generators"""
        
        test_script = '''#!/usr/bin/env python3
"""
Test script for quick-fixed V2 generators
"""

import asyncio
import os
import sys
import traceback
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_fixed_generators():
    """Test all quick-fixed generators"""
    print("🧪 Testing Quick-Fixed V2 Generators...")
    
    test_cases = [
        {
            'module': 'confession_generator_v2',
            'class': 'EnhancedConfessionGenerator',
            'method': 'generate_confession_video',
            'kwargs': {'category': 'general', 'output_path': 'output/test_confession_fixed.mp4'}
        },
        {
            'module': 'tips_generator_v2', 
            'class': 'EnhancedTipsGenerator',
            'method': 'generate_tips_video',
            'kwargs': {'category': 'productivity', 'output_path': 'output/test_tips_fixed.mp4'}
        },
        {
            'module': 'sandwich_generator_v2',
            'class': 'EnhancedSandwichGenerator', 
            'method': 'generate_sandwich_video',
            'kwargs': {'category': 'daily_compliments', 'output_path': 'output/test_sandwich_fixed.mp4'}
        },
        {
            'module': 'chaos_generator_v2',
            'class': 'EnhancedChaosGenerator',
            'method': 'generate_chaos_video', 
            'kwargs': {'chaos_type': 'random_chaos', 'output_path': 'output/test_chaos_fixed.mp4'}
        }
    ]
    
    results = []
    
    for test in test_cases:
        print(f"\\n🔧 Testing {test['module']}...")
        
        try:
            # Import module
            module = __import__(test['module'])
            generator_class = getattr(module, test['class'])
            
            # Create instance
            generator = generator_class()
            
            # Get method
            method = getattr(generator, test['method'])
            
            # Call method (handle both sync and async)
            if asyncio.iscoroutinefunction(method):
                result = await method(**test['kwargs'])
            else:
                result = method(**test['kwargs'])
            
            # Check result
            if result and os.path.exists(result):
                size = os.path.getsize(result)
                print(f"✅ {test['module']} - SUCCESS ({size} bytes)")
                results.append((test['module'], True, result))
            else:
                print(f"❌ {test['module']} - No output file")
                results.append((test['module'], False, "No output"))
                
        except Exception as e:
            print(f"❌ {test['module']} - ERROR: {e}")
            results.append((test['module'], False, str(e)))
    
    # Summary
    print("\\n" + "="*60)
    print("📊 QUICK FIX TEST RESULTS") 
    print("="*60)
    
    passed = sum(1 for _, success, _ in results if success)
    
    for module, success, info in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {module}")
        if success:
            print(f"    → {info}")
        else:
            print(f"    → Error: {info}")
    
    print(f"\\n🎯 Results: {passed}/{len(results)} generators working")
    
    return passed > 0

if __name__ == "__main__":
    asyncio.run(test_fixed_generators())
'''
        
        test_file = self.base_dir / "test_quick_fixed_generators.py"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_script)
        
        print(f"📝 Created test script: {test_file}")
        return test_file

def main():
    """Main function"""
    print("🔧 Kiin Content Factory V2 Generator Quick Fixer")
    print("="*60)
    
    fixer = QuickV2Fixer()
    
    # Apply fixes
    success = fixer.apply_quick_fixes_to_all()
    
    if success:
        print("\n✨ All generators have been patched!")
        
        # Create test script
        test_script = fixer.create_test_script_for_fixed_generators()
        
        print("\n📋 Next steps:")
        print(f"1. Run: python {test_script.name}")
        print("2. Check individual generator outputs")
        print("3. Fine-tune any generators that still have issues")
        print("4. Use validation_generator_v2_fixed.py as reference")
        
    else:
        print("\n⚠️ Some generators couldn't be automatically fixed")
        print("Manual intervention may be required")

if __name__ == "__main__":
    main()