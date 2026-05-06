"""Auth flow tests against a live Postgres.

Skipped unless RUN_DB_TESTS=1 (see conftest.py).
"""
import pytest

pytestmark = pytest.mark.requires_postgres


def _register(client, email="alice@example.com", username="alice", password="hunter2hunter2"):
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


def test_register_creates_user_and_sets_cookie(client, clean_db):
    response = _register(client)
    assert response.status_code == 303
    assert response.headers["location"] == "/"
    assert "auth_token" in response.cookies


def test_register_rejects_short_password(client, clean_db):
    response = client.post(
        "/register",
        data={
            "email": "alice@example.com",
            "username": "alice",
            "password": "short",
            "confirm_password": "short",
        },
        follow_redirects=False,
    )
    assert response.status_code == 400
    assert "auth_token" not in response.cookies


def test_register_rejects_mismatched_passwords(client, clean_db):
    response = client.post(
        "/register",
        data={
            "email": "alice@example.com",
            "username": "alice",
            "password": "hunter2hunter2",
            "confirm_password": "different",
        },
        follow_redirects=False,
    )
    assert response.status_code == 400


def test_register_duplicate_email_returns_409(client, clean_db):
    _register(client, email="dup@example.com", username="one")
    response = _register(client, email="dup@example.com", username="two")
    assert response.status_code == 409


def test_login_success_sets_cookie(client, clean_db):
    _register(client, email="bob@example.com", password="hunter2hunter2")
    # use a fresh client so the registration cookie doesn't bleed in
    from fastapi.testclient import TestClient
    from app.main import app
    fresh = TestClient(app)
    response = fresh.post(
        "/login",
        data={"email": "bob@example.com", "password": "hunter2hunter2", "next": "/"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert "auth_token" in response.cookies


def test_login_wrong_password_returns_401(client, clean_db):
    _register(client, email="carol@example.com", password="hunter2hunter2")
    response = client.post(
        "/login",
        data={"email": "carol@example.com", "password": "wrongwrongwrong"},
        follow_redirects=False,
    )
    assert response.status_code == 401
    assert "auth_token" not in response.cookies


def test_login_unknown_email_returns_401(client, clean_db):
    response = client.post(
        "/login",
        data={"email": "ghost@example.com", "password": "hunter2hunter2"},
        follow_redirects=False,
    )
    assert response.status_code == 401


def test_logout_clears_cookie(client, clean_db):
    _register(client)  # cookie now stuck on the client
    response = client.post("/logout", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"
    # delete_cookie sends Set-Cookie with empty value + Max-Age=0
    set_cookie = response.headers.get("set-cookie", "")
    assert "auth_token=" in set_cookie


def test_protected_route_serves_when_authed(client, clean_db):
    _register(client)
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 200


def test_login_safe_next_blocks_open_redirect(client, clean_db):
    _register(client, email="dave@example.com", password="hunter2hunter2")
    from fastapi.testclient import TestClient
    from app.main import app
    fresh = TestClient(app)
    response = fresh.post(
        "/login",
        data={
            "email": "dave@example.com",
            "password": "hunter2hunter2",
            "next": "//evil.example.com",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    # protocol-relative URL must be rejected back to "/"
    assert response.headers["location"] == "/"


def test_email_normalised_to_lowercase(client, clean_db):
    _register(client, email="Mixed@Example.COM", username="mix", password="hunter2hunter2")
    from fastapi.testclient import TestClient
    from app.main import app
    fresh = TestClient(app)
    response = fresh.post(
        "/login",
        data={"email": "mixed@example.com", "password": "hunter2hunter2"},
        follow_redirects=False,
    )
    assert response.status_code == 303
