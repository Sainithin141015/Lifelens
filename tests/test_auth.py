"""Authentication and access-control tests."""

from tests.conftest import login


def test_application_starts(client):
    response = client.get("/")
    assert response.status_code == 302
    assert "/dashboard" in response.headers["Location"]


def test_register_user(client, app):
    response = client.post(
        "/auth/register",
        data={
            "name": "New User",
            "email": "newuser@example.com",
            "password": "Test@123",
            "confirm_password": "Test@123",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "/dashboard" in response.headers["Location"]

    from models.user import User

    with app.app_context():
        saved = User.query.filter_by(email="newuser@example.com").first()
        assert saved is not None
        assert saved.name == "New User"
        assert saved.check_password("Test@123") is True


def test_valid_login(client, user):
    response = login(client)
    assert response.status_code == 302
    assert "/dashboard" in response.headers["Location"]


def test_invalid_login_is_rejected(client, user):
    response = login(client, password="WrongPassword")
    assert response.status_code == 200
    assert b"Invalid email or password" in response.data


def test_protected_page_requires_login(client):
    response = client.get("/finance/")
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]
