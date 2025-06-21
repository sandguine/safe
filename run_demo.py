#!/usr/bin/env python3
"""
Main demo script for oversight curriculum.
Runs baseline and oversight experiments and generates comparison reports.
Now includes CLI support and optimization for ≤15s execution.
"""

import os
import sys
import time
import json
import argparse
from pathlib import Path
from typing import Dict, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from deduction_loop import DeductionLoop
from metrics import MetricsCollector, ComparisonAnalyzer


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Oversight Curriculum Demo')
    parser.add_argument('--cycles', type=int, default=10, 
                       help='Number of cycles per experiment (default: 10)')
    parser.add_argument('--puzzles_per_cycle', type=int, default=2,
                       help='Puzzles per cycle for speed optimization (default: 2)')
    parser.add_argument('--solutions_per_puzzle', type=int, default=1,
                       help='Solutions per puzzle for speed optimization (default: 1)')
    parser.add_argument('--use_config', action='store_true', default=True,
                       help='Use hard-coded config puzzles (default: True)')
    parser.add_argument('--skip_plots', action='store_true',
                       help='Skip plot generation for faster execution')
    parser.add_argument('--output_dir', type=str, default='results',
                       help='Output directory for results (default: results)')
    
    return parser.parse_args()


def run_baseline_experiment(cycles: int, 
                          max_puzzles_per_cycle: int = 2,
                          max_solutions_per_puzzle: int = 1,
                          use_config: bool = True) -> MetricsCollector:
    """Run baseline experiment without referee oversight"""
    print("=" * 60)
    print("RUNNING BASELINE EXPERIMENT (No Referee)")
    print("=" * 60)
    
    # Initialize deduction loop without referee
    loop = DeductionLoop(
        enable_referee=False,
        max_puzzles_per_cycle=max_puzzles_per_cycle,
        max_solutions_per_puzzle=max_solutions_per_puzzle
    )
    
    # Set up config puzzles if requested
    if use_config:
        config_puzzles = load_config_puzzles()
        if config_puzzles:
            loop._use_config_puzzles = True
            loop._config_puzzles = config_puzzles
            loop._config_puzzle_index = 0
    
    # Run cycles
    for cycle in range(1, cycles + 1):
        print(f"\n--- Cycle {cycle}/{cycles} ---")
        metrics = loop.run_cycle()
        
        # Print cycle summary
        print(f"Puzzles: {metrics['puzzles_generated']} generated, "
              f"{metrics['puzzles_approved']} approved")
        print(f"Solutions: {metrics['solutions_generated']} generated, "
              f"{metrics['solutions_correct']} correct")
        print(f"Avg reward: {metrics['avg_solution_reward']:.3f}")
        print(f"Duration: {metrics['cycle_duration']:.2f}s")
    
    # Get final summary
    summary = loop.get_summary_stats()
    print(f"\nBASELINE SUMMARY:")
    print(f"Total cycles: {summary['total_cycles']}")
    print(f"Approval rate: {summary['approval_rate']:.2%}")
    print(f"Success rate: {summary['success_rate']:.2%}")
    print(f"Avg reward: {summary['avg_reward']:.3f}")
    
    return loop.metrics


def run_oversight_experiment(cycles: int,
                           max_puzzles_per_cycle: int = 2,
                           max_solutions_per_puzzle: int = 1,
                           use_config: bool = True) -> MetricsCollector:
    """Run oversight experiment with referee"""
    print("\n" + "=" * 60)
    print("RUNNING OVERSIGHT EXPERIMENT (With Referee)")
    print("=" * 60)
    
    # Initialize deduction loop with referee
    loop = DeductionLoop(
        enable_referee=True,
        max_puzzles_per_cycle=max_puzzles_per_cycle,
        max_solutions_per_puzzle=max_solutions_per_puzzle
    )
    
    # Set up config puzzles if requested
    if use_config:
        config_puzzles = load_config_puzzles()
        if config_puzzles:
            loop._use_config_puzzles = True
            loop._config_puzzles = config_puzzles
            loop._config_puzzle_index = 0
    
    # Run cycles
    for cycle in range(1, cycles + 1):
        print(f"\n--- Cycle {cycle}/{cycles} ---")
        metrics = loop.run_cycle()
        
        # Print cycle summary
        print(f"Puzzles: {metrics['puzzles_generated']} generated, "
              f"{metrics['puzzles_approved']} approved, "
              f"{metrics['puzzles_rejected']} rejected")
        print(f"Solutions: {metrics['solutions_generated']} generated, "
              f"{metrics['solutions_correct']} correct")
        print(f"Avg reward: {metrics['avg_solution_reward']:.3f}")
        print(f"Avg safety: {metrics['avg_puzzle_safety']:.3f}")
        print(f"Duration: {metrics['cycle_duration']:.2f}s")
    
    # Get final summary
    summary = loop.get_summary_stats()
    print(f"\nOVERSIGHT SUMMARY:")
    print(f"Total cycles: {summary['total_cycles']}")
    print(f"Approval rate: {summary['approval_rate']:.2%}")
    print(f"Success rate: {summary['success_rate']:.2%}")
    print(f"Avg reward: {summary['avg_reward']:.3f}")
    print(f"Avg safety: {summary['avg_safety']:.3f}")
    
    return loop.metrics


def load_config_puzzles() -> List[Dict]:
    """Load hard-coded puzzle triplets from config file"""
    config_path = "configs/deduction_mini.json"
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config.get('puzzles', [])
    except FileNotFoundError:
        print(f"Warning: Config file {config_path} not found, using dynamic generation")
        return []


def generate_comparison_report(baseline_metrics: MetricsCollector, 
                             oversight_metrics: MetricsCollector) -> str:
    """Generate comparison report between baseline and oversight runs"""
    print("\n" + "=" * 60)
    print("GENERATING COMPARISON REPORT")
    print("=" * 60)
    
    analyzer = ComparisonAnalyzer()
    analyzer.set_baseline(baseline_metrics)
    analyzer.set_oversight(oversight_metrics)
    
    report = analyzer.generate_report()
    print(report)
    
    return report


def save_results(baseline_metrics: MetricsCollector, 
                oversight_metrics: MetricsCollector, 
                comparison_report: str,
                output_dir: str = "results"):
    """Save all results to files"""
    print("\n" + "=" * 60)
    print("SAVING RESULTS")
    print("=" * 60)
    
    # Create results directory
    results_dir = Path(output_dir)
    results_dir.mkdir(exist_ok=True)
    
    # Save baseline metrics
    baseline_metrics.export_to_json(results_dir / "baseline_metrics.json")
    baseline_metrics.export_to_csv(results_dir / "baseline_demo.csv")
    print("✓ Saved baseline metrics")
    
    # Save oversight metrics
    oversight_metrics.export_to_json(results_dir / "oversight_metrics.json")
    oversight_metrics.export_to_csv(results_dir / "oversight_demo.csv")
    print("✓ Saved oversight metrics")
    
    # Save comparison report
    with open(results_dir / "comparison_report.txt", "w") as f:
        f.write(comparison_report)
    print("✓ Saved comparison report")
    
    # Save combined results
    combined_data = {
        'baseline': baseline_metrics.get_summary().__dict__,
        'oversight': oversight_metrics.get_summary().__dict__,
        'comparison': ComparisonAnalyzer().compare_runs()
    }
    
    with open(results_dir / "combined_results.json", "w") as f:
        json.dump(combined_data, f, indent=2)
    print("✓ Saved combined results")


def create_plots(baseline_metrics: MetricsCollector, 
                oversight_metrics: MetricsCollector,
                output_dir: str = "results"):
    """Create learning curve plots"""
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        
        print("\n" + "=" * 60)
        print("GENERATING PLOTS")
        print("=" * 60)
        
        # Get learning curve data
        baseline_curve = baseline_metrics.get_learning_curve()
        oversight_curve = oversight_metrics.get_learning_curve()
        
        if not baseline_curve or not oversight_curve:
            print("No learning curve data available")
            return
        
        # Create plots
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('Oversight Curriculum Learning Curves', fontsize=16)
        
        # Plot 1: Rewards over time
        axes[0, 0].plot(baseline_curve['cycles'], baseline_curve['rewards'], 
                       label='Baseline', marker='o')
        axes[0, 0].plot(oversight_curve['cycles'], oversight_curve['rewards'], 
                       label='Oversight', marker='s')
        axes[0, 0].set_title('Average Solution Reward')
        axes[0, 0].set_xlabel('Cycle')
        axes[0, 0].set_ylabel('Reward')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # Plot 2: Safety scores over time
        axes[0, 1].plot(baseline_curve['cycles'], baseline_curve['safety_scores'], 
                       label='Baseline', marker='o')
        axes[0, 1].plot(oversight_curve['cycles'], oversight_curve['safety_scores'], 
                       label='Oversight', marker='s')
        axes[0, 1].set_title('Average Puzzle Safety')
        axes[0, 1].set_xlabel('Cycle')
        axes[0, 1].set_ylabel('Safety Score')
        axes[0, 1].legend()
        axes[0, 1].grid(True)
        
        # Plot 3: Approval rates over time
        axes[1, 0].plot(baseline_curve['cycles'], baseline_curve['approval_rates'], 
                       label='Baseline', marker='o')
        axes[1, 0].plot(oversight_curve['cycles'], oversight_curve['approval_rates'], 
                       label='Oversight', marker='s')
        axes[1, 0].set_title('Puzzle Approval Rate')
        axes[1, 0].set_xlabel('Cycle')
        axes[1, 0].set_ylabel('Approval Rate')
        axes[1, 0].legend()
        axes[1, 0].grid(True)
        
        # Plot 4: Success rates over time
        axes[1, 1].plot(baseline_curve['cycles'], baseline_curve['success_rates'], 
                       label='Baseline', marker='o')
        axes[1, 1].plot(oversight_curve['cycles'], oversight_curve['success_rates'], 
                       label='Oversight', marker='s')
        axes[1, 1].set_title('Solution Success Rate')
        axes[1, 1].set_xlabel('Cycle')
        axes[1, 1].set_ylabel('Success Rate')
        axes[1, 1].legend()
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        
        # Save plot
        results_dir = Path(output_dir)
        results_dir.mkdir(exist_ok=True)
        plt.savefig(results_dir / "learning_curves.png", dpi=300, bbox_inches='tight')
        print("✓ Saved learning curves plot")
        
    except ImportError:
        print("Matplotlib not available, skipping plots")
    except Exception as e:
        print(f"Error creating plots: {e}")


def main():
    """Main demo function"""
    args = parse_args()
    
    print("🎯 OVERSIGHT CURRICULUM DEMO")
    print("=" * 60)
    
    # Check API key
    if not os.getenv("CLAUDE_API_KEY"):
        print("❌ CLAUDE_API_KEY environment variable not set")
        print("Please set your API key: export CLAUDE_API_KEY='your-key-here'")
        return
    
    # Configuration
    cycles = args.cycles
    max_puzzles_per_cycle = args.puzzles_per_cycle
    max_solutions_per_puzzle = args.solutions_per_puzzle
    use_config = args.use_config
    skip_plots = args.skip_plots
    output_dir = args.output_dir
    
    print(f"Configuration:")
    print(f"  Cycles per experiment: {cycles}")
    print(f"  Puzzles per cycle: {max_puzzles_per_cycle}")
    print(f"  Solutions per puzzle: {max_solutions_per_puzzle}")
    print(f"  Use config puzzles: {use_config}")
    print(f"  Skip plots: {skip_plots}")
    print(f"  Output directory: {output_dir}")
    print(f"  Model: claude-3-5-sonnet-20241022")
    
    start_time = time.time()
    
    try:
        # Run baseline experiment
        baseline_metrics = run_baseline_experiment(
            cycles, max_puzzles_per_cycle, max_solutions_per_puzzle, use_config
        )
        
        # Run oversight experiment
        oversight_metrics = run_oversight_experiment(
            cycles, max_puzzles_per_cycle, max_solutions_per_puzzle, use_config
        )
        
        # Generate comparison report
        comparison_report = generate_comparison_report(baseline_metrics, 
                                                     oversight_metrics)
        
        # Save results
        save_results(baseline_metrics, oversight_metrics, comparison_report, output_dir)
        
        # Create plots (unless skipped)
        if not skip_plots:
            create_plots(baseline_metrics, oversight_metrics, output_dir)
        
        total_time = time.time() - start_time
        print(f"\n🎉 Demo completed in {total_time:.2f} seconds!")
        print(f"Check the '{output_dir}/' directory for output files.")
        
        # Check if execution time meets plan requirements
        if total_time <= 15.0:
            print("✅ Execution time ≤15s - meets plan requirements!")
        else:
            print(f"⚠️  Execution time {total_time:.2f}s > 15s - consider reducing cycles/puzzles")
        
    except KeyboardInterrupt:
        print("\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 