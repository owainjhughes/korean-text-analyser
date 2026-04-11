import asyncio
from xml.etree import ElementTree as ET

import httpx

from app.config import settings

KRDICT_URL = "https://krdict.korean.go.kr/api/search"
REQUEST_TIMEOUT_SECONDS = 8.0
MAX_RETRIES = 3
RETRY_DELAYS_SECONDS = (0.3, 0.8)

_cache: dict[str, str | None] = {}


async def get_word_grade(word: str) -> str | None:
    """Look up a word in the Korean Basic Dictionary API and return its grade.

    Returns the grade string (e.g. '초급', '중급', '고급') or None if the word
    is not found or the request fails.
    """
    if not settings.api_key:
        return None

    if word in _cache:
        return _cache[word]

    params = {
        "key": settings.api_key,
        "q": word,
        "part": "word",
        "type_search": "search",
    }
    resp = None
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        for attempt in range(MAX_RETRIES):
            try:
                resp = await client.get(KRDICT_URL, params=params)
                resp.raise_for_status()
                break
            except httpx.HTTPError:
                if attempt == MAX_RETRIES - 1:
                    return None
                await asyncio.sleep(RETRY_DELAYS_SECONDS[min(attempt, len(RETRY_DELAYS_SECONDS) - 1)])

    if resp is None:
        return None

    try:
        root = ET.fromstring(resp.content)
    except ET.ParseError:
        return None

    # scan all items and return the first non-empty grade.
    for item in root.iter("item"):
        grade = item.findtext("word_grade")
        if grade and grade.strip():
            _cache[word] = grade.strip()
            return grade.strip()

    _cache[word] = None
    return None
