import pandas as pd
import joblib
import os
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from train_rf_multi_output import clean_data, calculate_derived_features

def evaluate_model(model_path, test_data_path):
    """
    Evaluate a trained Random Forest model on a test dataset.

    Args:
    - model_path (str): Path to the trained model.
    - test_data_path (str): Path to the test dataset.

    Returns:
    - mse (float): Mean Squared Error of the predictions.
    - r2 (float): R-squared of the predictions.
    - mae (float): Mean Absolute Error of the predictions.
    """
    # Load the trained model
    model = joblib.load(model_path)
    print(f"Loaded model from {model_path}.")

    # Load the test dataset
    test_data = pd.read_csv(test_data_path)
    print(f"Loaded test data from {test_data_path}. Dataset size: {test_data.shape}")

    # Clean and prepare the test data
    test_data = clean_data(test_data)  # Handle missing or invalid values
    test_data = calculate_derived_features(test_data)  # Add derived features

    # Extract input features (X) and true values (y)
    X_test = test_data[model.feature_names_in_]  # Ensure feature alignment
    y_true = test_data["Close"]  # Target variable

    # Predict using the model
    predictions = model.predict(X_test)

    # Evaluate predictions
    mse = mean_squared_error(y_true, predictions)
    r2 = r2_score(y_true, predictions)
    mae = mean_absolute_error(y_true, predictions)

    return mse, r2, mae

def main():
    """
    Main function to evaluate all models on various datasets for cross-testing.
    """
    # Directories for data and models
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "..", "data")
    models_dir = os.path.join(base_dir, "models")

    # Datasets and their corresponding models
    datasets = {
        "finance_historical": "final_enhanced_top25_finance_historical.csv",
        "finance_recent": "final_enhanced_top25_finance_recent.csv",
        "health_historical": "final_enhanced_top25_health_historical.csv",
        "health_recent": "final_enhanced_top25_health_recent.csv",
        "tech_historical": "final_enhanced_top25_tech_historical.csv",
        "tech_recent": "final_enhanced_top25_tech_recent.csv",
    }

    # Cross-testing configurations
    cross_tests = [
        ("rf_finance_historical", "final_enhanced_top25_finance_recent.csv"),
        ("rf_finance_recent", "final_enhanced_top25_finance_historical.csv"),
        ("rf_health_historical", "final_enhanced_top25_health_recent.csv"),
        ("rf_health_recent", "final_enhanced_top25_health_historical.csv"),
        ("rf_tech_historical", "final_enhanced_top25_tech_recent.csv"),
        ("rf_tech_recent", "final_enhanced_top25_tech_historical.csv"),
    ]

    # Evaluate cross-tests
    for model_name, test_dataset in cross_tests:
        model_path = os.path.join(models_dir, f"{model_name}.joblib")
        test_data_path = os.path.join(data_dir, test_dataset)
        print(f"Evaluating model: {model_name} on dataset: {test_dataset}...")
        try:
            mse, r2, mae = evaluate_model(model_path, test_data_path)
            print(f"Results for {model_name} on {test_dataset}:")
            print(f"MSE: {mse:.6f}, R²: {r2:.6f}, MAE: {mae:.6f}")
        except Exception as e:
            print(f"Error evaluating model {model_name} on {test_dataset}: {e}")
        print("-" * 50)

if __name__ == "__main__":
    main()
