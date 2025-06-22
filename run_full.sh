#!/bin/bash
# One-liner CLI shortcut for full AZR pipeline execution
# Usage: ./run_full.sh [--dry-run] [--max-cost 120]

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

echo -e "${BLUE}🚀 AZR Pipeline Execution${NC}"
echo "=================================="
echo -e "${YELLOW}Mode:${NC} $([ "$DRY_RUN" = true ] && echo "DRY RUN" || echo "FULL PRODUCTION")"
echo -e "${YELLOW}Tasks:${NC} $TASKS"
echo -e "${YELLOW}Max Cost:${NC} \$$MAX_COST"
echo -e "${YELLOW}Session:${NC} $SESSION_NAME"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ Error: .env file not found${NC}"
    echo "Please create .env file with your API key:"
    echo "ANTHROPIC_API_KEY=your_api_key_here"
    exit 1
fi

# Load environment variables
echo -e "${BLUE}📋 Loading environment variables...${NC}"
export $(cat .env | grep -v '^#' | xargs)

# Check if API key is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${RED}❌ Error: ANTHROPIC_API_KEY not found in .env${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Environment loaded successfully${NC}"

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
        python execute_refined_plan.py --dry-run --tasks "$TASKS" --max-cost "$MAX_COST" 2>&1 | tee -a "$LOG_FILE"
    else
        python execute_refined_plan.py --full-run --tasks "$TASKS" --max-cost "$MAX_COST" 2>&1 | tee -a "$LOG_FILE"
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
        tmux send-keys -t "$SESSION_NAME:main" "python execute_refined_plan.py --dry-run --tasks $TASKS --max-cost $MAX_COST 2>&1 | tee -a $LOG_FILE" Enter
    else
        tmux send-keys -t "$SESSION_NAME:main" "python execute_refined_plan.py --full-run --tasks $TASKS --max-cost $MAX_COST 2>&1 | tee -a $LOG_FILE" Enter
    fi
    
    # Create monitoring window
    tmux new-window -t "$SESSION_NAME" -n "monitor"
    tmux send-keys -t "$SESSION_NAME:monitor" "echo '📊 Monitoring Dashboard'" Enter
    tmux send-keys -t "$SESSION_NAME:monitor" "watch -n 30 'echo \"=== AZR Pipeline Status ===\"; echo \"Tasks completed: \$(ls results/ 2>/dev/null | wc -l)\"; echo \"Log file: $LOG_FILE\"; echo \"Last update: \$(date)\"'" Enter
    
    # Create safety tests window
    tmux new-window -t "$SESSION_NAME" -n "safety"
    tmux send-keys -t "$SESSION_NAME:safety" "echo '🛡️  Running Safety Tests in Parallel'" Enter
    tmux send-keys -t "$SESSION_NAME:safety" "python run_harm_suite.py --detailed-breakdown &" Enter
    tmux send-keys -t "$SESSION_NAME:safety" "python test_collusion.py --statistical-analysis &" Enter
    tmux send-keys -t "$SESSION_NAME:safety" "python test_latency.py --scenarios all &" Enter
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