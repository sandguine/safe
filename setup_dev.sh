#!/bin/bash
# Setup development environment
echo "🔧 Setting up development environment..."

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development tools
pip install black flake8 isort mypy pytest pytest-cov pre-commit

# Setup pre-commit
pre-commit install

# Setup automation
python setup_automation.py

echo "✅ Development environment setup complete!"
