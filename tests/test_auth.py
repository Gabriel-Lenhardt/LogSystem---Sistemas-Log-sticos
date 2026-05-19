"""Authentication tests."""

from __future__ import annotations


def test_dashboard_redirects_anonymous_user_to_login(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_login_page_loads(client):
    response = client.get("/auth/login")
    assert response.status_code == 200
    assert b"Sign in" in response.data


def test_login_with_valid_credentials_redirects_to_dashboard(client, admin_user):
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin123"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_login_with_invalid_credentials_shows_error(client, admin_user):
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "wrong"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Invalid username or password" in response.data


def test_logout_clears_session(auth_client):
    response = auth_client.get("/auth/logout", follow_redirects=False)
    assert response.status_code == 302

    response = auth_client.get("/", follow_redirects=False)
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_register_creates_user(client, db):
    from app.models import User

    response = client.post(
        "/auth/register",
        data={
            "username": "newuser",
            "email": "new@example.com",
            "password": "secret123",
            "confirm_password": "secret123",
        },
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert db.session.query(User).filter_by(username="newuser").one()


def test_register_rejects_duplicate_username(client, admin_user):
    response = client.post(
        "/auth/register",
        data={
            "username": "admin",
            "email": "other@example.com",
            "password": "secret123",
            "confirm_password": "secret123",
        },
        follow_redirects=True,
    )
    assert b"Username is already taken" in response.data
