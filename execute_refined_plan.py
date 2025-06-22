#!/usr/bin/env python3
"""
Execute Refined Plan - Comprehensive Implementation
==================================================

This script implements the complete refined plan with:

🎯 **Core Features:**
- HumanEval-164 dataset (164 tasks)
- Async execution with global rate limiting
- Progressive sampling (n=4 first, then +12 if needed)
- Confidence-weighted voting across top candidates
- Secure sandbox execution with partial credit
- Execute-then-grade selection
- Global throttling with exponential back-off

🛡️ **Safety & Security:**
- Multiprocessing sandboxing
- Deterministic execution
- Resource limits and timeouts
- Rate limit compliance

📊 **Advanced Analytics:**
- Progressive sampling analysis
- Confidence-weighted voting metrics
- Partial credit breakdown
- Performance tracking across cycles

⏱️ **Time Management:**
- 4-hour execution window
- Early stopping on high performance
- Intermediate result saving
- Progress monitoring
"""

import os
import sys
import json
import time
import asyncio
import argparse
from pathlib import Path
from typing import Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from enhanced_azr_loop import EnhancedAZRLoop, AZRConfig
    print("✅ Enhanced AZR loop imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


class RefinedPlanExecutor:
    """Executes the complete refined plan"""
    
    def __init__(self):
        self.start_time = time.time()
        self.max_duration = 4 * 60 * 60  # 4 hours
        self.results = {}
        
    def create_production_config(self, num_tasks: int = 164, n_samples: int = 16) -> AZRConfig:
        """Create production configuration for the refined plan"""
        
        return AZRConfig(
            # HumanEval dataset
            max_tasks=num_tasks,
            n_values=[1, 4, n_samples] if n_samples > 4 else [1, 4],
            
            # Async execution with rate limiting
            max_concurrent=8,  # Conservative for stability
            requests_per_minute=40,  # Respect API limits
            progressive_sampling=True,
            
            # Model settings
            temperature=0.7,  # Balanced creativity
            use_chain_of_thought=True,
            
            # Sandbox security
            timeout_seconds=30,  # Increased for complex tasks
            memory_limit_mb=1024,  # 1GB limit
            
            # Rate limiting
            exponential_backoff=True,
            max_retries=3
        )
    
    def create_testing_config(self, num_tasks: int = 20) -> AZRConfig:
        """Create testing configuration for validation"""
        
        return AZRConfig(
            max_tasks=num_tasks,
            n_values=[1, 4],  # Reduced for speed
            max_concurrent=3,
            requests_per_minute=20,
            progressive_sampling=True,
            temperature=0.7,
            timeout_seconds=10,
            memory_limit_mb=512
        )
    
    async def run_production_experiment(self, num_tasks: int = 164, n_samples: int = 16) -> Dict[str, Any]:
        """Run the full production experiment"""
        
        print("🚀 Starting Production Experiment")
        print("=" * 50)
        
        config = self.create_production_config(num_tasks, n_samples)
        
        print("📋 Production Configuration:")
        print(f"   - HumanEval tasks: {config.max_tasks}")
        print(f"   - Progressive sampling: {config.n_values}")
        print(f"   - Async concurrency: {config.max_concurrent}")
        print(f"   - Rate limit: {config.requests_per_minute}/min")
        print(f"   - Temperature: {config.temperature}")
        print(f"   - Timeout: {config.timeout_seconds}s")
        print(f"   - Memory limit: {config.memory_limit_mb}MB")
        
        # Create enhanced AZR loop
        azr_loop = EnhancedAZRLoop(config)
        
        # Run experiment with monitoring
        results = await self._run_with_monitoring(azr_loop, cycles=3)
        
        return results
    
    async def run_testing_experiment(self, num_tasks: int = 20) -> Dict[str, Any]:
        """Run a testing experiment for validation"""
        
        print("🧪 Starting Testing Experiment")
        print("=" * 50)
        
        config = self.create_testing_config(num_tasks)
        
        print("📋 Testing Configuration:")
        print(f"   - Tasks: {config.max_tasks}")
        print(f"   - N values: {config.n_values}")
        print(f"   - Concurrency: {config.max_concurrent}")
        
        # Create enhanced AZR loop
        azr_loop = EnhancedAZRLoop(config)
        
        # Run experiment
        results = await azr_loop.run_experiment(cycles=2)
        
        return results
    
    async def _run_with_monitoring(self, azr_loop: EnhancedAZRLoop, cycles: int) -> Dict[str, Any]:
        """Run experiment with time monitoring and early stopping"""
        
        experiment_start = time.time()
        
        # Run cycles with monitoring
        for cycle in range(1, cycles + 1):
            cycle_start = time.time()
            
            print(f"\n🔄 Cycle {cycle}/{cycles}")
            print(f"⏱️  Elapsed time: {(time.time() - self.start_time) / 60:.1f} minutes")
            
            # Check time budget
            elapsed = time.time() - self.start_time
            if elapsed > self.max_duration * 0.8:  # Stop at 80% of time budget
                print(f"⏰ Time budget reached (80%), stopping early")
                break
            
            try:
                # Run cycle
                cycle_data = await azr_loop.run_cycle(cycle)
                
                # Check for early stopping on performance
                if cycle_data['metrics']['best_pass_at_1'] >= 0.8:
                    print(f"🎯 Early stopping: achieved {cycle_data['metrics']['best_pass_at_1']:.4f} pass@1")
                    break
                
                cycle_duration = time.time() - cycle_start
                print(f"✅ Cycle {cycle} completed in {cycle_duration:.2f}s")
                
                # Estimate remaining time
                avg_cycle_time = (time.time() - experiment_start) / cycle
                remaining_cycles = cycles - cycle
                estimated_remaining = avg_cycle_time * remaining_cycles
                
                print(f"📊 Estimated remaining time: {estimated_remaining / 60:.1f} minutes")
                
            except Exception as e:
                print(f"❌ Error in cycle {cycle}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        # Calculate final metrics
        final_metrics = azr_loop._calculate_final_metrics()
        
        # Create final results
        final_results = {
            'experiment_type': 'production',
            'config': azr_loop.config.__dict__,
            'cycles_requested': cycles,
            'cycles_completed': len(azr_loop.results),
            'total_duration': time.time() - experiment_start,
            'cycle_results': azr_loop.results,
            'final_metrics': final_metrics,
            'early_stopping': len(azr_loop.results) < cycles
        }
        
        return final_results
    
    def save_comprehensive_results(self, results: Dict[str, Any], experiment_type: str, output_file: str = None):
        """Save comprehensive results with analysis"""
        
        os.makedirs('results', exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        # Use provided output file or generate default
        if output_file:
            json_file = output_file
        else:
            json_file = f"results/refined_plan_{experiment_type}_{timestamp}.json"
        
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Save CSV summary
        csv_file = f"results/refined_plan_{experiment_type}_summary_{timestamp}.csv"
        with open(csv_file, 'w') as f:
            f.write("cycle,best_pass_at_1,avg_ratio,duration,early_stop\n")
            
            for cycle_key, cycle_data in results['cycle_results'].items():
                cycle_num = cycle_data['cycle']
                best_pass_at_1 = cycle_data['metrics']['best_pass_at_1']
                avg_ratio = cycle_data['metrics'].get('avg_ratio_n4', 0.0)
                duration = cycle_data['duration']
                early_stop = results.get('early_stopping', False)
                
                f.write(f"{cycle_num},{best_pass_at_1:.4f},{avg_ratio:.4f},{duration:.2f},{early_stop}\n")
        
        # Save analysis report
        report_file = f"results/refined_plan_{experiment_type}_analysis_{timestamp}.txt"
        with open(report_file, 'w') as f:
            f.write("REFINED PLAN EXECUTION ANALYSIS\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Experiment Type: {experiment_type}\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Total Duration: {results['total_duration']:.2f}s\n")
            f.write(f"Cycles Completed: {results['cycles_completed']}/{results['cycles_requested']}\n")
            f.write(f"Early Stopping: {results.get('early_stopping', False)}\n\n")
            
            f.write("FINAL METRICS:\n")
            f.write("-" * 20 + "\n")
            for key, value in results['final_metrics'].items():
                if isinstance(value, float):
                    f.write(f"{key}: {value:.4f}\n")
                else:
                    f.write(f"{key}: {value}\n")
            
            f.write("\nCYCLE BREAKDOWN:\n")
            f.write("-" * 20 + "\n")
            for cycle_key, cycle_data in results['cycle_results'].items():
                f.write(f"Cycle {cycle_data['cycle']}:\n")
                f.write(f"  Duration: {cycle_data['duration']:.2f}s\n")
                f.write(f"  Best pass@1: {cycle_data['metrics']['best_pass_at_1']:.4f}\n")
                f.write(f"  Best ratio: {max(cycle_data['metrics'].get(f'avg_ratio_n{n}', 0) for n in results['config']['n_values']):.4f}\n\n")
        
        print(f"💾 Results saved:")
        print(f"   - JSON: {json_file}")
        print(f"   - CSV: {csv_file}")
        print(f"   - Analysis: {report_file}")
        
        return json_file, csv_file, report_file
    
    def print_summary(self, results: Dict[str, Any], experiment_type: str):
        """Print comprehensive summary with enhanced success criteria"""
        
        print(f"\n🎉 {experiment_type.upper()} EXPERIMENT COMPLETED!")
        print("=" * 60)
        
        print(f"⏱️  Total Duration: {results['total_duration']:.2f}s ({results['total_duration']/60:.1f} minutes)")
        print(f"🔄 Cycles: {results['cycles_completed']}/{results['cycles_requested']}")
        print(f"⏰ Early Stopping: {results.get('early_stopping', False)}")
        
        print(f"\n📊 FINAL PERFORMANCE:")
        print(f"   🏆 Best pass@1: {results['final_metrics']['best_pass_at_1']:.4f}")
        print(f"   📈 Average pass@1: {results['final_metrics']['avg_pass_at_1']:.4f}")
        print(f"   🎯 Best ratio: {results['final_metrics']['best_ratio']:.4f}")
        print(f"   📊 Average ratio: {results['final_metrics']['avg_ratio']:.4f}")
        
        # Enhanced success criteria with fallback
        best_pass = results['final_metrics']['best_pass_at_1']
        
        # Calculate pass@k uplift vs n=1 baseline
        n1_performance = 0.0
        n4_performance = 0.0
        n16_performance = 0.0
        
        for cycle_key, cycle_data in results['cycle_results'].items():
            n1_performance = max(n1_performance, cycle_data['metrics'].get('pass_at_1_n1', 0))
            n4_performance = max(n4_performance, cycle_data['metrics'].get('pass_at_1_n4', 0))
            n16_performance = max(n16_performance, cycle_data['metrics'].get('pass_at_1_n16', 0))
        
        uplift_4 = (n4_performance - n1_performance) * 100
        uplift_16 = (n16_performance - n1_performance) * 100
        max_uplift = max(uplift_4, uplift_16)
        
        print(f"\n📈 PROGRESSIVE SAMPLING ANALYSIS:")
        print(f"   n=1 baseline: {n1_performance:.4f}")
        print(f"   n=4 performance: {n4_performance:.4f} (uplift: {uplift_4:.1f}pp)")
        print(f"   n=16 performance: {n16_performance:.4f} (uplift: {uplift_16:.1f}pp)")
        print(f"   Max uplift: {max_uplift:.1f} percentage points")
        
        # Enhanced success assessment
        if best_pass >= 0.6:
            assessment = "🎯 EXCELLENT - Primary target achieved!"
            success_level = "PRIMARY"
        elif best_pass >= 0.45:
            assessment = "✅ GOOD - Fallback target achieved!"
            success_level = "FALLBACK"
        elif max_uplift >= 8.0:
            assessment = "📈 ACCEPTABLE - Significant uplift achieved!"
            success_level = "UPLIFT"
        else:
            assessment = "❌ NEEDS WORK - Below all targets"
            success_level = "FAILED"
        
        print(f"\n📋 ENHANCED ASSESSMENT: {assessment}")
        print(f"   Success Level: {success_level}")
        print(f"   Primary Target (pass@1 ≥ 0.6): {'✅' if best_pass >= 0.6 else '❌'}")
        print(f"   Fallback Target (pass@1 ≥ 0.45): {'✅' if best_pass >= 0.45 else '❌'}")
        print(f"   Uplift Target (≥ 8pp): {'✅' if max_uplift >= 8.0 else '❌'}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if success_level == "FAILED":
            print("   - Increase temperature for more creativity")
            print("   - Try higher n values (32, 64)")
            print("   - Implement chain-of-thought prompting")
            print("   - Consider ensemble methods")
        elif success_level == "UPLIFT":
            print("   - Progressive sampling working well")
            print("   - Focus on improving baseline performance")
            print("   - Fine-tune temperature settings")
        elif success_level == "FALLBACK":
            print("   - Good performance, near primary target")
            print("   - Optimize progressive sampling strategy")
            print("   - Consider higher n values for difficult tasks")
        else:
            print("   - Excellent performance achieved!")
            print("   - Consider scaling to larger datasets")
            print("   - Explore additional optimization techniques")
        
        # Return success metrics for external use
        return {
            'success_level': success_level,
            'best_pass_at_1': best_pass,
            'max_uplift': max_uplift,
            'assessment': assessment
        }


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Execute Refined Plan with HumanEval-164')
    
    parser.add_argument('--mode', choices=['test', 'production'], default='production',
                       help='Execution mode (default: production)')
    parser.add_argument('--num_tasks', type=int, default=164,
                       help='Number of HumanEval tasks to run (default: 164)')
    parser.add_argument('--n_samples', type=int, default=16,
                       help='Maximum number of samples for best-of-n (default: 16)')
    parser.add_argument('--save', type=str, default=None,
                       help='Output file for results (default: auto-generated)')
    parser.add_argument('--cache', type=str, default=None,
                       help='Cache directory for results (not implemented yet)')
    
    return parser.parse_args()


async def main():
    """Main execution function"""
    
    args = parse_arguments()
    
    print("🚀 REFINED PLAN EXECUTOR")
    print("=" * 50)
    print(f"Mode: {args.mode}")
    print(f"Tasks: {args.num_tasks}")
    print(f"N samples: {args.n_samples}")
    if args.save:
        print(f"Output: {args.save}")
    
    executor = RefinedPlanExecutor()
    
    try:
        if args.mode == 'test':
            print("🧪 Running in TEST mode")
            results = await executor.run_testing_experiment(args.num_tasks)
        else:
            print("🚀 Running in PRODUCTION mode")
            results = await executor.run_production_experiment(args.num_tasks, args.n_samples)
        
        # Save results
        executor.save_comprehensive_results(results, args.mode, args.save)
        executor.print_summary(results, args.mode)
        
        print(f"\n✅ Execution completed successfully!")
        print(f"📁 Check the 'results/' directory for detailed outputs")
        
    except Exception as e:
        print(f"\n❌ Execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 