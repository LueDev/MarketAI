from flask import request, jsonify
from flask_restful import Resource
import pandas as pd
import numpy as np
from joblib import load
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import os
from concurrent.futures import ThreadPoolExecutor
from utils.redis_helper import get_from_cache, set_to_cache
from datetime import datetime
import json
from resources.data_resource import DataFetchResource
import logging

# Cache expiration for predictions
PREDICTION_CACHE_EXPIRY = 86400  # 24 hours
DEFAULT_BATCH_SIZE = 2000  # Default batch size for predictions

# Utility functions for model paths
def get_model_path(sector, timeframe):
    """
    Returns the absolute path to the model based on sector and timeframe.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_dir = os.path.join(base_dir, '../ml_components/RF_multi_output/models')
    model_file = f"rf_{sector}_{timeframe}.joblib"
    return os.path.join(model_dir, model_file)

def evaluate_predictions(y_true, y_pred):
    """
    Calculates evaluation metrics for the predictions.
    """
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    return mae, mse, r2

def identify_sector(stock_name):
    """
    Maps stock tickers to their respective sectors.
    """
    tech_stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "ADBE", "AVGO", "CRM", "INTC", "AMD", "CSCO", "QCOM", "TXN", "INTU", "ORCL", "IBM", "V", "PYPL", "ADI", "SNOW", "SHOP", "NOW", "SQ", "MA"]
    finance_stocks = ["JPM", "BAC", "WFC", "GS", "MS", "PNC", "USB", "AXP", "RY", "TD", "SPGI", "CB", "CME", "MET", "ICE", "HSBC", "MCO", "SCHW", "COF", "C", "BLK", "BNS", "MUFG", "BMO", "CINF"]
    health_stocks = ["JNJ", "PFE", "MRK", "TMO", "UNH", "ABBV", "LLY", "BMY", "AMGN", "CVS", "MDT", "ABT", "SYK", "DHR", "BSX", "GILD", "HCA", "EW", "REGN", "CI", "IQV", "ILMN", "HUM", "ZBH", "BAX"]

    if stock_name in tech_stocks:
        return "tech"
    elif stock_name in finance_stocks:
        return "finance"
    elif stock_name in health_stocks:
        return "health"
    else:
        raise ValueError(f"Unknown sector for stock: {stock_name}")
    
# Utility function to update derived features
def update_derived_features(data):
    """
    Recalculates derived features (e.g., moving averages, RSI, MACD, etc.) dynamically
    to include new predictions or updates.
    """
    # Moving averages
    data["MA_10"] = data["Close"].rolling(window=10).mean()
    data["MA_50"] = data["Close"].rolling(window=50).mean()

    # Volatility
    data["Volatility"] = data["Close"].rolling(window=10).std()

    # Relative Strength Index (RSI)
    delta = data["Close"].diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
    rs = gain / loss
    data["RSI"] = 100 - (100 / (1 + rs))

    # MACD and Signal Line
    ema_12 = data["Close"].ewm(span=12, adjust=False).mean()
    ema_26 = data["Close"].ewm(span=26, adjust=False).mean()
    data["MACD"] = ema_12 - ema_26
    data["MACD_Signal"] = data["MACD"].ewm(span=9, adjust=False).mean()

    # Bollinger Bands
    rolling_mean = data["Close"].rolling(window=20).mean()
    rolling_std = data["Close"].rolling(window=20).std()
    data["BB_Lower"] = rolling_mean - (2 * rolling_std)
    data["BB_Middle"] = rolling_mean
    data["BB_Upper"] = rolling_mean + (2 * rolling_std)

    # Williams %R
    high_14 = data["High"].rolling(window=14).max()
    low_14 = data["Low"].rolling(window=14).min()
    data["Williams %R"] = ((high_14 - data["Close"]) / (high_14 - low_14)) * -100

    # Fill missing values for new rows
    data.fillna(method="ffill", inplace=True)
    data.fillna(method="bfill", inplace=True)
    data.fillna(0, inplace=True)

    return data

class AnalysisPredictResource(Resource):
    def post(self):
        """
        Endpoint for predicting stock prices using a Random Forest model.
        """
        try:
            # Parse request data
            data = request.get_json()
            stock_name = data.get("stock_name")
            days_out = data.get("days_out", 30)
            noise_level = data.get("noise_level", 0.000000000016180339887) 
            
            # Validate inputs
            if not stock_name:
                return {"error": "Stock name is required"}, 400
            if not (1 <= days_out <= 180):
                return {"error": "Days out must be between 1 and 180."}, 400
            if not (0 <= noise_level <= 1):
                return {"error": "Noise level must be between 0 and 1."}, 400

            # Identify sector
            sector = identify_sector(stock_name)

            # Paths for historical and recent models
            historical_model_path = get_model_path(sector, "historical")
            recent_model_path = get_model_path(sector, "recent")

            # Check model existence
            if not os.path.exists(historical_model_path) or not os.path.exists(recent_model_path):
                return {"error": f"Model(s) not found for sector: {sector}"}, 404

            # Load models
            historical_model = load(historical_model_path)
            recent_model = load(recent_model_path)

            # Retrieve transformed data
            transformed_cache_key = f"market_ai:stock_data:transformed_data:{stock_name}"
            transformed_data = get_from_cache(transformed_cache_key)
            if transformed_data is None:
                data_fetcher = DataFetchResource()
                raw_data = data_fetcher.fetch_raw_data(stock_name, period="max", interval="1d")
                transformed_data = data_fetcher.transform_data(raw_data)
                set_to_cache(transformed_cache_key, transformed_data, ttl=PREDICTION_CACHE_EXPIRY)

            # Prepare input data
            input_data = transformed_data.iloc[-1:].drop(columns=["Date"], errors="ignore")
            input_data.fillna(input_data.mean(), inplace=True)
            input_data = input_data.reindex(columns=historical_model.feature_names_in_, fill_value=0)

            # Predictions with noise
            predictions_historical = []
            predictions_recent = []

            for day in range(1, days_out + 1):
                # Predict the next close price
                next_close_historical = historical_model.predict(input_data.to_numpy())[0]
                next_close_recent = recent_model.predict(input_data.to_numpy())[0]

                # Calculate 10-day rolling volatility. This will be the second factor to noise to keep it aligned with the stock's natural movement/trading activity.
                # using 90 days (1 fiscal quarter) of rolled volatility as a strong basis
                volatility = transformed_data["Close"].rolling(window=90).std().iloc[-1]
                if np.isnan(volatility) or volatility == 0:
                    volatility = 0.01  # Default small volatility for stability

                # Introduce noise proportional to volatility using the golden ratio ϕ= (1+√5)/2=1.6180339887. This is a natural number and I think would be best for natural progression of noise.
                scale_factor_historical = np.random.uniform(0.0000000000016180339887, 1.0)  
                scale_factor_recent = np.random.uniform(0.0000000000016180339887, 1.0)  

                noise_historical = np.random.normal(0, scale_factor_historical * (volatility / 1.6180339887 ** 2))
                noise_recent = np.random.normal(0, scale_factor_recent * (volatility / 1.6180339887 ** 2))

                next_close_historical += noise_historical
                next_close_recent += noise_recent

                # Append predictions with noise
                predictions_historical.append(next_close_historical)
                predictions_recent.append(next_close_recent)

                # Update input data for the next prediction
                new_row = input_data.copy()
                new_row["Close"] = next_close_historical
                transformed_data = pd.concat([transformed_data, new_row], ignore_index=True)
                transformed_data = update_derived_features(transformed_data)
                input_data = transformed_data.iloc[-1:].drop(columns=["Date"], errors="ignore")
                input_data = input_data.reindex(columns=historical_model.feature_names_in_, fill_value=0)

            # Cache results
            historical_cache_key = f"market_ai:predictions:{stock_name}:historical:{days_out}"
            recent_cache_key = f"market_ai:predictions:{stock_name}:recent:{days_out}"
            set_to_cache(historical_cache_key, predictions_historical, ttl=PREDICTION_CACHE_EXPIRY)
            set_to_cache(recent_cache_key, predictions_recent, ttl=PREDICTION_CACHE_EXPIRY)

            return {
                "stock_name": stock_name,
                "historical_predictions": predictions_historical,
                "recent_predictions": predictions_recent,
            }, 200

        except Exception as e:
            logging.error(f"Error during prediction: {e}")
            return {"error": f"An error occurred: {str(e)}"}, 500


    def parallel_predictions(input_data, model_path, batch_size=DEFAULT_BATCH_SIZE):
        """
        Use parallel computation for batch predictions of single-target models.

        Args:
            input_data (np.ndarray): Input data for predictions.
            model_path (str): Path to the pre-trained model.
            batch_size (int): Number of samples per batch.

        Returns:
            np.ndarray: Flattened array of predicted Close prices.
        """
        # Ensure input_data is a NumPy array
        input_data = np.array(input_data) if not isinstance(input_data, np.ndarray) else input_data
        logging.info(f"Input data shape: {input_data.shape}, Type: {type(input_data)}")

        def predict_batch(data_batch):
            """
            Load a model and predict a batch of data.
            """
            model = load(model_path)
            return model.predict(data_batch)

        try:
            # Split input data into batches
            batches = [input_data[i:i + batch_size] for i in range(0, len(input_data), batch_size)]

            with ThreadPoolExecutor() as executor:
                # Submit tasks for predictions
                futures = [executor.submit(predict_batch, batch) for batch in batches]

                # Gather results
                predictions = np.concatenate([future.result() for future in futures])

            logging.info(f"Predictions shape: {predictions.shape}, Type: {type(predictions)}")
            return predictions
        except Exception as e:
            logging.error(f"Error during parallel predictions: {str(e)}")
            raise RuntimeError(f"Error during parallel predictions: {str(e)}")

    def extract_core_features(self, predictions):
        """
        Extract core features (Close, High, Low, Volume) from predictions.

        Args:
            predictions (np.ndarray): Predicted values with multiple columns.

        Returns:
            dict: Extracted features in dictionary format.
        """
        if predictions.ndim != 2 or predictions.shape[1] < 4:
            raise ValueError("Predictions must be a 2D array with at least 4 columns.")
        return {
            "Close": predictions[:, 0].tolist(),
            "High": predictions[:, 1].tolist(),
            "Low": predictions[:, 2].tolist(),
            "Volume": predictions[:, 3].tolist()
        }

    def cache_management(cache_key, transformed_data, action="set", expiry=PREDICTION_CACHE_EXPIRY):
        """
        Manage caching operations (set/get/clear) for transformed data.

        Args:
            cache_key (str): Redis cache key.
            transformed_data (pd.DataFrame | None): Data to cache (if action is 'set').
            action (str): Action to perform: 'set', 'get', or 'clear'.
            expiry (int): Time-to-live for cache in seconds.

        Returns:
            pd.DataFrame | None: Retrieved data for 'get' action, or None for others.
        """
        try:
            if action == "set" and transformed_data is not None:
                cache_value = transformed_data.to_json(orient="records")
                set_to_cache(cache_key, cache_value, expiry)
                logging.info(f"Data successfully set to cache for key: {cache_key}")
            elif action == "get":
                cached_value = get_from_cache(cache_key)
                if cached_value:
                    return pd.DataFrame(json.loads(cached_value))
                logging.info(f"No data found in cache for key: {cache_key}")
            elif action == "clear":
                # Implement clearing cache logic if required
                pass
        except Exception as e:
            logging.error(f"Cache management failed for key {cache_key}: {e}")
            raise e
