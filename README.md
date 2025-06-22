# SAFE MVP Demo

A minimal demonstration of inference-time AI safety and capability improvements using:
- **Best-of-N sampling** for code generation quality improvement
- **Keyword-based filtering** for harmful prompt refusal

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key (optional - demo works with mock responses)
export CLAUDE_API_KEY='your-api-key-here'

# Run demo
./demo.sh
```

## What This Shows

- **Capability improvement**: Best-of-N sampling improves pass@1 scores on coding tasks
- **Safety filtering**: Keyword-based filter refuses harmful prompts
- **Zero training required**: All improvements achieved through inference-time techniques

## Expected Results

- **Capability**: ~10-20% baseline → ~25-40% with oversight (with API key)
- **Safety**: 5/5 harmful prompts correctly refused
- **Time**: ~30 seconds (no API) / ~3-5 minutes (with API)

## Documentation

- **[MVP_DEMO.md](MVP_DEMO.md)** - Detailed guide with manual commands and technical details
- **[demo.sh](demo.sh)** - Automated demo script
- **[evaluate_results.py](evaluate_results.py)** - Results analysis

## Validation

- **[validate_docs.py](validate_docs.py)** - Automated documentation validation
- **[check_docs.sh](check_docs.sh)** - Quick documentation check script
- **[.pre-commit-config.yaml](.pre-commit-config.yaml)** - Pre-commit hooks for validation

Run validation:
```bash
# Quick check
./check_docs.sh

# Detailed validation
python validate_docs.py
```

## Files

- `oversight/features/humaneval_integration.py` - Capability testing
- `oversight/features/red_team_suite.py` - Safety testing
- `oversight/model.py` - Claude API wrapper
- `oversight/hhh_filter.py` - Safety filter implementation
- `demo.sh` - Demo execution script
- `evaluate_results.py` - Results analysis
- `requirements.txt` - Dependencies

## Troubleshooting

```bash
# Missing dependencies
pip install -r requirements.txt

# Permission issues
chmod +x demo.sh

# Verify setup
python -c "import anthropic, human_eval; print('Dependencies OK')"
```

**Note**: Demo works without API key but uses mock responses (0% pass rates).
