from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_about_is_public():
    response = client.get("/about")
    assert response.status_code == 200


def test_index_redirects_when_anonymous():
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login?next=/"


def test_analyze_get_redirects_when_anonymous():
    response = client.get("/analyze", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login?next=/analyze"


def test_analyze_post_redirects_when_anonymous():
    response = client.post("/analyze", data={"text": "학교"}, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login?next=/analyze"


def test_dictionary_redirects_when_anonymous():
    response = client.get("/dictionary", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login?next=/dictionary"


def test_dictionary_preserves_query_in_next():
    response = client.get("/dictionary?page=2", follow_redirects=False)
    assert response.status_code == 303
    # next should include the page=2 query
    assert "page%3D2" in response.headers["location"]


def test_login_page_public():
    response = client.get("/login")
    assert response.status_code == 200
    assert "Log in" in response.text or "login" in response.text.lower()


def test_register_page_public():
    response = client.get("/register")
    assert response.status_code == 200
    assert "Register" in response.text or "register" in response.text.lower()
