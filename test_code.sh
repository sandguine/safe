#!/bin/bash
# Run all tests
echo "🧪 Running tests..."

# Run pytest with coverage
pytest tests/ -v --cov=oversight --cov-report=html --cov-report=term

echo "✅ Testing complete!"
