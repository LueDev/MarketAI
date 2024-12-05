# Standard library imports
import os

# Remote library imports
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from dotenv import load_dotenv
from flasgger import Swagger
import redis

# Load environment variables
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Directory for instance-specific files
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")

# Ensure the instance directory exists
os.makedirs(INSTANCE_DIR, exist_ok=True)

# Update database paths to use the instance directory
DEV_DATABASE_URI = f"sqlite:///{os.path.join(INSTANCE_DIR, 'market_ai_dev.db')}"
TEST_DATABASE_URI = f"sqlite:///{os.path.join(INSTANCE_DIR, 'market_ai_test.db')}"
DATABASE_URI = f"sqlite:///{os.path.join(INSTANCE_DIR, 'market_ai.db')}"


# Base configuration class
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'mysecretkey')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_COMPACT = False  # Default JSON configuration

    # Redis configuration
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = 1  # Always use Redis DB 1
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

    # Swagger configuration
    SWAGGER = {
        "swagger": "2.0",
        "info": {
            "title": "MarketAI API",
            "description": "API for managing users, stocks, sectors, and analyses in MarketAI",
            "version": "1.0.0",
            "contact": {
                "name": "Luis Jorge",
                "email": "luisjorge@example.com",
            },
        },
        "schemes": ["http", "https"],
        "tags": [
            {"name": "User", "description": "Operations for users"},
            {"name": "Stock", "description": "Operations for stocks"},
            {"name": "Sector", "description": "Operations for sectors"},
            {"name": "Analysis", "description": "Operations for analyses"},
        ],
        "host": os.getenv('SWAGGER_HOST', "localhost:10000"),
        "basePath": "/",
    }

# Development configuration
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = DEV_DATABASE_URI

# Testing configuration
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = TEST_DATABASE_URI
    SECRET_KEY = 'test_secret_key'

# Production configuration
class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = DATABASE_URI
    REDIS_HOST = os.getenv('PROD_REDIS_HOST', 'redis-prod.example.com')  # Override host for production

# Configuration mapping
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}

# Instantiate app, configure with appropriate environment
app = Flask(__name__)
env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config_by_name[env])

# Set up Redis
try:
    redis_client = redis.StrictRedis(
        host=app.config['REDIS_HOST'],
        port=app.config['REDIS_PORT'],
        db=0,
        decode_responses=False
    )
    redis_client.ping()
    app.logger.info(f"Connected to Redis at {app.config['REDIS_HOST']}:{app.config['REDIS_PORT']} DB 0")
except redis.ConnectionError as e:
    app.logger.error(f"Redis connection error: {e}")
    redis_client = None

# Set up JSON formatting
app.json.compact = app.config.get('JSON_COMPACT', False)

# Define metadata convention, instantiate db and migration
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})
db = SQLAlchemy(metadata=metadata)
migrate = Migrate(app, db)
db.init_app(app)

# Instantiate REST API
api = Api(app)

# Instantiate CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# Instantiate Swagger using the app config
swagger = Swagger(app, template_file="./swagger.yml", config={
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/api/docs/apispec.json',
            "rule_filter": lambda rule: True,  # include all endpoints
            "model_filter": lambda tag: True,  # include all models
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs"  # This sets the Swagger UI route to /api/docs
})
