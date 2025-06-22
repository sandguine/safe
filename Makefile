.PHONY: dev-pytest test humaneval harm-suite demo clean evidence quick-humaneval help qr

# Show all available targets with descriptions
help:
	@echo "Available targets:"
	@echo ""
	@echo "## Development & Testing"
	@echo "  dev-pytest     - Run tests without API key (stub mode)"
	@echo "  test           - Run full test suite (requires API key)"
	@echo "  check          - Run all checks (dev-pytest + pre-commit)"
	@echo ""
	@echo "## Evidence Generation"
	@echo "  quick-humaneval - Quick HumanEval validation (2 cycles)"
	@echo "  humaneval      - Full HumanEval evaluation (10 cycles)"
	@echo "  harm-suite     - Run harm suite testing"
	@echo "  demo           - Run demo mode"
	@echo "  evidence       - Generate all evidence artifacts"
	@echo ""
	@echo "## Validation & Debugging"
	@echo "  validate-sandbox - Test platform-specific resource limits"
	@echo ""
	@echo "## Documentation"
	@echo "  qr             - Generate QR code for evidence dashboard"
	@echo ""
	@echo "## Maintenance"
	@echo "  clean          - Clean up artifacts and build files"
	@echo "  install-dev    - Install development dependencies"

# Development testing (no API key required)
dev-pytest:
	CLAUDE_API_KEY=dummy pytest -m "not external" -v

# Full testing (requires API key)
test:
	pytest -v

# Quick HumanEval validation (5 samples to verify sandbox fix)
quick-humaneval:
	CLAUDE_API_KEY=dummy python -m oversight run --mode demo --cycles 2

# Run HumanEval evaluation (full)
humaneval:
	python -m oversight run --mode robust --cycles 10

# Run harm suite
harm-suite:
	python run_harm_suite.py

# Run demo
demo:
	python -m oversight run --mode demo

# Generate all evidence artifacts
evidence: humaneval harm-suite demo
	@echo "Evidence generation complete"

# Generate QR code for evidence dashboard
qr:
	python scripts/generate_qr.py

# Clean up artifacts
clean:
	rm -rf results/*.json results/*.csv
	rm -rf coverage.xml htmlcov/
	rm -rf dist/ build/ *.egg-info/

# Install development dependencies
install-dev:
	pip install -e ".[dev]"
	pre-commit install

# Run all checks
check: dev-pytest
	pre-commit run --all-files

# Validate sandbox fix locally
validate-sandbox:
	python tools/smoke_humaneval.py

# ... rest of the file remains unchanged ...
