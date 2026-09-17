"""
User model – authentication + personal profile + goals.
"""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from models import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)

    # Personal details
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))

    # Education
    college = db.Column(db.String(200))
    degree = db.Column(db.String(100))
    current_year = db.Column(db.Integer)
    cgpa = db.Column(db.Float)

    # Financial
    monthly_income = db.Column(db.Float, default=0)
    monthly_expenses = db.Column(db.Float, default=0)
    savings_goal = db.Column(db.Float, default=0)

    # Study goals
    target_cgpa = db.Column(db.Float)
    daily_study_hours_goal = db.Column(db.Float, default=6)

    # Lifestyle goals
    sleep_goal = db.Column(db.Float, default=8)
    exercise_goal = db.Column(db.Float, default=30)  # minutes/day

    # Gamification
    total_points = db.Column(db.Integer, default=0)
    streak_days = db.Column(db.Integer, default=0)

    # Meta
    dark_mode = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Relationships
    income_records = db.relationship('Income', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    expense_records = db.relationship('Expense', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    study_logs = db.relationship('StudyLog', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    habit_logs = db.relationship('HabitLog', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    recommendations = db.relationship('Recommendation', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'
