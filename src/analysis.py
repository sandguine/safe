#!/usr/bin/env python3
"""
Analysis script for oversight curriculum results.
Loads baseline and oversight CSV files and generates comparison plots.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import argparse


def load_csv_data(baseline_path: str, oversight_path: str) -> tuple:
    """Load baseline and oversight CSV data"""
    try:
        baseline_df = pd.read_csv(baseline_path)
        oversight_df = pd.read_csv(oversight_path)
        return baseline_df, oversight_df
    except FileNotFoundError as e:
        print(f"Error loading CSV files: {e}")
        return None, None


def compute_statistics(baseline_df: pd.DataFrame, oversight_df: pd.DataFrame) -> dict:
    """Compute comparison statistics"""
    stats = {}
    
    # Mean solver reward per cycle
    stats['baseline_mean_reward'] = baseline_df['solver_reward'].mean()
    stats['oversight_mean_reward'] = oversight_df['solver_reward'].mean()
    stats['reward_improvement'] = stats['oversight_mean_reward'] - stats['baseline_mean_reward']
    
    # Percentage of tasks vetoed
    stats['baseline_veto_rate'] = (baseline_df['referee_veto'] > 0).mean()
    stats['oversight_veto_rate'] = (oversight_df['referee_veto'] > 0).mean()
    
    # Code length statistics
    stats['baseline_mean_code_len'] = baseline_df['code_len'].mean()
    stats['oversight_mean_code_len'] = oversight_df['code_len'].mean()
    
    return stats


def create_comparison_plot(baseline_df: pd.DataFrame, oversight_df: pd.DataFrame, 
                          output_path: str = "results/comparison_plot.png"):
    """Create comparison plot with bars and histogram inset"""
    
    # Create figure with subplots
    fig = plt.figure(figsize=(12, 8))
    
    # Main comparison bars
    ax1 = plt.subplot2grid((2, 3), (0, 0), colspan=2)
    
    # Prepare data for bar plot
    metrics = ['Mean Reward', 'Veto Rate', 'Code Length']
    baseline_values = [
        baseline_df['solver_reward'].mean(),
        (baseline_df['referee_veto'] > 0).mean(),
        baseline_df['code_len'].mean() / 1000  # Normalize for display
    ]
    oversight_values = [
        oversight_df['solver_reward'].mean(),
        (oversight_df['referee_veto'] > 0).mean(),
        oversight_df['code_len'].mean() / 1000  # Normalize for display
    ]
    
    x = np.arange(len(metrics))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, baseline_values, width, label='Baseline', alpha=0.8)
    bars2 = ax1.bar(x + width/2, oversight_values, width, label='Oversight', alpha=0.8)
    
    ax1.set_xlabel('Metrics')
    ax1.set_ylabel('Values')
    ax1.set_title('Baseline vs Oversight Comparison')
    ax1.set_xticks(x)
    ax1.set_xticklabels(metrics)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax1.annotate(f'{height:.3f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8)
    
    # Histogram inset for code length distribution
    ax2 = plt.subplot2grid((2, 3), (0, 2))
    
    ax2.hist(baseline_df['code_len'], alpha=0.7, label='Baseline', bins=10)
    ax2.hist(oversight_df['code_len'], alpha=0.7, label='Oversight', bins=10)
    ax2.set_xlabel('Code Length')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Code Length Distribution')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Learning curves over cycles
    ax3 = plt.subplot2grid((2, 3), (1, 0), colspan=3)
    
    cycles = range(1, len(baseline_df) + 1)
    ax3.plot(cycles, baseline_df['solver_reward'], 'o-', label='Baseline', alpha=0.8)
    ax3.plot(cycles, oversight_df['solver_reward'], 's-', label='Oversight', alpha=0.8)
    ax3.set_xlabel('Cycle')
    ax3.set_ylabel('Solver Reward')
    ax3.set_title('Learning Curves: Reward Over Time')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save plot
    output_path = Path(output_path)
    output_path.parent.mkdir(exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Comparison plot saved to {output_path}")
    
    return fig


def print_statistics(stats: dict):
    """Print comparison statistics"""
    print("\n" + "=" * 50)
    print("COMPARISON STATISTICS")
    print("=" * 50)
    
    print(f"Mean Solver Reward:")
    print(f"  Baseline: {stats['baseline_mean_reward']:.3f}")
    print(f"  Oversight: {stats['oversight_mean_reward']:.3f}")
    print(f"  Improvement: {stats['reward_improvement']:+.3f}")
    
    print(f"\nVeto Rate:")
    print(f"  Baseline: {stats['baseline_veto_rate']:.2%}")
    print(f"  Oversight: {stats['oversight_veto_rate']:.2%}")
    
    print(f"\nMean Code Length:")
    print(f"  Baseline: {stats['baseline_mean_code_len']:.0f}")
    print(f"  Oversight: {stats['oversight_mean_code_len']:.0f}")
    
    # Determine if oversight improved performance
    improvement_count = 0
    if stats['reward_improvement'] > 0:
        print("✓ Reward improved with oversight")
        improvement_count += 1
    if stats['oversight_veto_rate'] > 0:
        print("✓ Oversight is actively filtering content")
        improvement_count += 1
    
    print(f"\nOverall: {improvement_count}/2 key metrics show oversight impact")


def main():
    """Main analysis function"""
    parser = argparse.ArgumentParser(description='Analyze oversight curriculum results')
    parser.add_argument('--baseline', type=str, default='results/baseline_demo.csv',
                       help='Baseline CSV file path')
    parser.add_argument('--oversight', type=str, default='results/oversight_demo.csv',
                       help='Oversight CSV file path')
    parser.add_argument('--output', type=str, default='results/comparison_plot.png',
                       help='Output plot file path')
    
    args = parser.parse_args()
    
    print("📊 Oversight Curriculum Analysis")
    print("=" * 50)
    
    # Load data
    baseline_df, oversight_df = load_csv_data(args.baseline, args.oversight)
    
    if baseline_df is None or oversight_df is None:
        print("❌ Failed to load CSV data")
        return
    
    print(f"✓ Loaded baseline data: {len(baseline_df)} cycles")
    print(f"✓ Loaded oversight data: {len(oversight_df)} cycles")
    
    # Compute statistics
    stats = compute_statistics(baseline_df, oversight_df)
    
    # Print statistics
    print_statistics(stats)
    
    # Create comparison plot
    try:
        create_comparison_plot(baseline_df, oversight_df, args.output)
        print(f"\n🎉 Analysis complete! Check {args.output} for the comparison plot.")
    except Exception as e:
        print(f"❌ Error creating plot: {e}")


if __name__ == "__main__":
    main() 