from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"


class QueryHistory(db.Model):
    __tablename__ = "query_history"

    id = db.Column(db.Integer, primary_key=True)
    column = db.Column(db.String(50), nullable=False)
    dataset = db.Column(db.String(20), nullable=False)
    queried_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<QueryHistory {self.column} ({self.dataset})>"


class PredictionLog(db.Model):
    __tablename__ = "prediction_log"

    id = db.Column(db.Integer, primary_key=True)
    prediction = db.Column(db.String(10), nullable=False)
    probability = db.Column(db.Float, nullable=False)
    min_temp = db.Column(db.Float)
    max_temp = db.Column(db.Float)
    humidity_3pm = db.Column(db.Float)
    predicted_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<PredictionLog {self.prediction} ({self.probability}%)>"
