#!/usr/bin/env python3
"""
Simple test script for the deduction loop.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from deduction_loop import DeductionLoop


def test_single_cycle():
    """Test a single deduction cycle"""
    print("Testing single deduction cycle...")
    
    # Initialize loop with minimal settings
    loop = DeductionLoop(
        enable_referee=True,
        max_puzzles_per_cycle=2,  # Small number for testing
        max_solutions_per_puzzle=1
    )
    
    # Run one cycle
    metrics = loop.run_cycle()
    
    print(f"Cycle completed!")
    print(f"Puzzles generated: {metrics['puzzles_generated']}")
    print(f"Puzzles approved: {metrics['puzzles_approved']}")
    print(f"Solutions generated: {metrics['solutions_generated']}")
    print(f"Solutions correct: {metrics['solutions_correct']}")
    
    return metrics


def test_baseline_vs_oversight():
    """Test baseline vs oversight comparison"""
    print("\nTesting baseline vs oversight...")
    
    # Baseline run (no referee)
    print("Running baseline...")
    baseline_loop = DeductionLoop(
        enable_referee=False,
        max_puzzles_per_cycle=2,
        max_solutions_per_puzzle=1
    )
    baseline_metrics = baseline_loop.run_cycle()
    
    # Oversight run (with referee)
    print("Running oversight...")
    oversight_loop = DeductionLoop(
        enable_referee=True,
        max_puzzles_per_cycle=2,
        max_solutions_per_puzzle=1
    )
    oversight_metrics = oversight_loop.run_cycle()
    
    # Compare results
    print("\nComparison:")
    print(f"Baseline - Puzzles: {baseline_metrics['puzzles_generated']}, "
          f"Solutions: {baseline_metrics['solutions_generated']}")
    print(f"Oversight - Puzzles: {oversight_metrics['puzzles_generated']}, "
          f"Solutions: {oversight_metrics['solutions_generated']}")
    
    return baseline_metrics, oversight_metrics


def main():
    """Main test function"""
    print("🧪 Testing Deduction Loop")
    print("=" * 40)
    
    # Check API key
    if not os.getenv("CLAUDE_API_KEY"):
        print("❌ CLAUDE_API_KEY not set")
        return
    
    try:
        # Test single cycle
        test_single_cycle()
        
        # Test comparison
        test_baseline_vs_oversight()
        
        print("\n✅ All tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 