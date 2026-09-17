"""
Seed sample data for demonstration purposes.
Only runs if the database is empty (no users exist).
"""
from datetime import datetime, timedelta
import random


def seed_if_empty():
    from models import db
    from models.user import User
    from models.finance import Income, Expense
    from models.study import StudyLog
    from models.habit import HabitLog

    if User.query.count() > 0:
        return  # Already seeded

    # ── Demo User ────────────────────────────────────────────────────
    user = User(
        name='Alex Johnson',
        email='demo@lifelens.ai',
        age=21,
        gender='Male',
        college='Tech University',
        degree='B.Tech Computer Science',
        current_year=3,
        cgpa=7.8,
        monthly_income=25000,
        monthly_expenses=18000,
        savings_goal=100000,
        target_cgpa=9.0,
        daily_study_hours_goal=5,
        sleep_goal=8,
        exercise_goal=30,
        total_points=250,
        streak_days=7
    )
    user.set_password('demo1234')
    db.session.add(user)
    db.session.flush()

    today = datetime.utcnow().date()

    # ── Income (last 3 months) ───────────────────────────────────────
    income_sources = ['Part-time Job', 'Freelance', 'Internship Stipend', 'Scholarship']
    for months_ago in range(3, -1, -1):
        for _ in range(2):
            day_offset = random.randint(1, 28)
            month = today.month - months_ago
            year = today.year
            while month <= 0:
                month += 12
                year -= 1
            try:
                entry_date = datetime(year, month, day_offset).date()
            except Exception:
                entry_date = today
            inc = Income(
                user_id=user.id,
                amount=random.choice([12000, 13000, 15000, 8000, 10000]),
                source=random.choice(income_sources),
                description='Regular payment',
                date=entry_date
            )
            db.session.add(inc)

    # ── Expenses (last 3 months) ────────────────────────────────────
    expense_items = [
        ('Food', 'Cafeteria & snacks', 3000),
        ('Transport', 'Bus pass & Uber', 1500),
        ('Education', 'Books & courses', 2000),
        ('Entertainment', 'Movies & gaming', 1200),
        ('Shopping', 'Clothes & accessories', 2500),
        ('Healthcare', 'Gym & medicines', 800),
        ('Utilities', 'Phone & internet', 1000),
    ]
    for months_ago in range(3, -1, -1):
        for cat, desc, base_amt in expense_items:
            day_offset = random.randint(1, 28)
            month = today.month - months_ago
            year = today.year
            while month <= 0:
                month += 12
                year -= 1
            try:
                entry_date = datetime(year, month, day_offset).date()
            except Exception:
                entry_date = today
            exp = Expense(
                user_id=user.id,
                amount=base_amt + random.randint(-500, 500),
                category=cat,
                description=desc,
                date=entry_date
            )
            db.session.add(exp)

    # ── Study Logs (last 30 days) ────────────────────────────────────
    subjects = ['Mathematics', 'Data Structures', 'Machine Learning', 'DBMS', 'OS', 'Python']
    moods = ['Great', 'Good', 'Neutral', 'Tired', 'Good', 'Great']
    for days_ago in range(30, 0, -1):
        if random.random() < 0.7:  # Study 70% of days
            n_sessions = random.randint(1, 3)
            for _ in range(n_sessions):
                log = StudyLog(
                    user_id=user.id,
                    subject=random.choice(subjects),
                    hours_studied=round(random.uniform(0.5, 3.5), 1),
                    difficulty=random.randint(2, 5),
                    mood=random.choice(moods),
                    completed_topics=f'Chapter {random.randint(1, 10)}, Exercise {random.randint(1, 5)}',
                    date=today - timedelta(days=days_ago)
                )
                db.session.add(log)

    # ── Habit Logs (last 30 days) ────────────────────────────────────
    for days_ago in range(30, 0, -1):
        if random.random() < 0.75:
            sleep = round(random.uniform(5.5, 9.0), 1)
            water = round(random.uniform(4, 10), 1)
            exercise = random.randint(0, 60)
            reading = random.randint(0, 45)
            meditation = random.randint(0, 20)
            screen = round(random.uniform(2, 8), 1)

            log = HabitLog(
                user_id=user.id,
                date=today - timedelta(days=days_ago),
                sleep_hours=sleep,
                water_intake=water,
                exercise_minutes=exercise,
                reading_minutes=reading,
                meditation_minutes=meditation,
                screen_time_hours=screen
            )
            log.lifestyle_score = log.compute_score(user)
            db.session.add(log)

    db.session.commit()
    print("✅ Demo data seeded successfully! Login: demo@lifelens.ai / demo1234")
