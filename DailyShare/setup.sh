#!/bin/bash

# Setup script for News Sentiment Crawler
# This script creates a virtual environment and installs all dependencies

echo "Setting up News Sentiment Crawler environment..."

cd "$(dirname "$0")"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install requirements
if [ -f "requirements.txt" ]; then
    echo "Installing Python packages from requirements.txt..."
    pip install -r requirements.txt
else
    echo "Warning: requirements.txt not found. Installing basic packages..."
    pip install selenium webdriver-manager beautifulsoup4 pyyaml gitpython requests transformers torch yfinance
fi

echo "Setup complete!"
echo ""
echo "To run the crawler:"
echo "  ./run_crawler.sh"
echo ""
echo "To run with historical data collection:"
echo "  ./run_crawler.sh --collect-historical --start-date 2025-01-01 --end-date 2025-01-31"
echo ""
echo "To manually activate the environment:"
echo "  source venv/bin/activate"
