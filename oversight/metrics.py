"""
Metrics collection and analysis for oversight curriculum.
Provides tools for tracking experiment performance and safety metrics.
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime


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
            "duration_seconds": (
                self.end_time - self.start_time
            ).total_seconds()
        }


class MetricsCollector:
    """Collector for experiment metrics."""
    
    def __init__(self):
        self.metrics: List[ExperimentMetrics] = []
    
    def add_metrics(self, metrics: ExperimentMetrics) -> None:
        """Add metrics to the collection."""
        self.metrics.append(metrics)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        if not self.metrics:
            return {"total_experiments": 0}
        
        safety_scores = [m.safety_score for m in self.metrics]
        reasoning_scores = [m.reasoning_quality for m in self.metrics]
        
        completed_count = sum(
            1 for m in self.metrics 
            if m.completion_status == "completed"
        )
        
        return {
            "total_experiments": len(self.metrics),
            "avg_safety_score": sum(safety_scores) / len(safety_scores),
            "avg_reasoning_quality": (
                sum(reasoning_scores) / len(reasoning_scores)
            ),
            "completion_rate": completed_count / len(self.metrics)
        } 