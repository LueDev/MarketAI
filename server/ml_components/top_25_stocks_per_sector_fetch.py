import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime, timedelta

# Define top 25 stocks for each sector
finance_tickers = ['JPM', 'BAC', 'WFC', 'C', 'MS', 'GS', 'HSBC', 'USB', 'TD', 'RY', 'AXP', 'SCHW', 'BMO', 'PNC', 'BNS', 'MUFG', 'SPGI', 'MCO', 'BLK', 'ICE', 'COF', 'CME', 'CB', 'CINF', 'MET']
health_tickers = ['UNH', 'JNJ', 'PFE', 'MRK', 'ABBV', 'TMO', 'LLY', 'MDT', 'DHR', 'BMY', 'AMGN', 'GILD', 'CVS', 'CI', 'ABT', 'SYK', 'REGN', 'BAX', 'BSX', 'ZBH', 'EW', 'ILMN', 'HCA', 'HUM', 'IQV']
tech_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'ORCL', 'ADI', 'TXN', 'AVGO', 'IBM', 'INTC', 'CSCO', 'QCOM', 'AMD', 'NOW', 'CRM', 'SHOP', 'V', 'MA', 'PYPL', 'ADBE', 'SNOW', 'INTU', 'SQ']

# Define date range
historical_start = "2000-01-01"
recent_start = (datetime.today() - timedelta(days=365*2)).strftime('%Y-%m-%d')
end_date = datetime.today().strftime('%Y-%m-%d')

# Define function to calculate indicators
def calculate_indicators(df):
    df['MA_10'] = df['Close'].rolling(window=10).mean()
    df['MA_50'] = df['Close'].rolling(window=50).mean()
    df['Volatility'] = df['Close'].rolling(window=10).std()
    return df

# Fetch data and save for each sector
def fetch_and_save_data(tickers, historical_file, recent_file):
    # Historical data
    historical_data = yf.download(tickers, start=historical_start, end=end_date)
    historical_data = historical_data.stack(level=1).rename_axis(['Date', 'Ticker']).reset_index()
    historical_data = calculate_indicators(historical_data)
    historical_data.to_csv(historical_file, index=False)
    
    # Recent data
    recent_data = yf.download(tickers, start=recent_start, end=end_date)
    recent_data = recent_data.stack(level=1).rename_axis(['Date', 'Ticker']).reset_index()
    recent_data = calculate_indicators(recent_data)
    recent_data.to_csv(recent_file, index=False)

# Define file paths
data_dir = "./data/"
fetch_and_save_data(finance_tickers, f"{data_dir}top25_finance_historical.csv", f"{data_dir}top25_enhanced_finance_recent.csv")
fetch_and_save_data(health_tickers, f"{data_dir}top25_enhanced_health_historical.csv", f"{data_dir}top25_enhanced_health_recent.csv")
fetch_and_save_data(tech_tickers, f"{data_dir}top25_enhanced_tech_historical.csv", f"{data_dir}top25_enhanced_tech_recent.csv")
