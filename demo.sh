#!/usr/bin/env bash
set -eux

echo "🚀 Starting SAFE MVP Demo..."
echo "================================"

# Create demo directory
mkdir -p demo results

# Step 1: Generate harm prompts
echo "📝 Generating harm prompts..."
python -m oversight.features.red_team_suite --generate-prompts

# Step 2: Capability Demo - Baseline
echo "🧠 Running capability baseline (n=1)..."
python -m oversight.features.humaneval_integration \
  --mode baseline \
  --problems 5 \
  --samples-per-problem 1 \
  --output demo/baseline.json

# Step 3: Capability Demo - Oversight
echo "🧠 Running capability oversight (n=4)..."
python -m oversight.features.humaneval_integration \
  --mode oversight \
  --problems 5 \
  --samples-per-problem 4 \
  --hhh-filter stub_safe \
  --output demo/oversight.json

# Step 4: Safety Demo
echo "🛡️ Running safety demo..."
python -m oversight.features.red_team_suite \
  --prompts demo/harm_prompts.json \
  --hhh-filter keyword_ban \
  --output demo/safety.json

# Step 5: Quick Summary
echo "📊 Generating quick summary..."
python - <<'PYCODE'
import json
import os

# Load results
baseline_file = "demo/baseline.json"
oversight_file = "demo/oversight.json"
safety_file = "demo/safety.json"

if os.path.exists(baseline_file) and os.path.exists(oversight_file):
    b = json.load(open(baseline_file))
    o = json.load(open(oversight_file))
    print(f"Capability Results:")
    print(f"  Baseline pass@1: {b['pass1']:.3f}")
    print(f"  Oversight pass@1: {o['pass1']:.3f}")
    print(f"  Improvement: +{o['pass1']-b['pass1']:.3f}")
    print()

if os.path.exists(safety_file):
    s = json.load(open(safety_file))
    print(f"Safety Results:")
    print(f"  Harm refused: {s['refused']}/{s['total']}")
    print(f"  Refusal rate: {s['refusal_rate']:.1%}")
    print()

print("✅ Demo completed successfully!")
print("📁 Results saved in demo/ directory")
PYCODE

# Step 6: Comprehensive Evaluation
echo "🔍 Running comprehensive evaluation..."
python evaluate_results.py

echo "🎉 MVP Demo Complete!"
echo ""
echo "📋 Files generated:"
echo "  demo/baseline.json - Baseline capability results"
echo "  demo/oversight.json - Oversight capability results"
echo "  demo/safety.json - Safety filtering results"
echo "  demo/harm_prompts.json - Sample harmful prompts"
echo "  evaluation_report_*.txt - Comprehensive analysis"
echo "  evaluation_data_*.json - Structured data for further analysis"
