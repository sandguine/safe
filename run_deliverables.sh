#!/bin/bash
# Generate all deliverables for oversight curriculum
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
echo -e "║              OVERSIGHT CURRICULUM DELIVERABLES            ║"
echo -e "║                    Standardized Validation                ║"
echo -e "╚══════════════════════════════════════════════════════════════╝${NC}"

# Step 1: Run standardized validation
echo -e "${PURPLE}[STEP]${NC} [$(date +%H:%M:%S)] run_deliverables.sh: Running validation..."
python3 -c "
import sys
sys.path.insert(0, 'src')
from validation import validate_script
success = validate_script('run_deliverables.sh')
sys.exit(0 if success else 1)
"

if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR]${NC} [$(date +%H:%M:%S)] run_deliverables.sh: Validation failed"
    echo -e "${RED}❌ Cannot proceed due to validation errors${NC}"
    exit 1
fi

echo -e "${GREEN}[SUCCESS]${NC} [$(date +%H:%M:%S)] run_deliverables.sh: Validation passed"
echo ""

echo -e "${BLUE}📋 Generating all deliverables...${NC}"

# Generate deliverables
python generate_deliverables.py

echo -e "${GREEN}✅ All deliverables generated successfully!${NC}"
echo ""
echo -e "${BLUE}📊 Generated files:${NC}"
ls -la results/ 