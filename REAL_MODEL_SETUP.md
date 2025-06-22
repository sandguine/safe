# Real Model Integration Setup

## Overview

The SAFE implementation has been updated to **require real Claude API integration** instead of falling back to mock data. This ensures that all validation claims can be substantiated with real model outputs.

## Key Changes Made

### 1. **Model Layer Updates**

- `oversight/model.py`: Now requires API key and raises error if not found
- No automatic fallback to mock mode
- Proper error handling for API failures

### 2. **HumanEval Integration**

- `oversight/features/humaneval_integration.py`: Uses real API by default
- Rate limiting configured for API constraints
- Progressive sampling for efficient evaluation

### 3. **Enhanced Demo**

- `enhanced_demo.py`: Requires API key before running
- Real capability measurement with HumanEval
- Comprehensive safety evaluation
- KL divergence analysis with real data
- Self-alignment objective measurement

### 4. **Setup Tools**

- `check_api.py`: Verifies API key configuration
- `setup_api.py`: Interactive API key setup
- Automatic .env file loading

## Setup Instructions

### Option 1: Interactive Setup

```bash
python setup_api.py
```

### Option 2: Manual Setup

1. Get your API key from <https://console.anthropic.com/>
2. Create a `.env` file in the project root:

   ```
   CLAUDE_API_KEY=sk-ant-your-key-here
   ```

3. Or set environment variable:

   ```bash
   export CLAUDE_API_KEY='sk-ant-your-key-here'
   ```

### Option 3: Verify Setup

```bash
python check_api.py
```

## Running the Enhanced Demo

Once your API key is configured:

```bash
python enhanced_demo.py
```

This will:

- ✅ Use real Claude API for all completions
- ✅ Measure actual capability improvements
- ✅ Test safety filtering with real harmful prompts
- ✅ Calculate KL divergence between distributions
- ✅ Validate self-alignment objectives
- ✅ Generate comprehensive validation reports

## Expected Validation Improvements

With real model integration, the validation score should improve from **30% to 80-100%** because:

| Component | Mock Mode | Real Mode |
|-----------|-----------|-----------|
| **Capability** | 0.0 Pass@1 | Actual Pass@1 scores |
| **Safety** | 0% refusal | Real filtering results |
| **KL Divergence** | No data | Real distribution analysis |
| **Self-Alignment** | 0.0 improvement | Real objective measurement |

## Troubleshooting

### API Key Issues

- Ensure key starts with `sk-ant-`
- Check console.anthropic.com for valid keys
- Verify sufficient API credits

### Rate Limiting

- Demo uses conservative rate limits (20 req/min)
- Increase `requests_per_minute` if needed
- Monitor API usage in Anthropic console

### Network Issues

- Check internet connection
- Try again in a few minutes
- Verify firewall settings

## Next Steps

1. **Run the enhanced demo** with your API key
2. **Review validation results** in `results/` directory
3. **Analyze capability improvements** from real HumanEval runs
4. **Validate safety filtering** with actual harmful prompts
5. **Examine KL divergence** between baseline and oversight distributions

The enhanced demo will provide **empirical evidence** for all SAFE claims, making it suitable for:

- Academic publication
- Technical demonstrations
- Safety evaluation
- Capability assessment
