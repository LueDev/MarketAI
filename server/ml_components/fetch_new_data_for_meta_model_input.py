import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

def prepare_new_data(data_file, output_file):
    """
    Processes historical Top 25 data for model input.

    Parameters:
        data_file (str): Path to the CSV file containing historical data.
        output_file (str): Path to save the processed data.
    """
    # Load historical data
    data = pd.read_csv(data_file)
    if "Date" in data.columns:
        data["Date"] = pd.to_datetime(data["Date"])
        data = data.sort_values("Date")

    # Select necessary columns (remove Date and other non-numerical data)
    feature_data = data.select_dtypes(include=[np.number])

    # Handle missing values
    imputer = SimpleImputer(strategy="mean")
    feature_data = imputer.fit_transform(feature_data)

    # Standardize features
    scaler = StandardScaler()
    feature_data = scaler.fit_transform(feature_data)

    # Save processed data
    np.save(output_file, feature_data)
    print(f"Processed data saved to {output_file}")

if __name__ == "__main__":
    # Example usage
    data_dir = "./data"
    output_dir = "./prepared_data"

    os.makedirs(output_dir, exist_ok=True)

    datasets = [
        "final_enhanced_top25_finance_historical.csv",
        "final_enhanced_top25_health_historical.csv",
        "final_enhanced_top25_tech_historical.csv"
    ]

    for dataset in datasets:
        data_path = os.path.join(data_dir, dataset)
        output_path = os.path.join(output_dir, dataset.replace(".csv", ".npy"))
        print(f"Processing dataset: {dataset}")
        prepare_new_data(data_path, output_path)
