import pandas as pd
import numpy as np
import os
from tensorflow.keras.preprocessing.sequence import pad_sequences

class DataPreparer:
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def load_data(self, file_name):
        return pd.read_csv(os.path.join(self.input_dir, file_name), parse_dates=['Date'])

    def save_data(self, data, file_name):
        np.save(os.path.join(self.output_dir, file_name), data)

    def prepare_data_for_random_forest(self, df):
        """
        Prepares data for Random Forest models by excluding date and ticker columns.
        """
        return df.drop(columns=['Date', 'Ticker']).values

    def prepare_data_for_lstm(self, df):
        """
        Prepares data for LSTM models by normalizing all numerical columns and padding sequences.
        """
        # Columns to normalize
        columns_to_normalize = [
            'Open', 'High', 'Low', 'Close', 'Volume', 'MA_10', 'MA_50', 'Volatility', 'RSI', 
            'MACD', 'MACD_Signal', 'MACD_Hist', 'Stochastic', 'Williams %R', 'BB_Lower', 
            'BB_Middle', 'BB_Upper', 'EMA_10', 'EMA_50', 'Parabolic_SAR', 'OBV', 'VWAP', 
            'Pivot', 'R1', 'S1'
        ]
        
        # Normalize the data
        df[columns_to_normalize] = df[columns_to_normalize].apply(lambda x: (x - x.min()) / (x.max() - x.min()))
        
        # Group data by ticker
        tickers = df['Ticker'].unique()
        prepared_data = []
        
        # Maximum sequence length
        max_sequence_length = 200
        
        for ticker in tickers:
            ticker_data = df[df['Ticker'] == ticker].sort_values(by='Date')
            ticker_data = ticker_data[columns_to_normalize].values
            prepared_data.append(ticker_data)

        # Pad sequences to ensure uniform length
        padded_data = pad_sequences(prepared_data, maxlen=max_sequence_length, padding='post', dtype='float32')
        
        return np.array(padded_data)

    def process_all_files(self):
        for file_name in os.listdir(self.input_dir):
            if file_name.endswith(".csv"):
                df = self.load_data(file_name)

                # Prepare Random Forest data
                rf_data = self.prepare_data_for_random_forest(df)
                self.save_data(rf_data, f"RandomForest_{file_name.replace('.csv', '.npy')}")
                print(f"Random Forest data saved for {file_name}")

                # Prepare LSTM data
                lstm_data = self.prepare_data_for_lstm(df)
                self.save_data(lstm_data, f"LSTM_{file_name.replace('.csv', '.npy')}")
                print(f"LSTM data saved for {file_name}")

if __name__ == "__main__":
    input_dir = "./ml_components/production/data/transformed"
    output_dir = "./ml_components/production/data/prepared"

    preparer = DataPreparer(input_dir, output_dir)
    preparer.process_all_files()
