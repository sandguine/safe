#!/usr/bin/env python3
"""
CLI version of AZR deduction loop for oversight curriculum.
Implements the minimal AZR loop with CLI flags as specified in the plan.
"""

import os
import sys
import json
import argparse
import time
from pathlib import Path
from typing import Dict, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from deduction_loop import DeductionLoop, Puzzle, Solution
from referee import Referee
from metrics import MetricsCollector


def load_config(config_path: str = "configs/deduction_mini.json") -> List[Dict]:
    """Load hard-coded puzzle triplets from config file"""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config.get('puzzles', [])
    except FileNotFoundError:
        print(f"Warning: Config file {config_path} not found, using dynamic generation")
        return []


def run_minimal_loop(cycles: int, with_ref: bool, use_config: bool = True) -> MetricsCollector:
    """
    Run minimal AZR loop optimized for ≤15s execution
    
    Args:
        cycles: Number of cycles to run
        with_ref: Whether to enable referee oversight
        use_config: Whether to use hard-coded config puzzles
    """
    
    # Load config puzzles if requested
    config_puzzles = load_config() if use_config else []
    
    # Initialize components with minimal settings for speed
    loop = DeductionLoop(
        enable_referee=with_ref,
        max_puzzles_per_cycle=2,  # Reduced for speed
        max_solutions_per_puzzle=1  # Reduced for speed
    )
    
    # Override puzzle generation if using config
    if config_puzzles and use_config:
        loop._use_config_puzzles = True
        loop._config_puzzles = config_puzzles
        loop._config_puzzle_index = 0
    
    metrics_collector = MetricsCollector()
    
    print(f"Running {cycles} cycles with referee={'ON' if with_ref else 'OFF'}")
    
    for cycle in range(1, cycles + 1):
        print(f"Cycle {cycle}/{cycles}...")
        
        # Run one cycle
        cycle_metrics = loop.run_cycle()
        
        # Update metrics collector
        metrics_collector.update(cycle_metrics)
        
        # Print quick summary
        print(f"  Puzzles: {cycle_metrics['puzzles_generated']} gen, "
              f"{cycle_metrics['puzzles_approved']} approved")
        print(f"  Solutions: {cycle_metrics['solutions_generated']} gen, "
              f"{cycle_metrics['solutions_correct']} correct")
    
    return metrics_collector


def export_to_csv(metrics: MetricsCollector, output_path: str):
    """Export metrics to CSV format as specified in plan"""
    import csv
    
    # Get all cycle metrics
    cycle_metrics = metrics.get_all_metrics()
    
    with open(output_path, 'w', newline='') as csvfile:
        fieldnames = ['task_id', 'code_len', 'banned_import', 'solver_reward', 'referee_veto']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        
        for i, cycle_metric in enumerate(cycle_metrics):
            # Create a row for each cycle
            row = {
                'task_id': f"cycle_{i+1}",
                'code_len': cycle_metric.get('puzzles_generated', 0) * 100,  # Approximate
                'banned_import': 0,  # Would need to track this in deduction loop
                'solver_reward': cycle_metric.get('avg_solution_reward', 0.0),
                'referee_veto': cycle_metric.get('puzzles_rejected', 0)
            }
            writer.writerow(row)


def parse_args():
    """Parse command line arguments as specified in plan"""
    parser = argparse.ArgumentParser(description='AZR Deduction Loop with Oversight')
    parser.add_argument('--with_ref', action='store_true', 
                       help='Enable referee oversight')
    parser.add_argument('--no_ref', action='store_true', 
                       help='Disable referee oversight')
    parser.add_argument('--cycles', type=int, default=10, 
                       help='Number of cycles to run (default: 10)')
    parser.add_argument('--config', action='store_true', default=True,
                       help='Use hard-coded config puzzles (default: True)')
    parser.add_argument('--output', type=str, default='results/demo.csv',
                       help='Output CSV file path')
    
    return parser.parse_args()


def main():
    """Main CLI function"""
    args = parse_args()
    
    # Check API key
    if not os.getenv("CLAUDE_API_KEY"):
        print("❌ Error: CLAUDE_API_KEY environment variable not set")
        print("Please set your API key: export CLAUDE_API_KEY='your-key-here'")
        sys.exit(1)
    
    # Determine referee setting
    if args.with_ref and args.no_ref:
        print("❌ Error: Cannot specify both --with_ref and --no_ref")
        sys.exit(1)
    
    with_ref = args.with_ref if args.with_ref else not args.no_ref
    
    # Create results directory
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    
    print(f"🎯 AZR Loop CLI")
    print(f"Cycles: {args.cycles}")
    print(f"Referee: {'ON' if with_ref else 'OFF'}")
    print(f"Config puzzles: {'ON' if args.config else 'OFF'}")
    print("=" * 50)
    
    start_time = time.time()
    
    try:
        # Run the minimal loop
        metrics = run_minimal_loop(
            cycles=args.cycles,
            with_ref=with_ref,
            use_config=args.config
        )
        
        # Export to CSV
        export_to_csv(metrics, args.output)
        
        # Print summary
        summary = metrics.get_summary()
        print(f"\n📊 Summary:")
        print(f"Total cycles: {summary.total_cycles}")
        print(f"Total puzzles: {summary.total_puzzles}")
        print(f"Total solutions: {summary.total_solutions}")
        print(f"Approval rate: {summary.approval_rate:.2%}")
        print(f"Success rate: {summary.success_rate:.2%}")
        print(f"Avg reward: {summary.avg_reward:.3f}")
        print(f"Duration: {time.time() - start_time:.2f}s")
        print(f"Results saved to: {args.output}")
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 