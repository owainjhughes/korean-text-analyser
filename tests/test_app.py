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


def test_analyze_get():
    response = client.get("/analyze")
    assert response.status_code == 200
    assert "Analyze" in response.text


def test_analyze_post_empty_text():
    """Posting an empty form should return 200 with no results table."""
    with patch("app.main.tokenize", return_value=[]):
        response = client.post("/analyze", data={"text": ""})
    assert response.status_code == 200


def test_analyze_post_returns_results():
    """Posting Korean text triggers tokenisation and grade lookup."""
    with patch("app.main.tokenize", return_value=["학교"]), \
         patch("app.main.get_word_grade", new_callable=AsyncMock, return_value="초급"):
        response = client.post("/analyze", data={"text": "학교"})
    assert response.status_code == 200
    assert "학교" in response.text


def test_analyze_post_multiple_words_all_rendered():
    """Multiple words with different grades are all rendered in the response."""
    grades = {"학교": "초급", "사랑": "중급", "철학": "고급"}
    grade_mock = AsyncMock(side_effect=lambda w: grades.get(w))
    with patch("app.main.tokenize", return_value=list(grades.keys())), \
         patch("app.main.get_word_grade", grade_mock):
        response = client.post("/analyze", data={"text": "학교 사랑 철학"})
    assert response.status_code == 200
    for word in grades:
        assert word in response.text


def test_dictionary_first_page():
    response = client.get("/dictionary")
    assert response.status_code == 200
    assert "Dictionary" in response.text
    assert "Page 1 of" in response.text


def test_dictionary_pagination():
    response = client.get("/dictionary?page=2")
    assert response.status_code == 200
    assert "Page 2 of" in response.text


def test_dictionary_out_of_range_page_clamped():
    """A page far past the end clamps to the last page rather than 404-ing."""
    response = client.get("/dictionary?page=99999")
    assert response.status_code == 200
    assert "Page" in response.text
