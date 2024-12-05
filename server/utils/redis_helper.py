import json
import logging
import redis
from config import redis_client
import pickle

# Logging configuration
logging.basicConfig(level=logging.INFO)

# Namespace for Redis keys to avoid collisions
NAMESPACE = "market_ai"

def generate_key(key):
    """
    Generate a namespaced Redis key.
    """
    return f"{NAMESPACE}:{key}" if not key.startswith(NAMESPACE) else key

def get_from_cache(key):
    """
    Retrieve a value from Redis and deserialize it using Pickle.
    """
    try:
        serialized_value = redis_client.get(key)  # Fetch raw binary data
        if serialized_value is None:
            logging.info(f"Cache miss for key: {key}")
            return None
        # Deserialize using Pickle
        value = pickle.loads(serialized_value)
        logging.info(f"Cache hit for key: {key}")
        return value
    except (pickle.UnpicklingError, TypeError, KeyError) as e:
        logging.error(f"Error deserializing cache for key {key}: {e}")
        raise RuntimeError(f"Pickle deserialization error for key {key}: {e}")
    except Exception as e:
        logging.error(f"Error getting cache for key {key}: {e}")
        raise RuntimeError(f"Redis get error: {e}")
    
def set_to_cache(key, value, ttl=86400):
    """
    Store a value in the Redis cache using Pickle.
    """
    try:
        # Serialize the value with Pickle
        serialized_value = pickle.dumps(value)
        redis_client.set(key, serialized_value, ex=ttl)
        logging.info(f"Value set in cache for key: {key} with TTL: {ttl}")
    except Exception as e:
        logging.error(f"Error setting cache for key {key}: {e}")
        raise RuntimeError(f"Redis set error: {e}")


def delete_from_cache(key):
    """
    Delete a value from the Redis cache.

    Parameters:
        key (str): The cache key.
    """
    try:
        namespaced_key = generate_key(key)
        redis_client.delete(namespaced_key)
        logging.info(f"Key deleted from cache: {namespaced_key}")
    except redis.ConnectionError as e:
        logging.error(f"Redis connection error while deleting key {key}: {str(e)}")
        raise RuntimeError(f"Redis connection error: {str(e)}")


def cache_key_exists(key):
    """
    Check if a key exists in the Redis cache.

    Parameters:
        key (str): The cache key.

    Returns:
        bool: True if the key exists, False otherwise.
    """
    try:
        namespaced_key = generate_key(key)
        exists = redis_client.exists(namespaced_key) > 0
        logging.info(f"Key exists check for {namespaced_key}: {exists}")
        return exists
    except redis.ConnectionError as e:
        logging.error(f"Redis connection error while checking key {key}: {str(e)}")
        raise RuntimeError(f"Redis connection error: {str(e)}")


def increment_cache_key(key, amount=1):
    """
    Atomically increment a key's value in the Redis cache.

    Parameters:
        key (str): The cache key.
        amount (int): The increment amount (default is 1).

    Returns:
        int: The new value after incrementing.
    """
    try:
        namespaced_key = generate_key(key)
        new_value = redis_client.incrby(namespaced_key, amount)
        logging.info(f"Incremented key {namespaced_key} by {amount}. New value: {new_value}")
        return new_value
    except redis.ConnectionError as e:
        logging.error(f"Redis connection error while incrementing key {key}: {str(e)}")
        raise RuntimeError(f"Redis connection error: {str(e)}")


def get_ttl(key):
    """
    Get the remaining time-to-live (TTL) of a key in the Redis cache.

    Parameters:
        key (str): The cache key.

    Returns:
        int: The TTL in seconds, or -2 if the key does not exist, or -1 if the key exists but has no associated TTL.
    """
    try:
        namespaced_key = generate_key(key)
        ttl = redis_client.ttl(namespaced_key)
        logging.info(f"TTL for key {namespaced_key}: {ttl}")
        return ttl
    except redis.ConnectionError as e:
        logging.error(f"Redis connection error while getting TTL for key {key}: {str(e)}")
        raise RuntimeError(f"Redis connection error: {str(e)}")

import logging

logger = logging.getLogger(__name__)

def cache_predictions(key, predictions, ttl=3600):
    logger.debug(f"Caching predictions with key={key}, ttl={ttl}")
    redis_client.setex(key, ttl, json.dumps(predictions))
    logger.info(f"Cached predictions: {predictions}")

def get_cached_predictions(key):
    logger.debug(f"Fetching cached predictions with key={key}")
    data = redis_client.get(key)
    if data:
        logger.debug(f"Cache hit for key={key}")
    else:
        logger.warning(f"Cache miss for key={key}")
    return json.loads(data) if data else None

