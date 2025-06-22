#!/usr/bin/env python3
"""
Test API Integration for SAFE
============================

Simple test to verify Claude API integration is working.
"""

import os
import sys
from pathlib import Path

# Add oversight to path
sys.path.insert(0, str(Path(__file__).parent))

from oversight.model import get_model


def test_api_integration():
    """Test Claude API integration."""
    print("🧪 Testing Claude API Integration...")

    # Check if API key is set
    api_key = os.getenv("CLAUDE_API_KEY")
    if not api_key:
        print("❌ CLAUDE_API_KEY not set in environment")
        return False

    print(f"✅ API Key found: {api_key[:20]}...")

    # Test model initialization
    try:
        model = get_model()
        print("✅ Model initialized successfully")
    except Exception as e:
        print(f"❌ Model initialization failed: {e}")
        return False

    # Test simple API call
    try:
        print("🔄 Testing API call...")
        response = model.ask("Say 'Hello, World!'")
        print(f"✅ API call successful: {response[:50]}...")
        return True
    except Exception as e:
        print(f"❌ API call failed: {e}")
        return False


def test_humaneval_integration():
    """Test HumanEval integration with real API."""
    print("\n🧪 Testing HumanEval Integration...")

    try:
        import asyncio

        from oversight.features.humaneval_integration import (
            AsyncHumanEvalRunner,
        )

        # Create runner with real API
        runner = AsyncHumanEvalRunner(
            max_concurrent=1,
            requests_per_minute=10,
            progressive_sampling=False,
            use_mock=False,
        )

        print("✅ HumanEval runner created")

        # Test single task
        async def test_single_task():
            tasks = runner.tasks[:1]  # Just first task
            if tasks:
                task = tasks[0]
                print(f"🔄 Testing task: {task.task_id}")

                solution = await runner.generate_solution(
                    task, temperature=0.7
                )
                print(f"✅ Generated solution: {solution[:100]}...")

                result = runner.evaluate_solution(task, solution)
                print(f"✅ Evaluation result: {result.ratio:.3f}")

                return result.ratio > 0
            return False

        # Run test
        result = asyncio.run(test_single_task())
        return result

    except Exception as e:
        print(f"❌ HumanEval integration failed: {e}")
        return False


def main():
    """Main test function."""
    print("🚀 SAFE API Integration Test")
    print("=" * 50)

    # Test basic API integration
    api_ok = test_api_integration()

    if api_ok:
        # Test HumanEval integration
        humaneval_ok = test_humaneval_integration()

        if humaneval_ok:
            print("\n🎉 All tests passed! API integration is working.")
            return True
        else:
            print("\n⚠️ API integration works, but HumanEval needs attention.")
            return False
    else:
        print("\n❌ API integration failed. Check your API key.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
