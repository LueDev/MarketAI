import pandas as pd
import glob

# Adjusted file pattern to match {sector}_{timeframe}.csv files
file_pattern = "data/*_historical.csv"
all_tickers = set()

# Loop through each matching CSV file
for file in glob.glob(file_pattern):
    df = pd.read_csv(file)
    # Check if 'Ticker' column exists and add unique tickers to the set
    if 'Ticker' in df.columns:
        all_tickers.update(df['Ticker'].unique())

# Convert the set of tickers to a list for easier handling
all_tickers = list(all_tickers)
print("Unique Tickers:", all_tickers)
