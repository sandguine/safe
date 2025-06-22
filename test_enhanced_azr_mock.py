#!/usr/bin/env python3
"""
Mock test script for Enhanced AZR Loop (no API key required)
"""

import asyncio
import os
import sys
from unittest.mock import Mock, patch

# Add oversight_curriculum to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from oversight.enhanced_azr_loop import AZRConfig, EnhancedAZRLoop

    print("✅ Enhanced AZR loop imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


async def test_enhanced_azr_mock():
    """Test the enhanced AZR loop with mocked API calls"""

    print("🚀 Testing Enhanced AZR Loop (Mock Mode)...")

    try:
        # Create configuration for testing
        config = AZRConfig(
            max_tasks=3,  # Small sample for testing
            n_values=[1, 2],  # Reduced for testing
            max_concurrent=2,
            requests_per_minute=15,
            progressive_sampling=True,
            temperature=0.7,
        )

        print(f"✅ Configuration created")
        print(f"   - Tasks: {config.max_tasks}")
        print(f"   - N values: {config.n_values}")
        print(f"   - Temperature: {config.temperature}")

        # Mock the API call
        with patch("oversight.model.ask") as mock_ask:
            # Mock successful API responses
            mock_ask.return_value = """
def solution():
    return True
"""

            # Create and run enhanced AZR loop
            azr_loop = EnhancedAZRLoop(config)

            # Run experiment with 1 cycle
            results = await azr_loop.run_experiment(cycles=1)

            print("✅ Mock experiment completed successfully")

            # Print summary
            print("\n📊 Final Results:")
            print(
                f"   Best pass@1: {results['final_metrics']['best_pass_at_1']:.4f}"
            )
            print(
                f"   Total cycles: {results['final_metrics']['total_cycles']}"
            )
            print(f"   Total duration: {results['total_duration']:.2f}s")

            # Verify results structure
            assert "final_metrics" in results
            assert "total_duration" in results
            assert "cycle_results" in results
            print("✅ Results structure is correct")

            return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🧪 Running Mock Tests...")

    # Run test
    success = asyncio.run(test_enhanced_azr_mock())

    if success:
        print("\n🎉 Mock test passed!")
        sys.exit(0)
    else:
        print("\n❌ Test failed!")
        sys.exit(1)
