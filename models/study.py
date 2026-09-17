"""
Study models – StudyLog, StudyPrediction.
"""
from datetime import datetime
from models import db


class StudyLog(db.Model):
    __tablename__ = 'study_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    subject = db.Column(db.String(100), nullable=False)
    hours_studied = db.Column(db.Float, nullable=False)
    difficulty = db.Column(db.Integer, default=3)   # 1-5
    mood = db.Column(db.String(30), default='Neutral')  # Great/Good/Neutral/Tired/Stressed
    completed_topics = db.Column(db.Text)           # comma-separated
    notes = db.Column(db.Text)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'subject': self.subject,
            'hours_studied': self.hours_studied, 'difficulty': self.difficulty,
            'mood': self.mood, 'completed_topics': self.completed_topics,
            'notes': self.notes, 'date': self.date.isoformat()
        }
