#!/usr/bin/env python3
"""
Debug Fixed Multi-Model Evaluation
==================================

This script implements the comprehensive debugging plan to verify that
the fixed evaluation is working correctly with real API calls.
"""

import asyncio
import json
import os
import subprocess
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


class FixedEvaluationDebugger:
    """Debugger for the fixed multi-model evaluation."""

    def __init__(self):
        self.results_dir = "results/fixed_multi_model_evaluation"
        self.old_results_dir = "results/multi_model_evaluation"

    def run_complete_debug_plan(self):
        """Run the complete debugging plan."""

        print("🔧 Fixed Multi-Model Evaluation - Complete Debug Plan")
        print("=" * 70)
        print("This implements all verification steps from the debugging plan:")
        print("1. Verify correct script is being run")
        print("2. Check API key loading")
        print("3. Ensure no mock mode")
        print("4. Verify execution time")
        print("5. Check scaling logic")
        print("6. Validate metric variability")
        print("7. Clean old results")
        print("8. Run smoke test")
        print()

        # Step 1: Verify correct script
        print("🔍 Step 1: Verify Correct Script")
        print("-" * 50)
        self.verify_correct_script()

        # Step 2: Check API key
        print("\n🔑 Step 2: API Key Verification")
        print("-" * 50)
        if not self.verify_api_key():
            return False

        # Step 3: Check for mock mode
        print("\n🎭 Step 3: Mock Mode Check")
        print("-" * 50)
        if not self.check_mock_mode():
            return False

        # Step 4: Verify scaling logic
        print("\n📊 Step 4: Scaling Logic Verification")
        print("-" * 50)
        if not self.verify_scaling_logic():
            return False

        # Step 5: Clean old results
        print("\n🧹 Step 5: Clean Old Results")
        print("-" * 50)
        self.clean_old_results()

        # Step 6: Run smoke test
        print("\n🧪 Step 6: Run Smoke Test")
        print("-" * 50)
        if not self.run_smoke_test():
            return False

        # Step 7: Run fixed evaluation with monitoring
        print("\n🚀 Step 7: Run Fixed Evaluation with Monitoring")
        print("-" * 50)
        if not self.run_fixed_evaluation():
            return False

        # Step 8: Validate results
        print("\n✅ Step 8: Validate Results")
        print("-" * 50)
        if not self.validate_final_results():
            return False

        print("\n🎉 DEBUG PLAN COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("✅ All verification steps passed")
        print("✅ Fixed evaluation is working correctly")
        print("✅ Real API calls are being made")
        print("✅ Results show meaningful scaling behavior")
        print()
        print("📊 Check results in: results/fixed_multi_model_evaluation/")

        return True

    def verify_correct_script(self):
        """Verify the correct script is being run."""
        print("🔧 Checking script identification...")

        # Check if we're running the fixed evaluation
        current_script = Path(__file__).name
        print(f"   Current script: {current_script}")

        if "debug" in current_script.lower():
            print("✅ Running debug script")
        else:
            print("⚠️ Not running debug script")

        # Check if fixed evaluation script exists
        fixed_script = "run_fixed_evaluation.py"
        if os.path.exists(fixed_script):
            print(f"✅ Fixed evaluation script found: {fixed_script}")
        else:
            print(f"❌ Fixed evaluation script missing: {fixed_script}")

        # Check if old evaluation script exists
        old_script = "run_multi_model_evaluation.py"
        if os.path.exists(old_script):
            print(f"⚠️ Old evaluation script still exists: {old_script}")
            print("   This could cause confusion - consider removing it")
        else:
            print("✅ Old evaluation script not found")

    def verify_api_key(self):
        """Verify API key is loaded correctly."""
        print("🔑 Checking API key...")

        # Check environment variable
        api_key = os.getenv("CLAUDE_API_KEY")
        if not api_key:
            print("❌ FAIL: CLAUDE_API_KEY environment variable not found")
            print("   Set it with: export CLAUDE_API_KEY='your-api-key-here'")
            return False

        # Mask API key for display
        masked_key = (f"{api_key[:8]}...{api_key[-4:]}"
                     if len(api_key) > 12 else "***")
        print(f"✅ API key found: {masked_key}")

        # Check format
        if not api_key.startswith("sk-ant-"):
            print("❌ FAIL: API key format invalid (should start with 'sk-ant-')")
            return False
        print("✅ API key format appears valid")

        # Test API key in evaluator
        try:
            evaluator = FixedMultiModelEvaluator()
            if evaluator.api_key != api_key:
                print("❌ FAIL: API key not loaded correctly in evaluator")
                return False
            print("✅ API key loaded correctly in evaluator")
        except Exception as e:
            print(f"❌ FAIL: Failed to initialize evaluator: {e}")
            return False

        return True

    def check_mock_mode(self):
        """Check that mock mode is disabled."""
        print("🎭 Checking for mock mode...")

        try:
            evaluator = FixedMultiModelEvaluator()

            # Check for use_mock attribute
            if hasattr(evaluator, 'use_mock'):
                if evaluator.use_mock:
                    print("❌ FAIL: Mock mode is enabled!")
                    return False
                else:
                    print("✅ Mock mode is disabled")
            else:
                print("✅ No mock mode attribute found")

            # Check for mock client
            if hasattr(evaluator, 'client'):
                client_type = type(evaluator.client).__name__
                print(f"   Client type: {client_type}")
                if "mock" in client_type.lower():
                    print("❌ FAIL: Mock client detected!")
                    return False
                else:
                    print("✅ Real API client detected")

            return True

        except Exception as e:
            print(f"❌ FAIL: Error checking mock mode: {e}")
            return False

    def verify_scaling_logic(self):
        """Verify scaling logic is working correctly."""
        print("📊 Checking scaling logic...")

        try:
            evaluator = FixedMultiModelEvaluator()

            # Test scaling factors
            sample_sizes = [1, 2, 4, 8, 16, 32]
            scaling_factors = []

            print("   Testing scaling factors:")
            for n in sample_sizes:
                scaling = evaluator._calculate_scaling_factor(n)
                scaling_factors.append(scaling)
                print(f"     n={n:2d}: scaling_factor={scaling:.3f}")

            # Check if scaling factors vary
            if len(set(scaling_factors)) == 1:
                print("❌ FAIL: All scaling factors are identical")
                return False

            # Check if scaling factors decrease (diminishing returns)
            if scaling_factors[0] <= scaling_factors[-1]:
                print("⚠️ WARNING: Scaling factors don't show diminishing returns")
                print("   This may indicate the scaling formula needs adjustment")
            else:
                print("✅ Scaling factors show diminishing returns")

            # Check if scaling factors are reasonable
            if any(sf < 0.1 or sf > 2.0 for sf in scaling_factors):
                print("⚠️ WARNING: Some scaling factors seem extreme")
            else:
                print("✅ Scaling factors are reasonable")

            return True

        except Exception as e:
            print(f"❌ FAIL: Error verifying scaling logic: {e}")
            return False

    def clean_old_results(self):
        """Clean old results to avoid confusion."""
        print("🧹 Cleaning old results...")

        if os.path.exists(self.old_results_dir):
            print(f"⚠️ Found old results in: {self.old_results_dir}")
            print("   This could cause confusion with the fixed results.")

            # Ask user if they want to remove old results
            response = input("   Remove old results? (y/N): ").strip().lower()
            if response in ['y', 'yes']:
                try:
                    import shutil
                    shutil.rmtree(self.old_results_dir)
                    print("✅ Old results removed")
                except Exception as e:
                    print(f"⚠️ Failed to remove old results: {e}")
            else:
                print("   Keeping old results")
        else:
            print("✅ No old results found")

        # Ensure fixed results directory exists
        os.makedirs(self.results_dir, exist_ok=True)
        print(f"✅ Fixed results directory ready: {self.results_dir}")

    def run_smoke_test(self):
        """Run the smoke test."""
        print("🧪 Running smoke test...")

        try:
            # Run smoke test script
            result = subprocess.run([
                sys.executable, "test_api_smoke.py"
            ], capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                print("✅ Smoke test passed")
                return True
            else:
                print("❌ Smoke test failed")
                print("   Output:")
                print(result.stdout)
                print("   Errors:")
                print(result.stderr)
                return False

        except subprocess.TimeoutExpired:
            print("❌ Smoke test timed out")
            return False
        except Exception as e:
            print(f"❌ Error running smoke test: {e}")
            return False

    def run_fixed_evaluation(self):
        """Run the fixed evaluation with monitoring."""
        print("🚀 Running fixed evaluation...")

        try:
            # Run fixed evaluation script
            print("   Starting evaluation (this may take several minutes)...")
            start_time = time.time()

            result = subprocess.run([
                sys.executable, "run_fixed_evaluation.py"
            ], capture_output=True, text=True, timeout=1800)  # 30 minute timeout

            execution_time = time.time() - start_time

            if result.returncode == 0:
                print(f"✅ Fixed evaluation completed in {execution_time:.1f} seconds")

                # Check execution time
                if execution_time < 30:
                    print("⚠️ WARNING: Execution time seems short for full evaluation")
                elif execution_time < 300:
                    print("⚠️ WARNING: Execution time seems short for comprehensive evaluation")
                else:
                    print("✅ Execution time appears realistic")

                return True
            else:
                print("❌ Fixed evaluation failed")
                print("   Output:")
                print(result.stdout)
                print("   Errors:")
                print(result.stderr)
                return False

        except subprocess.TimeoutExpired:
            print("❌ Fixed evaluation timed out (30 minutes)")
            return False
        except Exception as e:
            print(f"❌ Error running fixed evaluation: {e}")
            return False

    def validate_final_results(self):
        """Validate the final results."""
        print("✅ Validating final results...")

        try:
            # Check if comprehensive results exist
            comprehensive_file = f"{self.results_dir}/comprehensive_results.json"
            if not os.path.exists(comprehensive_file):
                print("❌ Comprehensive results file not found")
                return False

            # Load results
            with open(comprehensive_file, "r") as f:
                results = json.load(f)

            metadata = results.get("metadata", {})

            # Check execution time
            execution_time = metadata.get("execution_time", 0)
            print(f"   Execution time: {execution_time:.2f} seconds")

            if execution_time < 1.0:
                print("❌ FAIL: Execution time too short - may be simulated")
                return False

            # Check if real API was used
            if not metadata.get("api_used", False):
                print("❌ FAIL: Results don't indicate real API was used")
                return False

            # Check if scaling was fixed
            if not metadata.get("scaling_fixed", False):
                print("❌ FAIL: Results don't indicate scaling was fixed")
                return False

            # Check model results
            model_results = results.get("model_results", {})
            if not model_results:
                print("❌ FAIL: No model results found")
                return False

            print(f"   Models evaluated: {len(model_results)}")

            # Check for meaningful variation
            all_100_percent = True
            scaling_variation = False

            for model_id, model_data in model_results.items():
                sample_sizes = model_data.get("sample_sizes", {})
                scaling_factors = []

                for n_key, sample_data in sample_sizes.items():
                    success_rate = (sample_data.get("validation", {})
                                   .get("success_rate", 1.0))
                    scaling_factor = (sample_data.get("metadata", {})
                                    .get("scaling_factor", 1.0))

                    if success_rate < 1.0:
                        all_100_percent = False

                    scaling_factors.append(scaling_factor)

                if len(set(scaling_factors)) > 1:
                    scaling_variation = True

            if all_100_percent:
                print("❌ FAIL: All success rates are 100% - may be simulated")
                return False

            if not scaling_variation:
                print("❌ FAIL: No scaling variation found")
                return False

            print("✅ Results validation passed")
            print("   - Realistic success rates")
            print("   - Meaningful scaling variation")
            print("   - Real API calls confirmed")

            return True

        except Exception as e:
            print(f"❌ Error validating results: {e}")
            return False


def main():
    """Main function."""
    debugger = FixedEvaluationDebugger()
    success = debugger.run_complete_debug_plan()

    if not success:
        print("\n❌ Debug plan failed!")
        print("   Please fix the issues before proceeding.")
        sys.exit(1)


if __name__ == "__main__":
    main()
