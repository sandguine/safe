# SAFE MVP Demo

A minimal demonstration of inference-time AI safety and capability improvements using:
- **Best-of-N sampling** for code generation quality improvement
- **Keyword-based filtering** for harmful prompt refusal

## What This Demo Shows

- **Capability improvement**: Best-of-N sampling (selecting the best of 4 generations) can improve pass@1 scores on coding tasks compared to single-sample generation
- **Safety filtering**: A simple keyword-based filter can reliably refuse obviously harmful prompts
- **Zero training required**: All improvements are achieved through inference-time techniques only

## Quick Start

### Prerequisites
- Python 3.7+
- Claude API key (optional - demo works with mock responses)

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set API key (optional)
export CLAUDE_API_KEY='your-api-key-here'
```

### Run Demo
```bash
# Execute complete demo
./demo.sh
```

## What Happens

The demo performs these steps:
1. Generates 5 sample harmful prompts
2. Tests capability baseline (1 sample per problem)
3. Tests capability with oversight (4 samples per problem)
4. Tests safety filtering on harmful prompts
5. Generates summary results

## Expected Results

### Capability Results
- **Baseline pass@1**: ~10-20% (with API key) / 0% (without API key)
- **Oversight pass@1**: ~25-40% (with API key) / 0% (without API key)
- **Improvement**: +0.15 (with API key) / 0.0 (without API key)

**Note**: Without a Claude API key, mock responses are used and pass@1 will be 0%.

### Safety Results
- **Harmful prompts refused**: 5/5
- **Refusal rate**: 100%
- **Harm slip-rate**: 0.0

**Note**: This demo tests only harmful prompts. Comprehensive safety evaluation would test both harmful and safe content.

## Manual Commands

### Capability Testing
```bash
# Baseline: 1 sample per problem
python -m oversight.features.humaneval_integration \
  --mode baseline \
  --problems 5 \
  --samples-per-problem 1 \
  --output demo/baseline.json

# Oversight: 4 samples per problem
python -m oversight.features.humaneval_integration \
  --mode oversight \
  --problems 5 \
  --samples-per-problem 4 \
  --hhh-filter stub_safe \
  --output demo/oversight.json
```

### Safety Testing
```bash
# Generate harmful prompts
python -m oversight.features.red_team_suite --generate-prompts

# Test safety filtering
python -m oversight.features.red_team_suite \
  --prompts demo/harm_prompts.json \
  --hhh-filter keyword_ban \
  --output demo/safety.json
```

## Technical Details

### Capability Improvement
- **Best-of-N sampling**: Generates multiple solutions and selects the best
- **Progressive sampling**: Starts with 4 samples, adds more if needed
- **Pass@1 metric**: Standard measure of code generation quality
- **HumanEval dataset**: 5 problems from the HumanEval-164 benchmark

### Safety Filtering
- **Keyword-based filtering**: Simple pattern matching for harmful content
- **Harmful keywords**: bomb, kill, hack, steal, delete, virus
- **Refusal mechanism**: Returns refusal reason when harmful content detected
- **Test prompts**: 5 obviously harmful prompts for demonstration

## Output Files

### Demo Results
- `demo/baseline.json` - Baseline capability results
- `demo/oversight.json` - Oversight capability results
- `demo/safety.json` - Safety filtering results
- `demo/harm_prompts.json` - Sample harmful prompts

### Analysis Reports
- `evaluation_report_*.txt` - Comprehensive analysis report
- `evaluation_data_*.json` - Structured data for further analysis

### Run Analysis
```bash
# Analyze existing results
python evaluate_results.py
```

## Time and Cost

- **Time**: ~30 seconds (without API key) / ~3-5 minutes (with API key)
- **Cost**: $0.00 (without API key) / ~$0.50 (with Claude API)
- **Dependencies**: Python, internet connection

## Limitations

- **Small scale**: Only 5 HumanEval problems (vs. full 164)
- **Simple safety**: Basic keyword filtering (vs. sophisticated HHH evaluation)
- **Limited scope**: Safety demo only tests harmful prompts
- **Mock responses**: Without API key, uses placeholder responses

## Next Steps

For production use, consider:
1. **Full HumanEval set**: Test on all 164 problems
2. **Real HHH filter**: Replace keyword matching with Claude-based evaluation
3. **Comprehensive safety**: Test both harmful and safe content
4. **Scale up**: Increase sample sizes and problem count
5. **Iterative oversight**: Implement multi-round self-evaluation

## Troubleshooting

### API Key Issues
```bash
export CLAUDE_API_KEY='your-api-key-here'
```

**Note**: Demo works without API key but uses mock responses.

### Missing Dependencies
```bash
pip install -r requirements.txt
```

### Permission Issues
```bash
chmod +x demo.sh
```

### Import Errors
```bash
# Check Python version
python --version

# Verify dependencies
python -c "import anthropic, human_eval; print('Dependencies OK')"
```

## Files

- `oversight/features/humaneval_integration.py` - Capability testing
- `oversight/features/red_team_suite.py` - Safety testing
- `oversight/model.py` - Claude API wrapper
- `oversight/hhh_filter.py` - Safety filter implementation
- `demo.sh` - Demo execution script
- `evaluate_results.py` - Results analysis
- `requirements.txt` - Dependencies
