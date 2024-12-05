import torch
import torch.nn as nn
from joblib import load
import tensorflow as tf
import os


class LSTMModel(nn.Module):
    """
    Defines a PyTorch LSTM model for time series forecasting.
    """
    def __init__(self, input_size, hidden_size=50, num_layers=2, output_size=1):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        last_output = lstm_out[:, -1, :]
        return self.fc(last_output)


class RandomForestModel:
    """
    Wrapper for a Random Forest model loaded from a .joblib file.
    """
    def __init__(self, model_path):
        self.model = load(model_path)

    def predict(self, X):
        return self.model.predict(X)


def load_pytorch_lstm_model(sector, timeframe, input_size, production_dir="./ml_components/production/models"):
    """
    Load a PyTorch LSTM model for the specified sector and timeframe.
    """
    model_path = os.path.join(production_dir, sector, f"{timeframe}_model.pth")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"PyTorch LSTM model not found at {model_path}")

    model = LSTMModel(input_size)
    model.load_state_dict(torch.load(model_path))
    model.eval()
    return model


def load_h5_lstm_model(sector, timeframe, production_dir="./ml_components/production/models"):
    """
    Load a Keras (TensorFlow) LSTM model for the specified sector and timeframe.
    """
    model_path = os.path.join(production_dir, f"lstm_model_LSTM_final_enhanced_{sector}_{timeframe}.h5")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"H5 LSTM model not found at {model_path}")

    return tf.keras.models.load_model(model_path)


def load_random_forest_model(sector, ticker=None, production_dir="./ml_components/production/models"):
    """
    Load a Random Forest model, either sector-wide or per stock.
    """
    if ticker:
        model_path = os.path.join(production_dir, f"{sector}_top25_models", ticker, "random_forest", "random_forest_model.joblib")
    else:
        model_path = os.path.join(production_dir, "random_forest_model.joblib")

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Random Forest model not found at {model_path}")

    return RandomForestModel(model_path)


def predict_with_all_models(sector, ticker, timeframe, data, production_dir="./ml_components/production/models"):
    """
    Generate predictions using all relevant models for the given stock.

    :param sector: The sector of the stock (e.g., 'finance', 'health', 'tech').
    :param ticker: The stock ticker symbol (e.g., 'AAPL').
    :param timeframe: The timeframe of the prediction ('historical' or 'recent').
    :param data: The input data for prediction.
    :param production_dir: Path to the production models directory.
    :return: A dictionary with predictions from all relevant models.
    """
    predictions = {}

    # Load and predict with sector-wide LSTM (h5) model
    try:
        sector_lstm_model = load_h5_lstm_model(sector, timeframe, production_dir)
        predictions["sector_lstm"] = sector_lstm_model.predict(data).flatten().tolist()
    except FileNotFoundError as e:
        predictions["sector_lstm"] = str(e)

    # Load and predict with per-stock LSTM (PyTorch) model
    try:
        input_size = data.shape[1]
        stock_lstm_model = load_pytorch_lstm_model(sector, timeframe, input_size, production_dir)
        data_tensor = torch.tensor(data).float()
        with torch.no_grad():
            predictions["stock_lstm"] = stock_lstm_model(data_tensor).numpy().flatten().tolist()
    except FileNotFoundError as e:
        predictions["stock_lstm"] = str(e)

    # Load and predict with sector-wide Random Forest model
    try:
        sector_rf_model = load_random_forest_model(sector, production_dir=production_dir)
        predictions["sector_rf"] = sector_rf_model.predict(data).tolist()
    except FileNotFoundError as e:
        predictions["sector_rf"] = str(e)

    # Load and predict with per-stock Random Forest model
    try:
        stock_rf_model = load_random_forest_model(sector, ticker, production_dir)
        predictions["stock_rf"] = stock_rf_model.predict(data).tolist()
    except FileNotFoundError as e:
        predictions["stock_rf"] = str(e)

    return predictions
