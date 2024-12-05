import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import joblib
import os
import argparse

class RandomForestModel:
    def __init__(self, data_file):
        self.data_file = data_file
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)

    def load_and_preprocess_data(self):
        df = pd.read_csv(self.data_file)
        
        # Drop non-numeric columns like Date and Ticker, but retain technical indicators
        df.drop(columns=['Date', 'Ticker'], inplace=True, errors='ignore')
        df.fillna(df.mean(), inplace=True)  # Fill any NaNs with mean for robust training

        # Features (X) and Target (y)
        X = df.drop(columns=['Close'])
        y = df['Close']

        return train_test_split(X, y, test_size=0.2, random_state=42)

    def train_model(self, X_train, y_train):
        self.model.fit(X_train, y_train)
        print("Random Forest model trained.")

    def evaluate_model(self, X_test, y_test):
        predictions = self.model.predict(X_test)
        mse = mean_squared_error(y_test, predictions)
        print(f"Mean Squared Error on Test Set: {mse}")
        return mse

    def save_model(self, model_path):
        joblib.dump(self.model, model_path)
        print(f"Model saved to {model_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Random Forest model per stock.")
    parser.add_argument("--data_file", required=True, help="Path to the stock-specific data file.")
    parser.add_argument("--output_dir", required=True, help="Directory to save the trained model.")
    args = parser.parse_args()

    rf_model = RandomForestModel(args.data_file)
    X_train, X_test, y_train, y_test = rf_model.load_and_preprocess_data()
    rf_model.train_model(X_train, y_train)
    rf_model.evaluate_model(X_test, y_test)

    model_path = os.path.join(args.output_dir, "random_forest_model.joblib")
    rf_model.save_model(model_path)
