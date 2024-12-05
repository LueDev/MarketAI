import pandas as pd
import numpy as np
import os
import joblib
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer

def rolling_window_backtest(data_path, model_path, window_size=30, step_size=1):
    """
    Perform rolling window backtesting using the specified data and model.
    """
    # Load the dataset
    df = pd.read_csv(data_path)

    # Ensure 'Date' is excluded or processed
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])  # Convert to datetime for any potential use
        df.drop(columns=['Date'], inplace=True)  # Drop the Date column for model input

    # Encode the Ticker column
    if 'Ticker' in df.columns:
        encoder = OneHotEncoder(sparse=False, handle_unknown='ignore')
        ticker_encoded = encoder.fit_transform(df[['Ticker']])
        ticker_df = pd.DataFrame(
            ticker_encoded, 
            columns=encoder.get_feature_names_out(['Ticker'])
        )
        df = pd.concat([df.drop(columns=['Ticker']), ticker_df], axis=1)

    # Extract features and target
    X = df.drop(columns=['Close']).values  # Exclude 'Close' as it's the target
    y = df['Close'].values

    # Scale features
    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    # Load the trained model
    model = joblib.load(model_path)

    # Rolling window evaluation
    mse_list, mae_list, r2_list = [], [], []
    for start_idx in range(0, len(X) - window_size, step_size):
        end_idx = start_idx + window_size
        X_train, y_train = X[start_idx:end_idx], y[start_idx:end_idx]
        X_test, y_test = X[end_idx:end_idx + step_size], y[end_idx:end_idx + step_size]

        if len(X_test) == 0:
            break  # Skip if no test data available

        # Fit the model on the rolling window training set
        model.fit(X_train, y_train)

        # Predict on the test set
        y_pred = model.predict(X_test)

        # Calculate metrics
        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        mse_list.append(mse)
        mae_list.append(mae)
        r2_list.append(r2)

    # Aggregate results
    avg_mse = np.mean(mse_list)
    avg_mae = np.mean(mae_list)
    avg_r2 = np.mean(r2_list)

    print(f"Backtest Results - MSE: {avg_mse:.4f}, MAE: {avg_mae:.4f}, R2: {avg_r2:.4f}")

if __name__ == "__main__":
    data_files = [
        "data/final_enhanced_top25_finance_historical.csv",
        "data/final_enhanced_top25_health_historical.csv",
        "data/final_enhanced_top25_tech_historical.csv",
    ]

    model_files = [
        "trained_meta_model/xgboost_meta_model_final_enhanced_finance_historical.joblib",
        "trained_meta_model/xgboost_meta_model_final_enhanced_health_historical.joblib",
        "trained_meta_model/xgboost_meta_model_final_enhanced_tech_historical.joblib",
    ]

    for data_path, model_path in zip(data_files, model_files):
        print(f"Evaluating dataset: {os.path.basename(data_path)}")
        rolling_window_backtest(data_path, model_path)
