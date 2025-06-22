#!/bin/bash
# Release script for oversight-curriculum package

set -e  # Exit on any error

echo "🚀 OVERSIGHT CURRICULUM RELEASE SCRIPT"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    print_error "pyproject.toml not found. Please run this script from the project root."
    exit 1
fi

print_status "Starting release process..."

# Step 1: Clean working directory
print_status "Step 1: Cleaning working directory..."
git clean -xfd
print_success "Working directory cleaned"

# Step 2: Run smoke test
print_status "Step 2: Running smoke test..."
python scripts/release_smoke_test.py
if [ $? -ne 0 ]; then
    print_error "Smoke test failed. Please fix issues before releasing."
    exit 1
fi
print_success "Smoke test passed"

# Step 3: Build package
print_status "Step 3: Building package..."
python -m build
print_success "Package built successfully"

# Step 4: Check package with twine
print_status "Step 4: Validating package with twine..."
if command -v twine &> /dev/null; then
    twine check dist/*
    print_success "Package validation passed"
else
    print_warning "twine not found. Install with: pip install twine"
fi

# Step 5: Show build artifacts
print_status "Step 5: Build artifacts:"
ls -la dist/

# Step 6: Ask for confirmation
echo ""
print_status "Package is ready for release!"
echo ""
echo "Next steps:"
echo "1. Review the build artifacts above"
echo "2. Create git tag: git tag v1.0.0"
echo "3. Push tag: git push origin v1.0.0"
echo "4. Upload to PyPI: twine upload dist/*"
echo ""
read -p "Do you want to proceed with creating the git tag? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Creating git tag v1.0.0..."
    git tag v1.0.0
    print_success "Git tag created"
    
    read -p "Do you want to push the tag to remote? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Pushing tag to remote..."
        git push origin v1.0.0
        print_success "Tag pushed to remote"
    fi
    
    read -p "Do you want to upload to PyPI? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Uploading to PyPI..."
        twine upload dist/*
        print_success "Package uploaded to PyPI!"
        echo ""
        print_success "🎉 Release completed successfully!"
        print_success "Package is now available on PyPI: https://pypi.org/project/oversight-curriculum/"
    else
        print_warning "Skipping PyPI upload. You can upload manually with: twine upload dist/*"
    fi
else
    print_warning "Release cancelled. You can manually create the tag and upload when ready."
fi

print_success "Release script completed!" 