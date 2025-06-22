#!/bin/bash
# Format all code files
echo "🔧 Formatting code..."

# Format Python files
black .
isort .

# Format other files
pre-commit run --all-files

echo "✅ Code formatting complete!"
