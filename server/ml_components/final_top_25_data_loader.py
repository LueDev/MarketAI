import pandas as pd
import pandas_ta as ta
import numpy as np
import os

class Top25DataEnhancer:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.columns = [
            'Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Ticker', 'MA_10', 'MA_50',
            'Volatility', 'RSI', 'MACD', 'MACD_Signal', 'MACD_Hist', 'Stochastic',
            'Williams %R', 'BB_Lower', 'BB_Middle', 'BB_Upper', 'EMA_10', 'EMA_50',
            'Parabolic_SAR', 'OBV', 'VWAP', 'Pivot', 'R1', 'S1'
        ]

    def preprocess_data(self, df):
        # Group by 'Ticker' and 'Date', taking the first occurrence if duplicates exist
        df = df.groupby(['Ticker', 'Date']).first().reset_index()

        # Convert 'Ticker' to string to avoid errors
        df['Ticker'] = df['Ticker'].astype(str)

        # Fill NaNs in numeric columns only
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = df[numeric_cols].apply(lambda x: x.fillna(x.mean()), axis=0)

        return df

    def add_indicators(self, df):
        # Ensure Date is a regular column, not an index
        df = df.reset_index(drop=True)

        # Technical indicators
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        macd = ta.macd(df['Close'], fast=12, slow=26, signal=9)
        df['MACD'] = macd['MACD_12_26_9']
        df['MACD_Signal'] = macd['MACDs_12_26_9']
        df['MACD_Hist'] = macd['MACDh_12_26_9']
        
        df['Stochastic'] = ta.stoch(df['High'], df['Low'], df['Close'])['STOCHk_14_3_3']
        
        lookback = 14
        # Calculate rolling max and min for Williams %R
        rolling_high = df['High'].rolling(window=lookback).max()
        rolling_low = df['Low'].rolling(window=lookback).min()
        df['Williams %R'] = ((rolling_high - df['Close']) / (rolling_high - rolling_low)) * -100
        
        bbands = ta.bbands(df['Close'], length=20, std=2)
        df['BB_Lower'] = bbands['BBL_20_2.0']
        df['BB_Middle'] = bbands['BBM_20_2.0']
        df['BB_Upper'] = bbands['BBU_20_2.0']
        
        df['EMA_10'] = ta.ema(df['Close'], length=10)
        df['EMA_50'] = ta.ema(df['Close'], length=50)
        df['Parabolic_SAR'] = ta.psar(df['High'], df['Low'], df['Close'], af=0.02, max_af=0.2)['PSARl_0.02_0.2']
        df['OBV'] = ta.obv(df['Close'], df['Volume'])
        
        # Set Date as the index for VWAP calculation, ensuring it is in datetime format
        df.set_index('Date', inplace=True)
        df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
        df.reset_index(inplace=True)  # Reset index back to default after VWAP calculation

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
    enhancer = Top25DataEnhancer(data_dir)

    input_output_mapping = {
        os.path.join(data_dir, 'top25_finance_historical.csv'): os.path.join(data_dir, 'final_enhanced_top25_finance_historical.csv'),
        os.path.join(data_dir, 'top25_enhanced_finance_recent.csv'): os.path.join(data_dir, 'final_enhanced_top25_finance_recent.csv'),
        os.path.join(data_dir, 'top25_enhanced_health_historical.csv'): os.path.join(data_dir, 'final_enhanced_top25_health_historical.csv'),
        os.path.join(data_dir, 'top25_enhanced_health_recent.csv'): os.path.join(data_dir, 'final_enhanced_top25_health_recent.csv'),
        os.path.join(data_dir, 'top25_enhanced_tech_historical.csv'): os.path.join(data_dir, 'final_enhanced_top25_tech_historical.csv'),
        os.path.join(data_dir, 'top25_enhanced_tech_recent.csv'): os.path.join(data_dir, 'final_enhanced_top25_tech_recent.csv'),
    }

    enhancer.process_files(input_output_mapping)
