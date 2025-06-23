#!/usr/bin/env python3
"""
API Setup Script for SAFE
=========================

Helps users configure their Claude API key for the SAFE demo.
"""

import os
import sys
from pathlib import Path


def setup_api_key():
    """Interactive setup for API key."""
    print("🔧 SAFE API Key Setup")
    print("=" * 30)
    print()

    # Check if already configured
    if os.getenv("CLAUDE_API_KEY"):
        print("✅ API key already configured!")
        print(f"   Found: {os.getenv('CLAUDE_API_KEY')[: 8]}..."
              f"{os.getenv('CLAUDE_API_KEY')[-4: ]}")
        return True

    print("To run the SAFE demo with real model integration, you need a "
          "Claude API key.")
    print()
    print("📋 Steps to get your API key: ")
    print("1. Go to https: //console.anthropic.com/")
    print("2. Sign up or log in to your account")
    print("3. Navigate to 'API Keys' section")
    print("4. Create a new API key")
    print("5. Copy the key (it starts with 'sk-ant-')")
    print()

    # Ask user for API key
    api_key = input("🔑 Enter your Claude API key (or press Enter to skip): ").strip()

    if not api_key:
        print("\n⚠️  No API key provided. You can: ")
        print("   - Run this script again later")
        print("   - Set CLAUDE_API_KEY environment variable manually")
        print("   - Create a .env file with CLAUDE_API_KEY=your-key")
        return False

    # Validate API key format
    if not api_key.startswith("sk-ant-"):
        print(
            "\n❌ Invalid API key format. Claude API keys start with 'sk-ant-'")
        return False

    # Save to .env file
    env_file = Path(".env")
    try:
        with open(env_file, "w") as f:
            f.write(f"CLAUDE_API_KEY={api_key}\n")
        print(f"\n✅ API key saved to {env_file}")
        print("   The key will be loaded automatically when you run the demo.")
        return True

    except Exception as e:
        print(f"\n❌ Failed to save API key: {e}")
        print("   You can manually create a .env file with: ")
        print(f"   CLAUDE_API_KEY={api_key}")
        return False


def main():
    """Main function."""
    success = setup_api_key()
    if success:
        print("\n🎉 Setup complete! You can now run: ")
        print("   python enhanced_demo.py")
    else:
        print("\n⚠️  Setup incomplete. Please configure your API key before "
              "running the demo.")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
