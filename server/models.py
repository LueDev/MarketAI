# server/models.py

from config import db
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import relationship
from sqlalchemy import func

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    serialize_rules = ('-stocks.user', '-alerts.user', '-notifications.user')

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)

    stocks = relationship('Stock', back_populates='user')
    alerts = relationship('Alert', back_populates='user')  # Relationship with Alert
    notifications = relationship('Notification', back_populates='user')  # Add this line

class Stock(db.Model, SerializerMixin):
    __tablename__ = 'stocks'
    serialize_rules = ('-user.stocks', '-user_id', '-user', '-sector.id', '-sector.stocks', '-analyses.stock', '-alerts.stock')

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    symbol = db.Column(db.String, nullable=False)
    sector_id = db.Column(db.Integer, db.ForeignKey('sectors.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    sector = relationship('Sector', back_populates='stocks')
    user = relationship('User', back_populates='stocks')
    analyses = relationship('Analysis', back_populates='stock')
    alerts = relationship('Alert', back_populates='stock')  # Added relationship
    notifications = relationship('Notification', back_populates='stock')


class Sector(db.Model, SerializerMixin):
    __tablename__ = 'sectors'
    serialize_rules = ('-stocks.sector','-stocks.stock_id', '-stocks.analyses', '-stocks.user', '-stocks.user_id', '-stocks.sector_id', '-stocks.id')

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)

    stocks = relationship('Stock', back_populates='sector')

class Analysis(db.Model, SerializerMixin):
    __tablename__ = 'analysis'
    serialize_rules = ('-id', '-stock_id','-updated_at', '-created_at', '-stock.stock_id', '-stock.analyses','-stock.user', '-stock.user_id', '-stock.sector_id', '-stock.id')

    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'))
    attribute = db.Column(db.String, nullable=False)
    value = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    stock = relationship('Stock', back_populates='analyses')

class Alert(db.Model):
    __tablename__ = 'alerts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    condition = db.Column(db.String, nullable=False)  # e.g., "predicted_gain > 10"
    days_out = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    is_triggered = db.Column(db.Boolean, default=False, nullable=False)

    user = relationship('User', back_populates='alerts')
    stock = relationship('Stock', back_populates='alerts')
    notifications = relationship('Notification', back_populates='alert')


class Notification(db.Model, SerializerMixin):
    __tablename__ = 'notifications'
    serialize_rules = ('-stocks.user', '-alerts.user', '-notifications.user')

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=True)
    alert_id = db.Column(db.Integer, db.ForeignKey('alerts.id'), nullable=True)  # Links to the triggered alert
    message = db.Column(db.String, nullable=False)  # Notification message
    channel = db.Column(db.String, default="in-app", nullable=False)  # in-app, email, sms, etc.
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)

    user = relationship('User', back_populates='notifications')  # Matches User.notifications
    stock = relationship('Stock', back_populates='notifications')
    alert = relationship('Alert', back_populates='notifications')
