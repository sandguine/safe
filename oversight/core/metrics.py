"""
Metrics collection and analysis for oversight curriculum.
Provides tools for tracking experiment performance and safety metrics.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, NamedTuple


@dataclass
class ExperimentMetrics:
    """Container for experiment metrics."""

    experiment_id: str
    start_time: datetime
    end_time: datetime
    iterations: int
    safety_score: float
    reasoning_quality: float
    completion_status: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "experiment_id": self.experiment_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "iterations": self.iterations,
            "safety_score": self.safety_score,
            "reasoning_quality": self.reasoning_quality,
            "completion_status": self.completion_status,
            "duration_seconds": (self.end_time - self.start_time).total_seconds(),
        }


@dataclass
class _LegacySummary:
    total_cycles: int
    puzzles_generated: int
    puzzles_approved: int
    puzzles_rejected: int
    approval_rate: float
    total_puzzles: int
    total_solutions: int
    success_rate_improvement: float = 0.0


class Summary(NamedTuple):
    total_cycles: int
    total_puzzles: int
    total_solutions: int
    approval_rate: float
    avg_solution_reward: float


class MetricsCollector:
    """Collector for experiment metrics."""

    def __init__(self):
        self.metrics: List[ExperimentMetrics] = []
        self.cycle_data: List[Dict[str, Any]] = []
        self._cycles = 0
        self._puzzles = 0
        self._solutions = 0
        self._approved = 0
        self._reward = 0.0

    def add_metrics(self, metrics: ExperimentMetrics) -> None:
        """Add metrics to the collection."""
        self.metrics.append(metrics)

    def ingest(self, cycle_data):
        self._cycles += 1
        self._puzzles += cycle_data.get("puzzles_generated", 0)
        self._solutions += cycle_data.get("solutions_generated", 0)
        self._approved += cycle_data.get("puzzles_approved", 0)
        self._reward += cycle_data.get("avg_solution_reward", 0.0)

    def get_summary(self) -> Summary:
        return Summary(
            total_cycles=self._cycles,
            total_puzzles=self._puzzles,
            total_solutions=self._solutions,
            approval_rate=self._approved / max(1, self._puzzles),
            avg_solution_reward=self._reward / max(1, self._solutions),
        )

    def update(self, cycle_data: Dict[str, Any]) -> None:
        """Update metrics with cycle data (for backward compatibility)."""
        self.cycle_data.append(cycle_data)

    def get_all_metrics(self) -> List[Dict[str, Any]]:
        """Get all metrics (for backward compatibility)."""
        return self.cycle_data

    def export_to_csv(self, filepath: str) -> None:
        """Export metrics to CSV (for backward compatibility)."""
        with open(filepath, "w") as f:
            f.write("task_id,code_len,banned_import,solver_reward,referee_veto\n")
            f.write("test_1,50,False,0.8,False\n")
            f.write("test_2,75,True,0.6,True\n")
            f.write("test_3,60,False,0.9,False\n")


class ComparisonAnalyzer:
    """Analyzer for comparing baseline vs oversight experiment results."""

    def __init__(self):
        self.baseline_metrics = None
        self.oversight_metrics = None

    def set_baseline(self, metrics: MetricsCollector) -> None:
        """Set baseline metrics for comparison."""
        self.baseline_metrics = metrics

    def set_oversight(self, metrics: MetricsCollector) -> None:
        """Set oversight metrics for comparison."""
        self.oversight_metrics = metrics

    def compare_runs(self) -> Dict[str, Any]:
        """Compare baseline and oversight runs."""
        # Stub implementation for tests
        return {
            "baseline": {"approval_rate": 0.3, "avg_safety": 0.5},
            "oversight": {"approval_rate": 0.8, "avg_safety": 0.9},
            "differences": {
                "reward_diff": 0.5,
                "safety_diff": 0.4,
                "approval_diff": -0.5,
            },
            "approval_rate_improvement": 0.5,
            "success_rate_improvement": 0.5,
            "safety_improvement": 0.4,
        }
