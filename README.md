# Oversight Curriculum

A reproduction of the Absolute-Zero Reasoner (AZR) deduction loop with Claude-based referee oversight to veto unsafe or trivial puzzles.

## Overview

This project implements a simplified version of the AZR self-play system where:
1. **PROPOSE**: Claude generates reasoning tasks (code snippets)
2. **SOLVE**: Claude attempts to solve self-generated tasks  
3. **Oversight**: Referee system filters unsafe/trivial content
4. **Metrics**: Track performance and learning progress

The system compares baseline performance (no referee) vs oversight performance (with referee) to measure the impact of safety filtering.

## Quick Start

### Prerequisites

1. **API Key**: Create a `.env` file with your Claude API key:
   ```bash
   echo "CLAUDE_API_KEY=your-api-key-here" > .env
   ```
   
   Get your API key from: https://console.anthropic.com/

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Run Complete Experiment

Execute the full oversight curriculum experiment:

```bash
./run_all.sh
```

This will:
- Run baseline experiment (no referee)
- Run oversight experiment (with referee) 
- Generate comparison analysis
- Create visualizations
- Run unit tests

### Individual Components

#### CLI Loop (Optimized for ≤15s execution)

```bash
# Baseline (no referee)
python azr_loop.py --no_ref --cycles 10 --output results/baseline.csv

# Oversight (with referee)
python azr_loop.py --with_ref --cycles 10 --output results/oversight.csv
```

#### Full Demo with Comparison

```bash
python run_demo.py --cycles 10 --puzzles_per_cycle 2 --solutions_per_puzzle 1
```

#### Analysis

```bash
python src/analysis.py --baseline results/baseline.csv --oversight results/oversight.csv
```

#### Unit Tests

```bash
python -m pytest tests/test_deduction_loop.py -v
```

## Configuration

### Hard-coded Puzzle Triplets

The system uses pre-defined puzzle triplets from `configs/deduction_mini.json`:

```json
{
  "puzzles": [
    {
      "id": "puzzle_1",
      "type": "code_i", 
      "content": "def add_numbers(a, b): return a + b",
      "input": "add_numbers(5, 3)",
      "output": "8"
    }
  ]
}
```

### CLI Options

- `--with_ref` / `--no_ref`: Enable/disable referee oversight
- `--cycles`: Number of deduction cycles (default: 10)
- `--config`: Use hard-coded config puzzles (default: True)
- `--output`: Output CSV file path
- `--skip_plots`: Skip plot generation for faster execution

## Architecture

### Core Components

- **`src/deduction_loop.py`**: Main AZR loop implementation
- **`src/referee.py`**: Claude-based safety referee
- **`src/metrics.py`**: Metrics collection and comparison
- **`src/model.py`**: Claude API wrapper
- **`src/analysis.py`**: CSV analysis and visualization

### Data Flow

1. **Puzzle Generation**: Claude generates code puzzles
2. **Referee Evaluation**: Safety and quality assessment
3. **Solution Generation**: Claude solves approved puzzles
4. **Metrics Collection**: Track performance metrics
5. **Comparison Analysis**: Baseline vs oversight comparison

## Output Files

The system generates several output files in the `results/` directory:

- `baseline_demo.csv`: Baseline experiment results
- `oversight_demo.csv`: Oversight experiment results  
- `comparison_plot.png`: Visual comparison
- `baseline_metrics.json`: Detailed baseline metrics
- `oversight_metrics.json`: Detailed oversight metrics
- `comparison_report.txt`: Text comparison report
- `combined_results.json`: All results combined

### CSV Format

The CSV files contain the following columns:
- `task_id`: Cycle identifier
- `code_len`: Approximate code length
- `banned_import`: Number of banned imports (tracked)
- `solver_reward`: Average solution reward
- `referee_veto`: Number of puzzles vetoed

## Metrics

The system tracks several key metrics:

- **Approval Rate**: Percentage of puzzles approved by referee
- **Success Rate**: Percentage of solutions that are correct
- **Average Reward**: Mean solution quality score
- **Safety Score**: Average puzzle safety rating
- **Veto Rate**: Percentage of cycles with vetoed content

## Performance Optimization

The system is optimized for ≤15s execution time:

- Reduced puzzles per cycle (2 instead of 8)
- Reduced solutions per puzzle (1 instead of 3)
- Use of hard-coded config puzzles
- Optional plot skipping
- Minimal API calls

## Research Applications

This system enables research on:

1. **Safety Filtering**: Impact of referee oversight on content quality
2. **Learning Curves**: How oversight affects learning over time
3. **Trade-offs**: Safety vs performance trade-offs
4. **Curriculum Design**: Optimal puzzle selection strategies

## Development

### Running Tests

```bash
python -m pytest tests/ -v
```

### Adding New Puzzle Types

1. Add puzzle type to `deduction_loop.py`
2. Create corresponding prompt templates
3. Update referee evaluation criteria
4. Add test cases

### Extending Metrics

1. Add new metrics to `MetricsCollector`
2. Update CSV export format
3. Modify analysis scripts
4. Update visualization code

## Troubleshooting

### Common Issues

1. **API Key Not Set**: Ensure `.env` file exists with `CLAUDE_API_KEY=your-key-here`
2. **Slow Execution**: Reduce cycles or puzzles per cycle
3. **Import Errors**: Install all dependencies with `pip install -r requirements.txt`
4. **Plot Errors**: Install matplotlib or use `--skip_plots` flag

### Performance Tips

- Use `--skip_plots` for faster execution
- Reduce `--cycles` for quick testing
- Use `--puzzles_per_cycle 1` for minimal execution
- Ensure stable internet connection for API calls

## License

This project is for research purposes. Please ensure compliance with Anthropic's API terms of service.

## Citation

If you use this code in your research, please cite:

```bibtex
@misc{oversight_curriculum_2024,
  title={Oversight Curriculum: AZR Deduction Loop with Claude Referee},
  author={Your Name},
  year={2024},
  url={https://github.com/your-repo/oversight-curriculum}
}
```
