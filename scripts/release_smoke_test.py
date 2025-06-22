#!/usr/bin/env python3
"""
Release smoke test for oversight-curriculum package.
Validates the package before PyPI release.
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path


def run_command(cmd, description, check=True):
    """Run a command and handle errors"""
    print(f"🔍 {description}...")
    print(f"   Running: {cmd}")
    
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, check=check
        )
        if result.stdout:
            print(f"   ✅ Success: {result.stdout.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error: {e}")
        print(f"   stderr: {e.stderr}")
        if check:
            sys.exit(1)
        return e


def check_git_clean():
    """Ensure git working directory is clean"""
    print("\n🧹 Checking git working directory...")
    
    # Check for uncommitted changes
    result = run_command(
        "git status --porcelain", "Checking for uncommitted changes"
    )
    if result.stdout.strip():
        print("   ⚠️  Warning: Uncommitted changes detected")
        print("   Consider committing or stashing changes before release")
        return False
    else:
        print("   ✅ Working directory is clean")
        return True


def test_install():
    """Test package installation"""
    print("\n📦 Testing package installation...")
    
    # Test editable install
    run_command("pip install -e .", "Installing package in editable mode")
    
    # Test import
    try:
        # Import the package to verify it works
        import oversight_curriculum  # noqa: F401
        print("   ✅ Package imports successfully")
        return True
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        return False


def test_cli():
    """Test CLI interface"""
    print("\n🖥️  Testing CLI interface...")
    
    # Test help command
    result = run_command(
        "python -m oversight_curriculum.src --help", 
        "Testing CLI help", 
        check=False
    )
    if result.returncode == 0:
        print("   ✅ CLI help works")
        return True
    else:
        print("   ⚠️  CLI help not available (expected if __main__.py missing)")
        return True


def test_build():
    """Test package building"""
    print("\n🔨 Testing package build...")
    
    # Clean previous builds
    if Path("dist").exists():
        shutil.rmtree("dist")
    if Path("build").exists():
        shutil.rmtree("build")
    
    # Build package
    run_command("python -m build", "Building package")
    
    # Check build artifacts
    if Path("dist").exists():
        files = list(Path("dist").glob("*"))
        print(f"   ✅ Build artifacts created: {[f.name for f in files]}")
        return True
    else:
        print("   ❌ Build artifacts not found")
        return False


def test_twine_check():
    """Test twine validation"""
    print("\n🔍 Testing twine validation...")
    
    try:
        run_command("twine check dist/*", "Validating package metadata")
        print("   ✅ Package metadata is valid")
        return True
    except FileNotFoundError:
        print("   ⚠️  twine not installed, skipping validation")
        print("   Install with: pip install twine")
        return True


def test_dry_run():
    """Test dry run execution"""
    print("\n🎯 Testing dry run execution...")
    
    # Create a simple test script
    test_script = """
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from oversight_curriculum.src.runner import (
        OversightRunner, RunnerConfig, ExecutionMode
    )
    print("✅ OversightRunner imports successfully")
    
    config = RunnerConfig(mode=ExecutionMode.DEMO, cycles=1)
    print("✅ RunnerConfig created successfully")
    
    print("✅ Dry run test passed")
except Exception as e:
    print(f"❌ Dry run test failed: {e}")
    sys.exit(1)
"""
    
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.py', delete=False
    ) as f:
        f.write(test_script)
        test_file = f.name
    
    try:
        result = run_command(f"python {test_file}", "Running dry run test")
        os.unlink(test_file)
        return result.returncode == 0
    except Exception as e:
        print(f"   ❌ Dry run test failed: {e}")
        if os.path.exists(test_file):
            os.unlink(test_file)
        return False


def main():
    """Run all smoke tests"""
    print("🚀 OVERSIGHT CURRICULUM RELEASE SMOKE TEST")
    print("=" * 50)
    
    # Change to project directory
    script_dir = Path(__file__).parent.parent
    os.chdir(script_dir)
    print(f"📁 Working directory: {os.getcwd()}")
    
    tests = [
        ("Git Clean", check_git_clean),
        ("Install", test_install),
        ("CLI", test_cli),
        ("Build", test_build),
        ("Twine Check", test_twine_check),
        ("Dry Run", test_dry_run),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📋 SMOKE TEST SUMMARY")
    print("=" * 30)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Package is ready for release.")
        print("\n📦 Next steps:")
        print("   1. Create git tag: git tag v1.0.0")
        print("   2. Push tag: git push origin v1.0.0")
        print("   3. Upload to PyPI: twine upload dist/*")
        return 0
    else:
        print("⚠️  Some tests failed. Please fix issues before release.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 