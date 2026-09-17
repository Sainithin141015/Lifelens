"""
Study routes – log sessions, analytics, ML predictions.
"""
from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db
from models.study import StudyLog
from services.study_service import StudyService
from ai_models.study_ml import StudyML

study_bp = Blueprint('study', __name__)

MOODS = ['Great', 'Good', 'Neutral', 'Tired', 'Stressed']


@study_bp.route('/')
@login_required
def index():
    uid = current_user.id
    logs = StudyLog.query.filter_by(user_id=uid).order_by(StudyLog.date.desc()).limit(30).all()
    stats = StudyService.weekly_stats(uid)
    subject_breakdown = StudyService.subject_breakdown(uid)
    weekly_trend = StudyService.weekly_trend(uid, weeks=6)
    study_score = StudyService.study_score(uid)

    try:
        predictions = StudyML.predict(uid)
    except Exception:
        predictions = {}

    return render_template('study/index.html',
        logs=logs, stats=stats,
        subject_breakdown=subject_breakdown,
        weekly_trend=weekly_trend,
        study_score=study_score,
        predictions=predictions,
        moods=MOODS,
        today=datetime.utcnow().date()
    )


@study_bp.route('/add', methods=['POST'])
@login_required
def add_log():
    try:
        subject = request.form['subject'].strip()
        hours = float(request.form['hours_studied'])
        difficulty = int(request.form.get('difficulty', 3))
        mood = request.form.get('mood', 'Neutral')
        completed = request.form.get('completed_topics', '').strip()
        notes = request.form.get('notes', '').strip()
        date_str = request.form.get('date') or datetime.utcnow().date().isoformat()
        entry_date = date.fromisoformat(date_str)

        if not subject or hours <= 0:
            flash('Subject and valid hours are required.', 'danger')
            return redirect(url_for('study.index'))

        log = StudyLog(
            user_id=current_user.id, subject=subject,
            hours_studied=hours, difficulty=difficulty,
            mood=mood, completed_topics=completed,
            notes=notes, date=entry_date
        )
        db.session.add(log)
        db.session.commit()
        flash(f'Logged {hours}h of {subject} – keep it up! 📖', 'success')
    except (ValueError, KeyError):
        flash('Invalid data submitted.', 'danger')
    return redirect(url_for('study.index'))


@study_bp.route('/delete/<int:log_id>', methods=['POST'])
@login_required
def delete_log(log_id):
    log = StudyLog.query.filter_by(id=log_id, user_id=current_user.id).first_or_404()
    db.session.delete(log)
    db.session.commit()
    flash('Study log deleted.', 'info')
    return redirect(url_for('study.index'))
