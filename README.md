# SAFE: AI Safety Evaluation Framework

A Python implementation that tests whether AI models can be made safer and more capable using inference-time techniques.

## What This Does

This codebase implements a pipeline that:

1. **Generates multiple responses** to coding problems using Claude API
2. **Tests each response** on HumanEval benchmark problems
3. **Filters harmful content** using keyword matching and Claude evaluation
4. **Measures improvements** in code quality and safety

## Core Components

### Main Scripts
- `enhanced_demo.py` - Runs the complete evaluation pipeline
- `evaluate_results.py` - Analyzes and reports results

### Core Modules
- `oversight/model.py` - Claude API wrapper (real and mock modes)
- `oversight/hhh_filter.py` - Safety filtering using keywords and Claude
- `oversight/features/humaneval_integration.py` - Code generation and testing
- `oversight/features/kl_analysis.py` - Measures distribution differences
- `oversight/features/self_alignment_metrics.py` - Calculates joint objectives

## How It Works

### Capability Testing
- Takes HumanEval coding problems
- Generates 1 response (baseline) vs 4 responses (oversight)
- Runs each response in a sandbox to check if it passes tests
- Measures Pass@1 improvement

### Safety Testing  
- Tests 10 harmful prompts (bomb-making, hacking, etc.)
- Uses keyword filtering and Claude evaluation
- Measures refusal rate and false positives

### Analysis
- Calculates KL divergence between baseline and oversight outputs
- Measures joint capability-safety objectives
- Generates reports and visualizations

## Setup

### Option 1: With Claude API Key (Recommended)
```bash
# Install dependencies
pip install -r requirements.txt

# Set Claude API key
export CLAUDE_API_KEY="your-key-here"

# Run demo with real model
python enhanced_demo.py
```

### Option 2: Without API Key (Mock Mode)
```bash
# Install dependencies
pip install -r requirements.txt

# Run demo with mock responses
python enhanced_demo.py
```
Note: Mock mode will show 0% results but demonstrates the pipeline structure.

## Requirements

- Python 3.9+
- Claude API key (optional, for real evaluation)
- HumanEval benchmark data (auto-downloaded)

## Expected Results

### With Claude API Key
- **Capability**: ~25% baseline → ~40% oversight (Pass@1 on HumanEval)
- **Safety**: ~90% harmful prompt refusal rate
- **Analysis**: KL divergence measurements and joint objective scores

### Without API Key (Mock Mode)
- All metrics show 0% or placeholder values
- Demonstrates pipeline structure without real model calls
- Useful for understanding the codebase and testing setup

## Limitations

- Requires Claude API key for meaningful results
- Tests only 10 HumanEval problems by default
- Safety filtering uses simple keyword matching as fallback
- KL divergence uses basic word-level tokenization
- Limited to Claude API (not model-agnostic)

## Files

- `enhanced_demo.py` - Main entry point
- `oversight/` - Core implementation modules
- `tests/` - Basic test coverage
- `results/` - Output directory for results
- `plots/` - Output directory for visualizations

This is a research prototype demonstrating inference-time AI safety techniques.
