import pandas as pd
import joblib
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from train_rf_multi_output import calculate_derived_features
import os

def clean_data(data, model):
    """
    Cleans the dataset by:
    - Removing unnecessary columns (e.g., 'Date', 'Ticker').
    - Converting all columns to numeric where applicable.
    - Replacing invalid entries with NaN and filling NaN with column means.
    - Ensures that the cleaned dataset has the same features as the model's feature names.

    Args:
    - data (pd.DataFrame): The raw dataset.
    - model: Trained model with expected feature names.

    Returns:
    - pd.DataFrame: The cleaned and aligned dataset.
    """
    # Drop unnecessary columns
    if "Date" in data.columns:
        data = data.drop(columns=["Date"])
    if "Ticker" in data.columns:
        data = data.drop(columns=["Ticker"])

    # Convert remaining columns to numeric
    for col in data.columns:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    # Fill NaN values with column means
    data.fillna(data.mean(), inplace=True)

    # Align with model feature names
    expected_features = model.feature_names_in_
    if set(data.columns) != set(expected_features):
        print(f"Aligning dataset columns to model's expected features...")
        data = data[expected_features]

    return data

def add_noise_to_features(data, noise_level=0.01):
    """
    Adds controlled noise to core features to simulate real-world variations.

    Args:
    - data (pd.DataFrame): The input dataset with core features.
    - noise_level (float): Percentage of the feature's value to use as noise.

    Returns:
    - pd.DataFrame: Dataset with added noise.
    """
    noisy_data = data.copy()
    core_features = ["Open", "High", "Low", "Volume"]  # Core features for noise
    for feature in core_features:
        if feature in noisy_data.columns:
            noise = np.random.normal(0, noise_level, size=noisy_data[feature].shape) * noisy_data[feature]
            noisy_data[feature] += noise
    return noisy_data

def backtest_batch(model, batch_data, noise_level=0.01):
    """
    Process a single batch of data with added noise and return predictions.

    Args:
    - model: Trained model to use for predictions.
    - batch_data (pd.DataFrame): Batch of test data.
    - noise_level (float): Percentage of the feature's value to use as noise.

    Returns:
    - np.array: Predictions for the batch.
    """
    # Add noise to batch data
    batch_data_noisy = add_noise_to_features(batch_data, noise_level)

    # Ensure batch data has valid feature names
    expected_features = model.feature_names_in_
    if set(batch_data_noisy.columns) != set(expected_features):
        print(f"Aligning batch data to model's expected features...")
        batch_data_noisy = batch_data_noisy[expected_features]

    # Convert batch data to numpy array for prediction
    predictions = model.predict(batch_data_noisy.values)
    return predictions



def backtest_model(model_path, test_data_path, intervals, batch_size=3000, noise_level=0.01):
    """
    Backtests the model using rolling predictions and processes data in batches.

    Args:
    - model_path (str): Path to the trained model.
    - test_data_path (str): Path to the test dataset.
    - intervals (list): List of intervals (in days) to backtest.
    - batch_size (int): Number of rows per batch.
    - noise_level (float): Percentage of the feature's value to use as noise.

    Returns:
    - dict: Results for each interval.
    """
    model = joblib.load(model_path)
    print(f"Loaded model from {model_path}")

    # Load and clean test dataset
    test_data = pd.read_csv(test_data_path)
    test_data = clean_data(test_data, model)  # Clean and align the dataset
    test_data = calculate_derived_features(test_data)  # Add derived features

    # Match training feature set
    print(f"Test data aligned with model features. Dataset size: {test_data.shape}")

    results = {}
    for interval in intervals:
        print(f"Backtesting for interval: {interval} days...")
        predictions = []

        # Process data in batches
        for start_idx in range(0, len(test_data) - interval, batch_size):
            end_idx = min(start_idx + batch_size, len(test_data) - interval)
            batch_data = test_data.iloc[start_idx:end_idx]

            # Debug output
            print(f"Processing batch {start_idx // batch_size + 1} from index {start_idx} to {end_idx}...")

            # Perform predictions on the batch with noise
            batch_predictions = backtest_batch(model, batch_data, noise_level)
            predictions.extend(batch_predictions)

        # Evaluate predictions
        mse = mean_squared_error(test_data["Close"][interval:], predictions)
        mae = mean_absolute_error(test_data["Close"][interval:], predictions)
        r2 = r2_score(test_data["Close"][interval:], predictions)

        results[interval] = {"MSE": mse, "MAE": mae, "R2": r2}
        print(f"Interval {interval} days: MSE={mse:.6f}, MAE={mae:.6f}, R2={r2:.6f}")

    return results



def main():
    base_dir = os.path.dirname(__file__)
    data_dir = os.path.join(base_dir, "../data")
    models_dir = os.path.join(base_dir, "models")

    # Configurations
    sectors = ["finance", "health", "tech"]
    intervals = list(range(1, 181))  # Test for days 1 through 180
    combinations = []

    # Generate combinations of models and datasets
    for sector in sectors:
        combinations.append((f"{models_dir}/rf_{sector}_historical.joblib", f"{data_dir}/final_enhanced_{sector}_historical.csv"))
        combinations.append((f"{models_dir}/rf_{sector}_historical.joblib", f"{data_dir}/final_enhanced_{sector}_recent.csv"))
        combinations.append((f"{models_dir}/rf_{sector}_recent.joblib", f"{data_dir}/final_enhanced_{sector}_recent.csv"))
        combinations.append((f"{models_dir}/rf_{sector}_recent.joblib", f"{data_dir}/final_enhanced_{sector}_historical.csv"))

    # Backtest all combinations
    all_results = {}
    for model_path, test_data_path in combinations:
        sector = model_path.split("_")[1]
        model_type = "historical" if "historical" in model_path else "recent"
        data_type = "historical" if "historical" in test_data_path else "recent"
        key = f"{sector}_{model_type}_on_{data_type}_data"

        print(f"Backtesting {model_type} model on {data_type} data for {sector} sector...")
        results = backtest_model(model_path, test_data_path, intervals)
        all_results[key] = results

    # Save results to a JSON file
    output_path = os.path.join(base_dir, "backtest_results.json")
    with open(output_path, "w") as outfile:
        import json
        json.dump(all_results, outfile, indent=4)
    print(f"Backtest results saved to {output_path}")

if __name__ == "__main__":
    main()
