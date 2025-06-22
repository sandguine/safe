#!/usr/bin/env python3
"""
GitHub Actions verification script for Claude API setup
Checks if the API key is available in GitHub Actions environment
"""

import os
import sys
from pathlib import Path


def check_github_environment():
    """Check if we're running in GitHub Actions"""
    print("=== GitHub Actions Environment Check ===")

    if os.getenv("GITHUB_ACTIONS"):
        print("✅ Running in GitHub Actions")
        print(f"   Workflow: {os.getenv('GITHUB_WORKFLOW', 'Unknown')}")
        print(f"   Run ID: {os.getenv('GITHUB_RUN_ID', 'Unknown')}")
        return True
    else:
        print("❌ Not running in GitHub Actions")
        print("   This script is designed for GitHub Actions CI/CD")
        return False


def check_api_key():
    """Check if API key is available in GitHub Actions"""
    print("\n=== API Key Check ===")
    api_key = os.getenv("CLAUDE_API_KEY")

    if not api_key:
        print("❌ CLAUDE_API_KEY is not set in GitHub Actions")
        print("   Please add it as a repository secret:")
        print("   1. Go to repository Settings")
        print("   2. Secrets and variables → Actions")
        print("   3. Add repository secret: CLAUDE_API_KEY")
        return False

    if not api_key.startswith("sk-"):
        print("❌ API key format looks wrong (should start with 'sk-')")
        return False

    print(f"✅ API key found: {api_key[:10]}...{api_key[-4:]}")
    return True


def check_dependencies():
    """Check if required packages are installed"""
    print("\n=== Dependencies Check ===")

    required_packages = ["requests", "pathlib", "dotenv", "anthropic"]

    for package in required_packages:
        try:
            if package == "dotenv":
                __import__("dotenv")
            else:
                __import__(package)
            print(f"✅ {package} is available")
        except ImportError:
            print(f"❌ {package} is missing")
            return False

    return True


def check_model_import():
    """Check if we can import the model module"""
    print("\n=== Model Import Check ===")

    oversight_path = Path(__file__).parent / "oversight"
    if not oversight_path.exists():
        print("❌ oversight/ directory not found")
        return False

    sys.path.insert(0, str(oversight_path))

    try:
        import model  # noqa: F401

        print("✅ Successfully imported model module from oversight/")
        return True
    except Exception as e:
        print(f"❌ Failed to import model: {e}")
        return False


def test_api_request():
    """Test actual API request in GitHub Actions"""
    print("\n=== API Request Test ===")

    if not check_api_key():
        return False

    try:
        oversight_path = Path(__file__).parent / "oversight"
        sys.path.insert(0, str(oversight_path))
        import model

        print("   Sending test request...")
        response = model.ask("Say 'GitHub Actions test' and nothing else.")

        print("✅ API request successful!")
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
    """Run all verification steps for GitHub Actions"""
    print("🔍 GitHub Actions Claude API Setup Verification\n")

    # First check if we're in GitHub Actions
    if not check_github_environment():
        print("\n⚠️  This script is designed for GitHub Actions.")
        print("   For local development, use: python verify_setup.py")
        return 1

    steps = [
        ("API Key", check_api_key),
        ("Dependencies", check_dependencies),
        ("Model Import", check_model_import),
        ("API Request", test_api_request),
    ]

    results = []
    for step_name, step_func in steps:
        try:
            result = step_func()
            results.append((step_name, result))
        except Exception as e:
            print(f"❌ Error in {step_name}: {e}")
            results.append((step_name, False))

    print("\n" + "=" * 50)
    print("📊 GITHUB ACTIONS VERIFICATION SUMMARY")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for step_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{step_name:15} {status}")

    print(f"\nOverall: {passed}/{total} steps passed")

    if passed == total:
        print("\n🎉 SUCCESS! GitHub Actions setup is working correctly.")
        print("   Your CI/CD pipeline can now use the Claude API.")
        return 0
    else:
        print("\n⚠️  Some issues found. Please fix them before proceeding.")
        print("   Check the error messages above for guidance.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
