# News Sentiment Crawler - Virtual Environment Setup

This document explains how to properly set up and run the News Sentiment Crawler in a virtual environment to avoid Python packaging conflicts.

## Quick Setup

1. **Run the setup script** (recommended):
   ```bash
   ./setup.sh
   ```

2. **Run the crawler**:
   ```bash
   ./run_crawler.sh
   ```

## Manual Setup

If you prefer to set up manually:

1. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   ```

2. **Activate virtual environment**:
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the crawler**:
   ```bash
   python NewsSentimentCrawler.py
   ```

## Usage Examples

### Run daily news analysis:
```bash
./run_crawler.sh
```

### Collect historical data:
```bash
./run_crawler.sh --collect-historical --start-date 2025-01-01 --end-date 2025-01-31
```

### Manual activation for development:
```bash
source venv/bin/activate
python NewsSentimentCrawler.py --help
```

## Troubleshooting

### PEP 668 Error
If you see the error about "externally-managed-environment", this is because macOS prevents installing packages system-wide. The virtual environment approach (above) solves this issue.

### Missing Packages
If you get import errors, make sure you're in the virtual environment:
```bash
source venv/bin/activate
pip list  # Check installed packages
```

### Python Version
This project requires Python 3.7+. Check your version:
```bash
python3 --version
```

## Project Structure
```
DailyShare/
├── venv/                          # Virtual environment (created by setup)
├── NewsSentimentCrawler.py       # Main crawler script
├── NewsSentimentCrawler.yaml     # Configuration file
├── requirements.txt              # Python dependencies
├── setup.sh                      # Setup script
├── run_crawler.sh               # Convenient runner script
└── data/                        # Output directory
```

## Dependencies
- selenium (web scraping)
- webdriver-manager (Chrome driver management)
- beautifulsoup4 (HTML parsing)
- pyyaml (configuration files)
- gitpython (Git operations)
- requests (HTTP requests)
- transformers (FinBERT sentiment analysis)
- torch (PyTorch for transformers)
- yfinance (stock data)
