import pandas as pd
import numpy as np
import os
from tensorflow.keras.preprocessing.sequence import pad_sequences  # Import pad_sequences

class DataPreparer:
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir

    def load_data(self, file_name):
        df = pd.read_csv(os.path.join(self.input_dir, file_name), parse_dates=['Date'])
        return df

    def save_data(self, data, file_name):
        np.save(os.path.join(self.output_dir, file_name), data)

    def prepare_data_for_random_forest(self, df):
        # Random Forest preparation (no padding needed)
        return df.drop(columns=['Date', 'Ticker']).values

    def prepare_data_for_lstm(self, df):
        # Normalize the columns and retain all technical indicators
        columns_to_normalize = [
            'Open', 'High', 'Low', 'Close', 'Volume', 'MA_10', 'MA_50', 'Volatility', 'RSI', 
            'MACD', 'MACD_Signal', 'MACD_Hist', 'Stochastic', 'Williams %R', 'BB_Lower', 
            'BB_Middle', 'BB_Upper', 'EMA_10', 'EMA_50', 'Parabolic_SAR', 'OBV', 'VWAP', 'Pivot', 'R1', 'S1'
        ]
        
        # Normalize the data for LSTM training
        df[columns_to_normalize] = df[columns_to_normalize].apply(lambda x: (x - x.min()) / (x.max() - x.min()))
        
        # Group data by ticker, and prepare each ticker's data as a separate sequence
        tickers = df['Ticker'].unique()
        prepared_data = []
        
        max_sequence_length = 200  # Set your maximum sequence length as per model requirements
        
        for ticker in tickers:
            ticker_data = df[df['Ticker'] == ticker].sort_values(by='Date')
            ticker_data = ticker_data[columns_to_normalize].values
            prepared_data.append(ticker_data)

        # Pad sequences so that all sequences are of the same length
        padded_data = pad_sequences(prepared_data, maxlen=max_sequence_length, padding='post', dtype='float32')
        
        return np.array(padded_data)

    def process_file(self, file_name):
        df = self.load_data(file_name)
        
        # Prepare data for Random Forest and save
        rf_data = self.prepare_data_for_random_forest(df)
        rf_file_name = f"RandomForest_{file_name}"
        self.save_data(rf_data, rf_file_name)
        print(f"Random Forest data saved to {os.path.join(self.output_dir, rf_file_name)}")
        
        # Prepare data for LSTM and save
        lstm_data = self.prepare_data_for_lstm(df)
        lstm_file_name = f"LSTM_{file_name.replace('.csv', '.npy')}"
        self.save_data(lstm_data, lstm_file_name)
        print(f"LSTM data saved to {os.path.join(self.output_dir, lstm_file_name)}")

if __name__ == "__main__":
    input_dir = "./transformed_top_25"
    output_dir = "./prepared_top_25"
    preparer = DataPreparer(input_dir, output_dir)

    for file in os.listdir(input_dir):
        if file.endswith(".csv"):
            preparer.process_file(file)
