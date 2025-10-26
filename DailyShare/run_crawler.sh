#!/bin/bash

# News Sentiment Crawler Runner Script
# This script activates the virtual environment and runs the crawler

cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if configuration file exists
if [ ! -f "NewsSentimentCrawler.yaml" ]; then
    echo "Configuration file 'NewsSentimentCrawler.yaml' not found."
    exit 1
fi

# Run the crawler with any passed arguments
python NewsSentimentCrawler.py "$@"

# Deactivate virtual environment
deactivate
