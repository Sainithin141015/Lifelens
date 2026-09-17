"""Simulation engine tests."""

from tests.conftest import login


def test_finance_simulation(client, user):
    login(client)
    response = client.post(
        "/simulation/run",
        json={
            "type": "finance",
            "current_savings": 5000,
            "goal": 20000,
            "months": 12,
        },
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["goal"] == 20000.0
    assert data["months"] == 12
    assert len(data["scenarios"]) == 4
    assert all(len(s["balance_series"]) == 12 for s in data["scenarios"])


def test_study_simulation(client, user):
    login(client)
    response = client.post(
        "/simulation/run",
        json={
            "type": "study",
            "current_cgpa": 8.0,
            "target_cgpa": 9.0,
        },
    )

    assert response.status_code == 200
    data = response.get_json()
    assert len(data["scenarios"]) == 4
    assert all(len(s["cgpa_series"]) == 16 for s in data["scenarios"])
    assert all(0 <= s["predicted_cgpa"] <= 10 for s in data["scenarios"])


def test_habit_simulation(client, user):
    login(client)
    response = client.post(
        "/simulation/run",
        json={"type": "habit", "current_score": 60},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert len(data["scenarios"]) == 4
    assert all(len(s["score_series"]) == 8 for s in data["scenarios"])
    assert all(0 <= s["final_score"] <= 100 for s in data["scenarios"])
