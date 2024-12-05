from config import redis_client
import yfinance as yf
import pandas as pd
import os
import json
from datetime import datetime, timedelta

class DataFetch:
    def __init__(self, output_dir, cache_expiry=86400):  # Default cache expiry: 1 day
        self.redis_client = redis_client
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.cache_expiry = cache_expiry

    def fetch_data(self, tickers, start_date, end_date, cache_key):
        """
        Fetches data for the given tickers from Redis or yFinance.
        """
        if self.redis_client.exists(cache_key):
            print(f"Fetching {cache_key} from Redis")
            cached_data = json.loads(self.redis_client.get(cache_key))
            return pd.DataFrame(cached_data)

        print(f"Fetching {cache_key} from yFinance")
        data = yf.download(tickers, start=start_date, end=end_date, group_by="ticker", progress=False)
        data = data.stack(level=1).rename_axis(['Date', 'Ticker']).reset_index()
        
        # Save the fetched data to Redis
        self.redis_client.setex(cache_key, self.cache_expiry, data.to_json(orient='records'))
        return data

    def save_data(self, data, file_name):
        """
        Saves the fetched data to the specified output directory.
        """
        file_path = os.path.join(self.output_dir, file_name)
        data.to_csv(file_path, index=False)
        print(f"Data saved to {file_path}")

if __name__ == "__main__":
    output_dir = "./ml_components/production/data"
    fetcher = DataFetch(output_dir)

    # Define the top 25 tickers for each sector
    finance_tickers = [
        'JPM', 'BAC', 'WFC', 'C', 'MS', 'GS', 'HSBC', 'USB', 'TD', 'RY', 'AXP', 'SCHW', 
        'BMO', 'PNC', 'BNS', 'MUFG', 'SPGI', 'MCO', 'BLK', 'ICE', 'COF', 'CME', 'CB', 
        'CINF', 'MET'
    ]
    health_tickers = [
        'UNH', 'JNJ', 'PFE', 'MRK', 'ABBV', 'TMO', 'LLY', 'MDT', 'DHR', 'BMY', 'AMGN', 
        'GILD', 'CVS', 'CI', 'ABT', 'SYK', 'REGN', 'BAX', 'BSX', 'ZBH', 'EW', 'ILMN', 
        'HCA', 'HUM', 'IQV'
    ]
    tech_tickers = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'ORCL', 'ADI', 'TXN', 'AVGO', 
        'IBM', 'INTC', 'CSCO', 'QCOM', 'AMD', 'NOW', 'CRM', 'SHOP', 'V', 'MA', 'PYPL', 
        'ADBE', 'SNOW', 'INTU', 'SQ'
    ]

    # Combine all tickers
    all_tickers = finance_tickers + health_tickers + tech_tickers

    # Define date ranges
    historical_start = "2000-01-01"
    recent_start = (datetime.today() - timedelta(days=730)).strftime('%Y-%m-%d')
    end_date = datetime.today().strftime('%Y-%m-%d')

    # Fetch and save historical data
    historical_data = fetcher.fetch_data(
        all_tickers, historical_start, end_date, "all_sectors_historical"
    )
    fetcher.save_data(historical_data, "all_sectors_historical.csv")

    # Fetch and save recent data
    recent_data = fetcher.fetch_data(
        all_tickers, recent_start, end_date, "all_sectors_recent"
    )
    fetcher.save_data(recent_data, "all_sectors_recent.csv")
