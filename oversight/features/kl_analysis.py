"""
KL Divergence Analysis for SAFE
==============================

Measures the KL divergence between the original model distribution p(x)
and the filtered distribution q(x) to validate the self-alignment objective.
"""

import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Tuple

import numpy as np


@dataclass
class KLDivergenceResult:
    """Result of KL divergence analysis"""

    kl_divergence: float
    entropy_p: float
    entropy_q: float
    sample_size_p: int
    sample_size_q: int
    confidence_interval: Tuple[float, float]
    analysis_timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "kl_divergence": self.kl_divergence,
            "entropy_p": self.entropy_p,
            "entropy_q": self.entropy_q,
            "sample_size_p": self.sample_size_p,
            "sample_size_q": self.sample_size_q,
            "confidence_interval": self.confidence_interval,
            "analysis_timestamp": self.analysis_timestamp,
        }


class KLDivergenceAnalyzer:
    """Analyzer for KL divergence between model distributions"""

    def __init__(self, smoothing_factor: float = 1e-8):
        self.smoothing_factor = smoothing_factor

    def estimate_token_distribution(
        self, texts: List[str]
    ) -> Dict[str, float]:
        """Estimate token distribution from text samples"""
        if not texts:
            return {}

        # Simple tokenization (words)
        all_tokens = []
        for text in texts:
            tokens = text.lower().split()
            all_tokens.extend(tokens)

        # Count frequencies
        token_counts = {}
        total_tokens = len(all_tokens)

        for token in all_tokens:
            token_counts[token] = token_counts.get(token, 0) + 1

        # Convert to probabilities with smoothing
        distribution = {}
        vocab_size = len(token_counts)
        for token, count in token_counts.items():
            prob = (count + self.smoothing_factor) / (
                total_tokens + vocab_size * self.smoothing_factor
            )
            distribution[token] = prob

        return distribution

    def calculate_entropy(self, distribution: Dict[str, float]) -> float:
        """Calculate Shannon entropy of a distribution"""
        if not distribution:
            return 0.0

        entropy = 0.0
        for prob in distribution.values():
            if prob > 0:
                entropy -= prob * np.log2(prob)
        return entropy

    def calculate_kl_divergence(
        self, p_dist: Dict[str, float], q_dist: Dict[str, float]
    ) -> float:
        """Calculate KL divergence KL(p||q)"""
        if not p_dist or not q_dist:
            return 0.0

        kl_div = 0.0
        all_tokens = set(p_dist.keys()) | set(q_dist.keys())

        for token in all_tokens:
            p_prob = p_dist.get(token, self.smoothing_factor)
            q_prob = q_dist.get(token, self.smoothing_factor)

            if p_prob > 0 and q_prob > 0:
                kl_div += p_prob * np.log2(p_prob / q_prob)

        return kl_div

    def bootstrap_confidence_interval(
        self,
        texts_p: List[str],
        texts_q: List[str],
        n_bootstrap: int = 1000,
        confidence: float = 0.95,
    ) -> Tuple[float, float]:
        """Calculate bootstrap confidence interval for KL divergence"""
        if len(texts_p) < 2 or len(texts_q) < 2:
            return (0.0, 0.0)

        kl_values = []

        for _ in range(n_bootstrap):
            # Bootstrap samples
            boot_p = np.random.choice(texts_p, size=len(texts_p), replace=True)
            boot_q = np.random.choice(texts_q, size=len(texts_q), replace=True)

            # Calculate KL divergence for bootstrap sample
            p_dist = self.estimate_token_distribution(boot_p.tolist())
            q_dist = self.estimate_token_distribution(boot_q.tolist())
            kl_val = self.calculate_kl_divergence(p_dist, q_dist)
            kl_values.append(kl_val)

        # Calculate confidence interval
        alpha = 1 - confidence
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100

        lower_bound = np.percentile(kl_values, lower_percentile)
        upper_bound = np.percentile(kl_values, upper_percentile)

        return (float(lower_bound), float(upper_bound))

    def analyze_distributions(
        self, baseline_texts: List[str], oversight_texts: List[str]
    ) -> KLDivergenceResult:
        """Analyze KL divergence between baseline and oversight distributions"""

        # Estimate distributions
        p_dist = self.estimate_token_distribution(baseline_texts)
        q_dist = self.estimate_token_distribution(oversight_texts)

        # Calculate metrics
        kl_div = self.calculate_kl_divergence(p_dist, q_dist)
        entropy_p = self.calculate_entropy(p_dist)
        entropy_q = self.calculate_entropy(q_dist)

        # Bootstrap confidence interval
        ci = self.bootstrap_confidence_interval(
            baseline_texts, oversight_texts
        )

        return KLDivergenceResult(
            kl_divergence=kl_div,
            entropy_p=entropy_p,
            entropy_q=entropy_q,
            sample_size_p=len(baseline_texts),
            sample_size_q=len(oversight_texts),
            confidence_interval=ci,
            analysis_timestamp=datetime.now().isoformat(),
        )

    def analyze_humaneval_results(
        self, baseline_file: str, oversight_file: str
    ) -> KLDivergenceResult:
        """Analyze KL divergence from HumanEval results files"""

        # Load results
        with open(baseline_file, "r") as f:
            baseline_data = json.load(f)
        with open(oversight_file, "r") as f:
            oversight_data = json.load(f)

        # Extract solution texts
        baseline_texts = []
        oversight_texts = []

        # Baseline solutions
        for result in baseline_data.get("results", {}).get("bo_1", []):
            solutions = result.get("solutions", [])
            baseline_texts.extend(solutions)

        # Oversight solutions
        for result in oversight_data.get("results", {}).get("bo_4", []):
            solutions = result.get("solutions", [])
            oversight_texts.extend(solutions)

        return self.analyze_distributions(baseline_texts, oversight_texts)

    def save_analysis(self, result: KLDivergenceResult, output_file: str):
        """Save KL divergence analysis to file"""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, "w") as f:
            json.dump(result.to_dict(), f, indent=2)

        print(f"KL divergence analysis saved to: {output_file}")
        print(f"KL(p||q) = {result.kl_divergence: .4f}")
        print(
            f"Entropy p = {result.entropy_p: .4f}, "
            f"Entropy q = {result.entropy_q: .4f}"
        )
        ci_low, ci_high = result.confidence_interval
        print(f"95% CI: [{ci_low: .4f}, {ci_high: .4f}]")


def main():
    """CLI interface for KL divergence analysis"""
    import argparse

    parser = argparse.ArgumentParser(description="KL Divergence Analysis")
    parser.add_argument(
        "--baseline", required=True, help="Baseline results file"
    )
    parser.add_argument(
        "--oversight", required=True, help="Oversight results file"
    )
    parser.add_argument(
        "--output", default="results/kl_analysis.json", help="Output file"
    )

    args = parser.parse_args()

    analyzer = KLDivergenceAnalyzer()
    result = analyzer.analyze_humaneval_results(args.baseline, args.oversight)
    analyzer.save_analysis(result, args.output)


if __name__ == "__main__":
    main()
