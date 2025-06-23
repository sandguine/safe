#!/usr/bin/env python3
"""
Test Environment Loading
=======================

Simple test to verify .env file loading and API key availability.
"""

import os
import sys

# Load environment variables from .env file first
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded environment variables from .env file")
except ImportError:
    print("⚠️ python-dotenv not installed, using system environment variables")
except Exception as e:
    print(f"⚠️ Error loading .env file: {e}")

# Check API key
api_key = os.getenv("CLAUDE_API_KEY")
if api_key:
    # Mask API key for display
    masked_key = (f"{api_key[:8]}...{api_key[-4:]}"
                 if len(api_key) > 12 else "***")
    print(f"✅ API key found: {masked_key}")

    # Check format
    if api_key.startswith("sk-ant-"):
        print("✅ API key format appears valid")
    else:
        print("❌ API key format appears invalid")
else:
    print("❌ No API key found")

print("🔧 Environment loading test completed")
