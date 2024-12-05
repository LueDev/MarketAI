from config import app, api, db
from resources.user_resource import UserResource, UserListResource
from resources.stock_resource import StockResource, StockListResource, StockBySymbolResource, StocksBySectorResourceID
from resources.sector_resource import SectorResource, SectorListResource, SectorStockCountResource, SectorByNameResource, StocksBySectorResourceName
from resources.analysis_resource import AnalysisPredictResource
from resources.data_resource import DataFetchResource, StockDataFetchResource
from models import User, Stock, Sector, Analysis, Alert, Notification

# User resources
api.add_resource(UserListResource, '/users')
api.add_resource(UserResource, '/users/<int:user_id>')
api.add_resource(UserResource, '/users/email/<string:email>', endpoint='user_by_email')
api.add_resource(UserResource, '/users/username/<string:username>', endpoint='user_by_username')

# Stock resources
api.add_resource(StockListResource, '/stocks')
api.add_resource(StockResource, '/stocks/<int:stock_id>')
api.add_resource(StockBySymbolResource, '/stocks/symbol/<string:symbol>')
api.add_resource(StocksBySectorResourceID, '/stocks/sector/<int:sector_id>')

# Sector resources
api.add_resource(SectorListResource, '/sectors')
api.add_resource(SectorResource, '/sectors/<int:sector_id>')
api.add_resource(SectorByNameResource, '/sectors/name/<string:name>')
api.add_resource(StocksBySectorResourceName, '/sectors/<string:sector_name>/stocks')
api.add_resource(SectorStockCountResource, '/sectors/stocks/min_count/<int:min_count>')

# Analysis resources
api.add_resource(AnalysisPredictResource, '/analysis/predict')

# Data resources
api.add_resource(StockDataFetchResource, '/stocks/fetch/<string:symbol>')
api.add_resource(DataFetchResource, '/data/historical/<string:sector>/<string:timeframe>')

if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
        print("Tables created successfully!")
        app.run(host='localhost', port=10000, debug=True)

