#!/bin/bash

# 🚀 ScanHero PyPI Upload Script
# This script helps you upload ScanHero to PyPI

echo "🎯 ScanHero PyPI Upload Script"
echo "=============================="

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
echo "🔑 To upload to PyPI, you need an API token:"
echo "1. Go to https://pypi.org/manage/account/"
echo "2. Create an API token"
echo "3. Copy the token"
echo ""

# Prompt for token
read -p "Enter your PyPI API token (starts with pypi-): " PYPI_TOKEN

if [ -z "$PYPI_TOKEN" ]; then
    echo "❌ No token provided. Exiting."
    exit 1
fi

echo ""
echo "🚀 Uploading to PyPI..."

# Upload to PyPI
twine upload --username __token__ --password "$PYPI_TOKEN" dist/scanhero-1.0.0*

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 SUCCESS! ScanHero has been uploaded to PyPI!"
    echo ""
    echo "📦 Users can now install ScanHero with:"
    echo "   pip install scanhero"
    echo ""
    echo "🧪 Test the installation:"
    echo "   pip install scanhero"
    echo "   scanhero --version"
    echo "   scanhero scan 127.0.0.1 --ports 80,443,22"
    echo ""
    echo "🌐 Check your package at:"
    echo "   https://pypi.org/project/scanhero/"
else
    echo ""
    echo "❌ Upload failed. Please check your token and try again."
    echo ""
    echo "🔍 Common issues:"
    echo "   - Invalid API token"
    echo "   - Package name already exists"
    echo "   - Network connection issues"
fi
