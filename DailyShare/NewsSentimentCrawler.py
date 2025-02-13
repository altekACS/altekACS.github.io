from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from textblob import TextBlob
from datetime import datetime, timedelta
#from transformers import pipeline
from sentiment_analysis import analyze_market_sentiment
from stock_price_service import get_stock_price
from git import Repo  # pip install gitpython
import requests
import yaml
import json
import csv
import os
import re
import urllib.parse

import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stdin.reconfigure(encoding='utf-8')


class NewsSentimentCrawler:
    def __init__(self, config_file):
        self.HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}
        self.config = self.load_config(config_file)
        self.urls = [source['url'] for source in self.config['sources']]
        self.companies = self.config['companies']
        self.stock_map = {company['name']: company['keywords'] for company in self.companies}
        if os.name == 'nt':  # Windows
            self.REPO_PATH = os.getcwd()
            self.DATA_DIR = os.path.join(self.REPO_PATH, "DailyShare\\data")
            self.OUTPUT_DIR = os.path.join(self.REPO_PATH, "DailyShare\\data")
        else:
            self.REPO_PATH = os.path.expanduser("/Users/jerome/Project/altekACS.github.io")
            self.DATA_DIR = os.path.join(self.REPO_PATH, "DailyShare/data")
            self.OUTPUT_DIR = os.path.join(self.REPO_PATH, "DailyShare/data")

        if not os.path.exists(self.OUTPUT_DIR):
            os.makedirs(self.OUTPUT_DIR)

    def load_config(self, config_file):
        with open(config_file, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        return config

    def extract_article_content(self, url):
        """Extract article content from the provided URL."""
        try:
            print(url)
            response = requests.get(url, headers=self.HEADERS, timeout=10)
            response.encoding = 'utf-8'  # 強制使用 UTF-8 編碼
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
            if "tw.stock.yahoo.com" in url or "tw.news.yahoo.com" in url:
                content = soup.find('div', class_='caas-body')  # Adjust based on the website's article structure
                content.get_text(strip=True) if content else ""
            elif "news.cnyes.com" in url:
                content_sections = soup.select('section[style*="margin-top"]')
                content = "\n".join([section.get_text(strip=True) for section in content_sections])
            # Extract article content
            
            if content:
                # Extract the publication date (assumed to be in 'time' element)
                if "tw.stock.yahoo.com" in url or "tw.news.yahoo.com" in url:
                    date_element = soup.find('time')
                    date = date_element['datetime'] if date_element else datetime.now().strftime("%Y-%m-%d")
                    return content.get_text(strip=True) if content else "", date
                elif "news.cnyes.com" in url:
                    date_element = soup.select_one('time') or soup.select_one('div.meta-info')
                    date = date_element.get('datetime') if date_element and date_element.has_attr('datetime') else datetime.now().strftime("%Y-%m-%d")
                    return content if content else "", date
                else:
                    return "", ""
            else:
                print("Unable to find article content.")
                return "", ""
        except Exception as e:
            print(f"Failed to extract article content: {e}")
            return "", ""

    def is_news_url(self, url):
        # 定義一組可能表明新聞內容的關鍵字
        keywords = ['news', 'article', 'post', 'stock', 'finance', 'report', 'story', 'press', 'release', 'announcement']
        # 檢查是否包含新聞相關的關鍵字, 並檢查是否包含日期或時間格式
        if any(keyword in url for keyword in keywords) and re.search(r'\d{6,}', url):        
            return True
        
        return False

    def fetch_news_selenium(self, url):
        """Fetch links to related news articles using Selenium."""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        if os.name == 'nt':  # Windows
            service = Service(r"DailyShare\\chromedriver.exe")  # Replace with your ChromeDriver path
        else:  # macOS or Linux
            service = Service("/usr/local/bin/chromedriver")  # Replace with your ChromeDriver path
        driver = webdriver.Chrome(service=service, options=options)

        try:
            driver.get(url)
            driver.implicitly_wait(10)
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Adjust logic to find news article links on the Yahoo page
            news_items = soup.find_all('a', href=True)
            news_links = [item['href'] for item in news_items if item and 'href' in item.attrs]

            # Filter out non-news links
            filter_news_links = [link for link in news_links if self.is_news_url(link)]

            # if the links not start with 'http', add the base url
            filter_news_links = [urllib.parse.urljoin(url, link) for link in filter_news_links]

            # Remove duplicate links
            filter_news_links = list(set(filter_news_links))

        except Exception as e:
            print(f"Failed to fetch news using Selenium: {e}")
            filter_news_links = []

        finally:
            driver.quit()

        return filter_news_links

    def analyze_sentiment(self, text, keywords=None):
        """對文章內容進行關鍵字情感分析"""
        #keywords = [keyword for sublist in self.stock_map.values() for keyword in sublist]
        
        # 如果文章內容包含任一個關鍵字，則進行分析
        if all(keyword not in text for keyword in keywords):
            return None

        try:
            blob = TextBlob(text)
            sentiment_score = blob.sentiment.polarity * 10  # -1: 負面, 0: 中性, 1: 正面

            return sentiment_score
        except Exception as e:
            print(f"An error occurred: {e}")
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
        repo = Repo(self.REPO_PATH)
        repo.git.add(A=True)
        repo.index.commit(f"Update report: {datetime.now().strftime('%Y-%m-%d')}")
        origin = repo.remote(name='origin')
        origin.pull()  # Pull the latest changes from the remote repository
        origin.push()  # Push the latest changes to the remote repository

    def generate_daily_report(self, news_data, date):
        """生成每日報表"""
        report_file = os.path.join(self.OUTPUT_DIR, f"report_{date}.csv")

        with open(report_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Date', 'Company', 'Price','Final Score', 'Article URL', 'Sentiment Score', 'Positive Mentions', 'Negative Mentions']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            Sentiment_score_per_company = {}
            for company in self.companies:    
                Sentiment_score_per_company[company['name']] = 0         
                for news in news_data.get(company['name'], []):
                    
                    # calculate the total sentiment score per company
                    Sentiment_score_per_company[company['name']] += news.get('entiment Score', 0)                        

                    writer.writerow({
                        'Date': date,
                        'Company': company['name'],
                        'Price': news.get('Price', ''),
                        'Final Score': news.get('Final Score', ''),
                        'Article URL': news.get('Article URL', ''),
                        'Sentiment Score': news.get('Sentiment Score', ''),
                        'Positive Mentions': news.get('Positive Mentions', ''),
                        'Negative Mentions': news.get('Negative Mentions', '')
                    })

        # generate the daily report in json format
        json_file = os.path.join(self.DATA_DIR, f"reports_{date}.json")
        self.csv_to_json(report_file, json_file)
        print(f"Daily report saved: {report_file}")

        # Generate the final sentiment score report for each company as JSON format
        final_sentiment_score = os.path.join(self.DATA_DIR, f"final_score_{date}.json")
        final_score_data = [{"Date": date, "Company": company, "Sentiment Score": score} for company, score in Sentiment_score_per_company.items()]
        
        with open(final_sentiment_score, 'w', encoding='utf-8') as f:
            json.dump(final_score_data, f, ensure_ascii=False, indent=4)
        
        print(f"Final sentiment score saved: {final_sentiment_score}")

    def fetch_news_links(self, url):
        # 發送 HTTP 請求
        response = requests.get(url)

        # 檢查是否成功抓取網頁
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # 找到所有文章鏈接
            articles = soup.find_all('a', href=True)
            news_links = [item['href'] for item in articles if item and 'href' in item.attrs]

        return news_links

    def extract_sentences_containing_keyword(self, text, keyword):
        """Extract sentences containing the keyword."""
        try:
            sentences = re.split(r'(。|！|？)', text)
            keyword_sentences = [sentence for sentence in sentences if keyword in sentence]
            return keyword_sentences
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def run(self):
        """Main function."""

        # Get today's date and yesterday's date
        dates = []
        dates.append(datetime.now().strftime("%Y-%m-%d"))
        dates.append((datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"))

        try:
            news_data = {}
            for url in self.urls:
                news_links = self.fetch_news_selenium(url)

                for link in news_links:

                    # Extract article content and publication date
                    article_content, pub_date = self.extract_article_content(link)

                    # 篩選日期為今天的文章 格式為'2025-01-13T07:30:00.000Z'
                    # check if all the any of the dates not in the pub_date
                    if all(date not in pub_date for date in dates):
                        continue

                    for company in self.companies:             
                        # Analyze sentiment of the article content
                        sentiment_score = self.analyze_sentiment(article_content, self.stock_map[company['name']])        
                        if sentiment_score is not None:
                            # Extract sentences containing the keyword
                            market_sentiment = 0
                            positive_mentions = 0
                            negative_mentions = 0
                            final_score = 0
                            keyword_sentences = self.extract_sentences_containing_keyword(article_content, company['keywords'][0])
                            for sentence in keyword_sentences:
                                #print(sentence)
                                market_sentiment += analyze_market_sentiment(sentence)
                                #print(market_sentiment)

                            # Calculate the average market sentiment score
                            market_sentiment = market_sentiment / len(keyword_sentences) if len(keyword_sentences) > 0 else 0
                            
                            # leave the float number to 2 decimal places
                            market_sentiment = round(market_sentiment, 2)

                            # Calculate the final score based on sentiment and market sentiment
                            positive_mentions += article_content.count("好") + article_content.count("佳") + article_content.count("增長")
                            negative_mentions += article_content.count("壞") + article_content.count("差") + article_content.count("下跌")
                            final_score = sentiment_score + market_sentiment
                            final_score = round(final_score, 2)

                            # Query current stock price
                            #https://stock-service-app-57e2a70ca0ad.herokuapp.com/stock?ticker=2330.TW
                            company_price = 0
                            #response = requests.get(f"https://stock-service-app-57e2a70ca0ad.herokuapp.com/stock?ticker={company['code']}.TW")  # Replace with your stock service URL
                            response = get_stock_price(f"{company['code']}.TW")
                            if response['status_code'] == 200:
                                stock_data = response['json']
                                company_price = stock_data['price']

                            if company['name'] not in news_data:
                                news_data[company['name']] = []

                            news_data[company['name']].append({
                                'Price': company_price,
                                'Final Score': final_score,
                                'Sentiment Score': market_sentiment,
                                'Positive Mentions': positive_mentions,
                                'Negative Mentions': negative_mentions,
                                'Article URL': link,                                
                            })

            # Generate daily report for each company
            self.generate_daily_report(news_data, dates[0])

            # Push to GitHub
            self.push_to_github()

        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    if os.name == 'nt':  # Windows
        crawler = NewsSentimentCrawler('DailyShare\\NewsSentimentCrawler.yaml')
    else:
        # get current directory
        def getcurrentdir():
            return os.path.dirname(os.path.realpath(__file__))

        yamlpath = getcurrentdir() + '/NewsSentimentCrawler.yaml'
        crawler = NewsSentimentCrawler(yamlpath)
        
    crawler.run()