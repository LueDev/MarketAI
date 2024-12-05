# server/resources/sector_resource.py

from flask_restful import Resource, reqparse
from config import db
from models import Sector, Stock, Alert
from sqlalchemy.exc import IntegrityError


# Primary Sector resource
class SectorResource(Resource):
    def get(self, sector_id=None):
        if sector_id:
            sector = Sector.query.get(sector_id)
            if not sector:
                return {"error": "Sector not found"}, 404

            # Fetch alerts for all stocks in this sector
            alerts = Alert.query.join(Stock).filter(Stock.sector_id == sector_id).all()
            return {
                "sector": sector.to_dict(),
                "alerts": [alert.to_dict() for alert in alerts],
            }, 200

        sectors = Sector.query.all()
        return [sector.to_dict() for sector in sectors], 200

    def get_by_name(self, name):
        sector = Sector.query.filter(Sector.name.ilike(f"%{name}%")).all()
        if not sector:
            return {"error": "Sector not found"}, 404
        return sector.to_dict(), 200

    def get_by_stock_count(self, min_count):
        sectors = Sector.query.join(Sector.stocks).group_by(Sector.id).having(db.func.count(Stock.id) >= min_count).all()
        if not sectors:
            return {"error": f"No sectors with at least {min_count} stocks found"}, 404
        return [sector.to_dict() for sector in sectors], 200

    def put(self, sector_id):
        put_parser = reqparse.RequestParser()
        put_parser.add_argument('name', type=str, required=True, help="Sector name is required")

        args = put_parser.parse_args()
        sector = Sector.query.get(sector_id)
        if not sector:
            return {"error": "Sector not found"}, 404

        try:
            sector.name = args['name']
            db.session.commit()
            return sector.to_dict(), 200
        except IntegrityError:
            db.session.rollback()
            return {"error": "Sector name must be unique"}, 400
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}, 500

    def delete(self, sector_id):
        sector = Sector.query.get(sector_id)
        if not sector:
            return {"error": "Sector not found"}, 404

        db.session.delete(sector)
        db.session.commit()
        return {"message": "Sector deleted"}, 200


# List all sectors and create a new sector
class SectorListResource(Resource):
    def get(self):
        sectors = Sector.query.all()
        return [sector.to_dict() for sector in sectors], 200

    def post(self):
        post_parser = reqparse.RequestParser()
        post_parser.add_argument('name', type=str, required=True, help="Sector name is required")
        post_parser.add_argument('description', type=str, required=False, help="Sector description is required")

        args = post_parser.parse_args()

        if Sector.query.filter_by(name=args['name']).first():
            return {"error": "Sector name already exists"}, 400

        new_sector = Sector(name=args['name'], description=args['description'])

        try:
            db.session.add(new_sector)
            db.session.commit()
            return new_sector.to_dict(), 201
        except IntegrityError:
            db.session.rollback()
            return {"error": "Sector name must be unique"}, 400
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}, 500


# Additional resource to get sectors with a specific number of stocks
class SectorStockCountResource(Resource):
    def get(self, min_count):
        sectors = Sector.query.join(Stock).group_by(Sector.id).having(db.func.count(Stock.id) >= min_count).all()
        if not sectors:
            return {"message": f"No sectors with at least {min_count} stocks found."}, 404
        return [sector.to_dict() for sector in sectors], 200


# Additional resource to get stocks by sector name
class StocksBySectorResourceName(Resource):
    def get(self, sector_name):
        sector = Sector.query.filter_by(name=sector_name).first()
        if not sector:
            return {"error": "Sector not found"}, 404
        return [stock.to_dict() for stock in sector.stocks], 200


class SectorByNameResource(Resource):
    def get(self, name):
        sector = Sector.query.filter_by(name=name).first()
        if not sector:
            return {"error": "Sector not found"}, 404
        return sector.to_dict(), 200
    
class SectorAlertsResource(Resource):
    def get(self, sector_id):
        """
        Fetch alerts for all stocks in a specific sector.
        """
        alerts = Alert.query.join(Stock).filter(Stock.sector_id == sector_id).all()
        if not alerts:
            return {"error": "No alerts found for this sector"}, 404
        return [alert.to_dict() for alert in alerts], 200