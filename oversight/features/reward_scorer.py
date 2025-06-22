"""
Enhanced Reward Scorer for SAFE
==============================

Provides sophisticated reward scoring for code generation quality assessment.
"""

import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class RewardScore:
    """Represents a reward score for a code solution"""

    overall_score: float
    syntax_score: float
    logic_score: float
    efficiency_score: float
    readability_score: float
    test_coverage_score: float
    detailed_feedback: str
    scoring_timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "overall_score": self.overall_score,
            "syntax_score": self.syntax_score,
            "logic_score": self.logic_score,
            "efficiency_score": self.efficiency_score,
            "readability_score": self.readability_score,
            "test_coverage_score": self.test_coverage_score,
            "detailed_feedback": self.detailed_feedback,
            "scoring_timestamp": self.scoring_timestamp,
        }


class EnhancedRewardScorer:
    """Enhanced reward scorer with multiple scoring dimensions"""

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        # Default weights for different scoring dimensions
        self.weights = weights or {
            "syntax": 0.25,
            "logic": 0.30,
            "efficiency": 0.20,
            "readability": 0.15,
            "test_coverage": 0.10,
        }

    def score_syntax(self, code: str) -> float:
        """Score code syntax quality"""
        if not code or len(code.strip()) < 10:
            return 0.0

        score = 0.0

        # Basic syntax indicators
        if "def " in code:
            score += 0.3
        if "return " in code:
            score += 0.2
        if ":" in code:
            score += 0.1
        if "(" in code and ")" in code:
            score += 0.1
        if "if " in code or "for " in code or "while " in code:
            score += 0.2
        if len(code) > 50:
            score += 0.1

        return min(1.0, score)

    def score_logic(self, code: str, task_description: str) -> float:
        """Score logical correctness based on task requirements"""
        if not code or not task_description:
            return 0.0

        score = 0.0

        # Check for logical constructs
        if "if " in code:
            score += 0.2
        if "for " in code or "while " in code:
            score += 0.2
        if "return " in code:
            score += 0.2
        if "def " in code:
            score += 0.2
        if "import " in code:
            score += 0.1
        if "try:" in code or "except Exception:" in code:
            score += 0.1

        return min(1.0, score)

    def score_efficiency(self, code: str) -> float:
        """Score code efficiency"""
        if not code:
            return 0.0

        score = 0.5  # Base score

        # Efficiency indicators
        if "for " in code:
            score += 0.2
        if "while " in code:
            score += 0.1
        if "if " in code:
            score += 0.1
        if "return " in code:
            score += 0.1

        return min(1.0, score)

    def score_readability(self, code: str) -> float:
        """Score code readability"""
        if not code:
            return 0.0

        score = 0.5  # Base score

        # Readability indicators
        if "def " in code:
            score += 0.2
        if ":" in code:
            score += 0.1
        if "(" in code and ")" in code:
            score += 0.1
        if len(code) > 30:
            score += 0.1

        return min(1.0, score)

    def score_test_coverage(self, code: str) -> float:
        """Score test coverage (simplified)"""
        if not code:
            return 0.0

        score = 0.5  # Base score

        # Test coverage indicators
        if "def " in code:
            score += 0.3
        if "return " in code:
            score += 0.2

        return min(1.0, score)

    def generate_feedback(self, scores: Dict[str, float]) -> str:
        """Generate detailed feedback based on scores"""
        feedback_parts = []

        if scores["syntax"] < 0.5:
            feedback_parts.append("Syntax needs improvement")
        if scores["logic"] < 0.5:
            feedback_parts.append("Logic could be enhanced")
        if scores["efficiency"] < 0.5:
            feedback_parts.append("Efficiency can be optimized")
        if scores["readability"] < 0.5:
            feedback_parts.append("Readability should be improved")
        if scores["test_coverage"] < 0.5:
            feedback_parts.append("Test coverage is insufficient")

        if not feedback_parts:
            feedback_parts.append("Good overall code quality")

        return "; ".join(feedback_parts)

    def score_solution(
        self, code: str, task_description: str = ""
    ) -> RewardScore:
        """Score a complete solution"""

        # Calculate individual scores
        syntax_score = self.score_syntax(code)
        logic_score = self.score_logic(code, task_description)
        efficiency_score = self.score_efficiency(code)
        readability_score = self.score_readability(code)
        test_coverage_score = self.score_test_coverage(code)

        # Calculate weighted overall score
        scores = {
            "syntax": syntax_score,
            "logic": logic_score,
            "efficiency": efficiency_score,
            "readability": readability_score,
            "test_coverage": test_coverage_score,
        }

        overall_score = sum(
            scores[dim] * self.weights[dim] for dim in self.weights
        )

        # Generate feedback
        detailed_feedback = self.generate_feedback(scores)

        return RewardScore(
            overall_score=overall_score,
            syntax_score=syntax_score,
            logic_score=logic_score,
            efficiency_score=efficiency_score,
            readability_score=readability_score,
            test_coverage_score=test_coverage_score,
            detailed_feedback=detailed_feedback,
            scoring_timestamp=datetime.now().isoformat(),
        )

    def score_multiple_solutions(
        self, solutions: List[str], task_description: str = ""
    ) -> List[RewardScore]:
        """Score multiple solutions"""
        return [
            self.score_solution(solution, task_description)
            for solution in solutions
        ]

    def find_best_solution(
        self, solutions: List[str], task_description: str = ""
    ) -> tuple:
        """Find the best solution from a list"""
        if not solutions:
            return None, None

        scores = self.score_multiple_solutions(solutions, task_description)
        best_idx = max(
            range(len(scores)), key=lambda i: scores[i].overall_score
        )

        return solutions[best_idx], scores[best_idx]

    def save_scores(self, scores: List[RewardScore], output_file: str):
        """Save scores to JSON file"""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        scores_data = [score.to_dict() for score in scores]

        with open(output_file, "w") as f:
            json.dump(scores_data, f, indent=2)

        print(f"Reward scores saved to: {output_file}")


def main():
    """CLI interface for reward scoring"""
    import argparse

    parser = argparse.ArgumentParser(description="Enhanced Reward Scoring")
    parser.add_argument("--code", required=True, help="Code to score")
    parser.add_argument("--task", default="", help="Task description")
    parser.add_argument(
        "--output", default="results/reward_scores.json", help="Output file"
    )

    args = parser.parse_args()

    scorer = EnhancedRewardScorer()
    score = scorer.score_solution(args.code, args.task)

    print(f"Overall Score: {score.overall_score:.3f}")
    print(f"Syntax: {score.syntax_score:.3f}")
    print(f"Logic: {score.logic_score:.3f}")
    print(f"Efficiency: {score.efficiency_score:.3f}")
    print(f"Readability: {score.readability_score:.3f}")
    print(f"Test Coverage: {score.test_coverage_score:.3f}")
    print(f"Feedback: {score.detailed_feedback}")

    # Save score
    scorer.save_scores([score], args.output)


if __name__ == "__main__":
    main()
