"""
Finance routes – income/expense CRUD, analytics, ML predictions.
"""
from datetime import datetime, date
from collections import defaultdict
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db
from models.finance import Income, Expense
from services.finance_service import FinanceService
from ai_models.finance_ml import FinanceML

finance_bp = Blueprint('finance', __name__)


@finance_bp.route('/')
@login_required
def index():
    uid = current_user.id
    today = datetime.utcnow().date()
    month_start = today.replace(day=1)

    incomes = Income.query.filter_by(user_id=uid).order_by(Income.date.desc()).limit(20).all()
    expenses = Expense.query.filter_by(user_id=uid).order_by(Expense.date.desc()).limit(20).all()

    stats = FinanceService.monthly_stats(uid)
    category_data = FinanceService.category_breakdown(uid)
    monthly_trend = FinanceService.monthly_trend(uid, months=6)
    health_score = FinanceService.health_score(uid)

    # ML predictions
    try:
        predictions = FinanceML.predict(uid)
    except Exception:
        predictions = {}

    return render_template('finance/index.html',
        incomes=incomes, expenses=expenses,
        stats=stats, category_data=category_data,
        monthly_trend=monthly_trend,
        health_score=health_score,
        predictions=predictions,
        categories=Expense.CATEGORIES,
        today=today
    )


@finance_bp.route('/add-income', methods=['POST'])
@login_required
def add_income():
    try:
        amount = float(request.form['amount'])
        source = request.form['source'].strip()
        description = request.form.get('description', '').strip()
        date_str = request.form.get('date') or datetime.utcnow().date().isoformat()
        entry_date = date.fromisoformat(date_str)

        if amount <= 0:
            flash('Amount must be positive.', 'danger')
            return redirect(url_for('finance.index'))

        income = Income(user_id=current_user.id, amount=amount,
                        source=source, description=description, date=entry_date)
        db.session.add(income)
        db.session.commit()
        flash(f'Income of ₹{amount:.2f} added successfully!', 'success')
    except (ValueError, KeyError) as e:
        flash('Invalid data. Please check your inputs.', 'danger')
    return redirect(url_for('finance.index'))


@finance_bp.route('/add-expense', methods=['POST'])
@login_required
def add_expense():
    try:
        amount = float(request.form['amount'])
        category = request.form['category']
        description = request.form.get('description', '').strip()
        date_str = request.form.get('date') or datetime.utcnow().date().isoformat()
        entry_date = date.fromisoformat(date_str)

        if amount <= 0:
            flash('Amount must be positive.', 'danger')
            return redirect(url_for('finance.index'))

        expense = Expense(user_id=current_user.id, amount=amount,
                          category=category, description=description, date=entry_date)
        db.session.add(expense)
        db.session.commit()
        flash(f'Expense of ₹{amount:.2f} in {category} added!', 'success')
    except (ValueError, KeyError):
        flash('Invalid data. Please check your inputs.', 'danger')
    return redirect(url_for('finance.index'))


@finance_bp.route('/delete-income/<int:income_id>', methods=['POST'])
@login_required
def delete_income(income_id):
    income = Income.query.filter_by(id=income_id, user_id=current_user.id).first_or_404()
    db.session.delete(income)
    db.session.commit()
    flash('Income record deleted.', 'info')
    return redirect(url_for('finance.index'))


@finance_bp.route('/delete-expense/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    expense = Expense.query.filter_by(id=expense_id, user_id=current_user.id).first_or_404()
    db.session.delete(expense)
    db.session.commit()
    flash('Expense record deleted.', 'info')
    return redirect(url_for('finance.index'))


@finance_bp.route('/api/chart-data')
@login_required
def chart_data():
    trend = FinanceService.monthly_trend(current_user.id, months=6)
    cat = FinanceService.category_breakdown(current_user.id)
    return jsonify({'trend': trend, 'categories': cat})
