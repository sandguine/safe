"""
Metrics collection system for oversight curriculum.
Tracks performance, learning progress, and comparison between baseline and oversight runs.
"""

import json
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict
import statistics


@dataclass
class CycleMetrics:
    """Metrics for a single deduction cycle"""
    cycle: int
    puzzles_generated: int
    puzzles_approved: int
    puzzles_rejected: int
    solutions_generated: int
    solutions_correct: int
    avg_solution_reward: float
    avg_puzzle_safety: float
    cycle_duration: float
    timestamp: float


@dataclass
class RunSummary:
    """Summary statistics for a complete run"""
    total_cycles: int
    total_puzzles: int
    total_solutions: int
    approval_rate: float
    success_rate: float
    avg_reward: float
    avg_safety: float
    total_duration: float
    puzzles_per_cycle: float
    solutions_per_cycle: float


class MetricsCollector:
    """
    Collects and analyzes metrics from deduction loop runs.
    
    Tracks:
    - Per-cycle metrics
    - Overall run statistics
    - Learning progress over time
    - Comparison between different runs
    """
    
    def __init__(self):
        self.cycle_metrics: List[CycleMetrics] = []
        self.run_start_time = time.time()
        
    def update(self, metrics: Dict):
        """Update metrics with new cycle data"""
        cycle_metrics = CycleMetrics(
            cycle=metrics.get('cycle', 0),
            puzzles_generated=metrics.get('puzzles_generated', 0),
            puzzles_approved=metrics.get('puzzles_approved', 0),
            puzzles_rejected=metrics.get('puzzles_rejected', 0),
            solutions_generated=metrics.get('solutions_generated', 0),
            solutions_correct=metrics.get('solutions_correct', 0),
            avg_solution_reward=metrics.get('avg_solution_reward', 0.0),
            avg_puzzle_safety=metrics.get('avg_puzzle_safety', 0.0),
            cycle_duration=metrics.get('cycle_duration', 0.0),
            timestamp=time.time()
        )
        
        self.cycle_metrics.append(cycle_metrics)
    
    def get_summary(self) -> RunSummary:
        """Get summary statistics for the entire run"""
        if not self.cycle_metrics:
            return RunSummary(
                total_cycles=0,
                total_puzzles=0,
                total_solutions=0,
                approval_rate=0.0,
                success_rate=0.0,
                avg_reward=0.0,
                avg_safety=0.0,
                total_duration=0.0,
                puzzles_per_cycle=0.0,
                solutions_per_cycle=0.0
            )
        
        total_cycles = len(self.cycle_metrics)
        total_puzzles = sum(m.puzzles_generated for m in self.cycle_metrics)
        total_solutions = sum(m.solutions_generated for m in self.cycle_metrics)
        total_approved = sum(m.puzzles_approved for m in self.cycle_metrics)
        total_correct = sum(m.solutions_correct for m in self.cycle_metrics)
        
        total_duration = time.time() - self.run_start_time
        
        return RunSummary(
            total_cycles=total_cycles,
            total_puzzles=total_puzzles,
            total_solutions=total_solutions,
            approval_rate=total_approved / max(total_puzzles, 1),
            success_rate=total_correct / max(total_solutions, 1),
            avg_reward=statistics.mean([m.avg_solution_reward for m in self.cycle_metrics]),
            avg_safety=statistics.mean([m.avg_puzzle_safety for m in self.cycle_metrics]),
            total_duration=total_duration,
            puzzles_per_cycle=total_puzzles / max(total_cycles, 1),
            solutions_per_cycle=total_solutions / max(total_cycles, 1)
        )
    
    def get_learning_curve(self) -> Dict[str, List[float]]:
        """Get learning curve data for plotting"""
        if not self.cycle_metrics:
            return {}
        
        cycles = [m.cycle for m in self.cycle_metrics]
        rewards = [m.avg_solution_reward for m in self.cycle_metrics]
        safety_scores = [m.avg_puzzle_safety for m in self.cycle_metrics]
        approval_rates = [m.puzzles_approved / max(m.puzzles_generated, 1) 
                         for m in self.cycle_metrics]
        success_rates = [m.solutions_correct / max(m.solutions_generated, 1) 
                        for m in self.cycle_metrics]
        
        return {
            'cycles': cycles,
            'rewards': rewards,
            'safety_scores': safety_scores,
            'approval_rates': approval_rates,
            'success_rates': success_rates
        }
    
    def get_all_metrics(self) -> List[Dict]:
        """Get all cycle metrics as dictionaries"""
        return [asdict(m) for m in self.cycle_metrics]
    
    def load_metrics(self, metrics_data: List[Dict]):
        """Load metrics from saved data"""
        self.cycle_metrics = [CycleMetrics(**m) for m in metrics_data]
    
    def export_to_json(self, filepath: str):
        """Export metrics to JSON file"""
        data = {
            'summary': asdict(self.get_summary()),
            'learning_curve': self.get_learning_curve(),
            'cycle_metrics': self.get_all_metrics()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def import_from_json(self, filepath: str):
        """Import metrics from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        if 'cycle_metrics' in data:
            self.load_metrics(data['cycle_metrics'])


class ComparisonAnalyzer:
    """
    Analyzes and compares results between baseline and oversight runs.
    """
    
    def __init__(self):
        self.baseline_metrics: Optional[MetricsCollector] = None
        self.oversight_metrics: Optional[MetricsCollector] = None
    
    def set_baseline(self, metrics: MetricsCollector):
        """Set baseline run metrics"""
        self.baseline_metrics = metrics
    
    def set_oversight(self, metrics: MetricsCollector):
        """Set oversight run metrics"""
        self.oversight_metrics = metrics
    
    def compare_runs(self) -> Dict:
        """Compare baseline vs oversight runs"""
        if not self.baseline_metrics or not self.oversight_metrics:
            return {}
        
        baseline_summary = self.baseline_metrics.get_summary()
        oversight_summary = self.oversight_metrics.get_summary()
        
        # Calculate differences
        reward_diff = oversight_summary.avg_reward - baseline_summary.avg_reward
        safety_diff = oversight_summary.avg_safety - baseline_summary.avg_safety
        approval_diff = oversight_summary.approval_rate - baseline_summary.approval_rate
        success_diff = oversight_summary.success_rate - baseline_summary.success_rate
        
        # Calculate percentage changes
        reward_pct = (reward_diff / max(baseline_summary.avg_reward, 0.01)) * 100
        safety_pct = (safety_diff / max(baseline_summary.avg_safety, 0.01)) * 100
        approval_pct = (approval_diff / max(baseline_summary.approval_rate, 0.01)) * 100
        success_pct = (success_diff / max(baseline_summary.success_rate, 0.01)) * 100
        
        return {
            'baseline': asdict(baseline_summary),
            'oversight': asdict(oversight_summary),
            'differences': {
                'reward_diff': reward_diff,
                'safety_diff': safety_diff,
                'approval_diff': approval_diff,
                'success_diff': success_diff,
                'reward_pct_change': reward_pct,
                'safety_pct_change': safety_pct,
                'approval_pct_change': approval_pct,
                'success_pct_change': success_pct
            },
            'oversight_impact': {
                'reward_improved': reward_diff > 0,
                'safety_improved': safety_diff > 0,
                'approval_improved': approval_diff > 0,
                'success_improved': success_diff > 0
            }
        }
    
    def generate_report(self) -> str:
        """Generate a human-readable comparison report"""
        comparison = self.compare_runs()
        if not comparison:
            return "No comparison data available"
        
        report = []
        report.append("=== OVERSIGHT CURRICULUM COMPARISON REPORT ===\n")
        
        # Baseline vs Oversight summary
        report.append("BASELINE RUN:")
        baseline = comparison['baseline']
        report.append(f"  Total cycles: {baseline['total_cycles']}")
        report.append(f"  Approval rate: {baseline['approval_rate']:.2%}")
        report.append(f"  Success rate: {baseline['success_rate']:.2%}")
        report.append(f"  Avg reward: {baseline['avg_reward']:.3f}")
        report.append(f"  Avg safety: {baseline['avg_safety']:.3f}")
        
        report.append("\nOVERSIGHT RUN:")
        oversight = comparison['oversight']
        report.append(f"  Total cycles: {oversight['total_cycles']}")
        report.append(f"  Approval rate: {oversight['approval_rate']:.2%}")
        report.append(f"  Success rate: {oversight['success_rate']:.2%}")
        report.append(f"  Avg reward: {oversight['avg_reward']:.3f}")
        report.append(f"  Avg safety: {oversight['avg_safety']:.3f}")
        
        # Differences
        report.append("\nCHANGES WITH OVERSIGHT:")
        diffs = comparison['differences']
        report.append(f"  Reward: {diffs['reward_diff']:+.3f} ({diffs['reward_pct_change']:+.1f}%)")
        report.append(f"  Safety: {diffs['safety_diff']:+.3f} ({diffs['safety_pct_change']:+.1f}%)")
        report.append(f"  Approval rate: {diffs['approval_diff']:+.2%} ({diffs['approval_pct_change']:+.1f}%)")
        report.append(f"  Success rate: {diffs['success_diff']:+.2%} ({diffs['success_pct_change']:+.1f}%)")
        
        # Impact summary
        report.append("\nOVERSIGHT IMPACT:")
        impact = comparison['oversight_impact']
        improvements = sum(impact.values())
        report.append(f"  Metrics improved: {improvements}/4")
        
        if impact['reward_improved']:
            report.append("  ✓ Reward improved")
        if impact['safety_improved']:
            report.append("  ✓ Safety improved")
        if impact['approval_improved']:
            report.append("  ✓ Approval rate improved")
        if impact['success_improved']:
            report.append("  ✓ Success rate improved")
        
        return "\n".join(report) 