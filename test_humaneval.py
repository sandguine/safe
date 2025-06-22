#!/usr/bin/env python3
"""
Test script for HumanEval integration
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from oversight.humaneval_integration import AsyncHumanEvalRunner, save_results, calculate_pass_at_k
    print("✅ HumanEval integration imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

async def test_humaneval():
    """Test the HumanEval integration with a small sample"""
    
    print("🚀 Testing HumanEval integration...")
    
    try:
        # Create runner with conservative settings
        runner = AsyncHumanEvalRunner(
            max_concurrent=2,
            requests_per_minute=20,
            progressive_sampling=True
        )
        
        print(f"✅ Runner created with {len(runner.tasks)} tasks")
        
        # Test with first 3 tasks
        results = await runner.run_experiment(
            n_values=[1, 4],
            max_tasks=3,
            temperature=0.7
        )
        
        print("✅ Experiment completed successfully")
        
        # Save results
        json_file, csv_file = save_results(results)
        print(f"✅ Results saved to {json_file} and {csv_file}")
        
        # Print summary
        print("\n📊 Results Summary:")
        for n_key, n_results in results.items():
            n = int(n_key.split('_')[1])
            pass_at_1 = calculate_pass_at_k(n_results, 1)
            avg_ratio = sum(r['result'].ratio for r in n_results) / len(n_results)
            print(f"  Best-of-{n}: pass@1 = {pass_at_1:.4f}, avg_ratio = {avg_ratio:.4f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_humaneval())
    sys.exit(0 if success else 1) 