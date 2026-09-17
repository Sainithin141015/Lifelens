"""
Habits routes – daily habit logging and analytics.
"""
from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db
from models.habit import HabitLog
from services.habit_service import HabitService
from ai_models.habit_ml import HabitML

habits_bp = Blueprint('habits', __name__)


@habits_bp.route('/')
@login_required
def index():
    uid = current_user.id
    logs = HabitLog.query.filter_by(user_id=uid).order_by(HabitLog.date.desc()).limit(30).all()
    stats = HabitService.weekly_stats(uid)
    weekly_trend = HabitService.weekly_trend(uid, weeks=6)
    avg_score = HabitService.avg_lifestyle_score(uid)

    try:
        analysis = HabitML.analyze(uid)
    except Exception:
        analysis = {}

    today_log = HabitLog.query.filter_by(
        user_id=uid, date=datetime.utcnow().date()
    ).first()

    return render_template('habits/index.html',
        logs=logs, stats=stats,
        weekly_trend=weekly_trend,
        avg_score=avg_score,
        analysis=analysis,
        today_log=today_log,
        today=datetime.utcnow().date()
    )


@habits_bp.route('/log', methods=['POST'])
@login_required
def log_habit():
    uid = current_user.id
    try:
        log_date = date.fromisoformat(
            request.form.get('date') or datetime.utcnow().date().isoformat()
        )
        sleep_h = float(request.form.get('sleep_hours', 0))
        water = float(request.form.get('water_intake', 0))
        exercise = int(request.form.get('exercise_minutes', 0))
        reading = int(request.form.get('reading_minutes', 0))
        meditation = int(request.form.get('meditation_minutes', 0))
        screen = float(request.form.get('screen_time_hours', 0))
        notes = request.form.get('notes', '').strip()

        # Update existing entry for the day or create new
        existing = HabitLog.query.filter_by(user_id=uid, date=log_date).first()
        if existing:
            log = existing
        else:
            log = HabitLog(user_id=uid, date=log_date)

        log.sleep_hours = sleep_h
        log.water_intake = water
        log.exercise_minutes = exercise
        log.reading_minutes = reading
        log.meditation_minutes = meditation
        log.screen_time_hours = screen
        log.notes = notes
        log.lifestyle_score = log.compute_score(current_user)

        if not existing:
            db.session.add(log)
        db.session.commit()
        flash(f'Habits logged! Lifestyle score: {log.lifestyle_score}/100 💪', 'success')
    except (ValueError, KeyError):
        flash('Invalid data submitted.', 'danger')
    return redirect(url_for('habits.index'))


@habits_bp.route('/delete/<int:log_id>', methods=['POST'])
@login_required
def delete_log(log_id):
    log = HabitLog.query.filter_by(id=log_id, user_id=current_user.id).first_or_404()
    db.session.delete(log)
    db.session.commit()
    flash('Habit log deleted.', 'info')
    return redirect(url_for('habits.index'))
