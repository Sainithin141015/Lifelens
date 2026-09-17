"""Study feature tests."""

from tests.conftest import login


def test_add_study_log(client, app, user):
    login(client)
    response = client.post(
        "/study/add",
        data={
            "subject": "DBMS",
            "hours_studied": "2.5",
            "difficulty": "3",
            "mood": "Good",
            "completed_topics": "Joins",
            "notes": "Practiced SQL joins",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302

    from models.study import StudyLog

    with app.app_context():
        log = StudyLog.query.filter_by(user_id=user.id).first()
        assert log is not None
        assert log.subject == "DBMS"
        assert log.hours_studied == 2.5
        assert log.mood == "Good"


def test_invalid_study_hours_are_not_saved(client, app, user):
    login(client)
    response = client.post(
        "/study/add",
        data={"subject": "DBMS", "hours_studied": "0"},
        follow_redirects=False,
    )

    assert response.status_code == 302

    from models.study import StudyLog

    with app.app_context():
        assert StudyLog.query.filter_by(user_id=user.id).count() == 0
