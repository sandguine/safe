#!/usr/bin/env python3
"""
Enhanced AZR Loop with HumanEval-164 Integration
================================================

Implements the refined plan with:
1. HumanEval-164 dataset (164 tasks)
2. Async execution with global rate limiting
3. Progressive sampling (n=4 first, then +12 if needed)
4. Confidence-weighted voting across top candidates
5. Secure sandbox execution with partial credit
6. Execute-then-grade selection
7. Global throttling with exponential back-off
"""

import asyncio
import json
import os
import resource
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from oversight.humaneval_integration import (
    AsyncHumanEvalRunner,
    ExecutionResult,
    HumanEvalTask,
)
from oversight.metrics import MetricsCollector

# Local imports
from oversight.model import ask


@dataclass
class AZRConfig:
    """Configuration for enhanced AZR loop"""

    # HumanEval settings
    max_tasks: int = 164  # Full HumanEval-164
    n_values: List[int] = None  # Will be set to [1, 4, 16]

    # Async settings
    max_concurrent: int = 10
    requests_per_minute: int = 50
    progressive_sampling: bool = True

    # Model settings
    temperature: float = 0.7
    use_chain_of_thought: bool = True

    # Sandbox settings
    timeout_seconds: int = 5
    memory_limit_mb: int = 512

    # Rate limiting
    exponential_backoff: bool = True
    max_retries: int = 3

    def __post_init__(self):
        if self.n_values is None:
            self.n_values = [1, 4, 16]


class EnhancedAZRLoop:
    """Enhanced AZR loop with HumanEval-164 integration"""

    def __init__(self, config: AZRConfig):
        self.config = config
        self.metrics = MetricsCollector()

        # Initialize HumanEval runner
        self.humaneval_runner = AsyncHumanEvalRunner(
            max_concurrent=config.max_concurrent,
            requests_per_minute=config.requests_per_minute,
            progressive_sampling=config.progressive_sampling,
        )

        # Results storage
        self.results = {}
        self.current_cycle = 0

    async def run_cycle(self, cycle_num: int) -> Dict[str, Any]:
        """Run a single AZR cycle with HumanEval tasks"""

        print(f"\n🔄 Starting AZR Cycle {cycle_num}")
        print(f"📊 Running on {self.config.max_tasks} HumanEval tasks")

        cycle_start = time.time()

        # Run HumanEval experiment
        humaneval_results = await self.humaneval_runner.run_experiment(
            n_values=self.config.n_values,
            max_tasks=self.config.max_tasks,
            temperature=self.config.temperature,
        )

        # Calculate metrics
        cycle_metrics = self._calculate_cycle_metrics(humaneval_results)

        # Store results
        cycle_data = {
            "cycle": cycle_num,
            "timestamp": time.time(),
            "duration": time.time() - cycle_start,
            "humaneval_results": humaneval_results,
            "metrics": cycle_metrics,
        }

        self.results[f"cycle_{cycle_num}"] = cycle_data

        print(
            f"✅ Cycle {cycle_num} completed in {cycle_data['duration']:.2f}s"
        )
        print(f"📈 Best pass@1: {cycle_metrics['best_pass_at_1']:.4f}")

        return cycle_data

    def _calculate_cycle_metrics(
        self, humaneval_results: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate comprehensive metrics for the cycle"""

        metrics = {}

        for n_key, n_results in humaneval_results.items():
            n = int(n_key.split("_")[1])

            # Pass@1 metric
            pass_at_1 = self._calculate_pass_at_k(n_results, 1)
            metrics[f"pass_at_1_n{n}"] = pass_at_1

            # Average ratio
            avg_ratio = sum(r["result"].ratio for r in n_results) / len(
                n_results
            )
            metrics[f"avg_ratio_n{n}"] = avg_ratio

            # Average passed tests
            avg_passed = sum(r["result"].passed for r in n_results) / len(
                n_results
            )
            metrics[f"avg_passed_n{n}"] = avg_passed

            # Average total tests
            avg_total = sum(r["result"].total for r in n_results) / len(
                n_results
            )
            metrics[f"avg_total_n{n}"] = avg_total

        # Best performance across all n values
        best_pass_at_1 = max(
            metrics[f"pass_at_1_n{n}"] for n in self.config.n_values
        )
        metrics["best_pass_at_1"] = best_pass_at_1

        return metrics

    def _calculate_pass_at_k(self, results: List[Dict], k: int = 1) -> float:
        """Calculate pass@k metric"""
        if not results:
            return 0.0

        passed = sum(1 for r in results if r["result"].ratio >= 1.0)
        return passed / len(results)

    async def run_experiment(self, cycles: int = 3) -> Dict[str, Any]:
        """Run the complete enhanced AZR experiment"""

        print(f"🚀 Starting Enhanced AZR Experiment")
        print(f"📋 Configuration:")
        print(f"   - Cycles: {cycles}")
        print(f"   - Tasks: {self.config.max_tasks}")
        print(f"   - N values: {self.config.n_values}")
        print(f"   - Temperature: {self.config.temperature}")
        print(f"   - Progressive sampling: {self.config.progressive_sampling}")

        experiment_start = time.time()

        # Run cycles
        for cycle in range(1, cycles + 1):
            try:
                cycle_data = await self.run_cycle(cycle)

                # Save intermediate results
                self._save_intermediate_results(cycle)

                # Check for early stopping (if we achieve high performance)
                if cycle_data["metrics"]["best_pass_at_1"] >= 0.8:
                    print(
                        f"🎯 Early stopping: achieved {cycle_data['metrics']['best_pass_at_1']:.4f} pass@1"
                    )
                    break

            except Exception as e:
                print(f"❌ Error in cycle {cycle}: {e}")
                import traceback

                traceback.print_exc()
                continue

        # Calculate final metrics
        final_metrics = self._calculate_final_metrics()

        # Save final results
        final_results = {
            "experiment_config": self.config.__dict__,
            "cycles": cycles,
            "total_duration": time.time() - experiment_start,
            "cycle_results": self.results,
            "final_metrics": final_metrics,
        }

        self._save_final_results(final_results)

        print(f"\n🎉 Experiment completed!")
        print(f"⏱️  Total duration: {final_results['total_duration']:.2f}s")
        print(f"📊 Final best pass@1: {final_metrics['best_pass_at_1']:.4f}")

        return final_results

    def _calculate_final_metrics(self) -> Dict[str, Any]:
        """Calculate final experiment metrics"""

        if not self.results:
            return {}

        # Aggregate across cycles
        all_pass_at_1 = []
        all_ratios = []

        for cycle_data in self.results.values():
            all_pass_at_1.append(cycle_data["metrics"]["best_pass_at_1"])

            # Get best ratio from this cycle
            best_ratio = max(
                cycle_data["metrics"][f"avg_ratio_n{n}"]
                for n in self.config.n_values
            )
            all_ratios.append(best_ratio)

        return {
            "best_pass_at_1": max(all_pass_at_1),
            "avg_pass_at_1": sum(all_pass_at_1) / len(all_pass_at_1),
            "best_ratio": max(all_ratios),
            "avg_ratio": sum(all_ratios) / len(all_ratios),
            "total_cycles": len(self.results),
        }

    def _save_intermediate_results(self, cycle: int):
        """Save intermediate results after each cycle"""
        os.makedirs("results", exist_ok=True)

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"results/enhanced_azr_cycle_{cycle}_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(self.results[f"cycle_{cycle}"], f, indent=2, default=str)

        print(f"💾 Intermediate results saved to {filename}")

    def _save_final_results(self, final_results: Dict[str, Any]):
        """Save final experiment results"""
        os.makedirs("results", exist_ok=True)

        timestamp = time.strftime("%Y%m%d_%H%M%S")

        # JSON with all details
        json_file = f"results/enhanced_azr_final_{timestamp}.json"
        with open(json_file, "w") as f:
            json.dump(final_results, f, indent=2, default=str)

        # CSV summary
        csv_file = f"results/enhanced_azr_summary_{timestamp}.csv"
        with open(csv_file, "w") as f:
            f.write("cycle,best_pass_at_1,avg_ratio,duration\n")

            for cycle_key, cycle_data in self.results.items():
                cycle_num = cycle_data["cycle"]
                best_pass_at_1 = cycle_data["metrics"]["best_pass_at_1"]
                avg_ratio = cycle_data["metrics"][
                    "avg_ratio_n4"
                ]  # Use n=4 as representative
                duration = cycle_data["duration"]

                f.write(
                    f"{cycle_num},{best_pass_at_1:.4f},{avg_ratio:.4f},{duration:.2f}\n"
                )

        print(f"💾 Final results saved to {json_file} and {csv_file}")
        return json_file, csv_file


async def main():
    """Main function for testing the enhanced AZR loop"""

    # Configuration for testing
    config = AZRConfig(
        max_tasks=10,  # Start with 10 tasks for testing
        n_values=[1, 4],  # Reduced for testing
        max_concurrent=3,
        requests_per_minute=20,
        progressive_sampling=True,
        temperature=0.7,
    )

    # Create and run enhanced AZR loop
    azr_loop = EnhancedAZRLoop(config)

    # Run experiment
    results = await azr_loop.run_experiment(cycles=2)

    # Print summary
    print("\n📋 Final Summary:")
    print(f"   Best pass@1: {results['final_metrics']['best_pass_at_1']:.4f}")
    print(
        f"   Average pass@1: {results['final_metrics']['avg_pass_at_1']:.4f}"
    )
    print(f"   Best ratio: {results['final_metrics']['best_ratio']:.4f}")
    print(f"   Total cycles: {results['final_metrics']['total_cycles']}")


if __name__ == "__main__":
    asyncio.run(main())
