# server/resources/data_resource.py

from flask import jsonify, abort, request
from flask_restful import Resource
import os
import json
import yfinance as yf
import pandas as pd
from config import redis_client
from utils.redis_helper import get_from_cache, set_to_cache
import logging

# Redis cache expiration
CACHE_EXPIRY = 86400  # 24 hours

# Logging configuration
logging.basicConfig(level=logging.INFO)

# Define the directory where data files are stored
DATA_DIRECTORY = os.path.join(os.path.dirname(__file__), '../ml_components/data')

# Valid periods and intervals for yFinance
VALID_PERIODS = {"1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"}
VALID_INTERVALS = {"1m", "2m", "5m", "15m", "30m", "60m", "1d", "5d", "1wk", "1mo", "3mo"}

# Utility function to get CSV path
def get_csv_path(sector, timeframe):
    return os.path.join(DATA_DIRECTORY, f"{sector}_{timeframe}.csv")

# Utility function to get JSON attribution path
def get_json_path(sector, data_type):
    return os.path.join(DATA_DIRECTORY, f"{sector}_{data_type}_attributions.json")


class BaseDataFetchResource(Resource):
    @staticmethod
    def fetch_and_cache(symbol, cache_key, fetch_function, transform_function=None):
        """
        Fetch data from cache or execute fetch_function and transform_function if not cached.

        Parameters:
            symbol (str): Stock ticker symbol.
            cache_key (str): Redis cache key.
            fetch_function (callable): Function to fetch raw data.
            transform_function (callable): Function to transform the fetched data.

        Returns:
            DataFrame: Cached or newly fetched/transformed data.
        """
        cached_data = get_from_cache(cache_key)
        if cached_data:
            try:
                return pd.DataFrame(json.loads(cached_data))
            except Exception as e:
                logging.error(f"Deserialization failed for {cache_key}: {e}")
                raise
        else:
            raw_data = fetch_function(symbol)
            transformed_data = transform_function(raw_data) if transform_function else raw_data
            set_to_cache(cache_key, transformed_data.to_json(orient="records"))
            return transformed_data


class DataFetchResource(Resource):
    def get(self, symbol):
        """
        Fetch and transform stock data simultaneously.
        """
        try:
            # Redis cache keys
            raw_cache_key = f"market_ai:stock_data:raw_data:{symbol}"
            transformed_cache_key = f"market_ai:stock_data:transformed_data:{symbol}"

            # Fetch raw and transformed data
            raw_data, transformed_data = self.fetch_and_transform(
                symbol, raw_cache_key, transformed_cache_key, self.fetch_raw_data, self.transform_data
            )

            return {
                "raw_data": raw_data.to_dict(orient="records"),
                "transformed_data": transformed_data.to_dict(orient="records")
            }, 200
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}, 500

    @staticmethod
    def fetch_raw_data(symbol, period="max", interval="1d"):
        """
        Fetch raw stock data using yfinance with the maximum available period.
        """
        stock = yf.Ticker(symbol)
        raw_data = stock.history(period=period, interval=interval).reset_index()
        if raw_data.empty:
            raise ValueError(f"No data available for stock: {symbol}")
        return raw_data[["Date", "Open", "High", "Low", "Close", "Volume"]]

    @staticmethod
    def transform_data(data):
        """
        Add derived features to the raw data, ensuring robust error handling.
        """
        if data.empty:
            raise ValueError("Input data for transformation is empty.")

        data = data.copy()
        try:
            # Derived features
            data["VWAP"] = ((data["Close"] + data["High"] + data["Low"]) / 3 * data["Volume"]).cumsum() / data["Volume"].cumsum()
            data["MA_10"] = data["Close"].rolling(window=10).mean()
            data["MA_50"] = data["Close"].rolling(window=50).mean()
            data["EMA_10"] = data["Close"].ewm(span=10, adjust=False).mean()
            data["EMA_50"] = data["Close"].ewm(span=50, adjust=False).mean()

            delta = data["Close"].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            data["RSI"] = 100 - (100 / (1 + rs))

            rolling_mean = data["Close"].rolling(window=20).mean()
            rolling_std = data["Close"].rolling(window=20).std()
            data["BB_Lower"] = rolling_mean - (2 * rolling_std)
            data["BB_Middle"] = rolling_mean
            data["BB_Upper"] = rolling_mean + (2 * rolling_std)

            ema_12 = data["Close"].ewm(span=12, adjust=False).mean()
            ema_26 = data["Close"].ewm(span=26, adjust=False).mean()
            data["MACD"] = ema_12 - ema_26
            data["MACD_Signal"] = data["MACD"].ewm(span=9, adjust=False).mean()
            data["MACD_Hist"] = data["MACD"] - data["MACD_Signal"]

            lowest_low = data["Low"].rolling(window=14).min()
            highest_high = data["High"].rolling(window=14).max()
            data["Stochastic"] = 100 * (data["Close"] - lowest_low) / (highest_high - lowest_low)
            data["Williams %R"] = -100 * (highest_high - data["Close"]) / (highest_high - lowest_low)
            data["Parabolic_SAR"] = DataFetchResource.calculate_parabolic_sar(data)

            obv = [0]
            for i in range(1, len(data)):
                if data["Close"].iloc[i] > data["Close"].iloc[i - 1]:
                    obv.append(obv[-1] + data["Volume"].iloc[i])
                elif data["Close"].iloc[i] < data["Close"].iloc[i - 1]:
                    obv.append(obv[-1] - data["Volume"].iloc[i])
                else:
                    obv.append(obv[-1])
            data["OBV"] = obv

            data["Pivot"] = (data["High"] + data["Low"] + data["Close"]) / 3
            data["R1"] = (2 * data["Pivot"]) - data["Low"]
            data["S1"] = (2 * data["Pivot"]) - data["High"]
            data["Volatility"] = data["Close"].rolling(window=10).std()

            # Fill NaNs if any
            data.fillna(method="ffill", inplace=True)
            data.fillna(method="bfill", inplace=True)

        except Exception as e:
            raise RuntimeError(f"Error during data transformation: {str(e)}")

        # Ensure the result is a DataFrame
        if not isinstance(data, pd.DataFrame):
            raise ValueError("transform_data must return a pandas DataFrame")

        return data

    @staticmethod
    def calculate_parabolic_sar(data, step=0.02, max_step=0.2):
        """
        Helper function to calculate Parabolic SAR.
        """
        psar = data["Close"].copy()
        af = step
        ep = data["High"].iloc[0] if data["Close"].iloc[0] > data["Open"].iloc[0] else data["Low"].iloc[0]
        rising = data["Close"].iloc[0] > data["Open"].iloc[0]

        for i in range(1, len(data)):
            psar.iloc[i] = psar.iloc[i - 1] + af * (ep - psar.iloc[i - 1])

            if rising:
                if data["Low"].iloc[i] < psar.iloc[i]:
                    rising = False
                    psar.iloc[i] = ep
                    ep = data["Low"].iloc[i]
                    af = step
                elif data["High"].iloc[i] > ep:
                    ep = data["High"].iloc[i]
                    af = min(af + step, max_step)
            else:
                if data["High"].iloc[i] > psar.iloc[i]:
                    rising = True
                    psar.iloc[i] = ep
                    ep = data["High"].iloc[i]
                    af = step
                elif data["Low"].iloc[i] < ep:
                    ep = data["Low"].iloc[i]
                    af = min(af + step, max_step)

        return psar

    def fetch_and_transform(self, symbol, raw_cache_key, transformed_cache_key, fetch_function, transform_function):
        # Ensure transformed data is returned as a DataFrame
        transformed_data = get_from_cache(transformed_cache_key)
        if transformed_data:
            logging.info(f"Cache hit for transformed data: {transformed_cache_key}")
            transformed_data = pd.DataFrame(json.loads(transformed_data))  # Always convert to DataFrame
            logging.info(f"Deserialized data for {transformed_cache_key}: {transformed_data}")
        else:
            # Fetch and transform raw data
            raw_data = get_from_cache(raw_cache_key)
            if raw_data:
                logging.info(f"Cache hit for raw data: {raw_cache_key}")
                raw_data = pd.DataFrame(json.loads(raw_data))
            else:
                logging.info(f"Cache miss for raw data. Fetching {symbol} from yFinance.")
                raw_data = fetch_function(symbol)
                logging.info(f"Storing transformed data in cache for {transformed_cache_key}: {transformed_data.to_json(orient='records')}")
                set_to_cache(raw_cache_key, raw_data.to_json(orient="records"), CACHE_EXPIRY)

            transformed_data = transform_function(raw_data)
            set_to_cache(transformed_cache_key, transformed_data.to_json(orient="records"), CACHE_EXPIRY)

        return pd.DataFrame(raw_data), pd.DataFrame(transformed_data)  # Ensure both are DataFrames


class StockDataFetchResource(BaseDataFetchResource):
    def get(self, symbol):
        """
        Fetch stock data with optional timeframes and derived features.
        """
        try:
            # Query parameters
            period = request.args.get("period", "1y")
            interval = request.args.get("interval", "1d")

            # Validate parameters
            if period not in VALID_PERIODS:
                return {"error": f"Invalid period '{period}'. Supported: {', '.join(VALID_PERIODS)}"}, 400
            if interval not in VALID_INTERVALS:
                return {"error": f"Invalid interval '{interval}'. Supported: {', '.join(VALID_INTERVALS)}"}, 400

            # Redis cache key
            cache_key = f"stock_data:{symbol}:{period}:{interval}"

            # Fetch data from cache or yFinance
            derived_data = self.fetch_and_cache(
                symbol,
                cache_key,
                lambda x: yf.Ticker(x).history(period=period, interval=interval).reset_index(),
                DataFetchResource.transform_data,
            )

            return {"symbol": symbol, "data": json.loads(derived_data.to_json(orient="records"))}, 200

        except Exception as e:
            logging.error(f"Error fetching stock data for {symbol}: {e}")
            return {"error": f"Failed to fetch stock data for {symbol}: {str(e)}"}, 500
