# Setup Guide for Claude API

## Quick Fix Steps

### 1. Set Your API Key

**Option A: Set environment variable (recommended for local development)**
```bash
# On macOS/Linux:
export CLAUDE_API_KEY="sk-your-actual-api-key-here"

# On Windows:
set CLAUDE_API_KEY=sk-your-actual-api-key-here
```

**Option B: Create a .env file (for local development)**
```bash
# Create .env file in project root
echo "CLAUDE_API_KEY=sk-your-actual-api-key-here" > .env
```

**Option C: GitHub Actions (for CI/CD)**
If you've set the API key as a GitHub repository secret:
1. Go to your repository → Settings → Secrets and variables → Actions
2. Add a new repository secret named `CLAUDE_API_KEY`
3. Set the value to your actual API key (starts with `sk-`)
4. The GitHub Actions workflow will automatically use this secret

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Test the Setup

**For Local Development:**
```bash
python verify_setup.py
```

**For GitHub Actions (CI/CD):**
The GitHub Actions workflow automatically runs verification using:
```bash
python verify_github_actions.py
```

## Project Structure

The project has the following structure:
```
oversight_curriculum/
├── oversight/
│   ├── core/                    # Always loaded
│   │   ├── __init__.py
│   │   ├── runner.py           # Main execution engine
│   │   ├── deduction_loop.py   # Core reasoning
│   │   ├── config.py           # Configuration
│   │   ├── metrics.py          # Metrics collection
│   │   ├── errors.py           # Error handling
│   │   └── model.py            # API wrapper
│   ├── features/               # Feature-flagged modules
│   │   ├── __init__.py
│   │   ├── humaneval_integration.py
│   │   ├── hhh_filter.py
│   │   ├── referee.py
│   │   └── red_team_suite.py
│   └── stubs/                  # Stub implementations
│       └── model_stub.py
├── requirements.txt      # Python dependencies
├── verify_setup.py      # Local setup verification script
├── verify_github_actions.py  # GitHub Actions verification script
├── .github/workflows/   # GitHub Actions workflows
└── SETUP_GUIDE.md       # This file
```

## Current Implementation Status

The `oversight/model.py` file includes:

✅ **API Key Validation** - Checks if `CLAUDE_API_KEY` is set
✅ **Correct Response Parsing** - Uses `response.content[0].text`
✅ **Error Handling** - Comprehensive error messages and retry logic
✅ **Anthropic SDK** - Uses the official `anthropic` Python client

## Verification Steps

Run `python verify_setup.py` to check:
1. ✅ API key is set and valid format
2. ✅ Dependencies are installed
3. ✅ Model module can be imported from `oversight/`
4. ✅ API request works with actual Claude API

## GitHub Actions Integration

The project includes GitHub Actions workflows that automatically:
- ✅ Use your `CLAUDE_API_KEY` secret
- ✅ Run tests and QA checks
- ✅ Generate safety reports
- ✅ Create progress dashboards

**Workflow files:**
- `.github/workflows/ci.yml` - Main CI pipeline
- `.github/workflows/evidence.yml` - Evidence collection

## Troubleshooting

### Common Issues

**Import Error: No module named 'model'**
- The model is located at `oversight/model.py`, not `src/model.py`
- The verification script has been updated to use the correct path

**API Key Not Found**
- Make sure you've set the `CLAUDE_API_KEY` environment variable
- Or create a `.env` file in the project root
- For GitHub Actions: Check that the secret is named exactly `CLAUDE_API_KEY`

**API Request Fails**
- Check your API key is valid and has sufficient credits
- Verify network connectivity
- Check for rate limiting

**GitHub Actions Failing**
- Ensure the `CLAUDE_API_KEY` secret is set in repository settings
- Check that the secret name matches exactly (case-sensitive)
- Verify the API key format starts with `sk-`

## Next Steps

Once the verification passes, you can proceed with implementing:
1. The main deduction loop (port from AZR)
2. The referee system
3. Metrics collection
4. Comparison framework

## Development

For development, you can also run individual test files:
```bash
python test_models.py          # Test the model wrapper
python test_api.py            # Test API connectivity
python test_simple.py         # Simple functionality test
```

For GitHub Actions testing:
```bash
# Test the CI workflow locally (if you have act installed)
act push
```

# oversight/core/config.py
import os
from typing import Optional

class FeatureFlags:
    """Feature flag management for oversight curriculum"""

    @staticmethod
    def is_enabled(flag: str) -> bool:
        """Check if a feature flag is enabled"""
        env_var = f"OVERSIGHT_{flag.upper()}"
        return os.getenv(env_var, "false").lower() == "true"

    @staticmethod
    def get_model_mode() -> str:
        """Get model execution mode"""
        if os.getenv("OVERSIGHT_FASTLANE") == "true":
            return "stub"
        return "live"

# Feature flags
HUMANEVAL_ENABLED = FeatureFlags.is_enabled("HUMANEVAL")
HHH_FILTER_ENABLED = FeatureFlags.is_enabled("HHH_FILTER")
RED_TEAM_ENABLED = FeatureFlags.is_enabled("RED_TEAM")
REFEREE_ENABLED = FeatureFlags.is_enabled("REFEREE")

# oversight/core/runner.py
from .config import FeatureFlags

class OversightRunner:
    def __init__(self, config: RunnerConfig):
        self.config = config

        # Conditional feature loading
        if FeatureFlags.HUMANEVAL_ENABLED:
            from ..features.humaneval_integration import AsyncHumanEvalRunner
            self.humaneval_runner = AsyncHumanEvalRunner()

        if FeatureFlags.HHH_FILTER_ENABLED:
            from ..features.hhh_filter import HHHFilter
            self.hhh_filter = HHHFilter()

        if FeatureFlags.REFEREE_ENABLED:
            from ..features.referee import Referee
            self.referee = Referee()

tests/
├── unit/                   # Fast tests (always run)
│   ├── test_deduction_loop.py
│   ├── test_config.py
│   └── test_metrics.py
├── integration/            # Feature tests (conditional)
│   ├── test_humaneval.py
│   ├── test_hhh_filter.py
│   └── test_red_team.py
└── external/              # API-dependent tests
    ├── test_latency.py
    └── test_api.py
