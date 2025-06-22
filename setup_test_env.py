#!/usr/bin/env python3
"""
Setup script for test environment.
Handles API key configuration for CI and local testing.
"""

import os
import sys
from pathlib import Path


def setup_test_env():
    """Set up test environment with proper API key handling."""
    
    # Check if we're in CI
    is_ci = os.getenv("CI") == "true"
    
    if is_ci:
        print("🔧 Setting up CI environment...")
        # In CI, use dummy key if real one not available
        if not os.getenv("CLAUDE_API_KEY"):
            os.environ["CLAUDE_API_KEY"] = "dummy-key-for-ci"
            print("⚠️  Using dummy API key for CI (tests will be skipped)")
    else:
        print("🔧 Setting up local environment...")
        # Check for real API key
        if not os.getenv("CLAUDE_API_KEY"):
            print("❌ CLAUDE_API_KEY not set")
            print("   Set it with: export CLAUDE_API_KEY=your-key-here")
            print("   Or create a .env file with: "
                  "CLAUDE_API_KEY=your-key-here")
            return False
        else:
            print("✅ CLAUDE_API_KEY found")
    
    # Set up test-specific environment variables
    os.environ["TESTING"] = "true"
    os.environ["PYTHONPATH"] = str(Path(__file__).parent)
    
    print("✅ Test environment ready")
    return True


if __name__ == "__main__":
    success = setup_test_env()
    sys.exit(0 if success else 1) 