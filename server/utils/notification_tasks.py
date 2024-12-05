import sys
import os
import logging
from celery import Celery
from flask import current_app
from config import db  # Database configuration
from models import Notification, Alert, User, Stock
from utils.redis_helper import cache_predictions, get_cached_predictions
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for detailed logs
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],  # Log to the console
)
logger = logging.getLogger(__name__)

# Ensure project root is in PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))  # Adjust for the utils folder depth
if project_root not in sys.path:
    sys.path.append(project_root)

# Initialize Celery
celery = Celery(
    'market_ai_tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',  # Enable result backend
)


@celery.task
def test_task():
    """
    A simple test task to validate Celery is working correctly.
    """
    logger.info("Test task executed successfully.")
    return "Test task executed!"


@celery.task
def create_notification(user_id, message, channel="in-app", stock_id=None, alert_id=None):
    """
    Create a notification asynchronously and optionally send via email.
    """
    logger.debug(f"Creating notification for user_id={user_id}, stock_id={stock_id}, alert_id={alert_id}")
    notification = Notification(
        user_id=user_id,
        stock_id=stock_id,
        alert_id=alert_id,
        message=message,
        channel=channel,
    )
    db.session.add(notification)
    db.session.commit()
    logger.info(f"Notification created: {notification}")

    if channel == "email":
        send_email_notification.delay(user_id, message)
        logger.info(f"Email notification sent to user_id={user_id}")


@celery.task
def process_alert(alert_id):
    """
    Evaluate an alert's condition and trigger a notification if needed.
    """
    logger.debug(f"Processing alert_id={alert_id}")
    alert = Alert.query.get(alert_id)
    if not alert:
        logger.error(f"Alert ID {alert_id} not found.")
        return

    stock = alert.stock
    logger.debug(f"Fetched stock for alert: {stock}")
    predictions = get_cached_predictions(stock.symbol, alert.days_out)
    logger.debug(f"Retrieved predictions: {predictions}")

    if not predictions:
        logger.warning(f"No predictions found for stock {stock.symbol} and alert {alert_id}.")
        return

    condition_met = eval(alert.condition, {"predicted_gain": predictions[-1] - predictions[0]})
    if condition_met and not alert.is_triggered:
        create_notification.delay(
            user_id=alert.user_id,
            message=f"Alert triggered: {stock.name} meets the condition '{alert.condition}'",
            stock_id=stock.id,
            alert_id=alert.id,
        )
        logger.info(f"Alert triggered for alert_id={alert_id}")
        alert.is_triggered = True
        db.session.commit()


@celery.task
def cache_stock_predictions(stock_symbol, days_out):
    """
    Generate and cache stock predictions.
    """
    from ml_components.operations.data_fetch import fetch_stock_data
    from ml_components.operations.model import get_predictions

    try:
        stock_data = fetch_stock_data(stock_symbol)
        predictions = get_predictions(stock_data, days_out)

        cache_predictions(stock_symbol, predictions)
        logger.info(f"Predictions cached for {stock_symbol} ({days_out} days).")
    except Exception as e:
        logger.error(f"Failed to cache predictions for {stock_symbol}: {e}")


@celery.task
def send_email_notification(user_id, message):
    """
    Send an email notification to the user.
    """
    user = User.query.get(user_id)
    if not user or not user.email:
        logger.error(f"Cannot send email: Invalid user ID {user_id}.")
        return

    logger.info(f"Sending email to {user.email}: {message}")
    # Placeholder for actual email-sending logic


@celery.task
def cleanup_old_notifications():
    """
    Delete notifications older than 30 days.
    """
    cutoff_date = datetime.utcnow() - timedelta(days=30)
    deleted_count = Notification.query.filter(Notification.created_at < cutoff_date).delete()
    db.session.commit()
    logger.info(f"Cleaned up {deleted_count} old notifications.")


@celery.task
def refresh_alerts():
    """
    Refresh alerts for all users and stocks.
    """
    alerts = Alert.query.all()
    for alert in alerts:
        process_alert.delay(alert.id)


@celery.task
def refresh_stock_data():
    """
    Refresh stock data for all tracked stocks.
    """
    from ml_components.operations.data_fetch import fetch_stock_data

    stocks = Stock.query.all()
    for stock in stocks:
        try:
            fetch_stock_data(stock.symbol)
            logger.info(f"Stock data refreshed for {stock.symbol}.")
        except Exception as e:
            logger.error(f"Failed to refresh stock data for {stock.symbol}: {e}")
