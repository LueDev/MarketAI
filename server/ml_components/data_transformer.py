import pandas as pd
import numpy as np

def transform_data(api_data):
    # Create DataFrame from the raw API data
    data = {
        "date": [entry["date"] for entry in api_data],
        "open": [entry["open"] for entry in api_data],
        "high": [entry["high"] for entry in api_data],
        "low": [entry["low"] for entry in api_data],
        "close": [entry["close"] for entry in api_data],
        "volume": [entry["volume"] for entry in api_data],
    }

    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'], unit='s')
    print("Initial DataFrame length:", len(df))

    # Calculate moving averages and volatility to match training features
    df['MA_10'] = df['close'].rolling(window=10).mean()
    df['MA_50'] = df['close'].rolling(window=50).mean()
    df['volatility'] = df['close'].rolling(window=10).std()

    # Drop rows with NaN values from rolling calculations
    df = df.dropna().reset_index(drop=True)
    print("Data length after dropna:", len(df))

    sequence_length = 60  # Set to the training sequence length

    # Check if there’s enough data for the required sequence length
    if len(df) < sequence_length:
        raise ValueError("Not enough data to form the required sequence length")

    # Normalize columns
    for column in ['open', 'high', 'low', 'close', 'volume', 'MA_10', 'MA_50', 'volatility']:
        min_val = df[column].min()
        max_val = df[column].max()
        df[column] = (df[column] - min_val) / (max_val - min_val)

    # Prepare input data
    input_data = df[['open', 'high', 'low', 'close', 'volume', 'MA_10', 'MA_50', 'volatility']].values[-sequence_length:]
    input_data = np.expand_dims(input_data, axis=0)  # Ensure shape is (1, sequence_length, 8)
    print("Input data shape:", input_data.shape)

    return input_data
