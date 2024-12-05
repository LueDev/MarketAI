import pandas as pd
import requests
import time
from transformers import pipeline

### Alpha vantage information is unreliable. 

# Initialize FinBERT for sentiment analysis
finbert = pipeline("sentiment-analysis", model="yiyanghkust/finbert-tone")

# Alpha Vantage settings
API_KEY = 'IZ6W9CC0LCAQGINR'
BASE_URL = "https://www.alphavantage.co/query"

# List of tickers
tickers = ['AMZN']  # You can add other tickers as needed

# Function to fetch news for given tickers and date range with API rate limit handling
def fetch_news_for_tickers(tickers, start_date, end_date):
    all_news_data = []
    daily_limit_reached = False

    for ticker in tickers:
        print(f"Fetching news for {ticker}...")
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')

        for single_date in date_range:
            if daily_limit_reached:
                print("API request limit reached. Stopping fetch.")
                break

            formatted_date = single_date.strftime('%Y-%m-%d')
            params = {
                "function": "NEWS_SENTIMENT",
                "tickers": ticker,
                "apikey": API_KEY,
                "time_from": formatted_date + "T00:00:00",
                "time_to": formatted_date + "T23:59:59",
                "limit": 5
            }
            
            response = requests.get(BASE_URL, params=params)
            if response.status_code == 200:
                news_data = response.json().get("feed", [])
                if not news_data:
                    print(f"No news data for {ticker} on {formatted_date}")
                    continue
                
                for article in news_data:
                    # Extract relevant information
                    ticker_data = next((ts for ts in article.get("ticker_sentiment", []) if ts["ticker"] == ticker), {})
                    all_news_data.append({
                        'date': article["time_published"][:10],
                        'ticker': ticker,
                        'title': article.get('title', ''),
                        'summary': article.get('summary', ''),
                        'url': article.get('url', ''),
                        'relevance_score': ticker_data.get('relevance_score', ''),
                        'sentiment_score': ticker_data.get('ticker_sentiment_score', ''),
                        'sentiment_label': ticker_data.get('ticker_sentiment_label', '')
                    })
                
                time.sleep(2)
                
            elif "Note" in response.json() or "Information" in response.json():
                print(response.json())
                daily_limit_reached = True
                break
            else:
                print(f"Error fetching news for {ticker} on {formatted_date}")
    
    news_df = pd.DataFrame(all_news_data)
    
    if 'date' not in news_df.columns or news_df['date'].isnull().any():
        print("Warning: Missing or malformed dates detected.")
    
    return news_df

# Function to analyze sentiment using FinBERT on fetched news data
def analyze_sentiment(news_df):
    # Check if the 'date' column exists before proceeding
    if 'date' not in news_df.columns:
        print("Error: 'date' column not found in news data.")
        return pd.DataFrame()  # Return empty DataFrame if 'date' column is missing
    
    # Ensure 'date' column is in the correct datetime format
    news_df['date'] = pd.to_datetime(news_df['date'], errors='coerce')
    
    # Drop any rows where 'date' couldn't be parsed correctly
    news_df = news_df.dropna(subset=['date'])
    
    # Aggregate daily headlines by ticker and date
    daily_news = news_df.groupby(['date', 'ticker'])['headline'].apply(' '.join).reset_index()
    
    # Run FinBERT sentiment analysis for each day's combined headlines
    sentiments = []
    for _, row in daily_news.iterrows():
        result = finbert(row['headline'])[0]
        sentiment_score = result['score'] if result['label'] == 'Positive' else -result['score']
        sentiments.append({'date': row['date'], 'ticker': row['ticker'], 'sentiment_score': sentiment_score})
    
    return pd.DataFrame(sentiments)

# Define date range
start_date = "2023-01-01"
end_date = "2024-01-01"  # Use a small range to test with limited API requests

# Fetch and analyze news data
news_df = fetch_news_for_tickers(tickers, start_date, end_date)

# Check if any data was returned before proceeding
if not news_df.empty:
    sentiment_df = analyze_sentiment(news_df)
    print(sentiment_df)
else:
    print("No news data available for the specified tickers and dates.")
