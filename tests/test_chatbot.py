"""Chatbot endpoint validation tests."""

from tests.conftest import login


def test_empty_chat_message_returns_400(client, user):
    login(client)
    response = client.post("/chatbot/ask", json={"message": ""})

    assert response.status_code == 400
    assert response.get_json()["error"] == "Empty message"
