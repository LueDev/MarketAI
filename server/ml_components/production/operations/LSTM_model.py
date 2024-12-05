import os
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
from tensorflow.keras.regularizers import l2
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split
import argparse

class LSTMModel:
    def __init__(self, sequence_length=200):
        self.sequence_length = sequence_length
        self.model = self.build_model()
        print("LSTM model initialized with additional regularization.")

    def load_and_preprocess_data(self, data_file):
        print(f"Loading and preprocessing data from: {data_file}")

        # Load data from CSV
        df = pd.read_csv(data_file)

        # Drop non-numeric columns like 'Date' and 'Ticker'
        df.drop(columns=['Date', 'Ticker'], inplace=True, errors='ignore')
        df.fillna(df.mean(), inplace=True)

        # Create sequences for LSTM (use sliding window technique)
        features = df.drop(columns=['Close']).values  # Exclude 'Close' from input features
        target = df['Close'].values  # 'Close' is the target variable

        X, y = [], []
        for i in range(len(features) - self.sequence_length):
            X.append(features[i:i + self.sequence_length])
            y.append(target[i + self.sequence_length])

        X = np.array(X)
        y = np.array(y)

        print(f"Generated {len(X)} sequences for LSTM model.")
        return train_test_split(X, y, test_size=0.2, random_state=42)

    def build_model(self):
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=(self.sequence_length, 24), kernel_regularizer=l2(0.001)),
            Dropout(0.2),
            LSTM(50, return_sequences=False, kernel_regularizer=l2(0.001)),
            Dropout(0.2),
            Dense(25),
            Dense(1)
        ])
        model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mean_absolute_error'])
        print("Model built and compiled with dropout and L2 regularization.")
        return model

    def train_model(self, X_train, y_train, epochs=20, batch_size=32):
        print("Training model...")
        self.model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_split=0.1)
        print("LSTM model training complete.")

    def evaluate_model(self, X_test, y_test):
        print("Evaluating model...")
        predictions = self.model.predict(X_test)
        mse = mean_squared_error(y_test, predictions)
        mae = mean_absolute_error(y_test, predictions)
        print(f"Mean Squared Error on Test Set: {mse}")
        print(f"Mean Absolute Error on Test Set: {mae}")
        return mse, mae

    def save_model(self, model_path):
        self.model.save(model_path)
        print(f"Model saved to {model_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train LSTM model per stock.")
    parser.add_argument("--data_file", required=True, help="Path to the stock-specific data file.")
    parser.add_argument("--output_dir", required=True, help="Directory to save the trained model.")
    args = parser.parse_args()

    lstm_model = LSTMModel(sequence_length=200)
    X_train, X_test, y_train, y_test = lstm_model.load_and_preprocess_data(args.data_file)
    lstm_model.train_model(X_train, y_train, epochs=20, batch_size=32)
    mse, mae = lstm_model.evaluate_model(X_test, y_test)

    model_path = os.path.join(args.output_dir, "lstm_model.h5")
    lstm_model.save_model(model_path)
