import numpy as np
import os

def dynamic_formatter(lstm_preds, rf_preds, lstm_targets, rf_targets):
    """
    Formats LSTM and Random Forest predictions for meta-model input.
    Ensures alignment and handles shape mismatches.
    """
    # Check shapes of predictions and targets
    print(f"LSTM Predictions Shape: {lstm_preds.shape}")
    print(f"Random Forest Predictions Shape: {rf_preds.shape}")
    print(f"LSTM Targets Shape: {lstm_targets.shape}")
    print(f"Random Forest Targets Shape: {rf_targets.shape}")

    # Adjust LSTM predictions (if needed)
    if len(lstm_preds.shape) == 3:  # Likely sequence data
        lstm_preds = lstm_preds[:, -1, :]  # Take the final time step
        print(f"LSTM Predictions Reshaped to: {lstm_preds.shape}")

    # Aggregate or subsample Random Forest predictions to match LSTM shape
    if rf_preds.shape[0] > lstm_preds.shape[0]:
        factor = rf_preds.shape[0] // lstm_preds.shape[0]
        rf_preds = rf_preds[:factor * lstm_preds.shape[0]]
        rf_preds = rf_preds.reshape(lstm_preds.shape[0], -1, rf_preds.shape[-1]).mean(axis=1)
        print(f"Random Forest Predictions Reshaped to: {rf_preds.shape}")
    else:
        raise ValueError("Random Forest predictions have fewer rows than LSTM predictions!")

    # Ensure targets match predictions
    if lstm_preds.shape[0] != lstm_targets.shape[0]:
        lstm_targets = lstm_targets[:lstm_preds.shape[0]]
    if rf_preds.shape[0] != rf_targets.shape[0]:
        rf_targets = rf_targets[:rf_preds.shape[0]]

    # Combine LSTM and RF predictions for meta-model input
    X_meta = np.hstack((lstm_preds, rf_preds))
    print(f"Formatted Meta-Model Input Shape: {X_meta.shape}")

    return X_meta, {"LSTM": lstm_targets, "RandomForest": rf_targets}

def process_all_datasets(lstm_files, rf_files, lstm_targets_file, rf_targets_file, output_dir="prepared_meta_data"):
    """
    Processes all LSTM and Random Forest predictions for each dataset and saves outputs.
    """
    os.makedirs(output_dir, exist_ok=True)

    for lstm_file, rf_file in zip(lstm_files, rf_files):
        dataset_name = os.path.basename(lstm_file).replace("LSTM_", "").replace(".npy", "")
        print(f"\nProcessing dataset: {dataset_name}")

        # Load predictions and targets
        lstm_preds = np.load(lstm_file)
        rf_preds = np.load(rf_file)
        lstm_targets = np.load(lstm_targets_file)
        rf_targets = np.load(rf_targets_file)

        # Format predictions and targets
        try:
            X_meta, formatted_targets = dynamic_formatter(lstm_preds, rf_preds, lstm_targets, rf_targets)
        except ValueError as e:
            print(f"Skipping dataset {dataset_name}: {e}")
            continue

        # Save formatted predictions and targets
        np.save(f"{output_dir}/X_meta_{dataset_name}.npy", X_meta)
        np.save(f"{output_dir}/Formatted_LSTM_y_{dataset_name}.npy", formatted_targets["LSTM"])
        np.save(f"{output_dir}/Formatted_RandomForest_y_{dataset_name}.npy", formatted_targets["RandomForest"])

        print(f"Saved outputs for {dataset_name} to {output_dir}/")

if __name__ == "__main__":
    # File paths for LSTM and RF predictions
    lstm_files = [
        "prepared_top_25/LSTM_final_enhanced_finance_historical.npy",
        "prepared_top_25/LSTM_final_enhanced_finance_recent.npy",
        "prepared_top_25/LSTM_final_enhanced_health_historical.npy",
        "prepared_top_25/LSTM_final_enhanced_health_recent.npy",
        "prepared_top_25/LSTM_final_enhanced_tech_historical.npy",
        "prepared_top_25/LSTM_final_enhanced_tech_recent.npy"
    ]

    rf_files = [
        "prepared_top_25/RandomForest_final_enhanced_finance_historical.csv.npy",
        "prepared_top_25/RandomForest_final_enhanced_finance_recent.csv.npy",
        "prepared_top_25/RandomForest_final_enhanced_health_historical.csv.npy",
        "prepared_top_25/RandomForest_final_enhanced_health_recent.csv.npy",
        "prepared_top_25/RandomForest_final_enhanced_tech_historical.csv.npy",
        "prepared_top_25/RandomForest_final_enhanced_tech_recent.csv.npy"
    ]

    # Targets files (assume shared for all datasets)
    lstm_targets_file = "prepared_data/lstm_y.npy"
    rf_targets_file = "prepared_data/random_forest_y.npy"

    # Process all datasets
    process_all_datasets(lstm_files, rf_files, lstm_targets_file, rf_targets_file)
