# ml_components/data_loader.py

import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader, TensorDataset
from sklearn.preprocessing import StandardScaler
import os

# Define the data directory path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIRECTORY = os.path.join(BASE_DIR, 'data')

class StockDataset(Dataset):
    def __init__(self, sector, timeframe, sequence_length=60):
        filename = f"{sector}_{timeframe}.csv"
        filepath = os.path.join(DATA_DIRECTORY, filename)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Data file not found: {filepath}")
        
        self.data = pd.read_csv(filepath)
        self.sequence_length = sequence_length
        self.scaler = StandardScaler()
        self.scaled_data = self.scaler.fit_transform(self.data[['Close']])

    def __len__(self):
        return len(self.data) - self.sequence_length

    def __getitem__(self, idx):
        seq = self.scaled_data[idx:idx + self.sequence_length]
        label = self.scaled_data[idx + self.sequence_length]
        return torch.tensor(seq, dtype=torch.float32), torch.tensor(label, dtype=torch.float32)

# Function to create DataLoader for a sector and timeframe
def create_dataloader(sector, timeframe, batch_size=32, sequence_length=60):
    filename = f"{sector}_{timeframe}.csv"
    data_path = os.path.join(DATA_DIRECTORY, filename)
    
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data file not found: {data_path}")
    
    # Load CSV and scale features
    df = pd.read_csv(data_path)
    feature_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'MA_10', 'MA_50', 'Volatility']
    if not all(col in df.columns for col in feature_columns):
        raise ValueError(f"Missing required columns: {feature_columns}")

    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df[feature_columns].values)

    # Create sequences and labels
    sequences = np.array([scaled_data[i:i + sequence_length] for i in range(len(scaled_data) - sequence_length)])
    labels = scaled_data[sequence_length:, 3]  # Use 'Close' as the target

    # Convert to tensors
    sequences = torch.tensor(sequences, dtype=torch.float32)
    labels = torch.tensor(labels, dtype=torch.float32)

    # Create DataLoader
    dataset = TensorDataset(sequences, labels)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    return dataloader
