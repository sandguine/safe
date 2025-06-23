#!/usr/bin/env python3
"""
Test Fixed Implementation
========================

Quick test to verify the fixed multi-model evaluation implementation
works correctly before running the full evaluation.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add oversight to path
sys.path.insert(0, str(Path(__file__).parent))

from fixed_multi_model_evaluation import FixedMultiModelEvaluator


class FixedImplementationTester:
    """Test the fixed implementation with minimal evaluation."""

    def __init__(self):
        self.api_key = os.getenv("CLAUDE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "CLAUDE_API_KEY environment variable is required for testing."
            )

    async def test_scaling_formula(self):
        """Test the fixed scaling formula."""
        print("🧪 Testing Fixed Scaling Formula")
        print("-" * 40)

        # Create evaluator instance
        evaluator = FixedMultiModelEvaluator()

        # Test scaling factors
        sample_sizes = [1, 4, 16, 32, 64]
        expected_values = [0.36, 0.52, 0.68, 0.76, 0.82]

        print("Sample Size | Expected | Actual | Status")
        print("-" * 40)

        for n, expected in zip(sample_sizes, expected_values):
            actual = evaluator._calculate_scaling_factor(n)
            status = "✅" if abs(actual - expected) < 0.01 else "❌"
            print(f"n={n:2d}        | {expected:.2f}     | {actual:.2f}   | {status}")

        print()

    async def test_model_tier_assignment(self):
        """Test model tier assignment."""
        print("🧪 Testing Model Tier Assignment")
        print("-" * 40)

        evaluator = FixedMultiModelEvaluator()

        test_models = [
            "claude-4-opus-20250514",
            "claude-4-sonnet-20250514",
            "claude-3-7-sonnet-20250219",
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022"
        ]

        print("Model | Tier | Status")
        print("-" * 40)

        for model_id in test_models:
            tier = evaluator._get_model_tier(model_id)
            status = "✅" if 0.5 <= tier <= 1.0 else "❌"
            print(f"{model_id[:20]:20} | {tier:.2f} | {status}")

        print()

    async def test_single_evaluation(self):
        """Test a single model evaluation with minimal samples."""
        print("🧪 Testing Single Model Evaluation")
        print("-" * 40)

        evaluator = FixedMultiModelEvaluator()

        # Test with just one model and one sample size
        model_id = "claude-3-5-sonnet-20241022"
        model_name = "Claude 3.5 Sonnet (Test)"
        n = 4

        print(f"Testing {model_name} with n={n}...")

        try:
            # Test individual components
            print("  Testing capability evaluation...")
            capability = await evaluator._evaluate_capability(model_id, n)
            print(f"    ✅ Capability: {capability['improvement']:.3f}")

            print("  Testing safety evaluation...")
            safety = await evaluator._evaluate_safety(model_id, n)
            print(f"    ✅ Safety: {safety['refusal_rate']:.1%}")

            print("  Testing KL divergence...")
            kl_analysis = await evaluator._evaluate_kl_divergence(model_id, n)
            print(f"    ✅ KL Divergence: {kl_analysis['kl_divergence']:.3f}")

            print("  Testing self-alignment...")
            self_alignment = await evaluator._evaluate_self_alignment(model_id, n)
            print(f"    ✅ Alignment: {self_alignment['improvement']:.3f}")

            # Test validation
            validation = evaluator._validate_criteria(capability, safety, kl_analysis, self_alignment)
            print(f"    ✅ Validation: {validation['success_rate']:.1%} success rate")

            print("  ✅ Single evaluation completed successfully!")

        except Exception as e:
            print(f"  ❌ Single evaluation failed: {e}")
            return False

        print()

    async def test_directory_creation(self):
        """Test that directories are created properly."""
        print("🧪 Testing Directory Creation")
        print("-" * 40)

        evaluator = FixedMultiModelEvaluator()

        # Check if directories were created
        required_dirs = [
            evaluator.results_dir,
            f"{evaluator.results_dir}/individual_models",
            f"{evaluator.results_dir}/charts",
            f"{evaluator.results_dir}/logs",
            f"{evaluator.results_dir}/validation"
        ]

        for dir_path in required_dirs:
            if os.path.exists(dir_path):
                print(f"  ✅ {dir_path}")
            else:
                print(f"  ❌ {dir_path}")

        print()

    async def test_rate_limiting(self):
        """Test rate limiting functionality."""
        print("🧪 Testing Rate Limiting")
        print("-" * 40)

        evaluator = FixedMultiModelEvaluator()

        # Test a simple API call
        try:
            print("  Testing simple API call...")
            response = await evaluator._rate_limited_api_call(
                "claude-3-5-sonnet-20241022",
                "Say 'Hello, test!'",
                temperature=0.1
            )

            if response and len(response) > 0:
                print(f"  ✅ API call successful: {response[:50]}...")
            else:
                print("  ❌ API call returned empty response")
                return False

        except Exception as e:
            print(f"  ❌ API call failed: {e}")
            return False

        print()

    async def run_all_tests(self):
        """Run all tests."""
        print("🔧 Testing Fixed Multi-Model Implementation")
        print("=" * 60)
        print("This will test the key components before running the full evaluation.")
        print()

        tests = [
            ("Scaling Formula", self.test_scaling_formula),
            ("Model Tier Assignment", self.test_model_tier_assignment),
            ("Directory Creation", self.test_directory_creation),
            ("Rate Limiting", self.test_rate_limiting),
            ("Single Evaluation", self.test_single_evaluation),
        ]

        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            try:
                await test_func()
                passed += 1
            except Exception as e:
                print(f"❌ {test_name} test failed: {e}")
                print()

        # Summary
        print("📊 Test Summary")
        print("=" * 40)
        print(f"Tests passed: {passed}/{total}")

        if passed == total:
            print("🎉 All tests passed! Ready to run full evaluation.")
            print("\nNext steps:")
            print("1. Run full evaluation: python run_fixed_evaluation.py")
            print("2. Or run individual components:")
            print("   - python fixed_multi_model_evaluation.py")
            print("   - python fixed_multi_model_charts.py")
            print("   - python compare_results.py")
        else:
            print("❌ Some tests failed. Please fix issues before running full evaluation.")
            return False

        return passed == total


async def main():
    """Main function to run tests."""

    print("🧪 Fixed Implementation Test Suite")
    print("=" * 50)

    try:
        tester = FixedImplementationTester()
        success = await tester.run_all_tests()

        if success:
            print("\n✅ All tests passed! Implementation is ready.")
        else:
            print("\n❌ Tests failed. Please fix issues before proceeding.")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
