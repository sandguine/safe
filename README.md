# Oversight-Shaped Curriculum  

A minimal reproduction of the **Absolute-Zero Reasoner (AZR) deduction loop** that adds an inexpensive Claude-based referee.  
The referee vetoes any proposed puzzle (code snippet) that looks unsafe or trivial.  
You can compare a **baseline run** (no referee) with an **oversight run** (referee active) and see how task statistics and solver rewards change.

---

## 1. Quick start (one-command demo)

```bash
# Clone and enter the project
git clone https://github.com/your-org/oversight_curriculum.git
cd oversight_curriculum

# Ensure the Anthropic key is available
export CLAUDE_API_KEY="sk-..."    # replace with your real key

# Create and activate a conda environment (Python 3.9)
conda create -n oversight python=3.9 -y
conda activate oversight

# Install dependencies
pip install -r requirements.txt

# Run a 10-cycle baseline and a 10-cycle oversight run, then build plots
bash run_demo.sh
