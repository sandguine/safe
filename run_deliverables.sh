#!/bin/bash

# Oversight Curriculum Hackathon Deliverable Generator
# This script generates all required deliverables for Jan and Akbir's requirements

set -e

echo "🎯 OVERSIGHT CURRICULUM HACKATHON DELIVERABLE GENERATOR"
echo "======================================================"
echo ""

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this script from the oversight_curriculum directory"
    exit 1
fi

# Check if API key is set
if [ -z "$CLAUDE_API_KEY" ]; then
    echo "❌ Error: CLAUDE_API_KEY environment variable not set"
    echo "Please set your API key: export CLAUDE_API_KEY='your-key-here'"
    echo ""
    echo "You can get your API key from: https://console.anthropic.com/"
    exit 1
fi

# Check Python dependencies
echo "🔍 Checking dependencies..."
if ! python -c "import anthropic, pandas, numpy" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Create results directory
mkdir -p results

echo ""
echo "🚀 Starting deliverable generation..."
echo "This will generate:"
echo "• KL divergence table (n=1/4/16/64)"
echo "• 200-prompt red-team sheet"
echo "• Collusion mitigation analysis"
echo "• Refusal transparency samples"
echo "• Fail-case appendix"
echo ""

# Run the deliverable generator
python generate_deliverables.py

echo ""
echo "✅ Deliverable generation complete!"
echo ""
echo "📁 Results saved to: results/"
echo ""
echo "📋 Key files generated:"
echo "• kl_divergence_table.csv - KL divergence analysis"
echo "• red_team_results.csv - 200-prompt red-team results"
echo "• transparency_samples_report.txt - Refusal transparency"
echo "• fail_case_appendix.txt - Fail-case analysis"
echo "• comprehensive_report.txt - Overall summary"
echo ""
echo "🎉 Ready for hackathon presentation!" 