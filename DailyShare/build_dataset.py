import os
import pandas as pd
from datetime import timedelta

DATA_DIR = 'data'

def build_dataset():
    """
    Builds a labeled dataset for training a predictive model.
    """
    # Load all historical stock data
    stock_data = {}
    for filename in os.listdir(DATA_DIR):
        if filename.endswith("_historical_stock.csv"):
            company_code = filename.split("_")[0]
            file_path = os.path.join(DATA_DIR, filename)
            try:
                df = pd.read_csv(file_path, index_col=0, parse_dates=True)
                df.index = pd.to_datetime(df.index, errors='coerce').date
                stock_data[company_code] = df
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    # Load all news sentiment reports
    news_reports = []
    for filename in os.listdir(DATA_DIR):
        if filename.startswith("report_"):
            file_path = os.path.join(DATA_DIR, filename)
            try:
                report_df = pd.read_csv(file_path)
                if not report_df.empty:
                    news_reports.append(report_df)
            except pd.errors.EmptyDataError:
                print(f"Warning: {filename} is empty and will be skipped.")

    if not news_reports:
        print("No news reports found. Exiting.")
        return

    news_df = pd.concat(news_reports, ignore_index=True)

    # Data processing and feature engineering
    news_df['Date'] = pd.to_datetime(news_df['Date']).dt.date

    company_mapping = {
        '台積電': '2330',
        '聯發科': '2454',
        '鴻海': '2317',
        '聯電': '2303',
        '長榮': '2603',
        '第一金': '2892',
        '大立光': '3008',
        '台達電': '2308',
    }

    # Create the target variable (price went up or down)
    labeled_data = []
    for _, row in news_df.iterrows():
        company_name = row['Company']
        company_code = company_mapping.get(company_name)

        if company_code and company_code in stock_data:
            stock_df = stock_data[company_code]
            stock_df.index = pd.to_datetime(stock_df.index).normalize()
            current_date = pd.to_datetime(row['Date'])

            # Find the stock price for the current day and the next day
            # Find the closest previous date for current price
            current_price_date_index = stock_df.index.searchsorted(current_date, side='right') - 1
            if current_price_date_index < 0:
                continue
            current_price_row = stock_df.iloc[[current_price_date_index]]

            # Find the closest future date for next day price
            next_day_price_date_index = current_price_date_index + 1
            if next_day_price_date_index >= len(stock_df):
                continue
            next_day_price_row = stock_df.iloc[[next_day_price_date_index]]

            if not current_price_row.empty and not next_day_price_row.empty:
                current_price = current_price_row['Close'].iloc[0]
                next_day_price = next_day_price_row['Close'].iloc[0]
                
                # Create the target label
                target = 1 if next_day_price > current_price else 0
                
                labeled_data.append({
                    'Date': current_date.date(),
                    'Company': company_name,
                    'Sentiment Score': row['Sentiment Score'],
                    'Target': target
                })
            else:
                print(f"Could not find stock data for {company_name} on {current_date.date()}")

    if not labeled_data:
        print("Could not create labeled data. Please check your historical data.")
        return

    # Create and save the final dataset
    final_df = pd.DataFrame(labeled_data)
    dataset_path = os.path.join(DATA_DIR, 'training_dataset.csv')
    final_df.to_csv(dataset_path, index=False)
    print(f"Successfully built and saved the training dataset to {dataset_path}")

if __name__ == "__main__":
    build_dataset()

