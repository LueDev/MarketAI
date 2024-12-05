import os
import joblib
import pandas as pd
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

# Directories
base_dir = os.path.dirname(__file__)
data_dir = os.path.join(base_dir, "../data")
models_dir = os.path.join(base_dir, "models")

# Test datasets and corresponding models
test_datasets = {
    "rf_finance_historical": "final_enhanced_top25_finance_historical.csv",
    "rf_finance_recent": "final_enhanced_top25_finance_recent.csv",
    "rf_health_historical": "final_enhanced_top25_health_historical.csv",
    "rf_health_recent": "final_enhanced_top25_health_recent.csv",
    "rf_tech_historical": "final_enhanced_top25_tech_historical.csv",
    "rf_tech_recent": "final_enhanced_top25_tech_recent.csv",
}

def evaluate_model(model_path, test_data_path):
    # Load model
    model = joblib.load(model_path)
    
    # Load test dataset
    test_data = pd.read_csv(test_data_path)
    X_test = test_data.iloc[:, :-1]  # Features
    y_test = test_data.iloc[:, -1]  # Target
    
    # Predict and evaluate
    predictions = model.predict(X_test)
    mse = mean_squared_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)
    mae = mean_absolute_error(y_test, predictions)
    
    return mse, r2, mae

def main():
    for model_name, dataset in test_datasets.items():
        model_path = os.path.join(models_dir, f"{model_name}.joblib")
        test_data_path = os.path.join(data_dir, dataset)
        
        print(f"Evaluating model: {model_name}...")
        mse, r2, mae = evaluate_model(model_path, test_data_path)
        print(f"Results for {model_name}:")
        print(f"MSE: {mse:.6f}, R²: {r2:.6f}, MAE: {mae:.6f}")
        print("-" * 50)

if __name__ == "__main__":
    main()
