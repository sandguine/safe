#!/bin/bash
# One-liner CLI shortcut for full AZR pipeline execution
# Usage: ./run_full.sh [--dry-run] [--max-cost 120]
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

# Use miniforge Python if available, otherwise fall back to system python3
if [ -f "/Users/sandy/miniforge3/bin/python3" ]; then
    PYTHON_CMD="/Users/sandy/miniforge3/bin/python3"
else
    PYTHON_CMD="python3"
fi

# Default settings
DRY_RUN=false
MAX_COST=120
TASKS=164
SESSION_NAME="azr_pipeline"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            TASKS=50
            shift
            ;;
        --max-cost)
            MAX_COST="$2"
            shift 2
            ;;
        --tasks)
            TASKS="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [--dry-run] [--max-cost N] [--tasks N]"
            echo "  --dry-run    Run with 50 tasks instead of 164"
            echo "  --max-cost   Maximum cost in dollars (default: 120)"
            echo "  --tasks      Number of tasks to run (default: 164)"
            echo "  --help       Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗"
echo -e "║                AZR PIPELINE EXECUTION                    ║"
echo -e "║                    Standardized Validation                ║"
echo -e "╚══════════════════════════════════════════════════════════════╝${NC}"

echo -e "${BLUE}🚀 AZR Pipeline Execution${NC}"
echo "=================================="
echo -e "${YELLOW}Mode:${NC} $([ "$DRY_RUN" = true ] && echo "DRY RUN" || echo "FULL PRODUCTION")"
echo -e "${YELLOW}Tasks:${NC} $TASKS"
echo -e "${YELLOW}Max Cost:${NC} \$$MAX_COST"
echo -e "${YELLOW}Session:${NC} $SESSION_NAME"
echo ""

# Step 1: Run standardized validation
echo -e "${PURPLE}[STEP]${NC} [$(date +%H:%M:%S)] run_full.sh: Running validation..."
$PYTHON_CMD -c "
import sys
sys.path.insert(0, 'src')
from validation import validate_script
success = validate_script('run_full.sh')
sys.exit(0 if success else 1)
"

if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR]${NC} [$(date +%H:%M:%S)] run_full.sh: Validation failed"
    echo -e "${RED}❌ Pipeline cannot proceed due to validation errors${NC}"
    exit 1
fi

echo -e "${GREEN}[SUCCESS]${NC} [$(date +%H:%M:%S)] run_full.sh: Validation passed"
echo ""

# Create results directory
mkdir -p results
mkdir -p logs

# Generate timestamp for log files
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="logs/azr_execution_${TIMESTAMP}.log"

echo -e "${BLUE}📝 Logging to: $LOG_FILE${NC}"

# Check if tmux is available
if ! command -v tmux &> /dev/null; then
    echo -e "${YELLOW}⚠️  tmux not found, running in current terminal${NC}"
    
    # Run directly without tmux
    echo -e "${GREEN}🚀 Starting AZR pipeline execution...${NC}"
    echo "Execution started at: $(date)" | tee -a "$LOG_FILE"
    
    if [ "$DRY_RUN" = true ]; then
        $PYTHON_CMD execute_refined_plan.py --dry-run --tasks "$TASKS" --max-cost "$MAX_COST" 2>&1 | tee -a "$LOG_FILE"
    else
        $PYTHON_CMD execute_refined_plan.py --full-run --tasks "$TASKS" --max-cost "$MAX_COST" 2>&1 | tee -a "$LOG_FILE"
    fi
    
    echo "Execution completed at: $(date)" | tee -a "$LOG_FILE"
    echo -e "${GREEN}✅ Execution completed! Check $LOG_FILE for details${NC}"
    
else
    # Check if session already exists
    if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  tmux session '$SESSION_NAME' already exists${NC}"
        read -p "Attach to existing session? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            tmux attach-session -t "$SESSION_NAME"
            exit 0
        else
            echo -e "${RED}❌ Aborting execution${NC}"
            exit 1
        fi
    fi
    
    # Create new tmux session
    echo -e "${BLUE}🖥️  Creating tmux session: $SESSION_NAME${NC}"
    tmux new-session -d -s "$SESSION_NAME" -n "main"
    
    # Set up the main window
    tmux send-keys -t "$SESSION_NAME:main" "echo '🚀 AZR Pipeline Execution Started'" Enter
    tmux send-keys -t "$SESSION_NAME:main" "echo 'Timestamp: $(date)'" Enter
    tmux send-keys -t "$SESSION_NAME:main" "echo 'Log file: $LOG_FILE'" Enter
    tmux send-keys -t "$SESSION_NAME:main" "" Enter
    
    # Start the execution
    if [ "$DRY_RUN" = true ]; then
        tmux send-keys -t "$SESSION_NAME:main" "$PYTHON_CMD execute_refined_plan.py --dry-run --tasks $TASKS --max-cost $MAX_COST 2>&1 | tee -a $LOG_FILE" Enter
    else
        tmux send-keys -t "$SESSION_NAME:main" "$PYTHON_CMD execute_refined_plan.py --full-run --tasks $TASKS --max-cost $MAX_COST 2>&1 | tee -a $LOG_FILE" Enter
    fi
    
    # Create monitoring window
    tmux new-window -t "$SESSION_NAME" -n "monitor"
    tmux send-keys -t "$SESSION_NAME:monitor" "echo '📊 Monitoring Dashboard'" Enter
    tmux send-keys -t "$SESSION_NAME:monitor" "watch -n 30 'echo \"=== AZR Pipeline Status ===\"; echo \"Tasks completed: \$(ls results/ 2>/dev/null | wc -l)\"; echo \"Log file: $LOG_FILE\"; echo \"Last update: \$(date)\"'" Enter
    
    # Create safety tests window
    tmux new-window -t "$SESSION_NAME" -n "safety"
    tmux send-keys -t "$SESSION_NAME:safety" "echo '🛡️  Running Safety Tests in Parallel'" Enter
    tmux send-keys -t "$SESSION_NAME:safety" "$PYTHON_CMD run_harm_suite.py --detailed-breakdown &" Enter
    tmux send-keys -t "$SESSION_NAME:safety" "$PYTHON_CMD test_collusion.py --statistical-analysis &" Enter
    tmux send-keys -t "$SESSION_NAME:safety" "$PYTHON_CMD test_latency.py --scenarios all &" Enter
    tmux send-keys -t "$SESSION_NAME:safety" "wait" Enter
    
    echo -e "${GREEN}✅ tmux session created successfully!${NC}"
    echo -e "${BLUE}📋 Session windows:${NC}"
    echo "  - main: Main execution"
    echo "  - monitor: Real-time monitoring"
    echo "  - safety: Parallel safety tests"
    echo ""
    echo -e "${YELLOW}To attach to the session:${NC}"
    echo "  tmux attach-session -t $SESSION_NAME"
    echo ""
    echo -e "${YELLOW}To detach from session:${NC}"
    echo "  Ctrl+B, then D"
    echo ""
    echo -e "${YELLOW}To kill session:${NC}"
    echo "  tmux kill-session -t $SESSION_NAME"
    echo ""
    
    # Ask if user wants to attach now
    read -p "Attach to session now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        tmux attach-session -t "$SESSION_NAME"
    else
        echo -e "${GREEN}✅ Session is running in background. Use 'tmux attach-session -t $SESSION_NAME' to connect${NC}"
    fi
fi

echo -e "${GREEN}🎯 Execution setup complete!${NC}" 