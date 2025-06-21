#!/bin/bash

# =============================================================================
# ROBUST EXECUTION SCRIPT FOR OVERSIGHT CURRICULUM
# =============================================================================
# This script guarantees smooth execution by:
# 1. Setting correct working directory
# 2. Loading environment variables properly
# 3. Checking all dependencies and prerequisites
# 4. Providing comprehensive error handling
# 5. Ensuring proper cleanup and reporting
# =============================================================================

set -euo pipefail  # Strict error handling

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# Function to print banner
print_banner() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                OVERSIGHT CURRICULUM RUNNER                   ║"
    echo "║                    Robust Execution Script                   ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Function to check if we're in the right directory
check_working_directory() {
    log_step "Checking working directory..."
    
    # Get the absolute path of the current script
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    # Check if we're already in the oversight_curriculum directory
    if [[ "$(basename "$PWD")" == "oversight_curriculum" ]]; then
        log_success "Already in oversight_curriculum directory"
        return 0
    fi
    
    # Try to change to the oversight_curriculum directory
    if [[ -d "$SCRIPT_DIR" ]]; then
        cd "$SCRIPT_DIR"
        log_success "Changed to oversight_curriculum directory: $PWD"
        return 0
    else
        log_error "Could not find oversight_curriculum directory"
        log_error "Expected: $SCRIPT_DIR"
        log_error "Current: $PWD"
        return 1
    fi
}

# Function to check and load environment variables
check_environment() {
    log_step "Checking environment setup..."
    
    # Check if .env file exists
    if [[ ! -f ".env" ]]; then
        log_warning ".env file not found"
        log_info "Creating .env file template..."
        cat > .env << EOF
# Claude API Configuration
CLAUDE_API_KEY=your-api-key-here

# Optional: Model configuration
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Optional: Logging level
LOG_LEVEL=INFO
EOF
        log_error "Please edit .env file and add your actual API key"
        log_info "Then run this script again"
        return 1
    fi
    
    # Load .env file
    if [[ -f ".env" ]]; then
        log_info "Loading .env file..."
        set -a  # automatically export all variables
        source .env
        set +a  # stop automatically exporting
        
        # Check if API key is set
        if [[ -z "${CLAUDE_API_KEY:-}" ]]; then
            log_error "CLAUDE_API_KEY not found in .env file"
            log_info "Please add your API key to the .env file:"
            log_info "CLAUDE_API_KEY=sk-your-actual-api-key-here"
            return 1
        fi
        
        # Validate API key format
        if [[ ! "$CLAUDE_API_KEY" =~ ^sk-[a-zA-Z0-9_-]+$ ]]; then
            log_error "Invalid API key format (should start with 'sk-')"
            return 1
        fi
        
        log_success "Environment variables loaded successfully"
        log_info "API Key: ${CLAUDE_API_KEY:0:10}...${CLAUDE_API_KEY: -4}"
        return 0
    fi
    
    return 1
}

# Function to check Python and dependencies
check_python_dependencies() {
    log_step "Checking Python and dependencies..."
    
    # Check Python version
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed or not in PATH"
        return 1
    fi
    
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    log_info "Python version: $PYTHON_VERSION"
    
    # Check if requirements.txt exists
    if [[ ! -f "requirements.txt" ]]; then
        log_error "requirements.txt not found"
        return 1
    fi
    
    # Check if virtual environment is recommended
    if [[ -z "${VIRTUAL_ENV:-}" ]]; then
        log_warning "Not running in a virtual environment"
        log_info "Consider creating one: python3 -m venv venv && source venv/bin/activate"
    else
        log_success "Running in virtual environment: $VIRTUAL_ENV"
    fi
    
    # Check if pip is available
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 is not installed or not in PATH"
        return 1
    fi
    
    # Check if all required packages are installed
    log_info "Checking required packages..."
    MISSING_PACKAGES=()
    
    while IFS= read -r package; do
        # Skip empty lines and comments
        [[ -z "$package" || "$package" =~ ^[[:space:]]*# ]] && continue
        
        # Extract package name (remove version specifiers)
        PKG_NAME=$(echo "$package" | cut -d'=' -f1 | cut -d'>' -f1 | cut -d'<' -f1 | cut -d'~' -f1 | xargs)
        
        if ! python3 -c "import $PKG_NAME" 2>/dev/null; then
            MISSING_PACKAGES+=("$package")
        fi
    done < requirements.txt
    
    if [[ ${#MISSING_PACKAGES[@]} -gt 0 ]]; then
        log_warning "Missing packages detected:"
        for pkg in "${MISSING_PACKAGES[@]}"; do
            log_info "  - $pkg"
        done
        
        log_info "Installing missing packages..."
        if pip3 install -r requirements.txt; then
            log_success "All packages installed successfully"
        else
            log_error "Failed to install packages"
            return 1
        fi
    else
        log_success "All required packages are installed"
    fi
    
    return 0
}

# Function to run verification script
run_verification() {
    log_step "Running verification script..."
    
    if [[ ! -f "verify_setup.py" ]]; then
        log_error "verify_setup.py not found"
        return 1
    fi
    
    if python3 verify_setup.py; then
        log_success "Verification passed"
        return 0
    else
        log_error "Verification failed"
        return 1
    fi
}

# Function to create necessary directories
create_directories() {
    log_step "Creating necessary directories..."
    
    DIRS=("results" "logs" "temp")
    
    for dir in "${DIRS[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            log_info "Created directory: $dir"
        else
            log_info "Directory exists: $dir"
        fi
    done
}

# Function to run the main application
run_main_application() {
    log_step "Running main application..."
    
    # Check if main script exists
    if [[ ! -f "azr_loop.py" ]]; then
        log_error "azr_loop.py not found"
        return 1
    fi
    
    # Set default parameters
    CYCLES=${CYCLES:-10}
    
    log_info "Running with parameters:"
    log_info "  - Cycles: $CYCLES"
    log_info "  - Referee: ON (with oversight)"
    log_info "  - Config puzzles: ON"
    
    # Generate output filename with timestamp
    timestamp=$(date +%Y%m%d_%H%M%S)
    output_file="results/robust_run_${timestamp}.csv"
    
    # Run the main application with correct arguments
    if python3 azr_loop.py \
        --with_ref \
        --cycles "$CYCLES" \
        --config \
        --output "$output_file"; then
        log_success "Main application completed successfully"
        return 0
    else
        log_error "Main application failed"
        return 1
    fi
}

# Function to run analysis
run_analysis() {
    log_step "Running analysis..."
    
    if [[ ! -f "src/analysis.py" ]]; then
        log_warning "analysis.py not found, skipping analysis"
        return 0
    fi
    
    # Find the most recent result files
    BASELINE_FILE=$(ls -t results/baseline_*.csv 2>/dev/null | head -1 || echo "")
    OVERSIGHT_FILE=$(ls -t results/oversight_*.csv 2>/dev/null | head -1 || echo "")
    
    if [[ -n "$BASELINE_FILE" && -n "$OVERSIGHT_FILE" ]]; then
        log_info "Running analysis on:"
        log_info "  - Baseline: $BASELINE_FILE"
        log_info "  - Oversight: $OVERSIGHT_FILE"
        
        if python3 src/analysis.py --baseline "$BASELINE_FILE" --oversight "$OVERSIGHT_FILE"; then
            log_success "Analysis completed successfully"
        else
            log_warning "Analysis failed, but continuing"
        fi
    else
        log_warning "No result files found for analysis"
    fi
}

# Function to run tests
run_tests() {
    log_step "Running tests..."
    
    if [[ ! -f "tests/test_deduction_loop.py" ]]; then
        log_warning "Tests not found, skipping"
        return 0
    fi
    
    if python3 -m pytest tests/test_deduction_loop.py -v; then
        log_success "Tests passed"
    else
        log_warning "Some tests failed, but continuing"
    fi
}

# Function to generate summary
generate_summary() {
    log_step "Generating summary..."
    
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                        EXECUTION SUMMARY                     ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo "📁 Working Directory: $PWD"
    echo "🐍 Python Version: $(python3 --version 2>&1)"
    echo "🔑 API Key: ${CLAUDE_API_KEY:0:10}...${CLAUDE_API_KEY: -4}"
    
    echo ""
    echo "📊 Generated Files:"
    if [[ -d "results" ]]; then
        ls -la results/ 2>/dev/null || echo "  No result files found"
    else
        echo "  No results directory found"
    fi
    
    echo ""
    echo "⏱️  Execution completed at: $(date)"
}

# Function to cleanup
cleanup() {
    log_step "Performing cleanup..."
    
    # Remove temporary files
    if [[ -d "temp" ]]; then
        rm -rf temp/*
        log_info "Cleaned temporary files"
    fi
    
    # Remove Python cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    log_success "Cleanup completed"
}

# Main execution function
main() {
    print_banner
    
    # Track overall success
    OVERALL_SUCCESS=true
    
    # Execute all steps
    STEPS=(
        "check_working_directory"
        "check_environment"
        "check_python_dependencies"
        "run_verification"
        "create_directories"
        "run_main_application"
        "run_analysis"
        "run_tests"
        "cleanup"
        "generate_summary"
    )
    
    for step in "${STEPS[@]}"; do
        log_step "Executing: $step"
        
        if $step; then
            log_success "$step completed successfully"
        else
            log_error "$step failed"
            OVERALL_SUCCESS=false
            
            # Ask user if they want to continue
            echo -e "${YELLOW}"
            read -p "Do you want to continue with the remaining steps? (y/N): " -n 1 -r
            echo -e "${NC}"
            
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                log_info "Execution stopped by user"
                break
            fi
        fi
        
        echo ""
    done
    
    # Final status
    if $OVERALL_SUCCESS; then
        echo -e "${GREEN}"
        echo "╔══════════════════════════════════════════════════════════════╗"
        echo "║                    🎉 EXECUTION SUCCESSFUL 🎉                ║"
        echo "╚══════════════════════════════════════════════════════════════╝"
        echo -e "${NC}"
    else
        echo -e "${RED}"
        echo "╔══════════════════════════════════════════════════════════════╗"
        echo "║                    ⚠️  EXECUTION HAD ISSUES ⚠️                ║"
        echo "╚══════════════════════════════════════════════════════════════╝"
        echo -e "${NC}"
    fi
}

# Handle script interruption
trap 'log_error "Script interrupted by user"; exit 1' INT TERM

# Run main function
main "$@" 