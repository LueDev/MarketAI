from sklearn.preprocessing import StandardScaler
import pandas as pd

def transform_enhanced_data(df):
    # Select relevant columns for model training
    # For example, include the technical indicators along with necessary stock info
    features = [
        'Open', 'High', 'Low', 'Close', 'Volume', 
        'MA_10', 'MA_50', 'Volatility', 'RSI', 'MACD', 'MACD_Signal', 'MACD_Hist', 
        'Stochastic', 'Williams %R', 'BB_Lower', 'BB_Middle', 'BB_Upper', 
        'EMA_10', 'EMA_50', 'Parabolic_SAR', 'OBV', 'VWAP', 'Pivot', 'R1', 'S1'
    ]
    
    # Extract only the selected features
    df_features = df[features]

    # Initialize the scaler and fit-transform the features
    scaler = StandardScaler()  # Or MinMaxScaler() for 0-1 scaling
    df_scaled = scaler.fit_transform(df_features)

    # Convert the scaled data back into a DataFrame for compatibility
    df_scaled = pd.DataFrame(df_scaled, columns=features)

    # Return the scaled DataFrame and the scaler (for inverse transformations if needed)
    return df_scaled, scaler
