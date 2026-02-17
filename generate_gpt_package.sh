#!/bin/bash

# Quick script to generate GPT ZIP package
# Usage: ./generate_gpt_package.sh

set -e

echo "=========================================="
echo "GPT Configuration Package Generator"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "create_gpt_zip_package.py" ]; then
    echo "❌ Error: create_gpt_zip_package.py not found"
    echo "Please run this script from the repository root directory"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found"
    echo "Please install Python 3.7 or later"
    exit 1
fi

# Run the ZIP packager
echo "🚀 Running ZIP package generator..."
echo ""
python3 create_gpt_zip_package.py

# Check if successful
if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ SUCCESS!"
    echo "=========================================="
    echo ""
    echo "Your ZIP package is ready in:"
    echo "  GPT_Complete_Package/"
    echo ""
    echo "Next steps:"
    echo "  1. Extract the ZIP file"
    echo "  2. Read README.txt for instructions"
    echo "  3. Deploy to OpenAI GPT Builder"
    echo ""
    echo "For help, see: GPT_ZIP_PACKAGE_GUIDE.md"
    echo ""
else
    echo ""
    echo "❌ Package generation failed"
    echo "Check the error messages above"
    exit 1
fi
