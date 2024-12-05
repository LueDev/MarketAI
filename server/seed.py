import yfinance as yf
import logging
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from models import db, Stock, Sector, User, Analysis
from config import app

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Define stock lists for each sector
tech_stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "ADBE", "AVGO", "CRM", "INTC"]
finance_stocks = ["JPM", "BAC", "WFC", "GS", "MS", "PNC", "USB", "AXP", "RY", "TD"]
health_stocks = ["JNJ", "PFE", "MRK", "TMO", "UNH", "ABBV", "LLY", "BMY", "AMGN", "CVS"]

# Map stocks to sectors
sectors = {
    "tech": tech_stocks,
    "finance": finance_stocks,
    "health": health_stocks,
}

def fetch_stock_data(symbol):
    """
    Fetch stock data using yfinance.
    Returns a dictionary with stock information.
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
    Seed the database with sector data.
    """
    logging.info("Seeding sectors...")
    for sector_name in sectors.keys():
        existing_sector = Sector.query.filter_by(name=sector_name).first()
        if not existing_sector:
            new_sector = Sector(name=sector_name, description=f"{sector_name.capitalize()} stocks")
            db.session.add(new_sector)
    db.session.commit()
    logging.info("Sectors seeded successfully.")

def seed_stocks():
    """
    Seed the database with stock data.
    """
    logging.info("Seeding stocks...")
    for sector_name, stock_list in sectors.items():
        sector = Sector.query.filter_by(name=sector_name).first()
        if not sector:
            logging.warning(f"Sector {sector_name} not found. Skipping stocks in this sector.")
            continue

        for symbol in stock_list:
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
    logging.info("Stocks seeded successfully.")

def seed_users():
    """
    Seed the database with sample user data.
    """
    logging.info("Seeding users...")
    sample_users = [
        {"username": "admin", "email": "admin@example.com"},
        {"username": "user1", "email": "user1@example.com"},
        {"username": "user2", "email": "user2@example.com"},
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
    logging.info("Users seeded successfully.")

def seed_analysis():
    """
    Seed the database with sample analysis data.
    """
    logging.info("Seeding analysis...")
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
    logging.info("Analysis seeded successfully.")

def run_seed():
    """
    Main function to seed the database.
    """
    with app.app_context():
        logging.info("Starting database seeding...")
        try:
            seed_sectors()
            seed_stocks()
            seed_users()
            seed_analysis()
            logging.info("Database seeding completed successfully.")
        except Exception as e:
            logging.error(f"Error during seeding: {e}")
            db.session.rollback()

if __name__ == "__main__":
    run_seed()
