import pandas as pd
import joblib
import os
from train_rf_multi_output import calculate_derived_features

def recursive_forecast(model_path, initial_data, steps=60):
    model = joblib.load(model_path)
    forecast_data = initial_data.copy()

    predictions = []
    for step in range(steps):
        # Predict core features
        prediction = model.predict(forecast_data[["Open", "High", "Low", "Volume"]].iloc[-1:])
        prediction_df = pd.DataFrame(prediction, columns=["Close"])
        prediction_df[["Open", "High", "Low", "Volume"]] = forecast_data[["Open", "High", "Low", "Volume"]].iloc[-1:].values

        # Calculate derived features
        prediction_df = calculate_derived_features(prediction_df)
        predictions.append(prediction_df)

        # Add prediction to forecast_data for the next iteration
        forecast_data = pd.concat([forecast_data, prediction_df], ignore_index=True)

    return pd.concat(predictions, ignore_index=True)

# Example usage in main
def main():
    model_path = "models/rf_finance_historical.joblib"
    initial_data_path = "path_to_initial_data.csv"
    initial_data = pd.read_csv(initial_data_path)

    forecast = recursive_forecast(model_path, initial_data)
    print(forecast)

if __name__ == "__main__":
    main()
