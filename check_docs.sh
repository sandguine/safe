#!/bin/bash

echo "🔍 Checking documentation for issues..."

# Check if validation script exists
if [ ! -f "validate_docs.py" ]; then
    echo "❌ Validation script not found: validate_docs.py"
    exit 1
fi

# Run validation
python validate_docs.py

# Check if demo script is executable
if [ ! -x "demo.sh" ]; then
    echo "⚠️  Demo script is not executable. Run: chmod +x demo.sh"
fi

# Check if required files exist
required_files=(
    "README.md"
    "MVP_DEMO.md"
    "demo.sh"
    "evaluate_results.py"
    "requirements.txt"
    "oversight/features/humaneval_integration.py"
    "oversight/features/red_team_suite.py"
    "oversight/model.py"
    "oversight/hhh_filter.py"
)

echo ""
echo "📁 Checking required files..."
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (missing)"
    fi
done

# Check for common issues
echo ""
echo "🔍 Checking for common issues..."

# Check for README_ENHANCED.md references
if grep -r "README_ENHANCED.md" README.md MVP_DEMO.md 2>/dev/null; then
    echo "  ❌ Found references to deleted README_ENHANCED.md"
fi

# Check for inconsistent paths
if grep -r "results/" README.md MVP_DEMO.md 2>/dev/null | grep -v "demo/"; then
    echo "  ⚠️  Found inconsistent output paths"
fi

# Check for overselling language
problematic_phrases=(
    "zero false positives"
    "perfect"
    "revolutionary"
    "breakthrough"
    "state of the art"
    "best in class"
    "unprecedented"
)

for phrase in "${problematic_phrases[@]}"; do
    if grep -ri "$phrase" README.md MVP_DEMO.md 2>/dev/null; then
        echo "  ⚠️  Found potentially overselling language: '$phrase'"
    fi
done

echo ""
echo "✅ Documentation check completed!"
