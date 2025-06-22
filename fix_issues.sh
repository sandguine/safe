#!/bin/bash

echo "🔧 Fixing common code quality issues..."

# 1. Format code with Black
echo "📝 Formatting code with Black..."
black . --line-length=79

# 2. Sort imports with isort
echo "📝 Sorting imports with isort..."
isort . --profile=black

# 3. Fix common issues automatically
echo "🔧 Fixing common issues..."

# Fix f-string issues
find . -name "*.py" -not -path "./venv/*" -not -path "./.venv/*" -exec sed -i '' 's/f"\([^}]*\)"/"\1"/g' {} \;

# Fix bare except statements
find . -name "*.py" -not -path "./venv/*" -not -path "./.venv/*" -exec sed -i '' 's/except:/except Exception:/g' {} \;

# 4. Run pre-commit hooks
echo "🔍 Running pre-commit hooks..."
pre-commit run --all-files

# 5. Run flake8 with our configuration
echo "🔍 Running flake8..."
flake8 . --config=.flake8

# 6. Run tests
echo "🧪 Running tests..."
pytest tests/ -v --tb=short

# 7. Validate documentation
echo "📚 Validating documentation..."
python validate_docs.py

echo "✅ Issue fixing complete!"
echo ""
echo "📋 Summary:"
echo "- Code formatted with Black"
echo "- Imports sorted with isort"
echo "- Pre-commit hooks applied"
echo "- Flake8 linting completed"
echo "- Tests run"
echo "- Documentation validated"
echo ""
echo "💡 Next steps:"
echo "1. Review any remaining issues above"
echo "2. Commit the changes: git add . && git commit -m 'Fix code quality issues'"
echo "3. Run: ./check_all.sh (to verify everything is clean)"
