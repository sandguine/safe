#!/usr/bin/env python3
"""
Test script for Enhanced AZR Loop
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from enhanced_azr_loop import EnhancedAZRLoop, AZRConfig
    print("✅ Enhanced AZR loop imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

async def test_enhanced_azr():
    """Test the enhanced AZR loop with a small sample"""
    
    print("🚀 Testing Enhanced AZR Loop...")
    
    try:
        # Create configuration for testing
        config = AZRConfig(
            max_tasks=5,  # Small sample for testing
            n_values=[1, 4],  # Reduced for testing
            max_concurrent=2,
            requests_per_minute=15,
            progressive_sampling=True,
            temperature=0.7
        )
        
        print(f"✅ Configuration created")
        print(f"   - Tasks: {config.max_tasks}")
        print(f"   - N values: {config.n_values}")
        print(f"   - Temperature: {config.temperature}")
        
        # Create and run enhanced AZR loop
        azr_loop = EnhancedAZRLoop(config)
        
        # Run experiment with 2 cycles
        results = await azr_loop.run_experiment(cycles=2)
        
        print("✅ Experiment completed successfully")
        
        # Print summary
        print("\n📊 Final Results:")
        print(f"   Best pass@1: {results['final_metrics']['best_pass_at_1']:.4f}")
        print(f"   Average pass@1: {results['final_metrics']['avg_pass_at_1']:.4f}")
        print(f"   Best ratio: {results['final_metrics']['best_ratio']:.4f}")
        print(f"   Total cycles: {results['final_metrics']['total_cycles']}")
        print(f"   Total duration: {results['total_duration']:.2f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_enhanced_azr())
    sys.exit(0 if success else 1) 