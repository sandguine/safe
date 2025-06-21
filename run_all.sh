#!/bin/bash
# Comprehensive run script for oversight curriculum.
# Executes all components: baseline, oversight, analysis, and comparison.

set -e  # Exit on any error

echo "🎯 OVERSIGHT CURRICULUM - COMPLETE RUN"
echo "======================================"

# Check if API key is set
if [ -z "$CLAUDE_API_KEY" ]; then
    echo "❌ Error: CLAUDE_API_KEY environment variable not set"
    echo "Please set your API key: export CLAUDE_API_KEY='your-key-here'"
    exit 1
fi

# Create results directory
mkdir -p results

echo "📋 Configuration:"
echo "  - Model: claude-3-5-sonnet-20241022"
echo "  - Cycles: 10 (optimized for ≤15s execution)"
echo "  - Puzzles per cycle: 2"
echo "  - Solutions per puzzle: 1"
echo "  - Use config puzzles: Yes"
echo ""

# Step 1: Run baseline experiment (no referee)
echo "🔄 Step 1: Running baseline experiment..."
python azr_loop.py --no_ref --cycles 10 --output results/baseline_demo.csv

echo ""

# Step 2: Run oversight experiment (with referee)
echo "🔄 Step 2: Running oversight experiment..."
python azr_loop.py --with_ref --cycles 10 --output results/oversight_demo.csv

echo ""

# Step 3: Run full demo (baseline + oversight + comparison)
echo "🔄 Step 3: Running full demo with comparison..."
python run_demo.py --cycles 10 --puzzles_per_cycle 2 --solutions_per_puzzle 1 --skip_plots

echo ""

# Step 4: Run analysis on CSV files
echo "🔄 Step 4: Running analysis on results..."
python src/analysis.py --baseline results/baseline_demo.csv --oversight results/oversight_demo.csv

echo ""

# Step 5: Run unit tests
echo "🔄 Step 5: Running unit tests..."
python -m pytest tests/test_deduction_loop.py -v

echo ""

# Step 6: Generate final summary
echo "📊 FINAL SUMMARY"
echo "================"
echo "Generated files:"
ls -la results/

echo ""
echo "🎉 Complete run finished successfully!"
echo "Check the 'results/' directory for all output files:"
echo "  - baseline_demo.csv: Baseline experiment results"
echo "  - oversight_demo.csv: Oversight experiment results"
echo "  - comparison_plot.png: Visual comparison"
echo "  - baseline_metrics.json: Detailed baseline metrics"
echo "  - oversight_metrics.json: Detailed oversight metrics"
echo "  - comparison_report.txt: Text comparison report"
echo "  - combined_results.json: All results combined"
echo ""

# Check execution time
echo "⏱️  Performance check:"
if [ -f results/combined_results.json ]; then
    echo "✅ All components executed successfully"
else
    echo "⚠️  Some components may have failed"
fi

echo ""
echo "🚀 Ready for research and experimentation!" 