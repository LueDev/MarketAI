import pandas as pd
import os

class DataTransformer:
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir

    def load_data(self, file_name):
        df = pd.read_csv(os.path.join(self.input_dir, file_name), parse_dates=['Date'])
        return df

    def transform_data(self, df):
        # Ensure all technical indicators are preserved
        required_columns = [
            'Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Ticker', 'MA_10', 'MA_50', 'Volatility',
            'RSI', 'MACD', 'MACD_Signal', 'MACD_Hist', 'Stochastic', 'Williams %R', 
            'BB_Lower', 'BB_Middle', 'BB_Upper', 'EMA_10', 'EMA_50', 'Parabolic_SAR', 'OBV', 'VWAP', 
            'Pivot', 'R1', 'S1'
        ]
        # Filter only columns needed for model training to avoid loss of important indicators
        df = df[required_columns]
        # Any further transformation steps, such as normalization or outlier handling, go here
        return df

    def save_data(self, df, file_name):
        df.to_csv(os.path.join(self.output_dir, file_name), index=False)
        print(f"Transformed data saved to {os.path.join(self.output_dir, file_name)}")

    def process_file(self, file_name):
        df = self.load_data(file_name)
        df = self.transform_data(df)
        self.save_data(df, file_name)

if __name__ == "__main__":
    input_dir = "./data"  # Change to the directory where your final_enhanced_top25_*.csv files are
    output_dir = "./transformed_top_25"
    os.makedirs(output_dir, exist_ok=True)

    transformer = DataTransformer(input_dir, output_dir)
    files = [
        'final_enhanced_finance_historical.csv', 'final_enhanced_finance_recent.csv',
        'final_enhanced_health_historical.csv', 'final_enhanced_health_recent.csv',
        'final_enhanced_tech_historical.csv', 'final_enhanced_tech_recent.csv'
    ]

    for file in files:
        transformer.process_file(file)
