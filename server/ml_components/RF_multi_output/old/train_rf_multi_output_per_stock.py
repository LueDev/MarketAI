import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from joblib import dump
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# Base directory where the script resides
base_dir = os.path.dirname(os.path.abspath(__file__))

# Data directory
data_dir = os.path.join(base_dir, "../data")

# Define paths using os.path.join
data_files = {
    "finance_historical": os.path.join(data_dir, "final_enhanced_top25_finance_historical.csv"),
    "finance_recent": os.path.join(data_dir, "final_enhanced_top25_finance_recent.csv"),
    "health_historical": os.path.join(data_dir, "final_enhanced_top25_health_historical.csv"),
    "health_recent": os.path.join(data_dir, "final_enhanced_top25_health_recent.csv"),
    "tech_historical": os.path.join(data_dir, "final_enhanced_top25_tech_historical.csv"),
    "tech_recent": os.path.join(data_dir, "final_enhanced_top25_tech_recent.csv"),
}

# Output directory for models
output_dir = os.path.join(base_dir, "RF_multi_output", "models")
os.makedirs(output_dir, exist_ok=True)

# Input and target columns
input_columns = [
    "Open", "High", "Low", "Close", "Volume", "MA_10", "MA_50", "Volatility", 
    "RSI", "MACD", "MACD_Signal", "MACD_Hist", "Stochastic", "Williams %R", 
    "BB_Lower", "BB_Middle", "BB_Upper", "EMA_10", "EMA_50", "Parabolic_SAR", 
    "OBV", "VWAP", "Pivot", "R1", "S1"
]
target_columns = ["Close"]

# Function to clean data
def clean_data(data):
    """
    Cleans numeric data and ensures Ticker column is preserved.
    """
    # Preserve the Ticker column
    ticker_column = data['Ticker'].astype(str).str.strip()

    # Convert other columns to numeric where applicable
    for col in data.columns:
        if col != "Ticker":
            data[col] = pd.to_numeric(data[col], errors="coerce")

    # Fill missing numeric values with column mean
    data.fillna(data.mean(), inplace=True)

    # Restore the Ticker column
    data['Ticker'] = ticker_column

    return data

# Function to train model for a specific stock
def train_model_for_stock(stock_df, ticker, category):
    # Ensure ticker is valid and not NaN
    if pd.isna(ticker):
        print(f"Skipping invalid ticker in {category}.")
        return

    # Prepare directories for each ticker
    stock_output_dir = os.path.join(output_dir, category, ticker)
    os.makedirs(stock_output_dir, exist_ok=True)

    # Data preparation
    X = stock_df[input_columns]
    y = stock_df[target_columns].values.ravel()

    # Train the model
    print(f"Training model for {ticker} in {category}...")
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X, y)

    # Evaluate the model
    mse = mean_squared_error(y, model.predict(X))
    print(f"Model for {ticker} trained. MSE: {mse}")

    # Save the model
    model_path = os.path.join(stock_output_dir, f"{ticker}_model.joblib")
    dump(model, model_path)

    # Log training information
    log_path = os.path.join(stock_output_dir, "training_log.txt")
    with open(log_path, "w") as log_file:
        log_file.write(f"Ticker: {ticker}\n")
        log_file.write(f"Category: {category}\n")
        log_file.write(f"Model Path: {model_path}\n")
        log_file.write(f"MSE: {mse}\n")

# Main function to iterate through categories and tickers
def train_per_stock():
    for category, data_file in data_files.items():
        # Check if the file exists
        if not os.path.exists(data_file):
            print(f"Data file {data_file} not found. Skipping {category}.")
            continue

        print(f"Processing category: {category}")
        try:
            # Read and clean the data
            df = pd.read_csv(data_file, encoding='utf-8')
            df = clean_data(df)

            # Check for the Ticker column
            if "Ticker" not in df.columns:
                print(f"Ticker column missing in {data_file}. Skipping {category}.")
                continue

            # Train a model for each ticker
            tickers = df['Ticker'].unique()
            print(f"Found {len(tickers)} tickers in {category}: {tickers}")

            for ticker in tickers:
                stock_df = df[df['Ticker'] == ticker]
                train_model_for_stock(stock_df, ticker, category)

        except Exception as e:
            print(f"Error processing {category}: {e}")

if __name__ == "__main__":
    train_per_stock()
