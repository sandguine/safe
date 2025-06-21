#!/bin/bash

# Oversight Curriculum Demo Runner
# This script runs the complete baseline vs oversight experiment

echo "🎯 Oversight Curriculum Demo"
echo "============================"

# Check if API key is set
if [ -z "$CLAUDE_API_KEY" ]; then
    echo "❌ Error: CLAUDE_API_KEY environment variable is not set"
    echo "Please set your API key:"
    echo "  export CLAUDE_API_KEY='your-key-here'"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 is not installed"
    exit 1
fi

# Check if required packages are installed
echo "🔍 Checking dependencies..."
python3 -c "import requests, dotenv" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Error: Required packages not installed"
    echo "Please run: pip install -r requirements.txt"
    exit 1
fi

# Verify setup
echo "🔍 Verifying setup..."
python3 verify_setup.py
if [ $? -ne 0 ]; then
    echo "❌ Setup verification failed"
    exit 1
fi

echo "✅ Setup verified successfully"
echo ""

# Run the demo
echo "🚀 Starting demo..."
python3 run_demo.py

# Check if demo completed successfully
if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Demo completed successfully!"
    echo ""
    echo "📊 Results saved in the 'results/' directory:"
    echo "  - baseline_metrics.json"
    echo "  - oversight_metrics.json" 
    echo "  - comparison_report.txt"
    echo "  - learning_curves.png"
    echo "  - combined_results.json"
    echo ""
    echo "📖 View the comparison report:"
    echo "  cat results/comparison_report.txt"
else
    echo ""
    echo "❌ Demo failed"
    exit 1
fi 