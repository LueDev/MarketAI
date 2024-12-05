import pandas as pd
import numpy as np
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from joblib import dump

# Define function to clean data
def clean_data(data):
    """
    Cleans the dataset by converting all columns to numeric where applicable,
    replacing invalid entries with NaN, and then filling NaN with column means.

    Args:
    - data (pd.DataFrame): The raw dataset.

    Returns:
    - pd.DataFrame: The cleaned dataset.
    """
    for col in data.columns:
        data[col] = pd.to_numeric(data[col], errors='coerce')
    data.fillna(data.mean(), inplace=True)
    return data

# Define function to calculate derived features
def calculate_derived_features(data):
    """
    Adds derived technical indicators to the dataset.
    """
    # Ensure required columns are available
    required_columns = ["Open", "High", "Low", "Close", "Volume"]
    for col in required_columns:
        if col not in data.columns:
            raise ValueError(f"Missing required column: {col}")

    # Add derived features
    data["VWAP"] = ((data["Close"] + data["High"] + data["Low"]) / 3 * data["Volume"]).cumsum() / data["Volume"].cumsum()
    data["MA_10"] = data["Close"].rolling(window=10).mean()
    data["MA_50"] = data["Close"].rolling(window=50).mean()
    data["EMA_10"] = data["Close"].ewm(span=10, adjust=False).mean()
    data["EMA_50"] = data["Close"].ewm(span=50, adjust=False).mean()
    delta = data["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data["RSI"] = 100 - (100 / (1 + rs))
    rolling_mean = data["Close"].rolling(window=20).mean()
    rolling_std = data["Close"].rolling(window=20).std()
    data["BB_Lower"] = rolling_mean - (2 * rolling_std)
    data["BB_Middle"] = rolling_mean
    data["BB_Upper"] = rolling_mean + (2 * rolling_std)
    ema_12 = data["Close"].ewm(span=12, adjust=False).mean()
    ema_26 = data["Close"].ewm(span=26, adjust=False).mean()
    data["MACD"] = ema_12 - ema_26
    data["MACD_Signal"] = data["MACD"].ewm(span=9, adjust=False).mean()
    data["MACD_Hist"] = data["MACD"] - data["MACD_Signal"]
    lowest_low = data["Low"].rolling(window=14).min()
    highest_high = data["High"].rolling(window=14).max()
    data["Stochastic"] = 100 * (data["Close"] - lowest_low) / (highest_high - lowest_low)
    data["Williams %R"] = -100 * (highest_high - data["Close"]) / (highest_high - lowest_low)
    data["Parabolic_SAR"] = calculate_parabolic_sar(data)
    obv = [0]
    for i in range(1, len(data)):
        if data["Close"].iloc[i] > data["Close"].iloc[i - 1]:
            obv.append(obv[-1] + data["Volume"].iloc[i])
        elif data["Close"].iloc[i] < data["Close"].iloc[i - 1]:
            obv.append(obv[-1] - data["Volume"].iloc[i])
        else:
            obv.append(obv[-1])
    data["OBV"] = obv
    data["Pivot"] = (data["High"] + data["Low"] + data["Close"]) / 3
    data["R1"] = (2 * data["Pivot"]) - data["Low"]
    data["S1"] = (2 * data["Pivot"]) - data["High"]
    
     # Ensure no NaN values remain after calculations
    data.fillna(data.mean(), inplace=True)  # Fill remaining NaNs with column means
    return data

def calculate_parabolic_sar(data, step=0.02, max_step=0.2):
    """
    Helper function to calculate Parabolic SAR.
    """
    psar = data["Close"].copy()
    af = step
    ep = data["High"].iloc[0] if data["Close"].iloc[0] > data["Open"].iloc[0] else data["Low"].iloc[0]
    rising = data["Close"].iloc[0] > data["Open"].iloc[0]

    for i in range(1, len(data)):
        psar.iloc[i] = psar.iloc[i - 1] + af * (ep - psar.iloc[i - 1])

        if rising:
            if data["Low"].iloc[i] < psar.iloc[i]:
                rising = False
                psar.iloc[i] = ep
                ep = data["Low"].iloc[i]
                af = step
            elif data["High"].iloc[i] > ep:
                ep = data["High"].iloc[i]
                af = min(af + step, max_step)
        else:
            if data["High"].iloc[i] > psar.iloc[i]:
                rising = True
                psar.iloc[i] = ep
                ep = data["High"].iloc[i]
                af = step
            elif data["Low"].iloc[i] < ep:
                ep = data["Low"].iloc[i]
                af = min(af + step, max_step)

    return psar

# Define function to train the model
def train_rf_model(data_path, output_dir, target_columns, input_columns, model_name):
    print(f"Loading dataset from {data_path}...")
    data = pd.read_csv(data_path)
    data = clean_data(data)  # Initial cleaning
    data = calculate_derived_features(data)
    data = clean_data(data)  # Final cleaning after derived features
    X = data[input_columns]
    y = data[target_columns].values.ravel()
    print(f"Dataset size: {data.shape}")
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X, y)
    mse = mean_squared_error(y, model.predict(X))
    print(f"Model: {model_name} | MSE: {mse}")
    dump(model, os.path.join(output_dir, f"{model_name}.joblib"))

# Main function
def main():
    # Dataset configurations and paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "..", "data")
    output_dir = os.path.join(base_dir, "models")
    os.makedirs(output_dir, exist_ok=True)
    datasets = {
        "finance_historical": "final_enhanced_top25_finance_historical.csv",
        "finance_recent":  "final_enhanced_top25_finance_recent.csv",
        "health_historical":  "final_enhanced_top25_health_historical.csv",
        "health_recent": "final_enhanced_top25_health_recent.csv",
        "tech_historical": "final_enhanced_top25_tech_historical.csv",
        "tech_recent": "final_enhanced_top25_tech_recent.csv",
    }
    input_columns = [
    "Open", "High", "Low", "Close", "Volume", "MA_10", "MA_50", "Volatility", 
    "RSI", "MACD", "MACD_Signal", "MACD_Hist", "Stochastic", "Williams %R", 
    "BB_Lower", "BB_Middle", "BB_Upper", "EMA_10", "EMA_50", "Parabolic_SAR", 
    "OBV", "VWAP", "Pivot", "R1", "S1"
    ]

    target_columns = ["Close"]
    for dataset_name, dataset_path in datasets.items():
        train_rf_model(os.path.join(data_dir, dataset_path), output_dir, target_columns, input_columns, f"rf_{dataset_name}")

if __name__ == "__main__":
    main()
