"""Unit tests for app/tokenizer.py."""

from unittest.mock import patch

import pytest

import app.tokenizer as tokenizer_module
from app.tokenizer import tokenize


@pytest.fixture(autouse=True)
def reset_okt_singleton():
    tokenizer_module._okt = None
    yield
    tokenizer_module._okt = None


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_tokenize_empty_string_returns_empty_list():
    with patch("app.tokenizer.Okt") as MockOkt:
        MockOkt.return_value.pos.return_value = []
        assert tokenize("") == []


def test_tokenize_returns_word_list():
    with patch("app.tokenizer.Okt") as MockOkt:
        MockOkt.return_value.pos.return_value = [("학교", "Noun"), ("가다", "Verb")]
        result = tokenize("학교에 가다")
    assert result == ["학교", "가다"]


def test_tokenize_deduplicates_words():
    with patch("app.tokenizer.Okt") as MockOkt:
        MockOkt.return_value.pos.return_value = [
            ("학교", "Noun"),
            ("가다", "Verb"),
            ("학교", "Noun"),
        ]
        result = tokenize("학교 가다 학교")
    assert result == ["학교", "가다"]


def test_tokenize_calls_pos_with_stem_true():
    """pos() must be called with stem=True so words are lemmatised."""
    with patch("app.tokenizer.Okt") as MockOkt:
        MockOkt.return_value.pos.return_value = []
        tokenize("달리다")
    MockOkt.return_value.pos.assert_called_once_with("달리다", stem=True)


def test_tokenize_all_skip_tags_filtered():
    """Tokens with any of the five skip tags are all excluded."""
    pairs = [
        (".", "Punctuation"),
        ("hi", "Foreign"),
        ("1", "Number"),
        ("a", "Alpha"),
        ("#", "Symbol"),
        ("학교", "Noun"),
    ]
    with patch("app.tokenizer.Okt") as MockOkt:
        MockOkt.return_value.pos.return_value = pairs
        result = tokenize("...")
    assert result == ["학교"]
