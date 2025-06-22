#!/bin/bash

# Oversight Curriculum Demo Runner
# This script runs the complete baseline vs oversight experiment
# Now with robust environment management and validation

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to log messages with timestamp
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date +%H:%M:%S)
    local color=$BLUE
    
    case $level in
        "INFO") color=$BLUE ;;
        "SUCCESS") color=$GREEN ;;
        "WARNING") color=$YELLOW ;;
        "ERROR") color=$RED ;;
        "STEP") color=$PURPLE ;;
    esac
    
    echo -e "${color}[${level}]${NC} [${timestamp}] run_demo.sh: ${message}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect Python environment
detect_python() {
    # Try miniforge Python first (preferred)
    if [ -f "/Users/sandy/miniforge3/bin/python3" ]; then
        echo "/Users/sandy/miniforge3/bin/python3"
        return 0
    fi
    
    # Try pyenv Python
    if command_exists pyenv; then
        local pyenv_python=$(pyenv which python3 2>/dev/null || echo "")
        if [ -n "$pyenv_python" ]; then
            echo "$pyenv_python"
            return 0
        fi
    fi
    
    # Try system python3
    if command_exists python3; then
        echo "python3"
        return 0
    fi
    
    # Try python
    if command_exists python; then
        echo "python"
        return 0
    fi
    
    return 1
}

# Function to check working directory
check_working_directory() {
    log "STEP" "Checking working directory..."
    
    # Get the directory where this script is located
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    # Check if we're in the oversight_curriculum directory
    if [[ "$(basename "$PWD")" == "oversight_curriculum" ]]; then
        log "SUCCESS" "Already in oversight_curriculum directory"
        return 0
    else
        # Try to find and change to oversight_curriculum directory
        if [ -d "$SCRIPT_DIR/oversight_curriculum" ]; then
            cd "$SCRIPT_DIR/oversight_curriculum"
            log "SUCCESS" "Changed to oversight_curriculum directory: $(pwd)"
            return 0
        else
            log "ERROR" "Could not find oversight_curriculum directory"
            return 1
        fi
    fi
}

# Function to check environment variables
check_environment() {
    log "STEP" "Checking environment setup..."
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        log "WARNING" ".env file not found"
        log "INFO" "Creating .env file template..."
        
        cat > .env << 'EOF'
# Claude API Configuration
CLAUDE_API_KEY=your-api-key-here

# Optional: Model configuration
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Optional: Logging level
LOG_LEVEL=INFO
EOF
        
        log "ERROR" "Please edit .env file and add your actual API key"
        log "INFO" "Then run this script again"
        return 1
    fi
    
    # Load .env file
    if [ -f ".env" ]; then
        export $(grep -v '^#' .env | xargs)
        log "SUCCESS" "Loaded .env file"
    fi
    
    # Check if API key is set
    if [ -z "$CLAUDE_API_KEY" ]; then
        log "ERROR" "CLAUDE_API_KEY not found in .env file"
        return 1
    fi
    
    # Validate API key format
    if [[ ! "$CLAUDE_API_KEY" =~ ^sk- ]]; then
        log "ERROR" "Invalid API key format (should start with 'sk-')"
        return 1
    fi
    
    log "SUCCESS" "Environment variables loaded successfully"
    log "INFO" "API Key: ${CLAUDE_API_KEY:0:10}...${CLAUDE_API_KEY: -4}"
    return 0
}

# Function to check Python and dependencies
check_python_dependencies() {
    log "STEP" "Checking Python and dependencies..."
    
    # Detect Python
    PYTHON_CMD=$(detect_python)
    if [ $? -ne 0 ]; then
        log "ERROR" "No Python installation found"
        return 1
    fi
    
    log "INFO" "Using Python: $PYTHON_CMD"
    
    # Check Python version
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
    log "INFO" "Python version: $PYTHON_VERSION"
    
    # Check if requirements.txt exists
    if [ ! -f "requirements.txt" ]; then
        log "ERROR" "requirements.txt not found"
        return 1
    fi
    
    # Check required packages
    REQUIRED_PACKAGES=("anthropic" "matplotlib" "pandas" "numpy" "seaborn")
    MISSING_PACKAGES=()
    
    for package in "${REQUIRED_PACKAGES[@]}"; do
        if $PYTHON_CMD -c "import $package" 2>/dev/null; then
            log "SUCCESS" "✓ $package available"
        else
            MISSING_PACKAGES+=("$package")
            log "ERROR" "✗ $package missing"
        fi
    done
    
    if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
        log "ERROR" "Missing packages: ${MISSING_PACKAGES[*]}"
        log "INFO" "Please install missing packages: pip install ${MISSING_PACKAGES[*]}"
        return 1
    fi
    
    log "SUCCESS" "All Python dependencies available"
    return 0
}

# Function to check directories and files
check_directories_and_files() {
    log "STEP" "Checking directories and files..."
    
    # Required directories
    REQUIRED_DIRS=("src" "configs" "results" "logs")
    for dir in "${REQUIRED_DIRS[@]}"; do
        if [ -d "$dir" ]; then
            log "SUCCESS" "✓ Directory $dir exists"
        else
            log "ERROR" "✗ Directory $dir missing"
            return 1
        fi
    done
    
    # Required files
    REQUIRED_FILES=("src/deduction_loop.py" "src/metrics.py" "configs/deduction_mini.json")
    for file in "${REQUIRED_FILES[@]}"; do
        if [ -f "$file" ]; then
            log "SUCCESS" "✓ File $file exists"
        else
            log "ERROR" "✗ File $file missing"
            return 1
        fi
    done
    
    log "SUCCESS" "All required directories and files present"
    return 0
}

# Function to run validation
run_validation() {
    log "STEP" "Running comprehensive validation..."
    
    validation_steps=(
        "check_working_directory"
        "check_environment"
        "check_python_dependencies"
        "check_directories_and_files"
    )
    
    for step in "${validation_steps[@]}"; do
        if ! $step; then
            log "ERROR" "Validation failed at step: $step"
            return 1
        fi
    done
    
    log "SUCCESS" "All validation steps passed"
    return 0
}

# Main execution
main() {
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗"
    echo -e "║                OVERSIGHT CURRICULUM DEMO RUNNER           ║"
    echo -e "║                    Robust Shell Execution                 ║"
    echo -e "╚══════════════════════════════════════════════════════════════╝${NC}"
    
    # Run validation
    if ! run_validation; then
        log "ERROR" "Validation failed - cannot proceed"
        exit 1
    fi
    
    # Detect Python
    PYTHON_CMD=$(detect_python)
    if [ $? -ne 0 ]; then
        log "ERROR" "No Python installation found"
        exit 1
    fi
    
    # Run the demo
    log "INFO" "Starting demo..."
    if $PYTHON_CMD run_demo.py "$@"; then
        echo ""
        log "SUCCESS" "Demo completed successfully!"
        echo ""
        log "INFO" "📊 Results saved in the 'results/' directory:"
        echo "  - baseline_metrics.json"
        echo "  - oversight_metrics.json" 
        echo "  - comparison_report.txt"
        echo "  - learning_curves.png"
        echo "  - combined_results.json"
        echo ""
        log "INFO" "📖 View the comparison report:"
        echo "  cat results/comparison_report.txt"
    else
        echo ""
        log "ERROR" "Demo failed"
        exit 1
    fi
}

# Run main function with all arguments
main "$@" 