import numpy as np
import pandas as pd
import joblib

def recursive_predict(model, X_init, steps):
    """
    Perform recursive multi-step predictions using RF model with all features.

    Args:
    - model: Trained Random Forest model.
    - X_init: Initial input as Pandas DataFrame (single row).
    - steps (int): Number of steps/days to predict.

    Returns:
    - DataFrame with predictions for all steps and features.
    """
    predictions = []
    current_input = X_init.copy()

    for _ in range(steps):
        # Predict next values
        pred = model.predict(current_input)
        predictions.append(pred[0])  # Save prediction

        # Update input for the next step
        current_input.iloc[0, :] = pred

    predictions_df = pd.DataFrame(predictions, columns=X_init.columns)
    return predictions_df

# Example usage
if __name__ == "__main__":
    # Load the model
    model_path = "models/rf_multi_output_finance_all_features.joblib"
    rf_model = joblib.load(model_path)

    # Load initial input (single row)
    data_path = "data/final_enhanced_finance_recent.csv"
    data = pd.read_csv(data_path)
    X_init = data.iloc[:1].drop(columns=["Date", "Close", "Ticker"])  # Exclude non-feature columns

    # Predict for next 10 days
    steps = 10
    future_predictions = recursive_predict(rf_model, X_init, steps)

    print("Future Predictions:")
    print(future_predictions)
