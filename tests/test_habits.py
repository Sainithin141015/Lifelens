"""Habit logging and scoring tests."""

from tests.conftest import login


def test_log_habit(client, app, user):
    login(client)
    response = client.post(
        "/habits/log",
        data={
            "sleep_hours": "8",
            "water_intake": "8",
            "exercise_minutes": "30",
            "reading_minutes": "30",
            "meditation_minutes": "10",
            "screen_time_hours": "3",
            "notes": "Good day",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302

    from models.habit import HabitLog

    with app.app_context():
        log = HabitLog.query.filter_by(user_id=user.id).first()
        assert log is not None
        assert log.sleep_hours == 8
        assert log.water_intake == 8
        assert log.exercise_minutes == 30
        assert log.lifestyle_score == 95.0


def test_habit_score_is_bounded(app, user):
    from models.habit import HabitLog

    with app.app_context():
        log = HabitLog(
            user_id=user.id,
            sleep_hours=20,
            water_intake=20,
            exercise_minutes=300,
            reading_minutes=300,
            meditation_minutes=100,
            screen_time_hours=20,
        )
        score = log.compute_score(user)
        assert 0 <= score <= 100
