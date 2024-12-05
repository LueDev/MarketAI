# ml_components/data_preparation.py

import pandas as pd
import yfinance as yf
import os
from datetime import datetime

# Define sectors and stocks to fetch
SECTORS = {
    "tech": ["AAPL", "MSFT", "GOOGL", "AMZN", "FB"],
    "finance": ["JPM", "BAC", "WFC", "GS", "MS"],
    "health": ["JNJ", "PFE", "MRK", "ABBV", "TMO"]
}

# Define time ranges for historical and recent data
HISTORICAL_START = "2000-01-01"
HISTORICAL_END = "2017-12-31"
RECENT_START = "2018-01-01"
RECENT_END = datetime.now().strftime("%Y-%m-%d")  # Up to today’s date

def fetch_data(tickers, start_date, end_date):
    """
    Fetch stock data for a list of tickers from Yahoo Finance.
    """
    data = yf.download(tickers, start=start_date, end=end_date, group_by="ticker")
    processed_data = {}
    for ticker in tickers:
        if ticker in data.columns.levels[0]:
            ticker_data = data[ticker][['Open', 'High', 'Low', 'Close', 'Volume']]
            ticker_data['Ticker'] = ticker  # Add a ticker column for tracking
            processed_data[ticker] = ticker_data
    return processed_data

def prepare_and_save_data(sector, data, timeframe):
    combined_data = pd.concat(data.values())

    # Add any additional preprocessing steps, such as feature engineering
    combined_data['MA_10'] = combined_data['Close'].rolling(window=10).mean()
    combined_data['MA_50'] = combined_data['Close'].rolling(window=50).mean()
    combined_data['Volatility'] = combined_data['Close'].rolling(window=10).std()

    # Drop NaN rows that may have been created by rolling calculations
    combined_data.dropna(inplace=True)

    # Retain only the columns used in training
    combined_data = combined_data[['Open', 'High', 'Low', 'Close', 'Volume', 'MA_10', 'MA_50', 'Volatility']]

    # Save to CSV
    filename = f"{sector}_{timeframe}.csv"
    output_path = os.path.join("data", filename)
    os.makedirs("data", exist_ok=True)
    combined_data.to_csv(output_path, index=False)
    print(f"Data for {sector} ({timeframe}) saved to {output_path}")


def main():
    # Fetch and save historical and recent data for each sector
    for sector, tickers in SECTORS.items():
        print(f"Fetching data for {sector} sector...")

        # Historical data
        historical_data = fetch_data(tickers, HISTORICAL_START, HISTORICAL_END)
        prepare_and_save_data(sector, historical_data, "historical")

        # Recent data
        recent_data = fetch_data(tickers, RECENT_START, RECENT_END)
        prepare_and_save_data(sector, recent_data, "recent")

if __name__ == "__main__":
    main()
