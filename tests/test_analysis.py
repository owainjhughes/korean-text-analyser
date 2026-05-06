"""Unit tests for app/analysis.py."""

from unittest.mock import AsyncMock, patch

import pytest

from app.analysis import _coverage_band, analyze_text


@pytest.fixture(autouse=True)
def reset_okt_singleton():
    import app.tokenizer as tokenizer_module
    tokenizer_module._okt = None
    yield
    tokenizer_module._okt = None


@pytest.mark.asyncio
async def test_empty_text_returns_zeroed_result():
    result = await analyze_text("")
    assert result.tokens == []
    assert result.counts == {"초급": 0, "중급": 0, "고급": 0, "unknown": 0, "total": 0}
    assert result.coverage_pct == 0.0
    assert result.coverage_band == "red"
    assert result.missing == []


@pytest.mark.asyncio
async def test_tokens_keep_reading_order_with_mixed_levels():
    pos_pairs = [("학교", "Noun"), ("에서", "Josa"), ("사랑", "Noun"), ("?", "Punctuation")]
    grades = {"학교": "초급", "에서": None, "사랑": "중급"}
    with patch("app.analysis._get_okt") as mock_get_okt, \
         patch("app.analysis.get_word_grade", new_callable=AsyncMock,
               side_effect=lambda w: grades.get(w)):
        mock_get_okt.return_value.pos.return_value = pos_pairs
        result = await analyze_text("학교에서 사랑?")

    # all 4 emitted in reading order (incl. punctuation as is_word=False)
    assert [t.text for t in result.tokens] == ["학교", "에서", "사랑", "?"]
    assert [t.is_word for t in result.tokens] == [True, True, True, False]
    # 에서 came back as None → unknown bucket
    assert result.counts["초급"] == 1
    assert result.counts["중급"] == 1
    assert result.counts["unknown"] == 1
    assert result.counts["total"] == 3
    assert result.missing == ["에서"]


@pytest.mark.asyncio
async def test_missing_list_is_deduplicated_first_occurrence():
    pos_pairs = [("어렵다", "Adjective"), ("어렵다", "Adjective"), ("쉽다", "Adjective")]
    with patch("app.analysis._get_okt") as mock_get_okt, \
         patch("app.analysis.get_word_grade", new_callable=AsyncMock, return_value=None):
        mock_get_okt.return_value.pos.return_value = pos_pairs
        result = await analyze_text("어렵다 어렵다 쉽다")

    assert result.missing == ["어렵다", "쉽다"]
    assert result.counts["unknown"] == 3  # counts are not deduped


@pytest.mark.asyncio
async def test_coverage_pct_rounds_to_one_decimal():
    pos_pairs = [("학교", "Noun"), ("사랑", "Noun"), ("어렵다", "Adjective")]
    grades = {"학교": "초급", "사랑": "초급", "어렵다": None}
    with patch("app.analysis._get_okt") as mock_get_okt, \
         patch("app.analysis.get_word_grade", new_callable=AsyncMock,
               side_effect=lambda w: grades.get(w)):
        mock_get_okt.return_value.pos.return_value = pos_pairs
        result = await analyze_text("학교 사랑 어렵다")

    # 2/3 = 66.6667 → 66.7
    assert result.coverage_pct == 66.7


def test_coverage_band_thresholds():
    assert _coverage_band(90.0) == ("Effective", "green")
    assert _coverage_band(85.0) == ("Effective", "green")
    assert _coverage_band(84.9) == ("Decent", "amber")
    assert _coverage_band(75.0) == ("Decent", "amber")
    assert _coverage_band(74.9) == ("Ineffective", "red")
    assert _coverage_band(0.0) == ("Ineffective", "red")
