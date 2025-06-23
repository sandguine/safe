#!/usr/bin/env python3
"""
Multi-Model Evaluation Runner
=============================

Comprehensive runner script that orchestrates the entire multi-model evaluation process:
1. Run multi-model evaluation
2. Generate visualizations
3. Create summary reports
4. Validate results
"""

import asyncio
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))


class MultiModelEvaluationRunner:
    """Comprehensive runner for multi-model evaluation"""

    def __init__(self):
        self.start_time = time.time()
        self.results_dir = "results/multi_model_evaluation"

    async def run_complete_evaluation(self):
        """Run the complete multi-model evaluation pipeline"""
        print("🚀 Multi-Model SAFE Evaluation Pipeline")
        print("=" * 80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Step 1: Run multi-model evaluation
        print("\n📊 Step 1: Running Multi-Model Evaluation")
        print("-" * 50)

        try:
            from multi_model_evaluation import MultiModelEvaluator

            evaluator = MultiModelEvaluator()
            results = await evaluator.run_comprehensive_evaluation()
            print("✅ Multi-model evaluation completed successfully")
        except Exception as e:
            print(f"❌ Error in multi-model evaluation: {e}")
            return False

        # Step 2: Generate visualizations
        print("\n📈 Step 2: Generating Visualizations")
        print("-" * 50)

        try:
            from generate_multi_model_charts import MultiModelVisualizer

            visualizer = MultiModelVisualizer(self.results_dir)
            visualizer.generate_all_charts()
            visualizer.generate_summary_report()
            print("✅ Visualizations generated successfully")
        except Exception as e:
            print(f"❌ Error generating visualizations: {e}")
            # Continue anyway as this is not critical

        # Step 3: Validate results
        print("\n🔍 Step 3: Validating Results")
        print("-" * 50)

        validation_results = self.validate_results()
        if validation_results:
            print("✅ Results validation passed")
        else:
            print("⚠️ Results validation had issues")

        # Step 4: Generate final summary
        print("\n📋 Step 4: Generating Final Summary")
        print("-" * 50)

        self.generate_final_summary()

        # Print completion message
        execution_time = time.time() - self.start_time
        print(f"\n🎉 COMPLETE EVALUATION PIPELINE FINISHED")
        print("=" * 80)
        print(f"Total execution time: {execution_time:.2f} seconds")
        print(f"Results saved to: {self.results_dir}/")
        print(f"Charts saved to: {self.results_dir}/charts/")

        return True

    def validate_results(self):
        """Validate the generated results"""
        try:
            # Check if comprehensive results exist
            comprehensive_file = (
                f"{self.results_dir}/comprehensive_results.json"
            )
            if not os.path.exists(comprehensive_file):
                print("❌ Comprehensive results file not found")
                return False

            # Load and validate results structure
            import json

            with open(comprehensive_file, "r") as f:
                results = json.load(f)

            # Check required fields
            required_fields = [
                "metadata",
                "model_results",
                "comprehensive_analysis",
            ]
            for field in required_fields:
                if field not in results:
                    print(f"❌ Missing required field: {field}")
                    return False

            # Check model results
            model_results = results["model_results"]
            if not model_results:
                print("❌ No model results found")
                return False

            # Check analysis
            analysis = results["comprehensive_analysis"]
            required_analysis = [
                "model_rankings",
                "sample_size_analysis",
                "best_configurations",
            ]
            for field in required_analysis:
                if field not in analysis:
                    print(f"❌ Missing analysis field: {field}")
                    return False

            # Check individual model files
            for model_id in model_results.keys():
                model_file = f"{self.results_dir}/{model_id}_results.json"
                if not os.path.exists(model_file):
                    print(f"⚠️ Individual model file missing: {model_id}")

            # Check charts directory
            charts_dir = f"{self.results_dir}/charts"
            if os.path.exists(charts_dir):
                chart_files = os.listdir(charts_dir)
                print(f"✅ Generated {len(chart_files)} chart files")
            else:
                print("⚠️ Charts directory not found")

            return True

        except Exception as e:
            print(f"❌ Error validating results: {e}")
            return False

    def generate_final_summary(self):
        """Generate a final summary of the evaluation"""
        try:
            import json

            # Load results
            comprehensive_file = (
                f"{self.results_dir}/comprehensive_results.json"
            )
            with open(comprehensive_file, "r") as f:
                results = json.load(f)

            metadata = results["metadata"]
            analysis = results["comprehensive_analysis"]

            # Create final summary
            summary = f"""
# Multi-Model SAFE Evaluation - Final Summary

## Evaluation Overview
- **Timestamp**: {metadata['timestamp']}
- **Execution Time**: {metadata['execution_time']:.2f} seconds
- **Models Evaluated**: {metadata['models_evaluated']}
- **Sample Sizes Tested**: {metadata['sample_sizes_tested']}
- **Total Evaluations**: {metadata['total_evaluations']}

## Key Results

### Top Performing Models
"""

            # Top 3 models
            rankings = analysis["model_rankings"][:3]
            for i, model in enumerate(rankings):
                medal = ["🥇", "🥈", "🥉"][i]
                summary += f"{medal} **{model['model_name']}**: {model['avg_success_rate']:.1%} avg success rate\n"

            summary += f"""
### Sample Size Performance
"""

            # Sample size analysis
            sample_analysis = analysis["sample_size_analysis"]
            for n_key, stats in sample_analysis.items():
                n = n_key.replace("n_", "")
                summary += f"- **n={n}**: {stats['average_success_rate']:.1%} avg, {stats['models_achieving_100']}/{stats['total_models']} models at 100%\n"

            summary += f"""
### 100% Achievement
- **Total 100% configurations**: {analysis['100_percent_achievement']['total_100_percent_configs']}
"""

            # Best 100% configurations
            configs = analysis["100_percent_achievement"]["configurations"]
            if configs:
                summary += "- **Best 100% configurations**:\n"
                for config in configs[:5]:
                    n = config["sample_size"].replace("n_", "")
                    summary += f"  - {config['model_name']} (n={n})\n"

            summary += f"""
### Optimal Configurations
"""

            # Top optimal configurations
            best_configs = analysis["best_configurations"][:5]
            for i, config in enumerate(best_configs):
                n = config["optimal_sample_size"].replace("n_", "")
                summary += f"{i+1}. **{config['model_name']}** (n={n}): {config['success_rate']:.1%} success rate\n"

            summary += f"""
## Files Generated
- **Comprehensive Results**: `{self.results_dir}/comprehensive_results.json`
- **Individual Model Results**: `{self.results_dir}/*_results.json`
- **Charts**: `{self.results_dir}/charts/`
- **Summary Report**: `{self.results_dir}/charts/summary_report.md`

## Next Steps
1. Review the generated charts and visualizations
2. Analyze model-specific performance patterns
3. Consider running additional evaluations with different parameters
4. Use results to inform model selection for production use

---
*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

            # Save final summary
            summary_file = f"{self.results_dir}/FINAL_SUMMARY.md"
            with open(summary_file, "w") as f:
                f.write(summary)

            print(f"✅ Final summary saved to {summary_file}")

        except Exception as e:
            print(f"❌ Error generating final summary: {e}")


async def main():
    """Main function to run the complete evaluation pipeline"""
    runner = MultiModelEvaluationRunner()
    success = await runner.run_complete_evaluation()

    if success:
        print("\n🎯 Evaluation pipeline completed successfully!")
        return 0
    else:
        print("\n❌ Evaluation pipeline encountered errors")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
