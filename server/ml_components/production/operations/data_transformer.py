import pandas as pd
import numpy as np
import os
import pandas_ta as ta  # Pandas Technical Analysis library

class DataTransformer:
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def load_data(self, file_name):
        return pd.read_csv(os.path.join(self.input_dir, file_name), parse_dates=['Date'])

    def calculate_indicators(self, df):
        """
        Calculate all required technical indicators and add them as new columns.
        """
        # Calculate Moving Averages
        df['MA_10'] = df['Close'].rolling(window=10).mean()
        df['MA_50'] = df['Close'].rolling(window=50).mean()
        
        # Volatility (Standard Deviation over a rolling window)
        df['Volatility'] = df['Close'].rolling(window=10).std()
        
        # Relative Strength Index (RSI)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        # MACD and its components
        macd = ta.macd(df['Close'], fast=12, slow=26, signal=9)
        df['MACD'] = macd['MACD_12_26_9']
        df['MACD_Signal'] = macd['MACDs_12_26_9']
        df['MACD_Hist'] = macd['MACDh_12_26_9']
        
        # Stochastic Oscillator
        stoch = ta.stoch(df['High'], df['Low'], df['Close'])
        df['Stochastic'] = stoch['STOCHk_14_3_3']
        
        # Williams %R
        df['Williams %R'] = ta.willr(df['High'], df['Low'], df['Close'], length=14)
        
        # Bollinger Bands
        bb = ta.bbands(df['Close'], length=20, std=2)
        df['BB_Lower'] = bb['BBL_20_2.0']
        df['BB_Middle'] = bb['BBM_20_2.0']
        df['BB_Upper'] = bb['BBU_20_2.0']
        
        # Exponential Moving Averages
        df['EMA_10'] = ta.ema(df['Close'], length=10)
        df['EMA_50'] = ta.ema(df['Close'], length=50)
        
        # Parabolic SAR
        df['Parabolic_SAR'] = ta.psar(df['High'], df['Low'], df['Close'])['PSARl_0.02_0.2']
        
        # On-Balance Volume (OBV)
        df['OBV'] = ta.obv(df['Close'], df['Volume'])
        
        # Volume-Weighted Average Price (VWAP)
        df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
        
        # Pivot Points, Resistance, and Support
        df['Pivot'] = (df['High'] + df['Low'] + df['Close']) / 3
        df['R1'] = (2 * df['Pivot']) - df['Low']
        df['S1'] = (2 * df['Pivot']) - df['High']
        
        return df

    def transform_data(self, df):
        # Ensure all technical indicators are calculated
        df = self.calculate_indicators(df)
        
        # Drop NaN values created during rolling calculations
        df = df.dropna().reset_index(drop=True)
        
        # Filter to include only required columns
        required_columns = [
            'Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Ticker', 'MA_10', 'MA_50', 'Volatility',
            'RSI', 'MACD', 'MACD_Signal', 'MACD_Hist', 'Stochastic', 'Williams %R',
            'BB_Lower', 'BB_Middle', 'BB_Upper', 'EMA_10', 'EMA_50', 'Parabolic_SAR', 'OBV', 'VWAP',
            'Pivot', 'R1', 'S1'
        ]
        return df[required_columns]

    def save_data(self, df, file_name):
        file_path = os.path.join(self.output_dir, file_name)
        df.to_csv(file_path, index=False)
        print(f"Transformed data saved to {file_path}")

    def process_all_files(self):
        for file_name in os.listdir(self.input_dir):
            if file_name.endswith(".csv"):
                df = self.load_data(file_name)
                df = self.transform_data(df)
                self.save_data(df, file_name)

if __name__ == "__main__":
    input_dir = "./ml_components/production/data"
    output_dir = "./ml_components/production/data/transformed"

    transformer = DataTransformer(input_dir, output_dir)
    transformer.process_all_files()
