import pandas as pd
import pandas_ta as ta
import numpy as np
import os

class DataEnhancer:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.columns = [
            'Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Ticker', 'MA_10', 'MA_50',
            'Volatility', 'RSI', 'MACD', 'MACD_Signal', 'MACD_Hist', 'Stochastic',
            'Williams %R', 'BB_Lower', 'BB_Middle', 'BB_Upper', 'EMA_10', 'EMA_50',
            'Parabolic_SAR', 'OBV', 'VWAP', 'Pivot', 'R1', 'S1'
        ]

    def preprocess_data(self, df):
        # Remove duplicates based on 'Date' and 'Ticker'
        df = df.drop_duplicates(subset=['Date', 'Ticker'])
        
        # Convert 'Ticker' and any other non-numeric columns to string types
        df['Ticker'] = df['Ticker'].astype(str)
        
        # Identify numeric columns for targeted NaN filling
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        # Fill NaN values for each numeric column individually
        for col in numeric_cols:
            df[col].fillna(df[col].mean(), inplace=True)
        
        return df

    def add_indicators(self, df):
        # Technical indicators
        df['RSI'] = ta.rsi(df['Close'], length=14)
        macd = ta.macd(df['Close'], fast=12, slow=26, signal=9)
        df['MACD'], df['MACD_Signal'], df['MACD_Hist'] = macd['MACD_12_26_9'], macd['MACDs_12_26_9'], macd['MACDh_12_26_9']
        df['Stochastic'] = ta.stoch(df['High'], df['Low'], df['Close'])['STOCHk_14_3_3']
        
        lookback = 14
        df['Williams %R'] = ((df['High'].rolling(window=lookback).max() - df['Close']) /
                            (df['High'].rolling(window=lookback).max() - df['Low'].rolling(window=lookback.min()))) * -100
        
        bbands = ta.bbands(df['Close'], length=20, std=2)
        df['BB_Lower'], df['BB_Middle'], df['BB_Upper'] = bbands['BBL_20_2.0'], bbands['BBM_20_2.0'], bbands['BBU_20_2.0']
        
        df['EMA_10'], df['EMA_50'] = ta.ema(df['Close'], length=10), ta.ema(df['Close'], length=50)
        df['Parabolic_SAR'] = ta.psar(df['High'], df['Low'], df['Close'], af=0.02, max_af=0.2)['PSARl_0.02_0.2']
        df['OBV'] = ta.obv(df['Close'], df['Volume'])
        df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'], anchor="D")

        # Calculate Pivot Points, R1, and S1
        df['Pivot'] = (df['High'] + df['Low'] + df['Close']) / 3
        df['R1'] = 2 * df['Pivot'] - df['Low']
        df['S1'] = 2 * df['Pivot'] - df['High']

        return df[self.columns]

    def enhance_and_save(self, input_file, output_file):
        # Load, preprocess, and enhance data
        df = pd.read_csv(input_file, parse_dates=['Date'])
        df = self.preprocess_data(df)
        df = self.add_indicators(df)
        df.to_csv(output_file, index=False)
        print(f"Enhanced data saved to {output_file}")

    def process_files(self, file_mapping):
        for input_file, output_file in file_mapping.items():
            print(f"Processing {input_file}...")
            self.enhance_and_save(input_file, output_file)

if __name__ == "__main__":
    data_dir = "./data"
    enhancer = DataEnhancer(data_dir)

    input_output_mapping = {
        os.path.join(data_dir, 'finance_historical.csv'): os.path.join(data_dir, 'final_enhanced_finance_historical.csv'),
        os.path.join(data_dir, 'finance_recent.csv'): os.path.join(data_dir, 'final_enhanced_finance_recent.csv'),
        os.path.join(data_dir, 'health_historical.csv'): os.path.join(data_dir, 'final_enhanced_health_historical.csv'),
        os.path.join(data_dir, 'health_recent.csv'): os.path.join(data_dir, 'final_enhanced_health_recent.csv'),
        os.path.join(data_dir, 'tech_historical.csv'): os.path.join(data_dir, 'final_enhanced_tech_historical.csv'),
        os.path.join(data_dir, 'tech_recent.csv'): os.path.join(data_dir, 'final_enhanced_tech_recent.csv'),
    }

    enhancer.process_files(input_output_mapping)
