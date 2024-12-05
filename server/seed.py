import yfinance as yf
import logging
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from models import db, Stock, Sector, User, Analysis
from config import app

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Stock lists
tech_stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "ADBE", "AVGO", "CRM", "INTC", "AMD", "CSCO", "QCOM", "TXN", "INTU", "ORCL", "IBM", "V", "PYPL", "ADI", "SNOW", "SHOP", "NOW", "SQ", "MA"]
finance_stocks = ["JPM", "BAC", "WFC", "GS", "MS", "PNC", "USB", "AXP", "RY", "TD", "SPGI", "CB", "CME", "MET", "ICE", "HSBC", "MCO", "SCHW", "COF", "C", "BLK", "BNS", "MUFG", "BMO", "CINF"]
health_stocks = ["JNJ", "PFE", "MRK", "TMO", "UNH", "ABBV", "LLY", "BMY", "AMGN", "CVS", "MDT", "ABT", "SYK", "DHR", "BSX", "GILD", "HCA", "EW", "REGN", "CI", "IQV", "ILMN", "HUM", "ZBH", "BAX"]

# Map stocks to sectors
sectors = {
    "tech": tech_stocks,
    "finance": finance_stocks,
    "health": health_stocks,
}

def fetch_stock_data(symbol):
    """
    Fetches stock data using yfinance for a given symbol.
    Returns a dictionary containing stock information.
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return {
            "symbol": symbol,
            "name": info.get("shortName", symbol),
        }
    except Exception as e:
        logging.warning(f"Error fetching data for {symbol}: {e}")
        return None

def seed_sectors():
    """
    Seeds the database with sector data.
    """
    try:
        for sector_name in sectors.keys():
            existing_sector = Sector.query.filter_by(name=sector_name).first()
            if not existing_sector:
                new_sector = Sector(name=sector_name, description=f"{sector_name.capitalize()} stocks")
                db.session.add(new_sector)
        db.session.commit()
        logging.info("Sectors seeded successfully!")
    except Exception as e:
        logging.error(f"Error seeding sectors: {e}")
        db.session.rollback()

def seed_stocks():
    """
    Seeds the database with stock data.
    """
    try:
        for sector_name, stock_list in sectors.items():
            sector = Sector.query.filter_by(name=sector_name).first()
            if not sector:
                logging.warning(f"Sector {sector_name} not found. Skipping stocks in this sector.")
                continue

            for symbol in stock_list:
                # Check if stock already exists
                existing_stock = Stock.query.filter_by(symbol=symbol).first()
                if existing_stock:
                    logging.info(f"Stock {symbol} already exists. Skipping.")
                    continue

                stock_data = fetch_stock_data(symbol)
                if not stock_data:
                    continue

                new_stock = Stock(
                    name=stock_data["name"],
                    symbol=stock_data["symbol"],
                    sector_id=sector.id
                )
                db.session.add(new_stock)
        db.session.commit()
        logging.info("Stocks seeded successfully!")
    except IntegrityError as e:
        logging.error(f"Integrity error: {e}")
        db.session.rollback()
    except Exception as e:
        logging.error(f"Error seeding stocks: {e}")
        db.session.rollback()

def seed_users():
    """
    Seeds the database with sample users.
    """
    try:
        sample_users = [
            {"username": "admin", "email": "admin@example.com"},
            {"username": "user1", "email": "user1@example.com"},
            {"username": "user2", "email": "user2@example.com"},
            {"username": "user3", "email": "user3@example.com"},
            {"username": "user4", "email": "user4@example.com"},
        ]

        for user_data in sample_users:
            existing_user = User.query.filter_by(email=user_data["email"]).first()
            if existing_user:
                logging.info(f"User {user_data['email']} already exists. Skipping.")
                continue

            new_user = User(
                username=user_data["username"],
                email=user_data["email"]
            )
            db.session.add(new_user)

        db.session.commit()
        logging.info("Users seeded successfully!")
    except Exception as e:
        logging.error(f"Error seeding users: {e}")
        db.session.rollback()


def seed_analysis():
    """
    Seeds the database with a sample analysis.
    """
    try:
        stock = Stock.query.first()
        user = User.query.filter_by(username="admin").first()

        if not stock or not user:
            logging.warning("No stock or admin user found. Skipping analysis seeding.")
            return

        new_analysis = Analysis(
            stock_id=stock.id,
            attribute="Volatility",
            value=0.15,
            created_at=datetime.now()
        )
        db.session.add(new_analysis)
        db.session.commit()
        logging.info("Analysis seeded successfully!")
    except Exception as e:
        logging.error(f"Error seeding analysis: {e}")
        db.session.rollback()

def run_seed():
    """
    Main function to run the seed process.
    """
    with app.app_context():
        logging.info("Seeding database...")
        seed_sectors()
        seed_stocks()
        seed_users()
        seed_analysis()
        logging.info("Database seeding complete.")

if __name__ == "__main__":
    run_seed()
