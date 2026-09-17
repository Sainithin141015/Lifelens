"""
Habit models – HabitLog, HabitPrediction.
"""
from datetime import datetime
from models import db


class HabitLog(db.Model):
    __tablename__ = 'habit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)

    # Tracked habits (all numeric)
    sleep_hours = db.Column(db.Float, default=0)
    water_intake = db.Column(db.Float, default=0)    # glasses
    exercise_minutes = db.Column(db.Integer, default=0)
    reading_minutes = db.Column(db.Integer, default=0)
    meditation_minutes = db.Column(db.Integer, default=0)
    screen_time_hours = db.Column(db.Float, default=0)

    # Computed daily score (0-100)
    lifestyle_score = db.Column(db.Float)

    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def compute_score(self, user):
        """Compute lifestyle score based on user goals."""
        score = 0
        # Sleep: up to 25 pts
        if self.sleep_hours:
            goal = user.sleep_goal or 8
            ratio = min(self.sleep_hours / goal, 1.0)
            score += ratio * 25
        # Water: up to 20 pts (goal = 8 glasses)
        score += min(self.water_intake / 8, 1.0) * 20
        # Exercise: up to 25 pts
        if self.exercise_minutes:
            goal = user.exercise_goal or 30
            ratio = min(self.exercise_minutes / goal, 1.0)
            score += ratio * 25
        # Reading: up to 15 pts (goal = 30 mins)
        score += min((self.reading_minutes or 0) / 30, 1.0) * 15
        # Meditation: up to 10 pts (goal = 10 mins)
        score += min((self.meditation_minutes or 0) / 10, 1.0) * 10
        # Screen time: penalty up to -5 pts (>4 hrs is bad)
        excess = max(0, (self.screen_time_hours or 0) - 4)
        score -= min(excess * 1.25, 5)
        return round(max(0, min(score, 100)), 1)

    def to_dict(self):
        return {
            'id': self.id, 'date': self.date.isoformat(),
            'sleep_hours': self.sleep_hours, 'water_intake': self.water_intake,
            'exercise_minutes': self.exercise_minutes, 'reading_minutes': self.reading_minutes,
            'meditation_minutes': self.meditation_minutes, 'screen_time_hours': self.screen_time_hours,
            'lifestyle_score': self.lifestyle_score
        }
