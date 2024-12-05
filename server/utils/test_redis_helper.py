import json
import logging
from utils.redis_helper import get_from_cache, set_to_cache
from config import redis_client
import pandas as pd
import numpy as np

# Logging configuration for debugging
logging.basicConfig(level=logging.INFO)

def test_set_and_get_json():
    """
    Test storing and retrieving a JSON object in Redis.
    """
    try:
        test_key = "test:json"
        test_data = [{"Close": 46.81, "Volume": 35024756, "MA_10": 47.03, "RSI": 61.32}]
        set_to_cache(test_key, test_data, ttl=60)
        logging.info(f"Data set in cache: {test_key} -> {test_data}")

        retrieved_data = get_from_cache(test_key)
        logging.info(f"Retrieved data: {retrieved_data}")

        assert retrieved_data == test_data, "Retrieved data does not match original!"
        logging.info("Test test_set_and_get_json passed.")
    except Exception as e:
        logging.error(f"Error in test_set_and_get_json: {e}")

def test_get_from_cache_with_helper():
    """
    Test retrieving JSON data from cache using helper functions.
    """
    try:
        test_key = "test:json:helper"
        test_data = [{"Close": 46.81, "Volume": 35024756, "MA_10": 47.03, "RSI": 61.32}]
        set_to_cache(test_key, test_data, ttl=60)
        logging.info(f"Data set using helper: {test_key} -> {test_data}")

        retrieved_data = get_from_cache(test_key)
        logging.info(f"Data retrieved using helper: {retrieved_data}")

        assert retrieved_data == test_data, "Retrieved data does not match original!"
        logging.info("Test test_get_from_cache_with_helper passed.")
    except Exception as e:
        logging.error(f"Error in test_get_from_cache_with_helper: {e}")

def test_non_json_value():
    """
    Test storing and retrieving a non-JSON value.
    """
    try:
        test_key = "test:non_json"
        test_value = "This is a plain string."

        # Save non-JSON value to Redis
        redis_client.set(test_key, test_value, ex=60)  # Set with 60 seconds expiry
        logging.info(f"Non-JSON data set: {test_key} -> {test_value}")

        # Retrieve from cache
        retrieved_data = redis_client.get(test_key)
        # Decode only if the data is bytes
        if isinstance(retrieved_data, bytes):
            retrieved_data = retrieved_data.decode("utf-8")
        logging.info(f"Retrieved data: {retrieved_data}")

        # Check equivalence
        assert retrieved_data == test_value, "Retrieved data does not match original!"
        logging.info("Test test_non_json_value passed.")
    except Exception as e:
        logging.error(f"Error in test_non_json_value: {e}")


def test_invalid_json_retrieval():
    """
    Test handling of invalid JSON data retrieval.
    """
    try:
        test_key = "test:invalid_json"
        invalid_json = "{'Invalid': 'JSON'}"  # Invalid JSON with single quotes
        redis_client.set(test_key, invalid_json, ex=60)
        logging.info(f"Invalid JSON set in Redis: {test_key} -> {invalid_json}")

        retrieved_data = get_from_cache(test_key)
        logging.info(f"Retrieved data: {retrieved_data}")
    except json.JSONDecodeError as e:
        logging.info(f"JSONDecodeError caught as expected: {e}")
    except Exception as e:
        logging.error(f"Error in test_invalid_json_retrieval: {e}")

def test_ttl_expiry():
    """
    Test that cache expiration works as expected.
    """
    try:
        test_key = "test:expiry"
        test_data = {"key": "value"}
        set_to_cache(test_key, test_data, ttl=2)  # 2 seconds TTL
        logging.info(f"Data set with TTL: {test_key} -> {test_data}")

        retrieved_data = get_from_cache(test_key)
        logging.info(f"Retrieved before expiry: {retrieved_data}")
        assert retrieved_data == test_data, "Data does not match before expiry."

        import time
        time.sleep(3)  # Wait for TTL to expire
        retrieved_data = get_from_cache(test_key)
        assert retrieved_data is None, "Data still exists after TTL expiry!"
        logging.info("Test test_ttl_expiry passed.")
    except Exception as e:
        logging.error(f"Error in test_ttl_expiry: {e}")

def test_complex_serialization():
    """
    Test storing and retrieving a complex object like transformed_data or prediction results.
    """
    try:
        # Define test key and complex data
        test_key = "test:complex_object"
        complex_data = {
            "day": 1,
            "input_features": [
                {
                    "Open": 47.369998931884766,
                    "High": 47.47779846191406,
                    "Low": 46.650001525878906,
                    "Close": 46.81999969482422,
                    "Volume": 35024756,
                    "MA_10": 47.03199996948242,
                    "MA_50": 43.13760009765625,
                    "Volatility": 0.5974536507,
                    "RSI": 61.320749624378095,
                    "MACD": 1.2362359615,
                    "MACD_Signal": 1.3315664732,
                    "MACD_Hist": -0.0953305117,
                    "Stochastic": 48.7804613297,
                    "Williams %R": -51.2195386703,
                    "BB_Lower": 43.5792540871,
                    "BB_Middle": 46.2345003128,
                    "BB_Upper": 48.8897465385,
                    "Parabolic_SAR": 46.5620266458,
                    "OBV": 11822292444,
                    "VWAP": 15.0886936714,
                    "Pivot": 46.9825998942,
                    "R1": 47.3151982625,
                    "S1": 46.4874013265,
                }
            ],
            "historical_prediction": 46.82021350860596,
            "recent_prediction": 46.822299537658694,
        }

        # Store the data in Redis using the helper
        set_to_cache(test_key, complex_data, ttl=60)
        logging.info(f"Complex object set in cache: {test_key} -> {complex_data}")

        # Retrieve the data using the helper
        retrieved_data = get_from_cache(test_key)
        logging.info(f"Complex object retrieved from cache: {retrieved_data}")

        # Check equivalence
        assert retrieved_data == complex_data, "Retrieved complex data does not match the original!"

    except Exception as e:
        logging.error(f"Error in test_complex_serialization: {e}")
        
def test_complex_object_handling():
    test_key = "test:complex_object"
    test_data = {
        "day": 1,
        "input_features": [
            {"Open": 47.37, "High": 47.47, "Low": 46.65, "Close": 46.82, "Volume": 35024756, "MA_10": 47.03}
        ],
        "historical_prediction": 46.82,
        "recent_prediction": 46.82,
    }

    # Set the data
    set_to_cache(test_key, test_data, ttl=60)
    logging.info(f"Complex object cached: {test_data}")

    # Retrieve and validate
    cached_data = get_from_cache(test_key)
    logging.info(f"Complex object retrieved: {cached_data}")
    assert cached_data == test_data, "Cached data does not match original!"

# def test_dataframe_caching():
#     test_key = "test:df"
#     df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})

#     # Save as JSON
#     set_to_cache(test_key, df.to_json(orient="records"), ttl=60)

#     # Retrieve and reconstruct DataFrame
#     cached_data = get_from_cache(test_key)
#     reconstructed_df = pd.DataFrame(json.loads(cached_data))
#     pd.testing.assert_frame_equal(df, reconstructed_df)
#     logging.info("DataFrame caching test passed.")

def test_dataframe_caching():
    """
    Test storing and retrieving a Pandas DataFrame in Redis using Pickle.
    """
    test_key = "test:df"
    df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})

    # Store the DataFrame in Redis
    set_to_cache(test_key, df, ttl=60)

    # Retrieve the DataFrame from Redis
    cached_data = get_from_cache(test_key)

    # Validate the retrieved DataFrame
    pd.testing.assert_frame_equal(df, cached_data)
    logging.info("DataFrame caching test passed.")

def test_pickle_cache():
    """
    Test caching and retrieval of a Pandas DataFrame using Pickle.
    """
    try:
        # Create a sample DataFrame
        test_key = "test:df"
        df = pd.DataFrame({
            "Open": [47.36],
            "High": [47.47],
            "Low": [46.65],
            "Close": [46.81],
            "Volume": [35024756],
        })

        # Cache the DataFrame
        logging.info(f"Setting cache for key: {test_key} with value type: {type(df)}")
        set_to_cache(test_key, df)
        logging.info("Stored DataFrame in cache.")

        # Retrieve and verify the DataFrame
        retrieved_df = get_from_cache(test_key)
        assert isinstance(retrieved_df, pd.DataFrame), "Retrieved object is not a DataFrame!"
        assert df.equals(retrieved_df), "Retrieved DataFrame does not match the original!"
        logging.info("Retrieved DataFrame matches the original. Test passed.")

    except Exception as e:
        logging.error(f"Error during test_pickle_cache: {e}")
        raise


def main():
    """
    Run all Redis helper tests.
    """
    logging.info("Starting Redis helper tests...")
    # test_set_and_get_json()
    # test_get_from_cache_with_helper()
    # test_non_json_value()
    # test_invalid_json_retrieval()
    # test_ttl_expiry()
    # test_complex_serialization()
    # test_complex_object_handling()
    # test_dataframe_caching()
    test_pickle_cache()
    logging.info("All Redis helper tests completed.")

if __name__ == "__main__":
    main()
