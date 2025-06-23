#!/bin/bash
# Setup script for automatic linting and formatting

echo "🔧 Setting up automatic linting and formatting..."
echo "================================================"

# Install pre-commit if not already installed
if ! command -v pre-commit &> /dev/null; then
    echo "📦 Installing pre-commit..."
    pip install pre-commit
else
    echo "✅ pre-commit already installed"
fi

# Install required tools
echo "📦 Installing linting tools..."
pip install black flake8 isort

# Install pre-commit hooks
echo "🔗 Installing pre-commit hooks..."
pre-commit install

# Run pre-commit on all files to fix existing issues
echo "🔧 Running pre-commit on all files..."
pre-commit run --all-files

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 What this setup does:"
echo "   • Automatically formats code with Black (79 char line length)"
echo "   • Sorts imports with isort"
echo "   • Checks for linting errors with flake8"
echo "   • Runs before every commit"
echo ""
echo "🚀 Usage:"
echo "   • Just commit normally - hooks run automatically"
echo "   • Run manually: pre-commit run --all-files"
echo "   • Skip hooks: git commit --no-verify"
echo ""
echo "✅ Your code will now be automatically formatted and linted!"
