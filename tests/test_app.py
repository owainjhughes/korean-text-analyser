from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_index_get():
    response = client.get("/")
    assert response.status_code == 200
    assert "Saebae" in response.text


def test_about_get():
    response = client.get("/about")
    assert response.status_code == 200
    assert "About" in response.text


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


def test_index_post_unknown_grade():
    """Words not found in the API should appear in the 'Other' column."""
    with patch("app.main.tokenize", return_value=["컴퓨터"]), \
         patch("app.main.get_word_grade", new_callable=AsyncMock, return_value=None):
        response = client.post("/", data={"text": "컴퓨터"})
    assert response.status_code == 200
    assert "컴퓨터" in response.text


def test_submitted_text_preserved():
    """The textarea should be repopulated with the original input after submission."""
    with patch("app.main.tokenize", return_value=["안녕"]), \
         patch("app.main.get_word_grade", new_callable=AsyncMock, return_value=None):
        response = client.post("/", data={"text": "안녕하세요"})
    assert "안녕하세요" in response.text


def test_index_post_chogup_grade_rendered():
    """A 초급-grade word is displayed in the 초급 column."""
    with patch("app.main.tokenize", return_value=["학교"]), \
         patch("app.main.get_word_grade", new_callable=AsyncMock, return_value="초급"):
        response = client.post("/", data={"text": "학교"})
    assert response.status_code == 200
    assert "학교" in response.text
    assert "초급" in response.text


def test_index_post_jungup_grade_rendered():
    """A 중급-grade word is displayed in the 중급 column."""
    with patch("app.main.tokenize", return_value=["사랑"]), \
         patch("app.main.get_word_grade", new_callable=AsyncMock, return_value="중급"):
        response = client.post("/", data={"text": "사랑"})
    assert response.status_code == 200
    assert "사랑" in response.text
    assert "중급" in response.text


def test_index_post_gogup_grade_rendered():
    """A 고급-grade word is displayed in the 고급 column."""
    with patch("app.main.tokenize", return_value=["철학"]), \
         patch("app.main.get_word_grade", new_callable=AsyncMock, return_value="고급"):
        response = client.post("/", data={"text": "철학"})
    assert response.status_code == 200
    assert "철학" in response.text
    assert "고급" in response.text


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


def test_index_post_whitespace_only_text_returns_200():
    """Posting whitespace-only text should not crash."""
    with patch("app.main.tokenize", return_value=[]):
        response = client.post("/", data={"text": "   "})
    assert response.status_code == 200


def test_no_results_section_when_result_is_empty():
    """The Results section should not appear when there are no tokenised words."""
    with patch("app.main.tokenize", return_value=[]):
        response = client.post("/", data={"text": ""})
    assert "Results" not in response.text
