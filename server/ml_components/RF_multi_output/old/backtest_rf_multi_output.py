import os
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error
import joblib

def recursive_predict(model, X_init, steps):
    """
    Perform recursive multi-step predictions using RF model.
    """
    predictions = []
    current_input = X_init.copy()

    for _ in range(steps):
        pred = model.predict(current_input)
        predictions.append(pred[0])
        current_input.iloc[0, :] = pred

    predictions_df = pd.DataFrame(predictions, columns=X_init.columns)
    return predictions_df

def backtest_rf(model_path, data_path, input_columns, target_columns, steps):
    """
    Backtest the recursive predictions of the RF model.

    Args:
    - model_path (str): Path to the trained model.
    - data_path (str): Path to the dataset for testing.
    - input_columns: Input columns for the model.
    - target_columns: Target columns for comparison.
    - steps: Number of steps for recursive prediction.

    Returns:
    - RMSE per feature.
    """
    model = joblib.load(model_path)
    data = pd.read_csv(data_path)

    # Prepare testing data
    split_idx = int(len(data) * 0.8)
    X_test = data[input_columns].iloc[split_idx:]
    Y_true = data[target_columns].iloc[split_idx: split_idx + steps]

    # Recursive predictions
    predictions = recursive_predict(model, X_test.iloc[:1], steps)

    # Calculate RMSE per feature
    errors = {}
    for feature in target_columns:
        rmse = np.sqrt(mean_squared_error(Y_true[feature], predictions[feature]))
        errors[feature] = rmse

    return errors

def main():
    # Paths
    output_dir = "RF_multi_output/models"
    datasets = {
        "finance_recent": "data/final_enhanced_top25_finance_recent.csv",
        "health_recent": "data/final_enhanced_top25_health_recent.csv",
        "tech_recent": "data/final_enhanced_top25_tech_recent.csv",
    }
    models = {
        "finance": os.path.join(output_dir, "rf_finance_recent.joblib"),
        "health": os.path.join(output_dir, "rf_health_recent.joblib"),
        "tech": os.path.join(output_dir, "rf_tech_recent.joblib"),
    }

    # Feature columns
    input_columns = [
        "Open", "High", "Low", "Volume", "MA_10", "MA_50", "Volatility", "RSI", 
        "MACD", "MACD_Signal", "MACD_Hist", "Stochastic", "Williams %R", 
        "BB_Lower", "BB_Middle", "BB_Upper", "EMA_10", "EMA_50", "Parabolic_SAR", 
        "OBV", "VWAP", "Pivot", "R1", "S1"
    ]
    target_columns = input_columns

    # Backtest models
    for sector, model_path in models.items():
        data_path = datasets[f"{sector}_recent"]
        errors = backtest_rf(model_path, data_path, input_columns, target_columns, steps=10)
        print(f"{sector.capitalize()} Backtest Errors (RMSE per feature):")
        print(errors)

if __name__ == "__main__":
    main()
