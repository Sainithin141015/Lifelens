"""
Habit ML – identifies patterns and predicts lifestyle improvement opportunities.
"""
import numpy as np


class HabitML:

    @staticmethod
    def analyze(user_id: int) -> dict:
        from services.habit_service import HabitService
        from models.user import User

        data = HabitService.get_all_daily_data(user_id)
        user = User.query.get(user_id)

        if len(data) < 3:
            return {
                'positive_habits': [],
                'negative_habits': [],
                'improvement_areas': ['Sleep', 'Exercise', 'Hydration'],
                'predicted_score_30d': 60,
                'trend': 'Insufficient data',
                'confidence': 'low'
            }

        scores = [d['lifestyle_score'] for d in data]
        sleep_vals = [d['sleep_hours'] for d in data]
        water_vals = [d['water_intake'] for d in data]
        exercise_vals = [d['exercise_minutes'] for d in data]
        screen_vals = [d['screen_time_hours'] for d in data]

        avg_score = float(np.mean(scores))
        avg_sleep = float(np.mean(sleep_vals))
        avg_water = float(np.mean(water_vals))
        avg_exercise = float(np.mean(exercise_vals))
        avg_screen = float(np.mean(screen_vals))

        # Trend
        recent = np.mean(scores[-7:]) if len(scores) >= 7 else avg_score
        earlier = np.mean(scores[:-7]) if len(scores) > 7 else avg_score
        trend = 'Improving' if recent > earlier + 2 else ('Declining' if recent < earlier - 2 else 'Stable')

        # Positive habits (above goal thresholds)
        positive, negative, improvements = [], [], []
        sleep_goal = user.sleep_goal or 8
        exercise_goal = user.exercise_goal or 30

        if avg_sleep >= sleep_goal * 0.9:
            positive.append(f'Good sleep average ({avg_sleep:.1f}h/night)')
        else:
            negative.append(f'Below-target sleep ({avg_sleep:.1f}h vs {sleep_goal}h goal)')
            improvements.append('Sleep')

        if avg_water >= 6:
            positive.append(f'Consistent hydration ({avg_water:.1f} glasses/day)')
        else:
            negative.append(f'Low water intake ({avg_water:.1f}/8 glasses target)')
            improvements.append('Hydration')

        if avg_exercise >= exercise_goal * 0.8:
            positive.append(f'Regular exercise ({avg_exercise:.0f} min/day)')
        else:
            negative.append(f'Insufficient exercise ({avg_exercise:.0f} vs {exercise_goal:.0f} min goal)')
            improvements.append('Exercise')

        if avg_screen <= 5:
            positive.append(f'Managed screen time ({avg_screen:.1f}h/day)')
        else:
            negative.append(f'High screen time ({avg_screen:.1f}h/day)')
            improvements.append('Screen Time')

        # Predict score in 30 days if user improves top area
        potential_gain = len(improvements) * 5
        predicted_30d = min(100, round(avg_score + potential_gain, 1))

        # Correlation analysis
        if len(data) >= 10:
            sleep_arr = np.array(sleep_vals)
            score_arr = np.array(scores)
            try:
                sleep_corr = float(np.corrcoef(sleep_arr, score_arr)[0, 1])
            except Exception:
                sleep_corr = 0
        else:
            sleep_corr = 0

        return {
            'positive_habits': positive,
            'negative_habits': negative,
            'improvement_areas': improvements,
            'avg_score': round(avg_score, 1),
            'predicted_score_30d': predicted_30d,
            'trend': trend,
            'sleep_score_correlation': round(sleep_corr, 2),
            'confidence': 'high' if len(data) >= 14 else 'medium',
            'data_points': len(data)
        }
