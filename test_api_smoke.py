#!/usr/bin/env python3
"""
API Smoke Test for Fixed Multi-Model Evaluation
===============================================

This script performs a quick smoke test to verify:
1. API key is loaded correctly
2. API client can make real calls
3. Scaling factors are calculated correctly
4. No mock mode is enabled
"""

import asyncio
import os
import sys
import time
from pathlib import Path

# Load environment variables from .env file first
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded environment variables from .env file")
except ImportError:
    print("⚠️ python-dotenv not installed, using system environment variables")
except Exception as e:
    print(f"⚠️ Error loading .env file: {e}")

# Add oversight to path
sys.path.insert(0, str(Path(__file__).parent))

from fixed_multi_model_evaluation import FixedMultiModelEvaluator


async def smoke_test():
    """Run a comprehensive smoke test."""

    print("🧪 API Smoke Test for Fixed Multi-Model Evaluation")
    print("=" * 60)

    # Test 1: Check API key
    print("\n🔑 Test 1: API Key Verification")
    print("-" * 40)

    api_key = os.getenv("CLAUDE_API_KEY")
    if not api_key:
        print("❌ FAIL: CLAUDE_API_KEY environment variable not found")
        print("   Set it with: export CLAUDE_API_KEY='your-api-key-here'")
        return False

    # Mask API key for display
    masked_key = (f"{api_key[:8]}...{api_key[-4:]}"
                 if len(api_key) > 12 else "***")
    print(f"✅ PASS: API key found: {masked_key}")

    # Check format
    if not api_key.startswith("sk-ant-"):
        print("❌ FAIL: API key format invalid (should start with 'sk-ant-')")
        return False
    print("✅ PASS: API key format appears valid")

    # Test 2: Initialize evaluator
    print("\n🔧 Test 2: Evaluator Initialization")
    print("-" * 40)

    try:
        evaluator = FixedMultiModelEvaluator()
        print("✅ PASS: Evaluator initialized successfully")
    except Exception as e:
        print(f"❌ FAIL: Failed to initialize evaluator: {e}")
        return False

    # Test 3: Check API client
    print("\n🌐 Test 3: API Client Verification")
    print("-" * 40)

    if not evaluator.client:
        print("❌ FAIL: API client not initialized")
        return False
    print("✅ PASS: API client initialized")

    if not evaluator.api_key:
        print("❌ FAIL: API key not loaded in evaluator")
        return False
    print("✅ PASS: API key loaded in evaluator")

    # Test 4: Check for mock mode
    print("\n🎭 Test 4: Mock Mode Check")
    print("-" * 40)

    if hasattr(evaluator, 'use_mock') and evaluator.use_mock:
        print("❌ FAIL: Mock mode is enabled!")
        return False
    print("✅ PASS: Mock mode is disabled")

    # Test 5: Verify scaling factors
    print("\n📊 Test 5: Scaling Factor Calculation")
    print("-" * 40)

    sample_sizes = [1, 2, 4, 8, 16, 32]
    scaling_factors = []

    for n in sample_sizes:
        scaling = evaluator._calculate_scaling_factor(n)
        scaling_factors.append(scaling)
        print(f"   n={n:2d}: scaling_factor={scaling:.3f}")

    # Check if scaling factors vary (not all 1.0)
    if len(set(scaling_factors)) == 1 and scaling_factors[0] == 1.0:
        print("❌ FAIL: All scaling factors are 1.0 - scaling not working")
        return False

    # Check if scaling factors decrease with sample size (diminishing returns)
    if scaling_factors[0] <= scaling_factors[-1]:
        print("⚠️ WARNING: Scaling factors don't show diminishing returns")
        print("   This may indicate the scaling formula needs adjustment")
    else:
        print("✅ PASS: Scaling factors show diminishing returns")

    print("✅ PASS: Scaling factors calculated successfully")

    # Test 6: Test real API call
    print("\n📡 Test 6: Real API Call Test")
    print("-" * 40)

    try:
        # Simple test prompt
        test_prompt = "What is 2 + 2? Please respond with just the number."

        print("   Making test API call...")
        start_time = time.time()

        response = await evaluator.client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=10,
            messages=[{"role": "user", "content": test_prompt}]
        )

        api_time = time.time() - start_time

        if api_time < 0.1:
            print("❌ FAIL: API call too fast - may be simulated")
            return False
        elif api_time < 1.0:
            print("⚠️ WARNING: API call seems fast - may be cached")
        else:
            print("✅ PASS: API call time appears realistic")

        response_text = response.content[0].text.strip()
        print(f"   Response: '{response_text}'")
        print(f"   API call took: {api_time:.2f} seconds")

        if "4" in response_text or "four" in response_text.lower():
            print("✅ PASS: API responded correctly")
        else:
            print("⚠️ WARNING: API response unexpected, but call succeeded")

    except Exception as e:
        print(f"❌ FAIL: API call failed: {e}")
        return False

    # Test 7: Test evaluation method
    print("\n🧪 Test 7: Evaluation Method Test")
    print("-" * 40)

    try:
        # Test with minimal parameters
        test_model = "claude-3-haiku-20240307"
        test_n = 1

        print(f"   Testing evaluation for {test_model} with n={test_n}")
        start_time = time.time()

        result = await evaluator.evaluate_sample_size(test_model, test_n)

        eval_time = time.time() - start_time

        if eval_time < 0.5:
            print("❌ FAIL: Evaluation too fast - may be simulated")
            return False

        print(f"   Evaluation took: {eval_time:.2f} seconds")
        success_rate = result.get('validation', {}).get('success_rate', 'N/A')
        scaling_factor = result.get('metadata', {}).get('scaling_factor', 'N/A')
        print(f"   Success rate: {success_rate}")
        print(f"   Scaling factor: {scaling_factor}")

        # Check if result has expected structure
        required_fields = ['validation', 'metadata', 'capability', 'safety']
        for field in required_fields:
            if field not in result:
                print(f"❌ FAIL: Missing required field: {field}")
                return False

        print("✅ PASS: Evaluation method working correctly")

    except Exception as e:
        print(f"❌ FAIL: Evaluation method failed: {e}")
        return False

    # All tests passed
    print("\n🎉 ALL SMOKE TESTS PASSED!")
    print("=" * 60)
    print("✅ API key loaded correctly")
    print("✅ API client initialized")
    print("✅ Mock mode disabled")
    print("✅ Scaling factors calculated")
    print("✅ Real API calls working")
    print("✅ Evaluation method functional")
    print()
    print("🚀 Ready to run full fixed evaluation!")
    print("   Run: python run_fixed_evaluation.py")

    return True


async def main():
    """Main function."""
    success = await smoke_test()
    if not success:
        print("\n❌ Smoke test failed!")
        print("   Please fix the issues before running the full evaluation.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
