#!/bin/bash
# Run all oversight curriculum components
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
echo -e "║                OVERSIGHT CURRICULUM RUN ALL               ║"
echo -e "║                    Standardized Validation                ║"
echo -e "╚══════════════════════════════════════════════════════════════╝${NC}"

# Step 1: Run standardized validation
echo -e "${PURPLE}[STEP]${NC} [$(date +%H:%M:%S)] run_all.sh: Running validation..."
python3 -c "
import sys
sys.path.insert(0, 'src')
from validation import validate_script
success = validate_script('run_all.sh')
sys.exit(0 if success else 1)
"

if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR]${NC} [$(date +%H:%M:%S)] run_all.sh: Validation failed"
    echo -e "${RED}❌ Cannot proceed due to validation errors${NC}"
    exit 1
fi

echo -e "${GREEN}[SUCCESS]${NC} [$(date +%H:%M:%S)] run_all.sh: Validation passed"
echo ""

echo -e "${BLUE}🚀 Running all oversight curriculum components...${NC}"

# Run all components
echo -e "${BLUE}1. Running demo...${NC}"
./run_demo.sh

echo -e "${BLUE}2. Running hackathon demo...${NC}"
./run_hackathon_demo.sh

echo -e "${BLUE}3. Running full pipeline...${NC}"
./run_full.sh --dry-run

echo -e "${GREEN}🎉 All components completed successfully!${NC}" 