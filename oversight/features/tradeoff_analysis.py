"""
Tradeoff Analysis for SAFE
=========================

Analyzes the tradeoff between capability and safety in the SAFE pipeline.
"""

import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Tuple

import numpy as np


@dataclass
class TradeoffPoint:
    """Represents a point on the capability-safety tradeoff curve"""

    capability_score: float
    safety_score: float
    model_config: Dict[str, Any]
    sample_size: int
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "capability_score": self.capability_score,
            "safety_score": self.safety_score,
            "model_config": self.model_config,
            "sample_size": self.sample_size,
            "timestamp": self.timestamp,
        }


class TradeoffAnalyzer:
    """Analyzer for capability-safety tradeoffs"""

    def __init__(self):
        pass

    def calculate_capability_score(self, results: Dict[str, Any]) -> float:
        """Calculate capability score from results"""
        if not results:
            return 0.0

        # Extract pass rates
        pass_rates = []
        for method, data in results.get("results", {}).items():
            if "pass@1" in data:
                pass_rates.append(data["pass@1"])

        if not pass_rates:
            return 0.0

        return np.mean(pass_rates)

    def calculate_safety_score(self, results: Dict[str, Any]) -> float:
        """Calculate safety score from results"""
        if not results:
            return 0.0

        # Extract safety metrics
        safety_scores = []

        # Check for safety-related fields
        if "safety_metrics" in results:
            safety_data = results["safety_metrics"]
            if "harmful_content_ratio" in safety_data:
                # Convert harmful ratio to safety score (1 - harmful_ratio)
                safety_scores.append(
                    1.0 - safety_data["harmful_content_ratio"]
                )

        # If no explicit safety metrics, use a default
        if not safety_scores:
            safety_scores.append(0.8)  # Default safety score

        return np.mean(safety_scores)

    def analyze_tradeoff_curve(
        self, result_files: List[str]
    ) -> List[TradeoffPoint]:
        """Analyze tradeoff curve from multiple result files"""
        tradeoff_points = []

        for file_path in result_files:
            try:
                with open(file_path, "r") as f:
                    results = json.load(f)

                capability = self.calculate_capability_score(results)
                safety = self.calculate_safety_score(results)

                # Extract model config from filename or results
                model_config = results.get("model_config", {})
                sample_size = results.get("sample_size", 0)

                point = TradeoffPoint(
                    capability_score=capability,
                    safety_score=safety,
                    model_config=model_config,
                    sample_size=sample_size,
                    timestamp=datetime.now().isoformat(),
                )

                tradeoff_points.append(point)

            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue

        return tradeoff_points

    def calculate_pareto_frontier(
        self, points: List[TradeoffPoint]
    ) -> List[TradeoffPoint]:
        """Calculate Pareto frontier of tradeoff points"""
        if not points:
            return []

        # Sort by capability score (ascending)
        sorted_points = sorted(points, key=lambda p: p.capability_score)

        pareto_points = []
        max_safety = -1

        for point in sorted_points:
            if point.safety_score > max_safety:
                pareto_points.append(point)
                max_safety = point.safety_score

        return pareto_points

    def calculate_efficiency_ratio(self, point: TradeoffPoint) -> float:
        """Calculate efficiency ratio (capability/safety tradeoff)"""
        if point.safety_score == 0:
            return 0.0

        return point.capability_score / point.safety_score

    def find_optimal_point(
        self, points: List[TradeoffPoint], target_safety: float = 0.8
    ) -> TradeoffPoint:
        """Find optimal point given safety constraint"""
        if not points:
            return None

        # Filter points meeting safety constraint
        valid_points = [p for p in points if p.safety_score >= target_safety]

        if not valid_points:
            return None

        # Return point with highest capability
        return max(valid_points, key=lambda p: p.capability_score)

    def save_tradeoff_analysis(
        self, points: List[TradeoffPoint], output_file: str
    ):
        """Save tradeoff analysis to file"""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        analysis_data = {
            "tradeoff_points": [p.to_dict() for p in points],
            "pareto_frontier": [
                p.to_dict() for p in self.calculate_pareto_frontier(points)
            ],
            "analysis_timestamp": datetime.now().isoformat(),
        }

        with open(output_file, "w") as f:
            json.dump(analysis_data, f, indent=2)

        print(f"Tradeoff analysis saved to: {output_file}")
        print(f"Analyzed {len(points)} points")
        print(
            f"Pareto frontier has {len(analysis_data['pareto_frontier'])} points"
        )


def main():
    """CLI interface for tradeoff analysis"""
    import argparse

    parser = argparse.ArgumentParser(description="Tradeoff Analysis")
    parser.add_argument(
        "--results", nargs="+", required=True, help="Result files to analyze"
    )
    parser.add_argument(
        "--output",
        default="results/tradeoff_analysis.json",
        help="Output file",
    )

    args = parser.parse_args()

    analyzer = TradeoffAnalyzer()
    points = analyzer.analyze_tradeoff_curve(args.results)
    analyzer.save_tradeoff_analysis(points, args.output)


if __name__ == "__main__":
    main()
