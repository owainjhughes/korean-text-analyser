from xml.etree import ElementTree as ET

import httpx

from app.config import settings

KRDICT_URL = "https://krdict.korean.go.kr/api/search"


async def get_word_grade(word: str) -> str | None:
    """Look up a word in the Korean Basic Dictionary API and return its grade.

    Returns the grade string (e.g. '초급', '중급', '고급') or None if the word
    is not found or the request fails.
    """
    if not settings.api_key:
        return None

    params = {
        "key": settings.api_key,
        "q": word,
        "part": "word",
        "type_search": "search",
    }
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(KRDICT_URL, params=params)
            resp.raise_for_status()
    except httpx.HTTPError:
        return None

    try:
        root = ET.fromstring(resp.content)
    except ET.ParseError:
        return None

    # The API may return multiple items (homographs/senses); scan all of them
    # for the first non-empty word_grade rather than trusting only the first item.
    for item in root.iter("item"):
        grade = item.findtext("word_grade")
        if grade and grade.strip():
            return grade.strip()
    return None
