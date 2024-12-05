import requests
import pandas as pd
import time
from datetime import datetime

# Define the base URL for the GDELT API
BASE_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

def fetch_gdelt_news_single_ticker(ticker, start_date, end_date):
    all_news_data = []
    
    # Format the dates as required by the GDELT API
    formatted_start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y%m%d")
    formatted_end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%Y%m%d")

    print(f"Fetching news for {ticker}...")
    
    # Define parameters for the API request
    params = {
        "query": f'"{ticker}"',
        "mode": "ArtList",  # Article metadata
        "startdatetime": formatted_start_date,
        "enddatetime": formatted_end_date,
        "maxrecords": 250,  # Adjust this as needed
        "format": "json",
        "sort": "date"
    }
    
    try:
        # Send request to the GDELT API
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        # Parse the JSON response
        data = response.json()
        if "articles" in data:
            news_data = data["articles"]
            for article in news_data:
                # Collect the necessary fields
                all_news_data.append({
                    'date': article.get('seendate', '')[:10],  # Extract date
                    'ticker': ticker,
                    'title': article.get('title', ''),
                    'source': article.get('source', ''),
                    'tone': article.get('tone', {}).get('value', 0),
                    'url': article.get('url', '')
                })
        else:
            print(f"No news data for {ticker}")
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news for {ticker}: {e}")
        print(f"Response content: {response.text}")
    
    # Delay after each ticker to avoid rate limiting
    time.sleep(20)
    
    # Convert the data to a DataFrame
    news_df = pd.DataFrame(all_news_data)
    if news_df.empty:
        print("No news data available for the specified tickers and dates.")
    return news_df

# Define ticker and date range
ticker = 'AAPL'  # Run the script separately for each ticker if necessary
start_date = "2023-01-01"
end_date = "2023-12-31"

# Fetch news data
news_df = fetch_gdelt_news_single_ticker(ticker, start_date, end_date)
print(news_df)
