import os
import pandas as pd

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
            stock_data[company_code] = pd.read_csv(file_path)

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
    for code, df in stock_data.items():
        df['Date'] = pd.to_datetime(df['Date']).dt.date

    # Create the target variable (price went up or down)
    labeled_data = []
    for _, row in news_df.iterrows():
        company_name = row['Company']
        # Find the company code from the company name
        company_code = None
        # This is a placeholder, in a real scenario you would have a more robust mapping
        if company_name == 'TSMC':
            company_code = '2330'
        elif company_name == 'MediaTek':
            company_code = '2454'
        elif company_name == 'Hon Hai':
            company_code = '2317'
        elif company_name == 'UMC':
            company_code = '2303'
        elif company_name == 'Evergreen Marine':
            company_code = '2603'
        elif company_name == 'First Financial Holding':
            company_code = '2892'
        elif company_name == 'Largan':
            company_code = '3008'
        elif company_name == 'Delta Electronics':
            company_code = '2308'

        if company_code and company_code in stock_data:
            stock_df = stock_data[company_code]
            current_date = row['Date']
            
            # Find the stock price for the current day and the next day
            current_price_row = stock_df[stock_df['Date'] == current_date]
            next_day = current_date + timedelta(days=1)
            next_day_price_row = stock_df[stock_df['Date'] == next_day]

            if not current_price_row.empty and not next_day_price_row.empty:
                current_price = current_price_row['Close'].iloc[0]
                next_day_price = next_day_price_row['Close'].iloc[0]
                
                # Create the target label
                target = 1 if next_day_price > current_price else 0
                
                labeled_data.append({
                    'Date': current_date,
                    'Company': company_name,
                    'Sentiment Score': row['Sentiment Score'],
                    'Target': target
                })

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
