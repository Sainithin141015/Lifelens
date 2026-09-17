"""
Auth routes – register, login, logout, profile.
"""
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db
from models.user import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        if not name or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('auth/register.html')
        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('auth/register.html')

        user = User(name=name, email=email)
        user.set_password(password)
        # Optional profile fields
        try:
            user.age = int(request.form.get('age') or 0) or None
        except ValueError:
            user.age = None
        user.gender = request.form.get('gender', '')
        user.college = request.form.get('college', '')
        user.degree = request.form.get('degree', '')
        try:
            user.current_year = int(request.form.get('current_year') or 0) or None
            user.cgpa = float(request.form.get('cgpa') or 0) or None
            user.monthly_income = float(request.form.get('monthly_income') or 0)
            user.monthly_expenses = float(request.form.get('monthly_expenses') or 0)
            user.savings_goal = float(request.form.get('savings_goal') or 0)
            user.target_cgpa = float(request.form.get('target_cgpa') or 0) or None
            user.daily_study_hours_goal = float(request.form.get('daily_study_hours_goal') or 6)
            user.sleep_goal = float(request.form.get('sleep_goal') or 8)
            user.exercise_goal = float(request.form.get('exercise_goal') or 30)
        except ValueError:
            pass

        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(f'Welcome to LifeLens AI, {name}! 🎉', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            user.last_login = datetime.utcnow()
            db.session.commit()
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(next_page or url_for('dashboard.index'))
        flash('Invalid email or password.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.name = request.form.get('name', current_user.name).strip()
        try:
            current_user.age = int(request.form.get('age') or 0) or current_user.age
            current_user.gender = request.form.get('gender', current_user.gender)
            current_user.college = request.form.get('college', current_user.college)
            current_user.degree = request.form.get('degree', current_user.degree)
            current_user.current_year = int(request.form.get('current_year') or 0) or current_user.current_year
            current_user.cgpa = float(request.form.get('cgpa') or 0) or current_user.cgpa
            current_user.monthly_income = float(request.form.get('monthly_income') or 0)
            current_user.monthly_expenses = float(request.form.get('monthly_expenses') or 0)
            current_user.savings_goal = float(request.form.get('savings_goal') or 0)
            current_user.target_cgpa = float(request.form.get('target_cgpa') or 0) or current_user.target_cgpa
            current_user.daily_study_hours_goal = float(request.form.get('daily_study_hours_goal') or 6)
            current_user.sleep_goal = float(request.form.get('sleep_goal') or 8)
            current_user.exercise_goal = float(request.form.get('exercise_goal') or 30)
        except ValueError:
            flash('Invalid numeric value.', 'danger')
            return render_template('auth/profile.html')
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html')


@auth_bp.route('/toggle-dark-mode', methods=['POST'])
@login_required
def toggle_dark_mode():
    current_user.dark_mode = not current_user.dark_mode
    db.session.commit()
    return {'dark_mode': current_user.dark_mode}
