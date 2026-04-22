"""Unit tests for app/dictionary.py."""

import pytest

import app.dictionary as dict_module
from app.dictionary import _LEVEL_MAP, _load_tsv, get_word_grade


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def clear_cache():
    # ensure cache is empty before and after every test
    dict_module._cache.clear()
    yield
    dict_module._cache.clear()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_known_word_returns_grade():
    dict_module._cache["가게"] = "초급"
    result = await get_word_grade("가게")
    assert result == "초급"


@pytest.mark.asyncio
async def test_unknown_word_returns_none():
    result = await get_word_grade("없는단어")
    assert result is None


def test_level_map_covers_all_grades():
    assert _LEVEL_MAP["A"] == "초급"
    assert _LEVEL_MAP["B"] == "중급"
    assert _LEVEL_MAP["C"] == "고급"
    assert _LEVEL_MAP["D"] == "고급"


def test_load_tsv_populates_cache(tmp_path, monkeypatch):
    tsv = "id\tsurface\tgloss\tlevel\n1\t가게\tstore\tA\n2\t사랑\tlove\tB\n3\t어렵다\tdifficult\tC\n"
    tsv_file = tmp_path / "test.tsv"
    tsv_file.write_text(tsv, encoding="utf-8")
    monkeypatch.setattr(dict_module, "_DATA_FILE", tsv_file)
    _load_tsv()
    assert dict_module._cache["가게"] == "초급"
    assert dict_module._cache["사랑"] == "중급"
    assert dict_module._cache["어렵다"] == "고급"


def test_load_tsv_first_entry_wins_on_duplicate(tmp_path, monkeypatch):
    tsv = "id\tsurface\tgloss\tlevel\n1\t가구\tfurniture\tB\n2\t가구\tfamily\tC\n"
    tsv_file = tmp_path / "test.tsv"
    tsv_file.write_text(tsv, encoding="utf-8")
    monkeypatch.setattr(dict_module, "_DATA_FILE", tsv_file)
    _load_tsv()
    assert dict_module._cache["가구"] == "중급"


def test_load_tsv_skips_unknown_level(tmp_path, monkeypatch):
    tsv = "id\tsurface\tgloss\tlevel\n1\t어떤단어\tsome word\tZ\n"
    tsv_file = tmp_path / "test.tsv"
    tsv_file.write_text(tsv, encoding="utf-8")
    monkeypatch.setattr(dict_module, "_DATA_FILE", tsv_file)
    _load_tsv()
    assert "어떤단어" not in dict_module._cache
