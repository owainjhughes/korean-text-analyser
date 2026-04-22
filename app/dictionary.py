import csv
from pathlib import Path

# api imports — kept for potential future use
# import asyncio
# from xml.etree import ElementTree as ET
# import httpx
# from app.config import settings

# KRDICT_URL = "https://krdict.korean.go.kr/api/search"
# REQUEST_TIMEOUT_SECONDS = 8.0
# MAX_RETRIES = 3
# RETRY_DELAYS_SECONDS = (0.3, 0.8)

# kengdic A/B/C/D levels mapped to topik-aligned korean grades
_LEVEL_MAP: dict[str, str] = {"A": "초급", "B": "중급", "C": "고급", "D": "고급"}

_DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "kengdic_graded.tsv"

_cache: dict[str, str | None] = {}


def _load_tsv() -> None:
    # load graded words from local tsv into cache at startup
    with open(_DATA_FILE, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            word = row.get("surface", "").strip()
            level = row.get("level", "").strip()
            if word and level and word not in _cache:
                grade = _LEVEL_MAP.get(level)
                if grade:
                    _cache[word] = grade


_load_tsv()


async def get_word_grade(word: str) -> str | None:
    return _cache.get(word)

    # api fallback — uncomment if tsv coverage proves insufficient
    # if not settings.api_key:
    #     return None
    # params = {
    #     "key": settings.api_key,
    #     "q": word,
    #     "part": "word",
    #     "type_search": "search",
    # }
    # resp = None
    # async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
    #     for attempt in range(MAX_RETRIES):
    #         try:
    #             resp = await client.get(KRDICT_URL, params=params)
    #             resp.raise_for_status()
    #             break
    #         except httpx.HTTPError:
    #             if attempt == MAX_RETRIES - 1:
    #                 return None
    #             await asyncio.sleep(RETRY_DELAYS_SECONDS[min(attempt, len(RETRY_DELAYS_SECONDS) - 1)])
    # if resp is None:
    #     return None
    # try:
    #     root = ET.fromstring(resp.content)
    # except ET.ParseError:
    #     return None
    # for item in root.iter("item"):
    #     grade = item.findtext("word_grade")
    #     if grade and grade.strip():
    #         _cache[word] = grade.strip()
    #         return grade.strip()
    # _cache[word] = None
    # return None
