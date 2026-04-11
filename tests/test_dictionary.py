"""Unit tests for app/dictionary.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

import app.dictionary as dict_module
from app.dictionary import get_word_grade


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _xml(grade: str) -> bytes:
    return (
        f"<channel><item><word_grade>{grade}</word_grade></item></channel>"
    ).encode()


def _xml_no_items() -> bytes:
    return b"<channel></channel>"


def _make_response(content: bytes) -> MagicMock:
    resp = MagicMock()
    resp.content = content
    resp.raise_for_status = MagicMock()
    return resp


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def clear_cache():
    """Ensure module-level cache is empty before and after every test."""
    dict_module._cache.clear()
    yield
    dict_module._cache.clear()


# ---------------------------------------------------------------------------
# Helpers to build a patched httpx.AsyncClient context manager
# ---------------------------------------------------------------------------


def _patch_client(mock_client):
    """Return a patch context that injects *mock_client* as the async-with result."""
    patcher = patch("app.dictionary.httpx.AsyncClient")
    MockClient = patcher.start()
    MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
    MockClient.return_value.__aexit__ = AsyncMock(return_value=None)
    return patcher


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_no_api_key_returns_none():
    with patch.object(dict_module.settings, "api_key", ""):
        result = await get_word_grade("학교")
    assert result is None


@pytest.mark.asyncio
async def test_cache_hit_returns_cached_grade_without_http():
    dict_module._cache["학교"] = "초급"
    with patch.object(dict_module.settings, "api_key", "key"), \
         patch("app.dictionary.httpx.AsyncClient") as MockClient:
        result = await get_word_grade("학교")
    MockClient.assert_not_called()
    assert result == "초급"


@pytest.mark.asyncio
async def test_successful_lookup_returns_grade():
    mock_client = AsyncMock()
    mock_client.get.return_value = _make_response(_xml("초급"))
    patcher = _patch_client(mock_client)
    try:
        with patch.object(dict_module.settings, "api_key", "key"):
            result = await get_word_grade("학교")
    finally:
        patcher.stop()
    assert result == "초급"


@pytest.mark.asyncio
async def test_successful_lookup_stores_grade_in_cache():
    mock_client = AsyncMock()
    mock_client.get.return_value = _make_response(_xml("중급"))
    patcher = _patch_client(mock_client)
    try:
        with patch.object(dict_module.settings, "api_key", "key"):
            await get_word_grade("사랑")
    finally:
        patcher.stop()
    assert dict_module._cache.get("사랑") == "중급"


@pytest.mark.asyncio
async def test_word_not_found_returns_none():
    mock_client = AsyncMock()
    mock_client.get.return_value = _make_response(_xml_no_items())
    patcher = _patch_client(mock_client)
    try:
        with patch.object(dict_module.settings, "api_key", "key"):
            result = await get_word_grade("없는단어")
    finally:
        patcher.stop()
    assert result is None


@pytest.mark.asyncio
async def test_all_retries_fail_returns_none():
    mock_client = AsyncMock()
    mock_client.get.side_effect = httpx.HTTPError("connection error")
    patcher = _patch_client(mock_client)
    try:
        with patch.object(dict_module.settings, "api_key", "key"), \
             patch("app.dictionary.asyncio.sleep", new_callable=AsyncMock):
            result = await get_word_grade("학교")
    finally:
        patcher.stop()
    assert result is None


@pytest.mark.asyncio
async def test_retry_succeeds_on_second_attempt():
    good_resp = _make_response(_xml("초급"))
    call_count = 0

    async def mock_get(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise httpx.HTTPError("transient error")
        return good_resp

    mock_client = AsyncMock()
    mock_client.get = mock_get
    patcher = _patch_client(mock_client)
    try:
        with patch.object(dict_module.settings, "api_key", "key"), \
             patch("app.dictionary.asyncio.sleep", new_callable=AsyncMock):
            result = await get_word_grade("학교")
    finally:
        patcher.stop()
    assert result == "초급"
    assert call_count == 2
