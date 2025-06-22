#!/bin/bash
# Package oversight artifacts for review

echo "📦 Packaging oversight curriculum artifacts..."

# Check if artifacts directory exists
if [ ! -d "oversight_artifacts" ]; then
    echo "❌ oversight_artifacts/ directory not found!"
    echo "Run 'python generate_artifacts.py' first to create artifacts."
    exit 1
fi

# Create timestamp for the zip file
TIMESTAMP=$(date +"%Y%m%d_%H%M")
ZIP_NAME="oversight_artifacts_${TIMESTAMP}.zip"

# Zip the artifacts directory
echo "📁 Creating ${ZIP_NAME}..."
zip -r "${ZIP_NAME}" oversight_artifacts/

if [ $? -eq 0 ]; then
    echo "✅ Successfully created ${ZIP_NAME}"
    echo "📊 File size: $(du -h "${ZIP_NAME}" | cut -f1)"
    echo ""
    echo "🚀 Ready to share! You can:"
    echo "   • Upload to GitHub/GitLab as a release"
    echo "   • Share via Dropbox, Google Drive, or WeTransfer"
    echo "   • Send via email (if under size limit)"
    echo ""
    echo "📋 Contents:"
    ls -la oversight_artifacts/
else
    echo "❌ Failed to create zip file"
    exit 1
fi 