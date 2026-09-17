"""
Habit analytics service.
"""
from datetime import datetime, timedelta
from models import db
from models.habit import HabitLog


class HabitService:

    @staticmethod
    def weekly_stats(user_id):
        today = datetime.utcnow().date()
        week_start = today - timedelta(days=today.weekday())

        logs = HabitLog.query.filter(
            HabitLog.user_id == user_id,
            HabitLog.date >= week_start
        ).all()

        if not logs:
            return {
                'avg_sleep': 0, 'avg_water': 0,
                'avg_exercise': 0, 'avg_screen': 0,
                'avg_score': 0, 'days_logged': 0
            }

        return {
            'avg_sleep': round(sum(l.sleep_hours for l in logs) / len(logs), 1),
            'avg_water': round(sum(l.water_intake for l in logs) / len(logs), 1),
            'avg_exercise': round(sum(l.exercise_minutes for l in logs) / len(logs), 0),
            'avg_screen': round(sum(l.screen_time_hours for l in logs) / len(logs), 1),
            'avg_score': round(sum((l.lifestyle_score or 0) for l in logs) / len(logs), 1),
            'days_logged': len(logs)
        }

    @staticmethod
    def weekly_trend(user_id, weeks=6):
        today = datetime.utcnow().date()
        labels, scores, sleep_list, exercise_list = [], [], [], []

        for i in range(weeks - 1, -1, -1):
            week_start = today - timedelta(days=today.weekday() + i * 7)
            week_end = week_start + timedelta(days=6)
            logs = HabitLog.query.filter(
                HabitLog.user_id == user_id,
                HabitLog.date >= week_start,
                HabitLog.date <= week_end
            ).all()

            if logs:
                avg_score = sum((l.lifestyle_score or 0) for l in logs) / len(logs)
                avg_sleep = sum(l.sleep_hours for l in logs) / len(logs)
                avg_ex = sum(l.exercise_minutes for l in logs) / len(logs)
            else:
                avg_score = avg_sleep = avg_ex = 0

            labels.append(week_start.strftime('W %b %d'))
            scores.append(round(avg_score, 1))
            sleep_list.append(round(avg_sleep, 1))
            exercise_list.append(round(avg_ex, 0))

        return {'labels': labels, 'scores': scores, 'sleep': sleep_list, 'exercise': exercise_list}

    @staticmethod
    def avg_lifestyle_score(user_id, days=30):
        today = datetime.utcnow().date()
        since = today - timedelta(days=days)
        logs = HabitLog.query.filter(
            HabitLog.user_id == user_id,
            HabitLog.date >= since
        ).all()
        if not logs:
            return 0
        return round(sum((l.lifestyle_score or 0) for l in logs) / len(logs), 1)

    @staticmethod
    def get_all_daily_data(user_id):
        logs = HabitLog.query.filter_by(user_id=user_id).order_by(HabitLog.date).all()
        return [
            {
                'date': str(l.date),
                'sleep_hours': l.sleep_hours or 0,
                'water_intake': l.water_intake or 0,
                'exercise_minutes': l.exercise_minutes or 0,
                'screen_time_hours': l.screen_time_hours or 0,
                'lifestyle_score': l.lifestyle_score or 0
            }
            for l in logs
        ]
