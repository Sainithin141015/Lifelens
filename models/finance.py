"""
Finance models – Income, Expense, FinancialPrediction.
"""
from datetime import datetime
from models import db


class Income(db.Model):
    __tablename__ = 'income'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    source = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300))
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'amount': self.amount,
            'source': self.source, 'description': self.description,
            'date': self.date.isoformat()
        }


class Expense(db.Model):
    __tablename__ = 'expenses'

    CATEGORIES = [
        'Food', 'Transport', 'Education', 'Entertainment',
        'Shopping', 'Healthcare', 'Utilities', 'Rent', 'Other'
    ]

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False, default='Other')
    description = db.Column(db.String(300))
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'amount': self.amount,
            'category': self.category, 'description': self.description,
            'date': self.date.isoformat()
        }


class FinancialPrediction(db.Model):
    __tablename__ = 'financial_predictions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    predicted_expense = db.Column(db.Float)
    predicted_savings = db.Column(db.Float)
    predicted_cashflow = db.Column(db.Float)
    financial_health_score = db.Column(db.Float)
    months_to_goal = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
