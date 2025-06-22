#!/usr/bin/env python3
"""
Quick demo path timing test.
Tests the exact parameters that will be used on stage.
"""

import time
import statistics
from typing import List
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from deduction_loop import DeductionLoop


def test_demo_timing():
    """Test demo path timing with exact stage parameters"""
    
    print("🎯 Testing Demo Path Timing")
    print("=" * 50)
    print("Parameters:")
    print("- Cycles: 3")
    print("- Puzzles per cycle: 1")
    print("- Solutions per puzzle: 4")
    print("- Model: claude-3-5-sonnet-20241022")
    print()
    
    # Initialize deduction loop with demo parameters
    loop = DeductionLoop(
        model_name="claude-3-5-sonnet-20241022",
        enable_referee=True,
        max_puzzles_per_cycle=1,
        max_solutions_per_puzzle=4
    )
    
    cycle_times = []
    
    # Run 3 cycles and measure timing
    for cycle in range(3):
        print(f"🔄 Running cycle {cycle + 1}/3...")
        
        start_time = time.time()
        
        try:
            # Run one cycle
            cycle_metrics = loop.run_cycle()
            cycle_duration = time.time() - start_time
            cycle_times.append(cycle_duration)
            
            print(f"✅ Cycle {cycle + 1} completed in {cycle_duration:.2f}s")
            print(f"   Puzzles: {cycle_metrics.get('new_puzzles', 0)}")
            print(f"   Solutions: {cycle_metrics.get('new_solutions', 0)}")
            print(f"   Approved: {cycle_metrics.get('approved_puzzles', 0)}")
            
        except Exception as e:
            print(f"❌ Cycle {cycle + 1} failed: {e}")
            cycle_times.append(30.0)  # Conservative estimate for failed cycle
        
        print()
    
    # Calculate timing statistics
    if cycle_times:
        median_time = statistics.median(cycle_times)
        mean_time = statistics.mean(cycle_times)
        
        # Calculate 95th percentile (approximate)
        sorted_times = sorted(cycle_times)
        percentile_95 = sorted_times[int(len(sorted_times) * 0.95)]
        
        print("📊 Demo Path Timing Results")
        print("=" * 50)
        print(f"Median cycle time: {median_time:.2f}s")
        print(f"Mean cycle time: {mean_time:.2f}s")
        print(f"95th percentile: {percentile_95:.2f}s")
        print(f"Min: {min(cycle_times):.2f}s")
        print(f"Max: {max(cycle_times):.2f}s")
        print()
        
        # Success criteria check
        print("🎯 Success Criteria Check")
        print("=" * 50)
        median_ok = median_time <= 5.0
        percentile_95_ok = percentile_95 <= 8.0
        
        print(f"Median ≤ 5s: {'✅' if median_ok else '❌'} ({median_time:.2f}s)")
        print(f"95th percentile ≤ 8s: {'✅' if percentile_95_ok else '❌'} ({percentile_95:.2f}s)")
        
        overall_success = median_ok and percentile_95_ok
        print(f"Overall: {'✅ PASS' if overall_success else '❌ FAIL'}")
        
        return {
            "median": median_time,
            "mean": mean_time,
            "percentile_95": percentile_95,
            "min": min(cycle_times),
            "max": max(cycle_times),
            "success": overall_success
        }
    
    return None


if __name__ == "__main__":
    results = test_demo_timing()
    
    if results:
        print(f"\n📋 Results Summary:")
        print(f"Demo path timing: {results['median']:.2f}s median, {results['percentile_95']:.2f}s 95th percentile")
        print(f"Status: {'READY' if results['success'] else 'NEEDS OPTIMIZATION'}")
    else:
        print("❌ No timing results available") 