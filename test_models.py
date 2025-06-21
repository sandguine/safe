#!/usr/bin/env python3
"""
Test multiple Claude model names to find which ones are available
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Common Claude model names to test
MODELS_TO_TEST = [
    "claude-3-haiku-20240307",
    "claude-3-haiku-20240229", 
    "claude-3-sonnet-20240229",
    "claude-3-opus-20240229",
    "claude-3-5-sonnet-20241022",
    "claude-3-5-haiku-20241022",
    "claude-3-5-opus-20241022"
]

def test_model(model_name):
    """Test if a specific model works"""
    try:
        import model
        
        # Override the default model
        response = model.ask("Say 'test'", model=model_name)
        return True, response
    except Exception as e:
        return False, str(e)

def main():
    print("🔍 Testing Claude Model Availability\n")
    
    api_key = os.getenv("CLAUDE_API_KEY")
    if not api_key:
        print("❌ No API key found. Please set CLAUDE_API_KEY in .env file")
        return
    
    print(f"✅ API key found: {api_key[:10]}...{api_key[-4:]}")
    print(f"Testing {len(MODELS_TO_TEST)} model names...\n")
    
    working_models = []
    
    for model_name in MODELS_TO_TEST:
        print(f"Testing: {model_name}")
        success, result = test_model(model_name)
        
        if success:
            print(f"✅ WORKING: {model_name}")
            print(f"   Response: {result}")
            working_models.append(model_name)
        else:
            print(f"❌ FAILED: {model_name}")
            print(f"   Error: {result}")
        print()
    
    print("="*50)
    print("📊 RESULTS SUMMARY")
    print("="*50)
    
    if working_models:
        print(f"✅ Found {len(working_models)} working model(s):")
        for model in working_models:
            print(f"   - {model}")
        print(f"\n💡 Use one of these in your model.py file")
    else:
        print("❌ No working models found")
        print("   This could mean:")
        print("   - Your API key doesn't have access to these models")
        print("   - You need to upgrade your Anthropic plan")
        print("   - Check the Anthropic console for available models")

if __name__ == "__main__":
    main() 