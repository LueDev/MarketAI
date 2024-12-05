import os
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, r2_score
from tensorflow.keras.models import load_model
from joblib import load

# Paths
BASE_DIR = "/Users/luisjorge/code/Flatiron-Phase-5/MarketAI/server/ml_components"
MODELS_DIR = os.path.join(BASE_DIR, "models")
DATA_DIR = os.path.join(BASE_DIR, "data")
RESULTS_DIR = os.path.join(BASE_DIR, "backtest_results")

# Ensure results directory exists
os.makedirs(RESULTS_DIR, exist_ok=True)

# Homogeneous models by sector
HOMOGENEOUS_MODELS = {
    "finance": {
        "lstm": os.path.join(MODELS_DIR, "lstm_model_LSTM_final_enhanced_finance_historical.h5"),
        "rf": os.path.join(MODELS_DIR, "random_forest_model.joblib")
    },
    "health": {
        "lstm": os.path.join(MODELS_DIR, "lstm_model_LSTM_final_enhanced_health_historical.h5"),
        "rf": os.path.join(MODELS_DIR, "random_forest_model.joblib")
    },
    "tech": {
        "lstm": os.path.join(MODELS_DIR, "lstm_model_LSTM_final_enhanced_tech_historical.h5"),
        "rf": os.path.join(MODELS_DIR, "random_forest_model.joblib")
    }
}

def load_models_for_ticker(sector, ticker):
    """
    Load both Random Forest and LSTM models for a specific ticker.
    """
    ticker_dir = os.path.join(MODELS_DIR, f"{sector}_top25_models", ticker)
    rf_path = os.path.join(ticker_dir, "random_forest", "random_forest_model.joblib")
    lstm_path = os.path.join(ticker_dir, "lstm", "lstm_model.h5")

    if not os.path.exists(rf_path) or not os.path.exists(lstm_path):
        raise FileNotFoundError(f"Models for {ticker} in {sector} not found!")

    rf_model = load(rf_path)
    lstm_model = load_model(lstm_path)
    return rf_model, lstm_model

def load_homogeneous_models(sector):
    """
    Load homogeneous models for a sector.
    """
    lstm_path = HOMOGENEOUS_MODELS[sector]["lstm"]
    rf_path = HOMOGENEOUS_MODELS[sector]["rf"]

    lstm_model = load_model(lstm_path)
    rf_model = load(rf_path)
    return rf_model, lstm_model

def load_backtesting_data(sector):
    """
    Load backtesting data for a sector from CSV files.
    """
    data_path = os.path.join(DATA_DIR, f"final_enhanced_top25_{sector}_recent.csv")
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data not found at {data_path}")
    return pd.read_csv(data_path)

def preprocess_data(ticker_data, expected_features, exclude_columns=["Ticker", "Date"]):
    """
    Preprocess data by selecting specific features, dropping non-numeric columns, and handling NaN values.
    """
    ticker_data = ticker_data.drop(columns=exclude_columns, errors="ignore")
    ticker_data = ticker_data[expected_features]
    ticker_data.fillna(ticker_data.mean(), inplace=True)
    return ticker_data.to_numpy()

def create_lstm_input(data, sequence_length):
    """
    Reshape data into a format compatible with LSTM models.
    """
    sequences = []
    for i in range(len(data) - sequence_length + 1):
        sequences.append(data[i:i + sequence_length])
    return np.array(sequences)

def evaluate_predictions(ticker, targets, predictions, model_name):
    """
    Evaluate predictions and print performance metrics.
    """
    mse = mean_squared_error(targets, predictions)
    r2 = r2_score(targets, predictions)
    print(f"{ticker} - {model_name} | MSE: {mse:.4f}, R2: {r2:.4f}")
    return mse, r2

def perform_backtest(sector, tickers):
    print(f"\nStarting backtest for sector: {sector}")
    data = load_backtesting_data(sector)

    # Load homogeneous models for the sector
    homogeneous_rf_model, homogeneous_lstm_model = load_homogeneous_models(sector)

    results = []

    for ticker in tickers:
        print(f"\nProcessing ticker: {ticker}")
        ticker_data = data[data["Ticker"] == ticker].copy()

        if ticker_data.empty:
            print(f"No data found for {ticker} in recent datasets.")
            continue

        try:
            # Load per-stock models
            per_stock_rf_model, per_stock_lstm_model = load_models_for_ticker(sector, ticker)
        except FileNotFoundError as e:
            print(e)
            continue

        # Extract the expected feature names from the per-stock RF model
        expected_features = per_stock_rf_model.feature_names_in_

        # Preprocess data
        features_rf = preprocess_data(ticker_data, expected_features)
        features_lstm = create_lstm_input(features_rf, sequence_length=200)
        targets = ticker_data["Close"].to_numpy()[199:]  # Match the LSTM sequence length

        if features_lstm.shape[0] == 0:
            print(f"Not enough data for LSTM prediction for ticker: {ticker}")
            continue

        # Per-stock model predictions
        per_stock_rf_preds = per_stock_rf_model.predict(features_rf[199:])
        per_stock_lstm_preds = per_stock_lstm_model.predict(features_lstm).flatten()

        # Homogeneous model predictions
        homogeneous_rf_preds = homogeneous_rf_model.predict(features_rf[199:])
        homogeneous_lstm_preds = homogeneous_lstm_model.predict(features_lstm).flatten()

        # Evaluate and log results
        results.append({
            "ticker": ticker,
            "per_stock_rf_mse": mean_squared_error(targets, per_stock_rf_preds),
            "per_stock_rf_r2": r2_score(targets, per_stock_rf_preds),
            "per_stock_lstm_mse": mean_squared_error(targets, per_stock_lstm_preds),
            "per_stock_lstm_r2": r2_score(targets, per_stock_lstm_preds),
            "homogeneous_rf_mse": mean_squared_error(targets, homogeneous_rf_preds),
            "homogeneous_rf_r2": r2_score(targets, homogeneous_rf_preds),
            "homogeneous_lstm_mse": mean_squared_error(targets, homogeneous_lstm_preds),
            "homogeneous_lstm_r2": r2_score(targets, homogeneous_lstm_preds)
        })

    # Save results to CSV
    results_df = pd.DataFrame(results)
    output_file = os.path.join(RESULTS_DIR, f"{sector}_backtest_results.csv")
    results_df.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")

def main():
    """
    Main function to execute backtesting.
    """
    sectors = {
        "finance": [
            'JPM', 'BAC', 'WFC', 'USB', 'GS', 'MS', 'C', 'PNC', 'TD', 'RY', 'SCHW', 'COF', 'BLK', 'AXP', 'ICE',
            'MET', 'HSBC', 'SPGI', 'BMO', 'MCO', 'CB', 'CME', 'CINF', 'MUFG'
        ],
        "health": [
            'JNJ', 'PFE', 'ABBV', 'TMO', 'MRK', 'LLY', 'UNH', 'AMGN', 'CVS', 'BMY', 'MDT', 'SYK', 'BSX', 'DHR',
            'CI', 'GILD', 'HUM', 'ZBH', 'EW', 'IQV', 'REGN', 'ABT', 'HCA', 'ILMN', 'BAX'
        ],
        "tech": [
            'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META', 'NVDA', 'ADBE', 'ORCL', 'IBM', 'CRM', 'INTC', 'AMD', 'CSCO',
            'AVGO', 'QCOM', 'ADI', 'PYPL', 'TXN', 'SHOP', 'NOW', 'SNOW', 'SQ', 'MA', 'V', 'INTU'
        ]
    }

    for sector, tickers in sectors.items():
        perform_backtest(sector, tickers)

    print("\nBacktesting complete! Results are saved in the 'backtest_results' directory.")

if __name__ == "__main__":
    main()
