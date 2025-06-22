#!/usr/bin/env python3
"""
Simple test to verify the Claude API is working
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    # Check API key
    api_key = os.getenv("CLAUDE_API_KEY")
    if not api_key:
        print("❌ Please set CLAUDE_API_KEY environment variable")
        print("   export CLAUDE_API_KEY='your-key-here'")
        return
    
    print(f"✅ API key found: {api_key[:10]}...{api_key[-4:]}")
    
    # Test the model
    try:
        import model
        print("✅ Model imported successfully")
        
        # Test a simple request
        response = model.ask("Say 'Hello' in one word.")
        print(f"✅ API response: {response}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 