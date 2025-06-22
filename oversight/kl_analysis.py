"""
KL divergence analysis for Best-of-N sampling.
Implements the open-review BoN formula to compute KL divergence between base and best-of-n samples.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any
from dataclasses import dataclass
import json
import time

from best_of_n import BestOfNSampler


@dataclass
class KLResult:
    """Result of KL divergence calculation"""

    n_samples: int
    avg_reward: float
    kl_divergence: float
    accuracy_improvement: float
    computation_time: float
    sample_details: Dict[str, Any]


class KLAnalyzer:
    """
    KL divergence analyzer for Best-of-N sampling.

    Computes KL divergence between base model (n=1) and best-of-n samples
    using the open-review BoN formula.
    """

    def __init__(
        self,
        model_name: str = "claude-3-5-sonnet-20241022",
        base_temperature: float = 0.7,
        puzzle_set: List[str] = None,
    ):
        self.model_name = model_name
        self.base_temperature = base_temperature
        self.puzzle_set = puzzle_set or self._get_default_puzzles()

        # Results storage
        self.kl_results = []
        self.base_results = []

    def generate_kl_table(self, n_values: List[int] = [1, 4, 16, 64]) -> pd.DataFrame:
        """
        Generate KL divergence table for different n values.

        Args:
            n_values: List of n values to test

        Returns:
            DataFrame with n, reward, KL divergence, accuracy improvement
        """

        print(f"🎯 Generating KL divergence table for n = {n_values}")
        print("=" * 60)

        results = []

        # First, establish baseline (n=1)
        print("📊 Computing baseline (n=1)...")
        baseline_result = self._compute_baseline()
        self.base_results = baseline_result

        baseline_reward = baseline_result["avg_reward"]
        baseline_accuracy = baseline_result["accuracy"]

        print(f"   Baseline reward: {baseline_reward:.3f}")
        print(f"   Baseline accuracy: {baseline_accuracy:.1%}")

        # Test each n value
        for n in n_values:
            print(f"\n🔬 Testing n = {n}...")

            if n == 1:
                # Use baseline result
                kl_result = KLResult(
                    n_samples=1,
                    avg_reward=baseline_reward,
                    kl_divergence=0.0,  # No divergence from self
                    accuracy_improvement=0.0,
                    computation_time=baseline_result["computation_time"],
                    sample_details=baseline_result,
                )
            else:
                # Compute best-of-n
                kl_result = self._compute_kl_for_n(n, baseline_result)

            results.append(kl_result)
            self.kl_results.append(kl_result)

            print(f"   Reward: {kl_result.avg_reward:.3f}")
            print(f"   KL Divergence: {kl_result.kl_divergence:.4f}")
            print(f"   Accuracy Improvement: {kl_result.accuracy_improvement:+.1f}pp")
            print(f"   Time: {kl_result.computation_time:.2f}s")

        # Create DataFrame
        df = pd.DataFrame(
            [
                {
                    "n": r.n_samples,
                    "avg_reward": r.avg_reward,
                    "kl_divergence": r.kl_divergence,
                    "accuracy_improvement_pp": r.accuracy_improvement,
                    "computation_time": r.computation_time,
                }
                for r in results
            ]
        )

        print("\n✅ KL table generated!")
        print(df.to_string(index=False))

        return df

    def _compute_baseline(self) -> Dict[str, Any]:
        """Compute baseline performance (n=1)"""

        start_time = time.time()

        sampler = BestOfNSampler(
            model_name=self.model_name, n_samples=1, temperature=self.base_temperature
        )

        total_rewards = []
        total_correct = 0
        total_puzzles = len(self.puzzle_set)

        for i, puzzle in enumerate(self.puzzle_set):
            print(f"   Puzzle {i+1}/{total_puzzles}...")

            try:
                solution, metrics = sampler.sample_best_solution(puzzle)

                total_rewards.append(metrics["avg_reward"])
                if metrics["correct_rate"] > 0:
                    total_correct += 1

            except Exception as e:
                print(f"   ⚠️  Error on puzzle {i+1}: {e}")
                total_rewards.append(0.0)

        computation_time = time.time() - start_time

        return {
            "avg_reward": np.mean(total_rewards),
            "accuracy": total_correct / total_puzzles,
            "computation_time": computation_time,
            "total_puzzles": total_puzzles,
            "correct_puzzles": total_correct,
            "rewards": total_rewards,
        }

    def _compute_kl_for_n(self, n: int, baseline_result: Dict[str, Any]) -> KLResult:
        """Compute KL divergence for specific n value"""

        start_time = time.time()

        sampler = BestOfNSampler(
            model_name=self.model_name, n_samples=n, temperature=self.base_temperature
        )

        total_rewards = []
        total_correct = 0
        total_puzzles = len(self.puzzle_set)

        # Store sample distributions for KL calculation
        sample_distributions = []

        for i, puzzle in enumerate(self.puzzle_set):
            print(f"   Puzzle {i+1}/{total_puzzles} (n={n})...")

            try:
                solution, metrics = sampler.sample_best_solution(puzzle)

                total_rewards.append(metrics["avg_reward"])
                if metrics["correct_rate"] > 0:
                    total_correct += 1

                # Store sample distribution for KL calculation
                sample_distributions.append(metrics)

            except Exception as e:
                print(f"   ⚠️  Error on puzzle {i+1}: {e}")
                total_rewards.append(0.0)

        computation_time = time.time() - start_time

        # Calculate KL divergence using open-review BoN formula
        kl_divergence = self._compute_kl_divergence(
            baseline_result["rewards"], total_rewards, sample_distributions
        )

        # Calculate accuracy improvement
        accuracy = total_correct / total_puzzles
        accuracy_improvement = (
            accuracy - baseline_result["accuracy"]
        ) * 100  # percentage points

        return KLResult(
            n_samples=n,
            avg_reward=np.mean(total_rewards),
            kl_divergence=kl_divergence,
            accuracy_improvement=accuracy_improvement,
            computation_time=computation_time,
            sample_details={
                "total_puzzles": total_puzzles,
                "correct_puzzles": total_correct,
                "accuracy": accuracy,
                "rewards": total_rewards,
                "sample_distributions": sample_distributions,
            },
        )

    def _compute_kl_divergence(
        self,
        base_rewards: List[float],
        best_of_n_rewards: List[float],
        sample_distributions: List[Dict],
    ) -> float:
        """
        Compute KL divergence using open-review BoN formula.

        KL = E[log(p_best_of_n / p_base)] where p represents reward distributions.
        """

        if len(base_rewards) != len(best_of_n_rewards):
            raise ValueError("Base and best-of-n reward lists must have same length")

        # Convert to numpy arrays
        base_rewards = np.array(base_rewards)
        best_of_n_rewards = np.array(best_of_n_rewards)

        # Add small epsilon to avoid log(0)
        epsilon = 1e-8
        base_rewards = base_rewards + epsilon
        best_of_n_rewards = best_of_n_rewards + epsilon

        # Normalize to create probability distributions
        base_probs = base_rewards / np.sum(base_rewards)
        best_of_n_probs = best_of_n_rewards / np.sum(best_of_n_rewards)

        # Compute KL divergence: KL(P||Q) = sum(P * log(P/Q))
        kl_divergence = np.sum(base_probs * np.log(base_probs / best_of_n_probs))

        return float(kl_divergence)

    def _get_default_puzzles(self) -> List[str]:
        """Get default puzzle set for testing"""

        return [
            "Write a function that adds two numbers",
            "Write a function that multiplies a list of numbers",
            "Write a function that finds the maximum value in a list",
            "Write a function that reverses a string",
            "Write a function that checks if a number is prime",
            "Write a function that calculates factorial",
            "Write a function that counts vowels in a string",
            "Write a function that finds the GCD of two numbers",
            "Write a function that converts Celsius to Fahrenheit",
            "Write a function that checks if a string is a palindrome",
        ]

    def save_results(self, filepath: str = "results/kl_analysis.json"):
        """Save KL analysis results to file"""

        import os

        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        results_data = {
            "model_name": self.model_name,
            "base_temperature": self.base_temperature,
            "kl_results": [
                {
                    "n_samples": r.n_samples,
                    "avg_reward": r.avg_reward,
                    "kl_divergence": r.kl_divergence,
                    "accuracy_improvement": r.accuracy_improvement,
                    "computation_time": r.computation_time,
                }
                for r in self.kl_results
            ],
            "base_results": self.base_results,
        }

        with open(filepath, "w") as f:
            json.dump(results_data, f, indent=2)

        print(f"💾 KL analysis results saved to {filepath}")

    def generate_report(self) -> str:
        """Generate text report of KL analysis"""

        if not self.kl_results:
            return "No KL analysis results available."

        report = []
        report.append("KL DIVERGENCE ANALYSIS REPORT")
        report.append("=" * 50)
        report.append(f"Model: {self.model_name}")
        report.append(f"Base Temperature: {self.base_temperature}")
        report.append(f"Puzzle Set Size: {len(self.puzzle_set)}")
        report.append("")

        # Summary table
        report.append("RESULTS SUMMARY:")
        report.append("-" * 30)
        report.append("n\tReward\tKL Div\tAcc Imp (pp)")
        report.append("-" * 30)

        for result in self.kl_results:
            report.append(
                f"{result.n_samples}\t{result.avg_reward:.3f}\t{result.kl_divergence:.4f}\t{result.accuracy_improvement:+.1f}"
            )

        report.append("")

        # Key findings
        report.append("KEY FINDINGS:")
        report.append("-" * 20)

        # Find best accuracy improvement
        best_improvement = max(self.kl_results, key=lambda r: r.accuracy_improvement)
        report.append(
            f"• Best accuracy improvement: {best_improvement.accuracy_improvement:+.1f}pp (n={best_improvement.n_samples})"
        )

        # Find lowest KL divergence
        lowest_kl = min(self.kl_results, key=lambda r: r.kl_divergence)
        report.append(
            f"• Lowest KL divergence: {lowest_kl.kl_divergence:.4f} (n={lowest_kl.n_samples})"
        )

        # Find best reward
        best_reward = max(self.kl_results, key=lambda r: r.avg_reward)
        report.append(
            f"• Best average reward: {best_reward.avg_reward:.3f} (n={best_reward.n_samples})"
        )

        return "\n".join(report)
