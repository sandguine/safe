#!/bin/bash
# Robust Execution Script for Oversight Curriculum
# Based on comprehensive guidelines for reliable execution

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗"
echo -e "║                OVERSIGHT CURRICULUM ROBUST RUN               ║"
echo -e "║                    Comprehensive Setup & Execution           ║"
echo -e "╚══════════════════════════════════════════════════════════════╝${NC}"

# Function to print colored output
print_step() {
    echo -e "${PURPLE}[STEP]${NC} [$(date +%H:%M:%S)] $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} [$(date +%H:%M:%S)] $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} [$(date +%H:%M:%S)] $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} [$(date +%H:%M:%S)] $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to validate API key format
validate_api_key() {
    local api_key="$1"
    if [[ -z "$api_key" ]]; then
        return 1
    fi
    if [[ "$api_key" =~ ^sk-[a-zA-Z0-9]{48}$ ]]; then
        return 0
    fi
    return 1
}

# Step 1: Directory and Environment Setup
print_step "Setting up environment and validating prerequisites..."

# Ensure we're in the right directory
if [[ ! -f "$PROJECT_ROOT/demo.sh" ]]; then
    print_error "demo.sh not found. Please run this script from the oversight_curriculum directory."
    exit 1
fi

cd "$PROJECT_ROOT"
print_success "Working directory: $(pwd)"

# Step 2: Check Python environment
print_step "Validating Python environment..."

if ! command_exists python3; then
    print_error "Python 3 is not installed. Please install Python 3.7+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
print_success "Python version: $PYTHON_VERSION"

# Step 3: Environment file setup
print_step "Setting up environment variables..."

ENV_FILE=".env"
if [[ ! -f "$ENV_FILE" ]]; then
    print_warning ".env file not found. Creating template..."
    cat > "$ENV_FILE" << EOF
# Oversight Curriculum Environment Configuration
CLAUDE_API_KEY=sk-your-actual-api-key-here
CLAUDE_MODEL=claude-3-5-sonnet-20241022
LOG_LEVEL=INFO
EOF
    print_warning "Please edit .env file and add your actual Claude API key"
    print_warning "Demo will run with mock responses if no valid API key is provided"
else
    print_success ".env file found"
fi

# Load environment variables
if [[ -f "$ENV_FILE" ]]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
fi

# Validate API key if provided
if [[ -n "$CLAUDE_API_KEY" && "$CLAUDE_API_KEY" != "sk-your-actual-api-key-here" ]]; then
    if validate_api_key "$CLAUDE_API_KEY"; then
        print_success "Valid API key format detected"
    else
        print_warning "API key format appears invalid. Demo will use mock responses."
    fi
else
    print_warning "No valid API key found. Demo will use mock responses."
fi

# Step 4: Install/check dependencies
print_step "Checking and installing dependencies..."

if ! python3 -c "import anthropic, human_eval" 2>/dev/null; then
    print_warning "Missing dependencies. Installing from requirements.txt..."
    pip3 install -r requirements.txt
else
    print_success "Core dependencies already installed"
fi

# Check enhanced dependencies
ENHANCED_DEPS=("dotenv" "requests" "pandas" "matplotlib")
MISSING_DEPS=()

for dep in "${ENHANCED_DEPS[@]}"; do
    if ! python3 -c "import $dep" 2>/dev/null; then
        MISSING_DEPS+=("$dep")
    fi
done

if [[ ${#MISSING_DEPS[@]} -gt 0 ]]; then
    print_warning "Installing enhanced dependencies: ${MISSING_DEPS[*]}"
    pip3 install python-dotenv requests pandas matplotlib
fi

print_success "All dependencies verified"

# Step 5: Create necessary directories
print_step "Creating output directories..."

mkdir -p results logs temp
print_success "Directories created: results/, logs/, temp/"

# Step 6: Run verification script
print_step "Running setup verification..."

if [[ -f "verify_setup.py" ]]; then
    python3 verify_setup.py
    if [[ $? -eq 0 ]]; then
        print_success "Setup verification passed"
    else
        print_error "Setup verification failed"
        exit 1
    fi
else
    print_warning "verify_setup.py not found, skipping verification"
fi

# Step 7: Execute main demo
print_step "Executing oversight curriculum demo..."

START_TIME=$(date +%s)

# Run the demo with error handling
if ./demo.sh 2>&1 | tee "logs/execution_${TIMESTAMP}.log"; then
    print_success "Demo execution completed successfully"
else
    print_error "Demo execution failed. Check logs/execution_${TIMESTAMP}.log for details"
    exit 1
fi

END_TIME=$(date +%s)
EXECUTION_TIME=$((END_TIME - START_TIME))

# Step 8: Generate execution summary
print_step "Generating execution summary..."

SUMMARY_FILE="results/execution_summary_${TIMESTAMP}.txt"
cat > "$SUMMARY_FILE" << EOF
OVERSIGHT CURRICULUM EXECUTION SUMMARY
=====================================
Timestamp: $(date)
Execution Time: ${EXECUTION_TIME} seconds

ENVIRONMENT:
- Working Directory: $(pwd)
- Python Version: $PYTHON_VERSION
- API Key Status: $(if [[ -n "$CLAUDE_API_KEY" && "$CLAUDE_API_KEY" != "sk-your-actual-api-key-here" ]]; then echo "Configured"; else echo "Not configured (using mock)"; fi)

FILES GENERATED:
- demo/baseline.json - Baseline capability results
- demo/oversight.json - Oversight capability results
- demo/safety.json - Safety filtering results
- demo/harm_prompts.json - Sample harmful prompts
- evaluation_report_*.txt - Comprehensive analysis
- evaluation_data_*.json - Structured data

LOGS:
- logs/execution_${TIMESTAMP}.log - Detailed execution log

COMPLETION: $(date)
EOF

print_success "Execution summary saved to $SUMMARY_FILE"

# Step 9: Cleanup
print_step "Performing cleanup..."

# Remove temporary files
rm -rf temp/* __pycache__/* 2>/dev/null || true
print_success "Temporary files cleaned"

# Step 10: Final summary
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗"
echo -e "║                    EXECUTION COMPLETE                        ║"
echo -e "╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}📊 Results available in:${NC}"
echo -e "  • demo/ directory - Raw results"
echo -e "  • results/ directory - Analysis and summaries"
echo -e "  • logs/ directory - Execution logs"
echo ""
echo -e "${CYAN}📋 Next steps:${NC}"
echo -e "  • Review evaluation_report_*.txt for detailed analysis"
echo -e "  • Check demo/ directory for raw results"
echo -e "  • Run 'python evaluate_results.py' for additional analysis"
echo ""
print_success "Oversight curriculum execution completed successfully!"
