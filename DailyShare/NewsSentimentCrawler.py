from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from transformers import pipeline
from git import Repo
import requests
import yaml
import json
import csv
import os
import re
import urllib.parse
import sys
import torch

sys.stdout.reconfigure(encoding='utf-8')
sys.stdin.reconfigure(encoding='utf-8')


class NewsSentimentCrawler:
    def __init__(self, config_file):
        self.HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}
        self.config = self.load_config(config_file)
        self.urls = [source['url'] for source in self.config['sources']]
        self.companies = self.config['companies']
        self.stock_map = {company['name']: company['keywords'] for company in self.companies}
        
        # Initialize FinBERT sentiment analysis pipeline
        self.sentiment_pipeline = pipeline("sentiment-analysis", model="ProsusAI/finbert")

        # More robust path handling for cross-platform compatibility
        self.REPO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.DATA_DIR = os.path.join(self.REPO_PATH, "DailyShare", "data")
        self.OUTPUT_DIR = os.path.join(self.REPO_PATH, "DailyShare", "data")

        if not os.path.exists(self.OUTPUT_DIR):
            os.makedirs(self.OUTPUT_DIR)

    def load_config(self, config_file):
        with open(config_file, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        return config

    def extract_article_content(self, url):
        """Extract article content from the provided URL."""
        try:
            print(f"Fetching article: {url}")
            response = requests.get(url, headers=self.HEADERS, timeout=10)
            response.encoding = 'utf-8'
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch the article: {e}")
            return "", ""
        except Exception as e:
            print(f"An error occurred: {e}")
            return "", ""

        soup = BeautifulSoup(response.text, 'html.parser')

        try:
            content = None
            date = datetime.now().strftime("%Y-%m-%d")

            if "tw.stock.yahoo.com" in url or "tw.news.yahoo.com" in url:
                content_div = soup.find('div', class_='caas-body')
                if content_div:
                    content = content_div.get_text(strip=True)
                    date_element = soup.find('time')
                    if date_element:
                        date = date_element['datetime']
            elif "news.cnyes.com" in url:
                content_sections = soup.select('section[style*="margin-top"]')
                content = "\n".join([section.get_text(strip=True) for section in content_sections])
                date_element = soup.select_one('time') or soup.select_one('div.meta-info')
                if date_element and date_element.has_attr('datetime'):
                    date = date_element.get('datetime')

            if content:
                return content, date
            else:
                print("Unable to find article content.")
                return "", ""
        except Exception as e:
            print(f"Failed to extract article content: {e}")
            return "", ""

    def is_news_url(self, url):
        keywords = ['news', 'article', 'post', 'stock', 'finance', 'report', 'story', 'press', 'release', 'announcement']
        return any(keyword in url for keyword in keywords) and re.search(r'\d{6,}', url)

    def fetch_news_selenium(self, url):
        """Fetch links to related news articles using Selenium."""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.get(url)
            driver.implicitly_wait(10)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            news_items = soup.find_all('a', href=True)
            news_links = [urllib.parse.urljoin(url, item['href']) for item in news_items if item and 'href' in item.attrs]
            
            filter_news_links = list(set([link for link in news_links if self.is_news_url(link)]))
            
        except Exception as e:
            print(f"Failed to fetch news using Selenium: {e}")
            filter_news_links = []
        finally:
            if 'driver' in locals() and driver:
                driver.quit()

        return filter_news_links

    def analyze_sentiment(self, text, keywords=None):
        """
        Analyzes the sentiment of a given text using FinBERT.
        Returns a sentiment score between -1 (very negative) and 1 (very positive).
        """
        if not any(keyword in text for keyword in keywords):
            return None

        try:
            # Split text into chunks to handle long articles
            max_length = 512
            chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
            
            sentiment_scores = []
            for chunk in chunks:
                results = self.sentiment_pipeline(chunk)
                for result in results:
                    score = result['score']
                    if result['label'] == 'negative':
                        score = -score
                    elif result['label'] == 'neutral':
                        score = 0
                    sentiment_scores.append(score)

            if not sentiment_scores:
                return 0

            # Average the sentiment scores of all chunks
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
            return round(avg_sentiment, 4)

        except Exception as e:
            print(f"An error occurred during sentiment analysis: {e}")
            return None

    def csv_to_json(self, csv_file, json_file):
        data = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            articles = [row for row in reader]
            date = datetime.now().strftime("%Y-%m-%d")
            data.append({"date": date, "articles": articles})

        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def push_to_github(self):
        try:
            repo = Repo(self.REPO_PATH)
            repo.git.add(A=True)
            repo.index.commit(f"Update report: {datetime.now().strftime('%Y-%m-%d')}")
            origin = repo.remote(name='origin')
            origin.pull()
            origin.push()
            print("Successfully pushed updates to GitHub.")
        except Exception as e:
            print(f"Failed to push to GitHub: {e}")

    def generate_daily_report(self, news_data, date):
        """Generates a daily report in CSV and JSON format."""
        report_file = os.path.join(self.OUTPUT_DIR, f"report_{date}.csv")

        with open(report_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Date', 'Company', 'Price', 'Sentiment Score', 'Article URL']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for company_name, articles in news_data.items():
                for article in articles:
                    writer.writerow({
                        'Date': date,
                        'Company': company_name,
                        'Price': article.get('Price', 'N/A'),
                        'Sentiment Score': article.get('Sentiment Score', 0),
                        'Article URL': article.get('Article URL', ''),
                    })

        json_file = os.path.join(self.DATA_DIR, f"reports_{date}.json")
        self.csv_to_json(report_file, json_file)
        print(f"Daily report saved: {report_file}")

    def get_stock_price(self, ticker):
        # This is a placeholder. In a real scenario, you would have a robust service for this.
        print(f"Fetching stock price for {ticker}... (placeholder)")
        return "N/A"

    def run(self):
        """Main function to run the crawler."""
        today_str = datetime.now().strftime("%Y-%m-%d")
        yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        relevant_dates = {today_str, yesterday_str}

        news_data = {}
        for url in self.urls:
            news_links = self.fetch_news_selenium(url)

            for link in news_links:
                article_content, pub_date = self.extract_article_content(link)

                if not article_content or not any(date in pub_date for date in relevant_dates):
                    continue

                for company in self.companies:
                    company_name = company['name']
                    keywords = self.stock_map[company_name]
                    
                    sentiment_score = self.analyze_sentiment(article_content, keywords)
                    
                    if sentiment_score is not None:
                        stock_price = self.get_stock_price(f"{company['code']}.TW")

                        if company_name not in news_data:
                            news_data[company_name] = []

                        news_data[company_name].append({
                            'Price': stock_price,
                            'Sentiment Score': sentiment_score,
                            'Article URL': link,
                        })

        if news_data:
            self.generate_daily_report(news_data, today_str)
            self.push_to_github()
        else:
            print("No new news articles found to process.")

if __name__ == "__main__":
    # The script expects the config file to be in the same directory.
    config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'NewsSentimentCrawler.yaml')
    if not os.path.exists(config_path):
        print(f"Error: Configuration file not found at {config_path}")
    else:
        crawler = NewsSentimentCrawler(config_path)
        crawler.run()
