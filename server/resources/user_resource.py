# server/resources/user_resource.py

from flask_restful import Resource, reqparse
from config import db
from models import User, Alert, Stock
from sqlalchemy.exc import IntegrityError
import re 

class UserResource(Resource):
    def dispatch_request(self, *args, **kwargs):
        if 'email' in kwargs:
            return self.get_by_email(kwargs['email'])
        elif 'username' in kwargs:
            return self.get_by_username(kwargs['username'])
        elif 'user_id' in kwargs:
            return self.get(kwargs['user_id'])
        else:
            return self.get()
    
    def get(self, user_id=None):    
        if user_id:
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found"}, 404

            # Fetch alerts for the user
            alerts = Alert.query.filter_by(user_id=user_id).all()
            return {
                "user": user.to_dict(),
                "alerts": [alert.to_dict() for alert in alerts],
            }, 200

        users = User.query.all()
        return [user.to_dict() for user in users], 200

    def get_by_email(self, email):
        user = User.query.filter_by(email=email).first()
        if not user:
            return {"error": "User not found"}, 404
        return user.to_dict(), 200

    def get_by_username(self, username):
        user = User.query.filter_by(username=username).first()
        if not user:
            return {"error": "User not found"}, 404
        return user.to_dict(), 200

    def put(self, user_id):
        put_parser = reqparse.RequestParser()
        put_parser.add_argument('username', type=str, required=True, help="Username is required")
        put_parser.add_argument('email', type=str, required=True, help="Email is required")
        
        args = put_parser.parse_args()
        user = User.query.get(user_id)
        if not user:
            return {"error": "User not found"}, 404

        # Enhanced validations
        if not re.match(r"[^@]+@[^@]+\.[^@]+", args['email']):
            return {"error": "Invalid email format"}, 400

        if len(args['username']) < 3 or len(args['username']) > 20:
            return {"error": "Username must be between 3 and 20 characters"}, 400

        try:
            user.username = args['username'].strip()
            user.email = args['email'].strip()
            db.session.commit()
            return user.to_dict(), 200
        except IntegrityError:
            db.session.rollback()
            return {"error": "Both username and email must be unique"}, 400
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}, 500

    def delete(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {"error": "User not found"}, 404

        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted"}, 200

class UserListResource(Resource):
    def get(self):
        users = User.query.all()
        return [user.to_dict() for user in users], 200

    def post(self):
        post_parser = reqparse.RequestParser()
        post_parser.add_argument('username', type=str, required=True, help="Username is required")
        post_parser.add_argument('email', type=str, required=True, help="Email is required")
        
        args = post_parser.parse_args()

        # Enhanced validations
        if not re.match(r"[^@]+@[^@]+\.[^@]+", args['email']):
            return {"error": "Invalid email format"}, 400

        if len(args['username']) < 3 or len(args['username']) > 20:
            return {"error": "Username must be between 3 and 20 characters"}, 400

        if User.query.filter_by(username=args['username']).first():
            return {"error": "Username already exists"}, 400
        if User.query.filter_by(email=args['email']).first():
            return {"error": "Email already exists"}, 400

        new_user = User(username=args['username'].strip(), email=args['email'].strip())

        try:
            db.session.add(new_user)
            db.session.commit()
            return new_user.to_dict(), 201
        except IntegrityError:
            db.session.rollback()
            return {"error": "Both username and email must be unique"}, 400
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}, 500
        
class UserAlertResource(Resource):
    def post(self, user_id):
        """
        Create a new alert for a user.
        """
        user = User.query.get(user_id)
        if not user:
            return {"error": "User not found"}, 404

        post_parser = reqparse.RequestParser()
        post_parser.add_argument('stock_id', type=int, required=True, help="Stock ID is required")
        post_parser.add_argument('condition', type=str, required=True, help="Condition is required (e.g., 'predicted_gain > 10')")
        post_parser.add_argument('days_out', type=int, required=True, help="Days out is required")
        args = post_parser.parse_args()

        stock = Stock.query.get(args['stock_id'])
        if not stock or stock.user_id != user_id:
            return {"error": "Stock not found or not owned by user"}, 404

        try:
            alert = Alert(
                user_id=user_id,
                stock_id=args['stock_id'],
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