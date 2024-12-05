import pandas as pd
import os

def load_and_prepare_enhanced_data(sector, timeframe):
    # Define file path for enhanced data
    file_path = f"data/enhanced_{sector}_{timeframe}.csv"
    
    # Load the enhanced data
    df = pd.read_csv(file_path, parse_dates=['Date'])
    
    # Handle missing values
    # Option 1: Drop rows with any NaN values (recommended if the dataset is large)
    df = df.dropna()

    # Option 2: Fill NaN values (e.g., forward fill or fill with a constant)
    # df = df.fillna(method='ffill')  # Forward fill
    # df = df.fillna(0)  # Fill with zeroes (if appropriate for the feature)
    
    # Return the prepared DataFrame
    return df
