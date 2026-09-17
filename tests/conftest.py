"""Pytest fixtures for LifeLens AI.

The tests use an isolated SQLite database so they do not modify the developer's
normal LifeLens database or require PostgreSQL.
"""

import os
import sys
from pathlib import Path

# Make the project root importable when pytest is run from any directory.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Set database configuration before importing the Flask application.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SESSION_SECRET"] = "test-secret-key"
os.environ.pop("GEMINI_API_KEY", None)
os.environ.pop("OPENAI_API_KEY", None)

import pytest

from app import create_app
from models import db


class TestConfig:
    TESTING = True
    SECRET_KEY = "test-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False


@pytest.fixture()
def app(monkeypatch):
    """Create a fresh application and database for each test."""
    # Prevent demo seed data from making tests depend on random seed records.
    import database.seed
    monkeypatch.setattr(database.seed, "seed_if_empty", lambda: None)

    flask_app = create_app(TestConfig)

    with flask_app.app_context():
        db.drop_all()
        db.create_all()

    yield flask_app

    with flask_app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def user(app):
    """Create a normal test user directly in the test database."""
    from models.user import User

    with app.app_context():
        test_user = User(
            name="Test User",
            email="test@example.com",
            age=21,
            college="Test College",
            degree="B.Tech CSE",
            cgpa=8.5,
            target_cgpa=9.0,
            monthly_income=25000,
            monthly_expenses=15000,
            savings_goal=100000,
            daily_study_hours_goal=4,
            sleep_goal=8,
            exercise_goal=30,
        )
        test_user.set_password("Test@123")
        # Keep attributes loaded after commit so the fixture remains usable
        # after the application context closes.
        db.session().expire_on_commit = False
        db.session.add(test_user)
        db.session.commit()
        return test_user


def login(client, email="test@example.com", password="Test@123"):
    """Log in through the real login route."""
    return client.post(
        "/auth/login",
        data={"email": email, "password": password},
        follow_redirects=False,
    )
