#!/usr/bin/env python3
"""
API Key Checker for SAFE
========================

Verifies that the Claude API key is properly configured and tests real
model access.
"""

import os
import sys
from pathlib import Path

# Add oversight to path
sys.path.insert(0, str(Path(__file__).parent))

from oversight.model import get_model


def check_api_key():
    """Check if API key is configured and test real model access."""
    print("🔍 Checking Claude API Configuration")
    print("=" * 40)

    # Check environment variable
    api_key = os.getenv("CLAUDE_API_KEY")
    if not api_key:
        print("❌ CLAUDE_API_KEY not found in environment")
        print("\nTo set up your API key:")
        print("1. Get your API key from https://console.anthropic.com/")
        print("2. Create a .env file in the project root:")
        print("   echo 'CLAUDE_API_KEY=your-key-here' > .env")
        print("3. Or set it in your shell:")
        print("   export CLAUDE_API_KEY='your-key-here'")
        return False

    print(f"✅ CLAUDE_API_KEY found: {api_key[:8]}...{api_key[-4:]}")

    # Test model initialization
    try:
        print("\n🧪 Testing model initialization...")
        model = get_model(use_mock=False)
        print("✅ Model initialized successfully")

        # Test a simple API call
        print("\n🧪 Testing API call...")
        response = model.ask("Say 'Hello, SAFE!'", temperature=0.1)
        print(f"✅ API call successful: {response[:50]}...")

        print("\n🎉 All checks passed! Ready to run enhanced demo.")
        return True

    except Exception as e:
        print(f"❌ API test failed: {e}")
        print("\nTroubleshooting:")
        print("1. Verify your API key is correct")
        print("2. Check your internet connection")
        print("3. Ensure you have sufficient API credits")
        print("4. Try again in a few minutes if rate limited")
        return False


def main():
    """Main function."""
    success = check_api_key()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
