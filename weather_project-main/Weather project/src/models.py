from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class QueryHistory(db.Model):
    __tablename__ = "query_history"

    id = db.Column(db.Integer, primary_key=True)
    column = db.Column(db.String(50), nullable=False)
    dataset = db.Column(db.String(20), nullable=False)
    queried_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<QueryHistory {self.column} ({self.dataset})>"
