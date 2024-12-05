# server/resources/notification_resource.py

from flask_restful import Resource, reqparse
from config import db
from models import Notification, User
from sqlalchemy.exc import IntegrityError

class NotificationResource(Resource):
    def get(self, user_id):
        """
        Retrieve the last 50 notifications for a specific user.
        """
        user = User.query.get(user_id)
        if not user:
            return {"error": "User not found"}, 404

        notifications = (
            Notification.query.filter_by(user_id=user_id)
            .order_by(Notification.created_at.desc())
            .limit(50)
            .all()
        )
        return [n.to_dict() for n in notifications], 200

    def post(self):
        """
        Internal API: Create a new notification.
        """
        post_parser = reqparse.RequestParser()
        post_parser.add_argument('user_id', type=int, required=True, help="User ID is required")
        post_parser.add_argument('message', type=str, required=True, help="Message is required")
        post_parser.add_argument('channel', type=str, choices=["in-app", "email", "sms"], default="in-app")
        post_parser.add_argument('stock_id', type=int, required=False)
        post_parser.add_argument('alert_id', type=int, required=False)

        args = post_parser.parse_args()

        try:
            notification = Notification(
                user_id=args['user_id'],
                stock_id=args.get('stock_id'),
                alert_id=args.get('alert_id'),
                message=args['message'],
                channel=args['channel']
            )
            db.session.add(notification)
            db.session.commit()
            return notification.to_dict(), 201
        except IntegrityError:
            db.session.rollback()
            return {"error": "Database integrity error"}, 400
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}, 500

    def delete(self, notification_id):
        """
        Delete a notification by ID.
        """
        notification = Notification.query.get(notification_id)
        if not notification:
            return {"error": "Notification not found"}, 404

        db.session.delete(notification)
        db.session.commit()
        return {"message": "Notification deleted"}, 200

class MarkNotificationReadResource(Resource):
    def post(self, notification_id):
        """
        Mark a notification as read.
        """
        notification = Notification.query.get(notification_id)
        if not notification:
            return {"error": "Notification not found"}, 404

        notification.is_read = True  # Add an `is_read` column if needed
        db.session.commit()
        return {"message": "Notification marked as read"}, 200
