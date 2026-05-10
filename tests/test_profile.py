"""Profile route tests against a live Postgres.

Skipped unless RUN_DB_TESTS=1 (see conftest.py).
"""
import pytest

pytestmark = pytest.mark.requires_postgres


def _register(client, email="erin@example.com", username="erin", password="hunter2hunter2"):
    return client.post(
        "/register",
        data={
            "email": email,
            "username": username,
            "password": password,
            "confirm_password": password,
            "next": "/",
        },
        follow_redirects=False,
    )


def test_profile_redirects_when_anonymous(client, clean_db):
    response = client.get("/profile", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login?next=/profile"


def test_profile_renders_when_authed(client, clean_db):
    _register(client, email="erin@example.com", username="erin")
    response = client.get("/profile")
    assert response.status_code == 200
    assert "erin@example.com" in response.text


def test_update_username(client, clean_db):
    _register(client, email="frank@example.com", username="frank")
    response = client.post(
        "/profile/username",
        data={"username": "francis"},
        follow_redirects=False,
    )
    assert response.status_code == 200
    # second GET reflects new username
    response = client.get("/profile")
    assert "francis" in response.text


def test_change_password_requires_current_password(client, clean_db):
    _register(client, email="gina@example.com", username="gina", password="hunter2hunter2")
    response = client.post(
        "/profile/password",
        data={
            "current_password": "wrongwrongwrong",
            "new_password": "newpasswordnew",
            "confirm_new_password": "newpasswordnew",
        },
        follow_redirects=False,
    )
    assert response.status_code == 400


def test_change_password_success(client, clean_db):
    _register(client, email="hank@example.com", username="hank", password="hunter2hunter2")
    response = client.post(
        "/profile/password",
        data={
            "current_password": "hunter2hunter2",
            "new_password": "newpasswordnew",
            "confirm_new_password": "newpasswordnew",
        },
        follow_redirects=False,
    )
    assert response.status_code == 200

    # log out and log in with the new password
    client.post("/logout", follow_redirects=False)
    from fastapi.testclient import TestClient
    from app.main import app
    fresh = TestClient(app)
    response = fresh.post(
        "/login",
        data={"email": "hank@example.com", "password": "newpasswordnew"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert "auth_token" in response.cookies


def test_change_password_mismatched_confirm(client, clean_db):
    _register(client, email="ivy@example.com", username="ivy", password="hunter2hunter2")
    response = client.post(
        "/profile/password",
        data={
            "current_password": "hunter2hunter2",
            "new_password": "newpasswordnew",
            "confirm_new_password": "different",
        },
        follow_redirects=False,
    )
    assert response.status_code == 400
