#!/bin/bash

# Oversight Curriculum Demo Runner
# This script runs the complete baseline vs oversight experiment
# Now with standardized validation from run_robust.py

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗"
echo -e "║                OVERSIGHT CURRICULUM DEMO RUNNER           ║"
echo -e "║                    Standardized Validation                ║"
echo -e "╚══════════════════════════════════════════════════════════════╝${NC}"

# Step 1: Run standardized validation
echo -e "${PURPLE}[STEP]${NC} [$(date +%H:%M:%S)] run_demo.sh: Running validation..."
python3 -c "
import sys
sys.path.insert(0, 'src')
from validation import validate_script
success = validate_script('run_demo.sh')
sys.exit(0 if success else 1)
"

if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR]${NC} [$(date +%H:%M:%S)] run_demo.sh: Validation failed"
    echo -e "${RED}❌ Demo cannot proceed due to validation errors${NC}"
    exit 1
fi

echo -e "${GREEN}[SUCCESS]${NC} [$(date +%H:%M:%S)] run_demo.sh: Validation passed"
echo ""

# Step 2: Run the demo
echo -e "${BLUE}[INFO]${NC} [$(date +%H:%M:%S)] run_demo.sh: Starting demo..."
python3 run_demo.py

# Check if demo completed successfully
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 Demo completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}📊 Results saved in the 'results/' directory:${NC}"
    echo "  - baseline_metrics.json"
    echo "  - oversight_metrics.json" 
    echo "  - comparison_report.txt"
    echo "  - learning_curves.png"
    echo "  - combined_results.json"
    echo ""
    echo -e "${BLUE}📖 View the comparison report:${NC}"
    echo "  cat results/comparison_report.txt"
else
    echo ""
    echo -e "${RED}❌ Demo failed${NC}"
    exit 1
fi 