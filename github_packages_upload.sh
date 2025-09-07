#!/bin/bash

# 🚀 ScanHero GitHub Packages Upload Script
# This script helps you upload ScanHero to GitHub Packages

echo "📦 ScanHero GitHub Packages Upload Script"
echo "=========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run: python3 -m venv venv"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if twine is installed
if ! command -v twine &> /dev/null; then
    echo "📦 Installing twine..."
    pip install twine
fi

# Check if packages exist
if [ ! -f "dist/scanhero-1.0.0-py3-none-any.whl" ]; then
    echo "❌ Package files not found. Please run: python -m build"
    exit 1
fi

echo "✅ Package files found:"
ls -la dist/scanhero-1.0.0*

echo ""
echo "🔑 To upload to GitHub Packages, you need a GitHub token:"
echo "1. Go to https://github.com/settings/tokens"
echo "2. Click 'Generate new token (classic)'"
echo "3. Select scopes: 'write:packages' and 'read:packages'"
echo "4. Copy the token (starts with ghp_)"
echo ""

# Prompt for token
read -p "Enter your GitHub token (starts with ghp_): " GITHUB_TOKEN

if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ No token provided. Exiting."
    exit 1
fi

echo ""
echo "🚀 Uploading to GitHub Packages..."

# For GitHub Packages, we need to use a different approach
# GitHub Packages for Python uses PyPI-compatible API
# The correct repository URL for GitHub Packages is organization-specific

echo "📝 Note: GitHub Packages for Python requires organization-specific setup."
echo "For your repository 'ahmetxhero/scanhero', the upload URL should be:"
echo "https://upload.pypi.org/legacy/"

# Try upload with GitHub token
twine upload --repository-url https://upload.pypi.org/legacy/ --username __token__ --password "$GITHUB_TOKEN" dist/scanhero-1.0.0*

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 SUCCESS! ScanHero has been uploaded to GitHub Packages!"
    echo ""
    echo "📦 Users can now install ScanHero with:"
    echo "   pip install --index-url https://pypi.pkg.github.com/ahmetxhero/simple/ scanhero"
    echo ""
    echo "🧪 Test the installation:"
    echo "   pip install --index-url https://pypi.pkg.github.com/ahmetxhero/simple/ scanhero"
    echo "   scanhero --version"
    echo ""
    echo "🌐 Check your package at:"
    echo "   https://github.com/ahmetxhero/scanhero/packages"
else
    echo ""
    echo "❌ Upload failed. This might be because:"
    echo "   1. GitHub Packages requires organization setup"
    echo "   2. Token doesn't have correct permissions"
    echo "   3. Repository needs to be configured for packages"
    echo ""
    echo "💡 Alternative: Use PyPI instead:"
    echo "   ./upload_to_pypi.sh"
fi
