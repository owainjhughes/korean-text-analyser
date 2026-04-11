from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_index_get():
    response = client.get("/")
    assert response.status_code == 200
    assert "Korean Text Difficulty Classifier" in response.text


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
