#!/usr/bin/env python3
"""
Test script to verify Claude API key and debug model.py issues
"""

import os
import sys
from pathlib import Path

# Add src to path so we can import model
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_api_key():
    """Test if the API key is properly set"""
    api_key = os.getenv("CLAUDE_API_KEY")
    
    print("=== API Key Test ===")
    if not api_key:
        print("❌ CLAUDE_API_KEY environment variable is not set")
        print("   Please set it with: export CLAUDE_API_KEY='your-key-here'")
        return False
    
    if not api_key.startswith("sk-"):
        print("❌ API key doesn't start with 'sk-' - this might be invalid")
        return False
    
    print(f"✅ API key found: {api_key[:10]}...{api_key[-4:]}")
    return True

def test_model_import():
    """Test if we can import the model module"""
    print("\n=== Model Import Test ===")
    try:
        import model
        print("✅ Successfully imported model module")
        return True
    except Exception as e:
        print(f"❌ Failed to import model: {e}")
        return False

def test_simple_request():
    """Test a simple API request"""
    print("\n=== Simple API Request Test ===")
    
    if not test_api_key():
        return False
    
    try:
        import model
        
        # Test with a simple prompt
        response = model.ask("Say 'Hello, world!' in one word.", model="claude-3-haiku-20240307")
        print(f"✅ API request successful!")
        print(f"   Response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ API request failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing Claude API setup...\n")
    
    tests = [
        test_api_key,
        test_model_import,
        test_simple_request
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"=== Summary ===")
    print(f"Passed: {passed}/{len(tests)} tests")
    
    if passed == len(tests):
        print("🎉 All tests passed! Your API setup is working correctly.")
    else:
        print("❌ Some tests failed. Please fix the issues above.")

if __name__ == "__main__":
    main() 