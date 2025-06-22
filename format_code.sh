#!/bin/bash
# Format and lint code to ensure flake8 compliance

set -e

echo "🔧 Formatting and linting code..."

# Run Black to format code
echo "📝 Running Black formatter..."
black . --line-length=79

# Run isort to sort imports
echo "📦 Sorting imports..."
isort . --profile=black --line-length=79

# Run flake8 to check for issues
echo "🔍 Running flake8 linting..."
flake8 . --max-line-length=79 --ignore=E203,W503

echo "✅ Code formatting and linting complete!"
echo "💡 Tip: Your VSCode is now configured to show a ruler at 79 characters"
echo "💡 Tip: Pre-commit hooks will automatically run these checks on commit"
