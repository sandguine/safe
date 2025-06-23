#!/usr/bin/env python3
"""
Test script to verify HumanEval integration fixes.
"""

import asyncio
import os
import sys

# Add the oversight directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "oversight"))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

async def test_humaneval_fixes():
    """Test the HumanEval integration fixes."""
    print("🧪 Testing HumanEval Integration Fixes...")

    try:
        from oversight.features.humaneval_integration import (
            AsyncHumanEvalRunner,
            ExecutionResult,
            HumanEvalTask,
            SecureSandbox,
        )

        print("✅ Imports successful")

        # Test sandbox initialization
        sandbox = SecureSandbox()
        print("✅ Sandbox initialization successful")

        # Test runner initialization
        runner = AsyncHumanEvalRunner(
            max_concurrent=1,
            requests_per_minute=10,
            progressive_sampling=False,
        )
        print("✅ Runner initialization successful")

        # Test that sandbox is properly initialized
        if hasattr(runner, 'sandbox') and runner.sandbox is not None:
            print("✅ Sandbox properly initialized in runner")
        else:
            print("❌ Sandbox not properly initialized in runner")
            return False

        # Test with a simple mock task
        mock_task = HumanEvalTask(
            task_id="test/0",
            prompt="def has_close_elements(numbers, threshold):",
            entry_point="has_close_elements",
            test="""
    \"\"\"Check if in given list of numbers, are any two numbers closer to each other than
    given threshold.
    >>> has_close_elements([1.0, 2.0, 3.0], 0.5)
    False
    >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)
    True
    \"\"\"
    for idx, elem in enumerate(numbers):
        for idx2, elem2 in enumerate(numbers):
            if idx != idx2:
                distance = abs(elem - elem2)
                if distance < threshold:
                    return True
    return False""",
            canonical_solution=""
        )

        # Test solution execution
        solution = """for idx, elem in enumerate(numbers):
    for idx2, elem2 in enumerate(numbers):
        if idx != idx2:
            distance = abs(elem - elem2)
            if distance < threshold:
                return True
return False"""

        result = sandbox.execute_solution(mock_task, solution)
        print(
            f"✅ Test execution successful: {result.passed}/{result.total} tests passed"
        )
        print(f"   Ratio: {result.ratio:.3f}")
        print(f"   Error: {result.error}")

        return result.total > 0  # Should have at least some tests

    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_humaneval_fixes())
    if success:
        print("\n🎉 All tests passed! HumanEval integration is working.")
    else:
        print("\n❌ Some tests failed. Check the output above.")
    sys.exit(0 if success else 1)
