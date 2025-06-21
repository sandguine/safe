#!/usr/bin/env python3
"""
Comprehensive verification script for the Claude API setup
"""

import os
import sys
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Install with: pip install python-dotenv")

def check_api_key():
    """Step 1: Check if API key is set"""
    print("=== Step 1: Checking API Key ===")
    api_key = os.getenv("CLAUDE_API_KEY")
    
    if not api_key:
        print("❌ CLAUDE_API_KEY is not set")
        print("   Please set it with one of these methods:")
        print("   - export CLAUDE_API_KEY='your-key-here'")
        print("   - set CLAUDE_API_KEY=your-key-here (Windows)")
        print("   - Or create a .env file with CLAUDE_API_KEY=your-key-here")
        return False
    
    if not api_key.startswith("sk-"):
        print("❌ API key format looks wrong (should start with 'sk-')")
        return False
    
    print(f"✅ API key found: {api_key[:10]}...{api_key[-4:]}")
    return True

def check_dependencies():
    """Step 2: Check if required packages are installed"""
    print("\n=== Step 2: Checking Dependencies ===")
    
    required_packages = ['requests', 'pathlib', 'dotenv']
    
    for package in required_packages:
        try:
            if package == 'dotenv':
                __import__('dotenv')
            else:
                __import__(package)
            print(f"✅ {package} is available")
        except ImportError:
            print(f"❌ {package} is missing")
            print(f"   Run: pip install {package}")
            return False
    
    return True

def check_model_import():
    """Step 3: Check if we can import the model module"""
    print("\n=== Step 3: Checking Model Import ===")
    
    # Add src to path
    src_path = Path(__file__).parent / "src"
    if not src_path.exists():
        print("❌ src/ directory not found")
        return False
    
    sys.path.insert(0, str(src_path))
    
    try:
        import model
        print("✅ Successfully imported model module")
        return True
    except Exception as e:
        print(f"❌ Failed to import model: {e}")
        return False

def test_api_request():
    """Step 4: Test actual API request"""
    print("\n=== Step 4: Testing API Request ===")
    
    if not check_api_key():
        return False
    
    try:
        import model
        
        # Test with a very simple prompt
        print("   Sending test request...")
        response = model.ask("Say 'test' and nothing else.")
        
        print(f"✅ API request successful!")
        print(f"   Response: '{response.strip()}'")
        return True
        
    except Exception as e:
        print(f"❌ API request failed: {e}")
        print("   This could be due to:")
        print("   - Invalid API key")
        print("   - Network issues")
        print("   - API rate limits")
        return False

def main():
    """Run all verification steps"""
    print("🔍 Claude API Setup Verification\n")
    
    steps = [
        ("API Key", check_api_key),
        ("Dependencies", check_dependencies),
        ("Model Import", check_model_import),
        ("API Request", test_api_request)
    ]
    
    results = []
    for step_name, step_func in steps:
        try:
            result = step_func()
            results.append((step_name, result))
        except Exception as e:
            print(f"❌ Error in {step_name}: {e}")
            results.append((step_name, False))
    
    print("\n" + "="*50)
    print("📊 VERIFICATION SUMMARY")
    print("="*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for step_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{step_name:15} {status}")
    
    print(f"\nOverall: {passed}/{total} steps passed")
    
    if passed == total:
        print("\n🎉 SUCCESS! Your Claude API setup is working correctly.")
        print("   You can now proceed with the main project.")
    else:
        print("\n⚠️  Some issues found. Please fix them before proceeding.")
        print("   Check the error messages above for guidance.")

if __name__ == "__main__":
    main() 