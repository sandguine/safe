#!/usr/bin/env python3
"""
Organize Results Script
======================

Organizes scattered results files into a clean, structured format.
"""

import glob
import json
import shutil
from datetime import datetime
from pathlib import Path


def organize_existing_results():
    """Organize existing scattered results into clean structure."""

    # Create results directory
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    # Find all existing result files
    enhanced_results = glob.glob("enhanced_results_*.json")
    enhanced_reports = glob.glob("enhanced_report_*.txt")
    evaluation_data = glob.glob("evaluation_data_*.json")
    evaluation_reports = glob.glob("evaluation_report_*.txt")

    print(f"📁 Found {len(enhanced_results)} enhanced results files")
    print(f"📁 Found {len(enhanced_reports)} enhanced report files")
    print(f"📁 Found {len(evaluation_data)} evaluation data files")
    print(f"📁 Found {len(evaluation_reports)} evaluation report files")

    # Organize enhanced demo results
    for result_file in enhanced_results:
        # Extract timestamp from filename
        timestamp = result_file.replace("enhanced_results_", "").replace(
            ".json", ""
        )

        # Create organized directory
        organized_dir = results_dir / f"enhanced_demo_{timestamp}"
        organized_dir.mkdir(exist_ok=True)

        # Move and rename files
        shutil.move(result_file, organized_dir / "data.json")

        # Find corresponding report
        report_file = f"enhanced_report_{timestamp}.txt"
        if Path(report_file).exists():
            shutil.move(report_file, organized_dir / "report.txt")

        # Create summary
        create_summary_from_old_data(
            organized_dir / "data.json", organized_dir / "summary.md"
        )

        print(f"✅ Organized: {result_file} → {organized_dir}")

    # Organize evaluation results
    for data_file in evaluation_data:
        # Extract timestamp from filename
        timestamp = data_file.replace("evaluation_data_", "").replace(
            ".json", ""
        )

        # Create organized directory
        organized_dir = results_dir / f"evaluation_{timestamp}"
        organized_dir.mkdir(exist_ok=True)

        # Move and rename files
        shutil.move(data_file, organized_dir / "data.json")

        # Find corresponding report
        report_file = f"evaluation_report_{timestamp}.txt"
        if Path(report_file).exists():
            shutil.move(report_file, organized_dir / "report.txt")

        print(f"✅ Organized: {data_file} → {organized_dir}")

    # Create latest symlink to most recent enhanced demo
    enhanced_dirs = list(results_dir.glob("enhanced_demo_*"))
    if enhanced_dirs:
        latest_dir = max(enhanced_dirs, key=lambda x: x.name)
        latest_link = results_dir / "latest"
        if latest_link.exists():
            latest_link.unlink()
        latest_link.symlink_to(latest_dir.name)
        print(f"🔗 Created latest symlink: {latest_link} → {latest_dir.name}")

    print("\n✅ Organization complete! Check the 'results' directory.")


def create_summary_from_old_data(data_file: Path, summary_file: Path):
    """Create a summary from old data format."""
    try:
        with open(data_file, "r") as f:
            data = json.load(f)

        capability = data.get("capability_analysis", {})
        safety = data.get("safety_analysis", {})

        summary = """# Enhanced SAFE Demo Results
**Generated**: {data.get('timestamp', 'Unknown')}

## 📊 Key Metrics

| Metric | Value |
|--------|-------|
| **Safety Refusal Rate** | {safety.get('refusal_rate', 0):.1%} |
| **Baseline Pass@1** | {capability.get('baseline_pass1', 0):.3f} |
| **Oversight Pass@1** | {capability.get('oversight_pass1', 0):.3f} |
| **Capability Improvement** | {capability.get('improvement', 0):.3f} |
| **Total Problems Tested** | {capability.get('total_problems', 0)} |
| **Harmful Prompts Tested** | {safety.get('total_prompts', 0)} |

## 📁 Files

- `data.json` - Complete raw results and logs
- `report.txt` - Detailed human-readable report
- `summary.md` - This summary document

---
*Enhanced SAFE Demo - Inference-time Safety Framework*
"""

        with open(summary_file, "w") as f:
            f.write(summary)

    except Exception as e:
        print(f"⚠️ Could not create summary for {data_file}: {e}")


def main():
    """Main entry point"""
    print("🧹 Organizing existing results files...")
    organize_existing_results()


if __name__ == "__main__":
    main()
