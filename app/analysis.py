import string
from dataclasses import dataclass
from typing import Optional

from app.dictionary import get_word_grade
from app.tokenizer import _SKIP_TAGS, _get_okt

_KNOWN_LEVELS = ("초급", "중급", "고급")


@dataclass
class Token:
    text: str           # surface/lemma as Okt emits it (stem=True)
    level: Optional[str]  # 초급 / 중급 / 고급 / None
    is_word: bool       # False for punctuation, foreign, number, alpha, symbol


@dataclass
class AnalysisResult:
    tokens: list[Token]                 # in reading order, includes non-word fillers
    counts: dict[str, int]              # keys: 초급, 중급, 고급, unknown, total
    coverage_pct: float                 # (초급+중급+고급) / total * 100, 0 if total=0
    coverage_label: str                 # ineffective / decent / effective
    coverage_band: str                  # red / amber / green
    missing: list[str]                  # unique unknown lemmas in first-occurrence order


def _coverage_band(pct: float) -> tuple[str, str]:
    """Same thresholds as ObuCon: <75 red, 75–85 amber, 85+ green."""
    if pct >= 85.0:
        return "Effective", "green"
    if pct >= 75.0:
        return "Decent", "amber"
    return "Ineffective", "red"


async def analyze_text(text: str) -> AnalysisResult:
    raw = _get_okt().pos(text, stem=True) if text.strip() else []

    counts = {"초급": 0, "중급": 0, "고급": 0, "unknown": 0, "total": 0}
    tokens: list[Token] = []
    missing_seen: set[str] = set()
    missing: list[str] = []

    for word, tag in raw:
        if tag in _SKIP_TAGS or word in string.punctuation:
            tokens.append(Token(text=word, level=None, is_word=False))
            continue

        level = await get_word_grade(word)
        is_known = level in _KNOWN_LEVELS
        tokens.append(Token(text=word, level=level if is_known else None, is_word=True))

        counts["total"] += 1
        if is_known:
            counts[level] += 1
        else:
            counts["unknown"] += 1
            if word not in missing_seen:
                missing_seen.add(word)
                missing.append(word)

    coverage_pct = (
        round((counts["초급"] + counts["중급"] + counts["고급"]) / counts["total"] * 100, 1)
        if counts["total"]
        else 0.0
    )
    label, band = _coverage_band(coverage_pct)

    return AnalysisResult(
        tokens=tokens,
        counts=counts,
        coverage_pct=coverage_pct,
        coverage_label=label,
        coverage_band=band,
        missing=missing,
    )
