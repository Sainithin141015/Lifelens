"""
Simulation routes – what-if scenario engine.
"""
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from services.finance_service import FinanceService
from services.study_service import StudyService
from services.habit_service import HabitService

simulation_bp = Blueprint('simulation', __name__)


@simulation_bp.route('/')
@login_required
def index():
    uid = current_user.id
    fin_stats = FinanceService.monthly_stats(uid)
    study_stats = StudyService.weekly_stats(uid)
    habit_stats = HabitService.weekly_stats(uid)
    return render_template('simulation/index.html',
        fin_stats=fin_stats,
        study_stats=study_stats,
        habit_stats=habit_stats,
        user=current_user
    )


@simulation_bp.route('/run', methods=['POST'])
@login_required
def run():
    data = request.get_json()
    sim_type = data.get('type', 'finance')
    results = {}

    if sim_type == 'finance':
        results = _simulate_finance(data)
    elif sim_type == 'study':
        results = _simulate_study(data)
    elif sim_type == 'habit':
        results = _simulate_habit(data)

    return jsonify(results)


def _simulate_finance(data):
    """Project savings under different monthly saving rates."""
    current_savings = float(data.get('current_savings', 0))
    goal = float(data.get('goal', 100000))
    months = int(data.get('months', 12))

    scenarios = []
    for label, rate in [
        ('Conservative (+10%)', 1.1),
        ('Current Rate', 1.0),
        ('Optimistic (+25%)', 1.25),
        ('Aggressive (+50%)', 1.5)
    ]:
        monthly = current_savings * rate
        balance_series = []
        bal = 0
        months_to_goal = None
        for m in range(1, months + 1):
            bal += monthly
            balance_series.append(round(bal, 2))
            if months_to_goal is None and bal >= goal:
                months_to_goal = m

        scenarios.append({
            'label': label,
            'monthly_saving': round(monthly, 2),
            'final_balance': round(bal, 2),
            'balance_series': balance_series,
            'months_to_goal': months_to_goal,
            'goal_reached': bal >= goal
        })

    return {'scenarios': scenarios, 'goal': goal, 'months': months,
            'labels': [f'Month {i+1}' for i in range(months)]}


def _simulate_study(data):
    """Predict expected CGPA improvement under different study intensities."""
    current_cgpa = float(data.get('current_cgpa', 6.0))
    target_cgpa = float(data.get('target_cgpa', 8.0))

    scenarios = []
    for hours, label in [(2, '2 hrs/day'), (4, '4 hrs/day'), (6, '6 hrs/day'), (8, '8 hrs/day')]:
        weekly_hours = hours * 7
        # Simple model: each 10 hrs/week above baseline (20h) adds ~0.05 GPA
        baseline = 20
        improvement_per_week = max(0, (weekly_hours - baseline) / 10) * 0.05
        weeks_to_target = None
        if improvement_per_week > 0:
            gap = target_cgpa - current_cgpa
            weeks_to_target = round(gap / improvement_per_week, 0) if gap > 0 else 0

        weeks = 16  # semester
        cgpa_series = []
        cgpa = current_cgpa
        for w in range(weeks):
            cgpa = min(10, cgpa + improvement_per_week)
            cgpa_series.append(round(cgpa, 2))

        scenarios.append({
            'label': label,
            'hours': hours,
            'weekly_hours': weekly_hours,
            'predicted_cgpa': round(cgpa_series[-1], 2),
            'cgpa_series': cgpa_series,
            'weeks_to_target': weeks_to_target
        })

    return {
        'scenarios': scenarios,
        'current_cgpa': current_cgpa,
        'target_cgpa': target_cgpa,
        'labels': [f'Week {i+1}' for i in range(16)]
    }


def _simulate_habit(data):
    """Predict productivity score under different lifestyle changes."""
    current_score = float(data.get('current_score', 50))

    scenarios = [
        {'label': 'More Sleep (+1h)', 'delta': 8, 'changes': ['Sleep +1h/night']},
        {'label': 'More Exercise (+30min)', 'delta': 10, 'changes': ['Exercise +30 min']},
        {'label': 'Less Screen Time (-2h)', 'delta': 7, 'changes': ['Screen time -2h']},
        {'label': 'All Combined', 'delta': 22, 'changes': ['Sleep +1h', 'Exercise +30 min', 'Screen -2h', 'Meditation +10 min']},
    ]

    weeks = 8
    results = []
    for s in scenarios:
        weekly_gain = s['delta'] / 8
        series = []
        score = current_score
        for w in range(weeks):
            score = min(100, score + weekly_gain)
            series.append(round(score, 1))
        results.append({
            'label': s['label'],
            'changes': s['changes'],
            'final_score': series[-1],
            'score_series': series
        })

    return {
        'scenarios': results,
        'current_score': current_score,
        'labels': [f'Week {i+1}' for i in range(weeks)]
    }
