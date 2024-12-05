import numpy as np

def load_and_process_lstm_predictions(lstm_file):
    """
    Load LSTM predictions and extract the final step for each sequence.
    """
    lstm_preds = np.load(lstm_file)
    print(f"LSTM Predictions Shape (raw): {lstm_preds.shape}")
    
    # Extract the final time step from each sequence
    lstm_final_preds = lstm_preds[:, -1, :]  # Shape: (datasets, features)
    print(f"LSTM Predictions Shape (processed): {lstm_final_preds.shape}")
    return lstm_final_preds

def load_and_process_rf_predictions(rf_file):
    """
    Load Random Forest predictions and reshape to match LSTM predictions.
    """
    rf_preds = np.load(rf_file)
    print(f"Random Forest Predictions Shape (raw): {rf_preds.shape}")
    
    # Reshape and aggregate (e.g., take mean for consistency)
    rf_preds_reshaped = rf_preds.reshape(5, -1, rf_preds.shape[-1]).mean(axis=1)
    print(f"Random Forest Predictions Shape (processed): {rf_preds_reshaped.shape}")
    return rf_preds_reshaped

def combine_predictions(lstm_final_preds, rf_preds_reshaped):
    """
    Combine LSTM and Random Forest predictions into a single feature matrix.
    """
    # Combine along the feature axis
    X_meta = np.hstack((lstm_final_preds, rf_preds_reshaped))
    print(f"Meta-Model Input Shape: {X_meta.shape}")
    return X_meta

def load_targets(targets_file):
    """
    Load the true targets for training or evaluation.
    """
    targets = np.load(targets_file)
    print(f"Targets Shape: {targets.shape}")
    return targets

def save_meta_model_data(X_meta, targets, output_dir="prepared_meta_data"):
    """
    Save the processed meta-model input features and targets.
    """
    # Create directory if not exists
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    np.save(f"{output_dir}/X_meta.npy", X_meta)
    np.save(f"{output_dir}/targets.npy", targets)
    print(f"Saved meta-model data to {output_dir}")

if __name__ == "__main__":
    # File paths (update with actual file paths)
    lstm_file = "/Users/luisjorge/code/Flatiron-Phase-5/MarketAI/server/ml_components/prepared_top_25/LSTM_final_enhanced_finance_historical.npy"
    rf_file = "/Users/luisjorge/code/Flatiron-Phase-5/MarketAI/server/ml_components/prepared_top_25/RandomForest_final_enhanced_finance_historical.csv.npy"
    targets_file = "/Users/luisjorge/code/Flatiron-Phase-5/MarketAI/server/ml_components/prepared_data/lstm_y.npy"  # Update to the actual targets file

    # Step 1: Process LSTM predictions
    lstm_final_preds = load_and_process_lstm_predictions(lstm_file)

    # Step 2: Process Random Forest predictions
    rf_preds_reshaped = load_and_process_rf_predictions(rf_file)

    # Step 3: Combine predictions
    X_meta = combine_predictions(lstm_final_preds, rf_preds_reshaped)

    # Step 4: Load targets
    targets = load_targets(targets_file)

    # Step 5: Save processed data
    save_meta_model_data(X_meta, targets)
