"""
Study analytics service.
"""
from datetime import datetime, timedelta
from models import db
from models.study import StudyLog


class StudyService:

    @staticmethod
    def weekly_stats(user_id):
        today = datetime.utcnow().date()
        week_start = today - timedelta(days=today.weekday())

        logs = StudyLog.query.filter(
            StudyLog.user_id == user_id,
            StudyLog.date >= week_start
        ).all()

        total_hours = sum(l.hours_studied for l in logs)
        avg_difficulty = round(
            sum(l.difficulty for l in logs) / len(logs), 1
        ) if logs else 0

        subjects = list({l.subject for l in logs})

        return {
            'total_hours': round(total_hours, 1),
            'sessions': len(logs),
            'avg_difficulty': avg_difficulty,
            'subjects': subjects
        }

    @staticmethod
    def subject_breakdown(user_id):
        """Hours per subject (all time)."""
        rows = db.session.query(
            StudyLog.subject,
            db.func.sum(StudyLog.hours_studied).label('total')
        ).filter(StudyLog.user_id == user_id).group_by(StudyLog.subject).all()
        return {r.subject: round(r.total, 1) for r in rows}

    @staticmethod
    def weekly_trend(user_id, weeks=6):
        today = datetime.utcnow().date()
        labels, hours_list = [], []

        for i in range(weeks - 1, -1, -1):
            week_start = today - timedelta(days=today.weekday() + i * 7)
            week_end = week_start + timedelta(days=6)
            total = db.session.query(db.func.sum(StudyLog.hours_studied)).filter(
                StudyLog.user_id == user_id,
                StudyLog.date >= week_start,
                StudyLog.date <= week_end
            ).scalar() or 0
            labels.append(week_start.strftime('W %b %d'))
            hours_list.append(round(total, 1))

        return {'labels': labels, 'hours': hours_list}

    @staticmethod
    def study_score(user_id):
        """0-100 study engagement score."""
        today = datetime.utcnow().date()
        last_30 = today - timedelta(days=30)
        logs = StudyLog.query.filter(
            StudyLog.user_id == user_id,
            StudyLog.date >= last_30
        ).all()
        if not logs:
            return 0

        total_hours = sum(l.hours_studied for l in logs)
        # Target: 4h/day * 30 days = 120 hours
        hours_score = min(total_hours / 120, 1.0) * 50

        # Consistency: days studied / 30
        days_studied = len({l.date for l in logs})
        consistency_score = (days_studied / 30) * 30

        # Difficulty bonus
        avg_diff = sum(l.difficulty for l in logs) / len(logs)
        diff_score = (avg_diff / 5) * 20

        return round(hours_score + consistency_score + diff_score, 1)

    @staticmethod
    def get_all_daily_data(user_id):
        """All-time daily study data for ML."""
        rows = db.session.query(
            StudyLog.date,
            db.func.sum(StudyLog.hours_studied).label('hours'),
            db.func.avg(StudyLog.difficulty).label('avg_diff'),
            db.func.count(StudyLog.id).label('sessions')
        ).filter(StudyLog.user_id == user_id).group_by(StudyLog.date).all()

        return [
            {'date': str(r.date), 'hours': float(r.hours or 0),
             'avg_difficulty': float(r.avg_diff or 0), 'sessions': int(r.sessions)}
            for r in rows
        ]
