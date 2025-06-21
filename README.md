# Oversight-Shaped Curriculum  

A minimal reproduction of the **Absolute-Zero Reasoner (AZR) deduction loop** that adds an inexpensive Claude-based referee.  
The referee vetoes any proposed puzzle (code snippet) that looks unsafe or trivial.  
You can compare a **baseline run** (no referee) with an **oversight run** (referee active) and see how task statistics and solver rewards change.

## 🎯 What's New

✅ **Complete AZR Deduction Loop** - Ported and simplified from the original AZR project  
✅ **Claude-based Referee System** - Evaluates puzzles for safety, quality, and triviality  
✅ **Comprehensive Metrics Framework** - Tracks performance and learning progress  
✅ **Baseline vs Oversight Comparison** - Analyzes the impact of oversight on learning  
✅ **End-to-End Demo Script** - Complete experiment runner with visualization  

## 🚀 Quick Start

### 1. Setup

```bash
# Clone and enter the project
git clone https://github.com/your-org/oversight_curriculum.git
cd oversight_curriculum

# Set your Anthropic API key
export CLAUDE_API_KEY="sk-..."    # replace with your real key

# Install dependencies
pip install -r requirements.txt

# Verify setup
python verify_setup.py
```

### 2. Run the Demo

```bash
# Run complete baseline vs oversight experiment
python run_demo.py

# Or run a quick test
python test_deduction_loop.py
```

### 3. View Results

Check the `results/` directory for:
- `baseline_metrics.json` - Baseline run statistics
- `oversight_metrics.json` - Oversight run statistics  
- `comparison_report.txt` - Human-readable comparison
- `learning_curves.png` - Learning progress visualization
- `combined_results.json` - All data in one file

## 📊 How It Works

### The Deduction Loop

The system implements the core AZR self-play mechanism:

1. **PROPOSE Phase**: Claude generates programming puzzles (code_i, code_o, code_e, code_f)
2. **SOLVE Phase**: Claude attempts to solve the self-generated puzzles
3. **Oversight**: Referee evaluates and filters unsafe/trivial content
4. **Learning**: System improves through both generation and solving

### The Referee System

The Claude-based referee evaluates each puzzle on:

- **Safety** (0-10): No harmful code, security vulnerabilities, or inappropriate content
- **Quality** (0-10): Educational value, appropriate complexity, clear problem statement  
- **Triviality** (0-10): Not too simple or obvious, requires some thought

Puzzles are approved only if they meet minimum thresholds on all criteria.

### Metrics & Comparison

The system tracks:
- **Puzzle Generation**: Number generated, approved, rejected
- **Solution Quality**: Success rate, average rewards
- **Safety Scores**: Average puzzle safety ratings
- **Learning Progress**: Performance over time

## 🏗️ Architecture

```
src/
├── model.py              # Claude API wrapper with caching
├── deduction_loop.py     # Core AZR self-play implementation
├── referee.py           # Safety and quality evaluation system
└── metrics.py           # Performance tracking and comparison

run_demo.py              # Main experiment runner
test_deduction_loop.py   # Simple testing script
```

## 🔧 Configuration

Key parameters in `run_demo.py`:

```python
cycles = 10                    # Number of deduction cycles per experiment
max_puzzles_per_cycle = 8      # Puzzles generated per cycle
max_solutions_per_puzzle = 2   # Solutions attempted per puzzle
model_name = "claude-3-5-sonnet-20241022"  # Claude model to use
```

## 📈 Example Output

```
=== OVERSIGHT CURRICULUM COMPARISON REPORT ===

BASELINE RUN:
  Total cycles: 10
  Approval rate: 100.00%
  Success rate: 75.00%
  Avg reward: 0.234
  Avg safety: 0.500

OVERSIGHT RUN:
  Total cycles: 10
  Approval rate: 65.00%
  Success rate: 85.00%
  Avg reward: 0.312
  Avg safety: 0.823

CHANGES WITH OVERSIGHT:
  Reward: +0.078 (+33.3%)
  Safety: +0.323 (+64.6%)
  Approval rate: -35.00% (-35.0%)
  Success rate: +10.00% (+13.3%)

OVERSIGHT IMPACT:
  Metrics improved: 3/4
  ✓ Reward improved
  ✓ Safety improved
  ✓ Success rate improved
```

## 🎓 Research Applications

This implementation enables research on:

- **AI Safety**: How oversight affects content generation
- **Curriculum Learning**: Impact of filtering on learning dynamics
- **Self-Play Systems**: Balancing exploration vs. safety in self-improving AI
- **Evaluation Methods**: Comparing baseline vs. oversight approaches

## 🔬 Extending the System

### Adding New Puzzle Types

Extend `deduction_loop.py` with new puzzle types:

```python
def _create_math_prompt(self) -> str:
    return "Generate a mathematical problem..."

def _create_math_solve_prompt(self, puzzle_content: str) -> str:
    return f"Solve this math problem: {puzzle_content}"
```

### Customizing the Referee

Modify `referee.py` to add new evaluation criteria:

```python
safety_criteria = SafetyCriteria(
    banned_keywords=['your_keywords'],
    banned_patterns=[r'your_patterns'],
    min_complexity=0.2,
    max_complexity=0.8,
    require_educational_value=True
)
```

### Advanced Metrics

Extend `metrics.py` to track additional metrics:

```python
def custom_metric(self, data):
    # Your custom analysis
    return result
```

## 📚 References

- **Absolute-Zero Reasoner**: [Paper](https://arxiv.org/abs/2505.03335) | [Code](https://github.com/LeapLabTHU/Absolute-Zero-Reasoner)
- **Self-Play Learning**: [AlphaGo Zero](https://www.nature.com/articles/nature24270)
- **AI Safety**: [Constitutional AI](https://arxiv.org/abs/2212.08073)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
