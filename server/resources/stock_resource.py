# server/resources/stock_resource.py

from flask_restful import Resource, reqparse
from config import db
from models import Stock, Alert, User
from sqlalchemy.exc import IntegrityError
import re

class StockResource(Resource):
    def get(self, stock_id=None):
        if stock_id:
            stock = Stock.query.get(stock_id)
            if not stock:
                return {"error": "Stock not found"}, 404

            # Fetch alerts for this stock
            alerts = Alert.query.filter_by(stock_id=stock_id).all()
            return {
                "stock": stock.to_dict(),
                "alerts": [alert.to_dict() for alert in alerts],
            }, 200

        stocks = Stock.query.all()
        return [stock.to_dict() for stock in stocks], 200

    def get_by_symbol(self, symbol):
        stock = Stock.query.filter_by(symbol=symbol).first()
        if not stock:
            return {"error": "Stock not found"}, 404
        return stock.to_dict(), 200

    def get_by_sector(self, sector_id):
        stocks = Stock.query.filter_by(sector_id=sector_id).all()
        if not stocks:
            return {"error": "No stocks found in this sector"}, 404
        return [stock.to_dict() for stock in stocks], 200

    def put(self, stock_id):
        put_parser = reqparse.RequestParser()
        put_parser.add_argument('name', type=str, required=True, help="Stock name is required")
        put_parser.add_argument('symbol', type=str, required=True, help="Stock symbol is required")

        args = put_parser.parse_args()
        stock = Stock.query.get(stock_id)
        if not stock:
            return {"error": "Stock not found"}, 404

        # Enhanced validations
        if not re.match(r"^[A-Za-z0-9]{1,5}$", args['symbol']):
            return {"error": "Symbol must be 1-5 alphanumeric characters"}, 400

        if len(args['name'].strip()) == 0:
            return {"error": "Stock name cannot be empty"}, 400

        try:
            stock.name = args['name'].strip()
            stock.symbol = args['symbol'].upper()
            db.session.commit()
            return stock.to_dict(), 200
        except IntegrityError:
            db.session.rollback()
            return {"error": "Stock name and symbol must be unique"}, 400
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}, 500
    
    def delete(self, stock_id):
        stock = Stock.query.get(stock_id)
        if not stock:
            return {"error": "Stock not found"}, 404

        db.session.delete(stock)
        db.session.commit()
        return {"message": "Stock deleted"}, 200


class StockListResource(Resource):
    def get(self):
        stocks = Stock.query.all()
        return [stock.to_dict() for stock in stocks], 200

    def post(self):
        post_parser = reqparse.RequestParser()
        post_parser.add_argument('name', type=str, required=True, help="Stock name is required")
        post_parser.add_argument('symbol', type=str, required=True, help="Stock symbol is required")

        args = post_parser.parse_args()

        if Stock.query.filter_by(name=args['name']).first():
            return {"error": "Stock name already exists"}, 400
        if Stock.query.filter_by(symbol=args['symbol']).first():
            return {"error": "Stock symbol already exists"}, 400

        new_stock = Stock(name=args['name'], symbol=args['symbol'])

        try:
            db.session.add(new_stock)
            db.session.commit()
            return new_stock.to_dict(), 201
        except IntegrityError:
            db.session.rollback()
            return {"error": "Stock name and symbol must be unique"}, 400
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}, 500

# Additional resource to get a stock by symbol
class StockBySymbolResource(Resource):
    def get(self, symbol):
        stock = Stock.query.filter_by(symbol=symbol).first()
        if not stock:
            return {"error": "Stock not found"}, 404
        return stock.to_dict(), 200

# Additional resource to get stocks by sector ID
class StocksBySectorResourceID(Resource):
    def get(self, sector_id):
        stocks = Stock.query.filter_by(sector_id=sector_id).all()
        if not stocks:
            return {"error": "No stocks found in this sector"}, 404
        return [stock.to_dict() for stock in stocks], 200

class StockAlertResource(Resource):
    def post(self, stock_id):
        """
        Create an alert for a stock.
        """
        stock = Stock.query.get(stock_id)
        if not stock:
            return {"error": "Stock not found"}, 404

        post_parser = reqparse.RequestParser()
        post_parser.add_argument('user_id', type=int, required=True, help="User ID is required")
        post_parser.add_argument('condition', type=str, required=True, help="Condition is required (e.g., 'predicted_gain > 10')")
        post_parser.add_argument('days_out', type=int, required=True, help="Days out is required")
        args = post_parser.parse_args()

        user = User.query.get(args['user_id'])
        if not user:
            return {"error": "User not found"}, 404

        try:
            alert = Alert(
                user_id=args['user_id'],
                stock_id=stock_id,
                condition=args['condition'],
                days_out=args['days_out']
            )
            db.session.add(alert)
            db.session.commit()
            return {"message": "Alert created successfully", "alert": alert.to_dict()}, 201
        except IntegrityError:
            db.session.rollback()
            return {"error": "Alert creation failed due to integrity issues"}, 400
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}, 500