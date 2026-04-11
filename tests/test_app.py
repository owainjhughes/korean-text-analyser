from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_index_get():
    response = client.get("/")
    assert response.status_code == 200
    assert "Saebae" in response.text


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_index_post_empty_text():
    """Posting an empty form should return 200 with no results table."""
    with patch("app.main.tokenize", return_value=[]):
        response = client.post("/", data={"text": ""})
    assert response.status_code == 200


def test_index_post_returns_results():
    """Posting Korean text triggers tokenisation and grade lookup."""
    with patch("app.main.tokenize", return_value=["학교"]), \
         patch("app.main.get_word_grade", new_callable=AsyncMock, return_value="초급"):
        response = client.post("/", data={"text": "학교"})
    assert response.status_code == 200
    assert "학교" in response.text


def test_index_post_multiple_words_all_rendered():
    """Multiple words with different grades are all rendered in the response."""
    grades = {"학교": "초급", "사랑": "중급", "철학": "고급"}
    grade_mock = AsyncMock(side_effect=lambda w: grades.get(w))
    with patch("app.main.tokenize", return_value=list(grades.keys())), \
         patch("app.main.get_word_grade", grade_mock):
        response = client.post("/", data={"text": "학교 사랑 철학"})
    assert response.status_code == 200
    for word in grades:
        assert word in response.text
