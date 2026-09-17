"""
Study ML – predicts expected GPA, study trend, and performance score.
"""
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor


class StudyML:

    @staticmethod
    def predict(user_id: int) -> dict:
        from services.study_service import StudyService
        from models.user import User

        data = StudyService.get_all_daily_data(user_id)
        user = User.query.get(user_id)

        if len(data) < 5:
            weekly_stats = StudyService.weekly_stats(user_id)
            study_score = StudyService.study_score(user_id)
            current_cgpa = user.cgpa or 0
            target_cgpa = user.target_cgpa or 0

            # Estimate time to target
            hours_per_week = weekly_stats['total_hours']
            weeks_needed = None
            if target_cgpa > current_cgpa and hours_per_week > 0:
                gap = target_cgpa - current_cgpa
                weekly_gain = max(0, (hours_per_week - 20) / 10) * 0.05
                weeks_needed = round(gap / weekly_gain, 0) if weekly_gain > 0 else None

            return {
                'study_trend': 'Insufficient data',
                'predicted_score': study_score,
                'weeks_to_target': weeks_needed,
                'weak_subjects': [],
                'consistency_score': 0,
                'confidence': 'low',
                'note': 'Log more sessions for accurate ML predictions.'
            }

        # Features: [day_idx, avg_difficulty, sessions_per_day] -> hours
        X, y = [], []
        for i, d in enumerate(data):
            X.append([i, d['avg_difficulty'], d['sessions']])
            y.append(d['hours'])

        X, y = np.array(X), np.array(y)
        model = Ridge(alpha=1.0).fit(X, y)

        # Predict next 7 days
        n = len(data)
        preds = []
        avg_diff = float(np.mean([d['avg_difficulty'] for d in data[-7:]]))
        avg_sess = float(np.mean([d['sessions'] for d in data[-7:]]))
        for i in range(7):
            preds.append(max(0, model.predict([[n + i, avg_diff, avg_sess]])[0]))
        predicted_weekly = round(sum(preds), 1)

        # Trend
        recent_5 = [d['hours'] for d in data[-5:]]
        earlier_5 = [d['hours'] for d in data[-10:-5]] if len(data) >= 10 else [d['hours'] for d in data[:5]]
        trend = 'Improving' if np.mean(recent_5) > np.mean(earlier_5) else 'Declining'

        # Consistency (% days studied in last 30 days)
        from datetime import datetime, timedelta
        from models.study import StudyLog
        today = datetime.utcnow().date()
        since = today - timedelta(days=30)
        days_with_study = len({d['date'] for d in data if d['date'] >= str(since)})
        consistency = round(days_with_study / 30 * 100, 1)

        # Weak subjects (fewest total hours)
        subject_data = StudyService.subject_breakdown(user_id)
        sorted_subs = sorted(subject_data.items(), key=lambda x: x[1])
        weak_subjects = [s[0] for s in sorted_subs[:2]] if sorted_subs else []

        # Estimated weeks to CGPA target
        from models.user import User
        user = User.query.get(user_id)
        current_cgpa = user.cgpa or 0
        target_cgpa = user.target_cgpa or 0
        weekly_gain = max(0, (predicted_weekly - 20) / 10) * 0.05
        weeks_needed = None
        if target_cgpa > current_cgpa and weekly_gain > 0:
            gap = target_cgpa - current_cgpa
            weeks_needed = round(gap / weekly_gain, 0)

        return {
            'study_trend': trend,
            'predicted_weekly_hours': predicted_weekly,
            'weeks_to_target': weeks_needed,
            'weak_subjects': weak_subjects,
            'consistency_score': consistency,
            'confidence': 'high' if n >= 20 else 'medium',
            'data_points': n
        }
