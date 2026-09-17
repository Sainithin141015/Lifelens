"""
Dashboard route – main overview with all analytics.
"""
from datetime import datetime, timedelta
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from models import db
from models.finance import Income, Expense
from models.study import StudyLog
from models.habit import HabitLog
from models.recommendation import Recommendation
from services.finance_service import FinanceService
from services.study_service import StudyService
from services.habit_service import HabitService

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@dashboard_bp.route('/index')
@login_required
def index():
    uid = current_user.id
    today = datetime.utcnow().date()
    month_start = today.replace(day=1)

    # ── Financial Overview ──────────────────────────────────────────
    month_income = db.session.query(db.func.sum(Income.amount)).filter(
        Income.user_id == uid,
        Income.date >= month_start
    ).scalar() or 0

    month_expense = db.session.query(db.func.sum(Expense.amount)).filter(
        Expense.user_id == uid,
        Expense.date >= month_start
    ).scalar() or 0

    total_savings = month_income - month_expense
    savings_pct = round((total_savings / month_income * 100) if month_income > 0 else 0, 1)

    fin_score = FinanceService.health_score(uid)

    # ── Study Overview ───────────────────────────────────────────────
    week_start = today - timedelta(days=today.weekday())
    week_study = db.session.query(db.func.sum(StudyLog.hours_studied)).filter(
        StudyLog.user_id == uid,
        StudyLog.date >= week_start
    ).scalar() or 0

    total_study_logs = StudyLog.query.filter_by(user_id=uid).count()
    study_score = StudyService.study_score(uid)

    # ── Habit Overview ───────────────────────────────────────────────
    today_habit = HabitLog.query.filter_by(user_id=uid, date=today).first()
    lifestyle_score = today_habit.lifestyle_score if today_habit else 0
    avg_lifestyle = HabitService.avg_lifestyle_score(uid)

    # ── Overall Life Score ──────────────────────────────────────────
    life_score = round((fin_score * 0.35 + study_score * 0.35 + avg_lifestyle * 0.30), 1)

    # ── Recent Recommendations ───────────────────────────────────────
    recent_recs = Recommendation.query.filter_by(
        user_id=uid, is_read=False
    ).order_by(Recommendation.created_at.desc()).limit(5).all()

    # ── Last 7 day chart data ────────────────────────────────────────
    days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    daily_expense = []
    daily_income = []
    daily_study = []
    daily_habit = []

    for d in days:
        inc = db.session.query(db.func.sum(Income.amount)).filter(
            Income.user_id == uid, Income.date == d).scalar() or 0
        exp = db.session.query(db.func.sum(Expense.amount)).filter(
            Expense.user_id == uid, Expense.date == d).scalar() or 0
        st = db.session.query(db.func.sum(StudyLog.hours_studied)).filter(
            StudyLog.user_id == uid, StudyLog.date == d).scalar() or 0
        hl = HabitLog.query.filter_by(user_id=uid, date=d).first()
        daily_income.append(round(inc, 2))
        daily_expense.append(round(exp, 2))
        daily_study.append(round(st, 2))
        daily_habit.append(hl.lifestyle_score if hl else 0)

    chart_labels = [d.strftime('%a %d') for d in days]

    # ── Badges ───────────────────────────────────────────────────────
    badges = _compute_badges(uid, total_study_logs, life_score)

    return render_template('dashboard/index.html',
        month_income=round(month_income, 2),
        month_expense=round(month_expense, 2),
        total_savings=round(total_savings, 2),
        savings_pct=savings_pct,
        fin_score=fin_score,
        week_study=round(week_study, 1),
        study_score=study_score,
        lifestyle_score=lifestyle_score,
        avg_lifestyle=avg_lifestyle,
        life_score=life_score,
        recent_recs=recent_recs,
        chart_labels=chart_labels,
        daily_income=daily_income,
        daily_expense=daily_expense,
        daily_study=daily_study,
        daily_habit=daily_habit,
        badges=badges,
        today=today
    )


def _compute_badges(uid, study_logs, life_score):
    badges = []
    if study_logs >= 7:
        badges.append({'icon': '📚', 'name': 'Study Starter', 'desc': '7 study sessions logged'})
    if study_logs >= 30:
        badges.append({'icon': '🎓', 'name': 'Scholar', 'desc': '30 study sessions logged'})
    if life_score >= 70:
        badges.append({'icon': '⭐', 'name': 'Well-Balanced', 'desc': 'Life score above 70'})
    if life_score >= 85:
        badges.append({'icon': '🏆', 'name': 'Peak Performer', 'desc': 'Life score above 85'})
    return badges
