#!/bin/bash
# Lint all code files
echo "🔍 Linting code..."

# Run flake8 with our configuration
flake8 . --config=.flake8

# Run mypy
mypy . --ignore-missing-imports

echo "✅ Code linting complete!"
