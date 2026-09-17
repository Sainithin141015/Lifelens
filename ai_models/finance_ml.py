"""
Finance ML – predicts next-month expenses, savings, and cashflow.
Uses LinearRegression with time-series features.
"""
import os
import numpy as np
import joblib
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

MODEL_DIR = os.path.join(os.path.dirname(__file__), 'saved')
os.makedirs(MODEL_DIR, exist_ok=True)


class FinanceML:

    @staticmethod
    def predict(user_id: int) -> dict:
        from services.finance_service import FinanceService
        data = FinanceService.get_all_monthly_data(user_id)

        if len(data) < 2:
            # Not enough data — return smart estimates
            stats = FinanceService.monthly_stats(user_id)
            return {
                'predicted_expense': round(stats['expense'] * 1.02, 2),
                'predicted_savings': round(stats['savings'] * 0.98, 2),
                'predicted_cashflow': round(stats['savings'] * 0.98, 2),
                'months_to_goal': None,
                'confidence': 'low',
                'note': 'Based on current month data. Log more months for accurate predictions.'
            }

        # Build feature matrix: [month_index, expense_lag1, income_lag1]
        incomes = [d['income'] for d in data]
        expenses = [d['expense'] for d in data]
        savings = [d['savings'] for d in data]
        n = len(data)

        # Prepare sequences
        X_exp, y_exp = [], []
        X_sav, y_sav = [], []
        for i in range(1, n):
            X_exp.append([i, expenses[i-1], incomes[i]])
            y_exp.append(expenses[i])
            X_sav.append([i, savings[i-1], incomes[i]])
            y_sav.append(savings[i])

        if not X_exp:
            return {'predicted_expense': expenses[-1], 'predicted_savings': savings[-1],
                    'predicted_cashflow': savings[-1], 'months_to_goal': None, 'confidence': 'low'}

        # Train expense model
        model_exp = LinearRegression().fit(np.array(X_exp), np.array(y_exp))
        model_sav = LinearRegression().fit(np.array(X_sav), np.array(y_sav))

        # Predict next month
        next_idx = n
        avg_income = np.mean(incomes[-3:]) if len(incomes) >= 3 else incomes[-1]
        pred_expense = max(0, model_exp.predict([[next_idx, expenses[-1], avg_income]])[0])
        pred_savings = model_sav.predict([[next_idx, savings[-1], avg_income]])[0]
        pred_cashflow = avg_income - pred_expense

        # Months to savings goal
        from models.user import User
        user = User.query.get(user_id)
        goal = user.savings_goal if user else 0
        current_total = sum(s for s in savings if s > 0)
        months_to_goal = None
        if goal and pred_savings > 0:
            remaining = max(0, goal - current_total)
            months_to_goal = round(remaining / pred_savings, 1)

        return {
            'predicted_expense': round(pred_expense, 2),
            'predicted_savings': round(pred_savings, 2),
            'predicted_cashflow': round(pred_cashflow, 2),
            'months_to_goal': months_to_goal,
            'confidence': 'high' if n >= 6 else 'medium',
            'data_points': n
        }
