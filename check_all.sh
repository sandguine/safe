#!/bin/bash
# Run all quality checks
echo "🔍 Running all quality checks..."

# Format code
./format_code.sh

# Lint code
./lint_code.sh

# Run tests
./test_code.sh

# Validate documentation
python validate_docs.py

echo "✅ All quality checks complete!"
