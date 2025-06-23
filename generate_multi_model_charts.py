#!/usr/bin/env python3
"""
Multi-Model Results Visualization
================================

Generate comprehensive charts and visualizations from multi-model evaluation results.
"""

import json
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


class MultiModelVisualizer:
    """Generate visualizations from multi-model evaluation results"""

    def __init__(self, results_dir="results/multi_model_evaluation"):
        self.results_dir = results_dir
        self.charts_dir = f"{results_dir}/charts"
        os.makedirs(self.charts_dir, exist_ok=True)

        # Load comprehensive results
        self.load_results()

    def load_results(self):
        """Load comprehensive results from JSON file"""
        comprehensive_file = f"{self.results_dir}/comprehensive_results.json"

        if os.path.exists(comprehensive_file):
            with open(comprehensive_file, "r") as f:
                self.results = json.load(f)
            print(f"✅ Loaded results from {comprehensive_file}")
        else:
            print(f"❌ Results file not found: {comprehensive_file}")
            self.results = None

    def generate_all_charts(self):
        """Generate all visualization charts"""
        if not self.results:
            print("❌ No results to visualize")
            return

        print("📊 Generating comprehensive visualizations...")

        # Set style
        plt.style.use("seaborn-v0_8")
        sns.set_palette("husl")

        # Generate charts
        self.plot_model_rankings()
        self.plot_sample_size_analysis()
        self.plot_100_percent_achievement()
        self.plot_metric_comparison()
        self.plot_heatmap()
        self.plot_optimal_configurations()

        print(f"✅ All charts saved to {self.charts_dir}/")

    def plot_model_rankings(self):
        """Plot model rankings by average success rate"""
        rankings = self.results["comprehensive_analysis"]["model_rankings"]

        models = [r["model_name"] for r in rankings]
        success_rates = [r["avg_success_rate"] * 100 for r in rankings]

        plt.figure(figsize=(12, 8))
        bars = plt.barh(models, success_rates, color="skyblue", alpha=0.7)

        # Add value labels on bars
        for i, (bar, rate) in enumerate(zip(bars, success_rates)):
            plt.text(
                bar.get_width() + 1,
                bar.get_y() + bar.get_height() / 2,
                f"{rate:.1f}%",
                ha="left",
                va="center",
                fontweight="bold",
            )

        plt.xlabel("Average Success Rate (%)")
        plt.title(
            "Model Rankings by Average Success Rate",
            fontsize=16,
            fontweight="bold",
        )
        plt.gca().invert_yaxis()
        plt.grid(axis="x", alpha=0.3)

        # Add medals for top 3
        for i in range(min(3, len(rankings))):
            plt.text(
                -5,
                i,
                ["🥇", "🥈", "🥉"][i],
                fontsize=20,
                ha="center",
                va="center",
            )

        plt.tight_layout()
        plt.savefig(
            f"{self.charts_dir}/model_rankings.png",
            dpi=300,
            bbox_inches="tight",
        )
        plt.close()

    def plot_sample_size_analysis(self):
        """Plot sample size analysis"""
        sample_analysis = self.results["comprehensive_analysis"][
            "sample_size_analysis"
        ]

        sample_sizes = []
        avg_success_rates = []
        models_100_percent = []
        total_models = []

        for n_key, stats in sample_analysis.items():
            n = int(n_key.replace("n_", ""))
            sample_sizes.append(n)
            avg_success_rates.append(stats["average_success_rate"] * 100)
            models_100_percent.append(stats["models_achieving_100"])
            total_models.append(stats["total_models"])

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # Success rate by sample size
        ax1.plot(
            sample_sizes,
            avg_success_rates,
            "o-",
            linewidth=3,
            markersize=8,
            color="green",
        )
        ax1.set_xlabel("Sample Size (n)")
        ax1.set_ylabel("Average Success Rate (%)")
        ax1.set_title("Success Rate vs Sample Size", fontweight="bold")
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, 105)

        # Models achieving 100% by sample size
        ax2.bar(sample_sizes, models_100_percent, color="gold", alpha=0.7)
        ax2.set_xlabel("Sample Size (n)")
        ax2.set_ylabel("Models Achieving 100%")
        ax2.set_title("100% Achievement by Sample Size", fontweight="bold")
        ax2.grid(axis="y", alpha=0.3)
        ax2.set_ylim(0, max(total_models) + 1)

        # Add value labels
        for i, (n, count) in enumerate(zip(sample_sizes, models_100_percent)):
            ax2.text(
                n,
                count + 0.1,
                str(count),
                ha="center",
                va="bottom",
                fontweight="bold",
            )

        plt.tight_layout()
        plt.savefig(
            f"{self.charts_dir}/sample_size_analysis.png",
            dpi=300,
            bbox_inches="tight",
        )
        plt.close()

    def plot_100_percent_achievement(self):
        """Plot 100% achievement analysis"""
        achievement = self.results["comprehensive_analysis"][
            "100_percent_achievement"
        ]
        configs = achievement["configurations"]

        if not configs:
            print("⚠️ No 100% configurations to plot")
            return

        # Group by model
        model_counts = {}
        for config in configs:
            model_name = config["model_name"]
            if model_name not in model_counts:
                model_counts[model_name] = 0
            model_counts[model_name] += 1

        models = list(model_counts.keys())
        counts = list(model_counts.values())

        plt.figure(figsize=(12, 8))
        bars = plt.bar(models, counts, color="lightgreen", alpha=0.7)

        # Add value labels
        for bar, count in zip(bars, counts):
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.1,
                str(count),
                ha="center",
                va="bottom",
                fontweight="bold",
            )

        plt.xlabel("Model")
        plt.ylabel("Number of 100% Configurations")
        plt.title("100% Achievement by Model", fontsize=16, fontweight="bold")
        plt.xticks(rotation=45, ha="right")
        plt.grid(axis="y", alpha=0.3)

        plt.tight_layout()
        plt.savefig(
            f"{self.charts_dir}/100_percent_achievement.png",
            dpi=300,
            bbox_inches="tight",
        )
        plt.close()

    def plot_metric_comparison(self):
        """Plot metric comparison across models"""
        best_configs = self.results["comprehensive_analysis"][
            "best_configurations"
        ]

        models = [config["model_name"] for config in best_configs]
        capability = [
            config["capability_improvement"] for config in best_configs
        ]
        safety = [
            config["safety_refusal_rate"] * 100 for config in best_configs
        ]
        kl_div = [config["kl_divergence"] for config in best_configs]
        alignment = [
            config["alignment_improvement"] for config in best_configs
        ]

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))

        # Capability improvement
        ax1.bar(models, capability, color="blue", alpha=0.7)
        ax1.set_title("Capability Improvement", fontweight="bold")
        ax1.set_ylabel("Improvement")
        ax1.tick_params(axis="x", rotation=45)
        ax1.grid(axis="y", alpha=0.3)

        # Safety refusal rate
        ax2.bar(models, safety, color="red", alpha=0.7)
        ax2.set_title("Safety Refusal Rate", fontweight="bold")
        ax2.set_ylabel("Refusal Rate (%)")
        ax2.tick_params(axis="x", rotation=45)
        ax2.grid(axis="y", alpha=0.3)

        # KL divergence
        ax3.bar(models, kl_div, color="green", alpha=0.7)
        ax3.set_title("KL Divergence", fontweight="bold")
        ax3.set_ylabel("KL Divergence")
        ax3.tick_params(axis="x", rotation=45)
        ax3.grid(axis="y", alpha=0.3)

        # Self-alignment improvement
        ax4.bar(models, alignment, color="purple", alpha=0.7)
        ax4.set_title("Self-Alignment Improvement", fontweight="bold")
        ax4.set_ylabel("Improvement")
        ax4.tick_params(axis="x", rotation=45)
        ax4.grid(axis="y", alpha=0.3)

        plt.tight_layout()
        plt.savefig(
            f"{self.charts_dir}/metric_comparison.png",
            dpi=300,
            bbox_inches="tight",
        )
        plt.close()

    def plot_heatmap(self):
        """Plot heatmap of success rates by model and sample size"""
        model_results = self.results["model_results"]

        # Create data matrix
        models = list(model_results.keys())
        sample_sizes = [1, 4, 16, 32, 64]

        data_matrix = []
        for model_id in models:
            row = []
            for n in sample_sizes:
                n_key = f"n_{n}"
                if n_key in model_results[model_id]["sample_sizes"]:
                    success_rate = model_results[model_id]["sample_sizes"][
                        n_key
                    ]["validation"]["success_rate"]
                    row.append(success_rate)
                else:
                    row.append(0)
            data_matrix.append(row)

        # Create heatmap
        plt.figure(figsize=(12, 8))
        sns.heatmap(
            data_matrix,
            xticklabels=sample_sizes,
            yticklabels=[model_results[m]["model_name"] for m in models],
            annot=True,
            fmt=".2f",
            cmap="RdYlGn",
            cbar_kws={"label": "Success Rate"},
        )

        plt.xlabel("Sample Size (n)")
        plt.ylabel("Model")
        plt.title(
            "Success Rate Heatmap: Model vs Sample Size",
            fontsize=16,
            fontweight="bold",
        )

        plt.tight_layout()
        plt.savefig(
            f"{self.charts_dir}/success_rate_heatmap.png",
            dpi=300,
            bbox_inches="tight",
        )
        plt.close()

    def plot_optimal_configurations(self):
        """Plot optimal configurations for each model"""
        best_configs = self.results["comprehensive_analysis"][
            "best_configurations"
        ]

        models = [config["model_name"] for config in best_configs]
        optimal_ns = [
            int(config["optimal_sample_size"].replace("n_", ""))
            for config in best_configs
        ]
        success_rates = [
            config["success_rate"] * 100 for config in best_configs
        ]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # Optimal sample sizes
        bars1 = ax1.bar(models, optimal_ns, color="orange", alpha=0.7)
        ax1.set_title("Optimal Sample Size by Model", fontweight="bold")
        ax1.set_ylabel("Sample Size (n)")
        ax1.tick_params(axis="x", rotation=45)
        ax1.grid(axis="y", alpha=0.3)

        # Add value labels
        for bar, n in zip(bars1, optimal_ns):
            ax1.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.5,
                str(n),
                ha="center",
                va="bottom",
                fontweight="bold",
            )

        # Success rates at optimal configuration
        bars2 = ax2.bar(models, success_rates, color="lightblue", alpha=0.7)
        ax2.set_title(
            "Success Rate at Optimal Configuration", fontweight="bold"
        )
        ax2.set_ylabel("Success Rate (%)")
        ax2.tick_params(axis="x", rotation=45)
        ax2.grid(axis="y", alpha=0.3)
        ax2.set_ylim(0, 105)

        # Add value labels
        for bar, rate in zip(bars2, success_rates):
            ax2.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 1,
                f"{rate:.1f}%",
                ha="center",
                va="bottom",
                fontweight="bold",
            )

        plt.tight_layout()
        plt.savefig(
            f"{self.charts_dir}/optimal_configurations.png",
            dpi=300,
            bbox_inches="tight",
        )
        plt.close()

    def generate_summary_report(self):
        """Generate a summary report with key findings"""
        if not self.results:
            return

        analysis = self.results["comprehensive_analysis"]

        report = f"""
# Multi-Model Evaluation Summary Report

## Key Findings

### Model Rankings
"""

        # Top 3 models
        rankings = analysis["model_rankings"][:3]
        for i, model in enumerate(rankings):
            medal = ["🥇", "🥈", "🥉"][i]
            report += f"{medal} **{model['model_name']}**: {model['avg_success_rate']:.1%} average success rate\n"

        report += f"""
### Sample Size Analysis
"""

        # Sample size findings
        sample_analysis = analysis["sample_size_analysis"]
        for n_key, stats in sample_analysis.items():
            n = n_key.replace("n_", "")
            report += f"- **n={n}**: {stats['average_success_rate']:.1%} avg, {stats['models_achieving_100']}/{stats['total_models']} models at 100%\n"

        report += f"""
### 100% Achievement Summary
- **Total 100% configurations**: {analysis['100_percent_achievement']['total_100_percent_configs']}
"""

        # Best 100% configurations
        configs = analysis["100_percent_achievement"]["configurations"]
        if configs:
            report += "- **Best 100% configurations**:\n"
            for config in configs[:5]:
                n = config["sample_size"].replace("n_", "")
                report += f"  - {config['model_name']} (n={n})\n"

        report += f"""
### Optimal Configurations
"""

        # Top optimal configurations
        best_configs = analysis["best_configurations"][:5]
        for i, config in enumerate(best_configs):
            n = config["optimal_sample_size"].replace("n_", "")
            report += f"{i+1}. **{config['model_name']}** (n={n}): {config['success_rate']:.1%} success rate\n"

        # Save report
        report_file = f"{self.charts_dir}/summary_report.md"
        with open(report_file, "w") as f:
            f.write(report)

        print(f"✅ Summary report saved to {report_file}")


def main():
    """Main function to generate all visualizations"""
    print("📊 Multi-Model Results Visualization")
    print("=" * 50)

    visualizer = MultiModelVisualizer()
    visualizer.generate_all_charts()
    visualizer.generate_summary_report()

    print("🎉 All visualizations completed!")


if __name__ == "__main__":
    main()
