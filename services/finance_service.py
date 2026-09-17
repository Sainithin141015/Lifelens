"""
Finance analytics service – aggregation helpers used by routes and ML.
"""
from datetime import datetime, timedelta
from collections import defaultdict
from models import db
from models.finance import Income, Expense


class FinanceService:

    @staticmethod
    def monthly_stats(user_id):
        today = datetime.utcnow().date()
        month_start = today.replace(day=1)

        inc = db.session.query(db.func.sum(Income.amount)).filter(
            Income.user_id == user_id, Income.date >= month_start
        ).scalar() or 0

        exp = db.session.query(db.func.sum(Expense.amount)).filter(
            Expense.user_id == user_id, Expense.date >= month_start
        ).scalar() or 0

        savings = inc - exp
        savings_pct = round((savings / inc * 100) if inc > 0 else 0, 1)

        return {
            'income': round(inc, 2),
            'expense': round(exp, 2),
            'savings': round(savings, 2),
            'savings_pct': savings_pct
        }

    @staticmethod
    def category_breakdown(user_id):
        """Returns dict: {category: total_amount} for current month."""
        today = datetime.utcnow().date()
        month_start = today.replace(day=1)

        rows = db.session.query(
            Expense.category, db.func.sum(Expense.amount)
        ).filter(
            Expense.user_id == user_id,
            Expense.date >= month_start
        ).group_by(Expense.category).all()

        return {cat: round(amt, 2) for cat, amt in rows}

    @staticmethod
    def monthly_trend(user_id, months=6):
        """Returns last N months income/expense/savings as lists."""
        today = datetime.utcnow().date()
        labels, incomes, expenses, savings = [], [], [], []

        for i in range(months - 1, -1, -1):
            # Calculate month boundaries
            month = today.month - i
            year = today.year
            while month <= 0:
                month += 12
                year -= 1
            start = datetime(year, month, 1).date()
            if month == 12:
                end = datetime(year + 1, 1, 1).date()
            else:
                end = datetime(year, month + 1, 1).date()

            inc = db.session.query(db.func.sum(Income.amount)).filter(
                Income.user_id == user_id,
                Income.date >= start, Income.date < end
            ).scalar() or 0

            exp = db.session.query(db.func.sum(Expense.amount)).filter(
                Expense.user_id == user_id,
                Expense.date >= start, Expense.date < end
            ).scalar() or 0

            labels.append(start.strftime('%b %Y'))
            incomes.append(round(inc, 2))
            expenses.append(round(exp, 2))
            savings.append(round(inc - exp, 2))

        return {'labels': labels, 'incomes': incomes, 'expenses': expenses, 'savings': savings}

    @staticmethod
    def health_score(user_id):
        """Financial health score 0-100."""
        stats = FinanceService.monthly_stats(user_id)
        inc = stats['income']
        if inc == 0:
            return 50

        savings_ratio = stats['savings'] / inc  # -1 to 1
        score = 50 + (savings_ratio * 50)

        # Bonus: savings above 30% target
        if savings_ratio >= 0.3:
            score = min(100, score + 10)
        elif savings_ratio < 0:
            score = max(0, score - 20)

        return round(score, 1)

    @staticmethod
    def get_all_monthly_data(user_id):
        """Returns all-time monthly aggregates for ML training."""
        rows_inc = db.session.query(
            db.func.date_trunc('month', Income.date).label('month'),
            db.func.sum(Income.amount).label('total')
        ).filter(Income.user_id == user_id).group_by('month').all()

        rows_exp = db.session.query(
            db.func.date_trunc('month', Expense.date).label('month'),
            db.func.sum(Expense.amount).label('total')
        ).filter(Expense.user_id == user_id).group_by('month').all()

        inc_map = {str(r.month)[:7]: r.total for r in rows_inc}
        exp_map = {str(r.month)[:7]: r.total for r in rows_exp}

        months = sorted(set(list(inc_map.keys()) + list(exp_map.keys())))
        data = []
        for m in months:
            inc = inc_map.get(m, 0) or 0
            exp = exp_map.get(m, 0) or 0
            data.append({'month': m, 'income': inc, 'expense': exp, 'savings': inc - exp})
        return data
