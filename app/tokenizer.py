import string
from konlpy.tag import Okt

_okt: Okt | None = None

_SKIP_TAGS = {"Punctuation", "Foreign", "Number", "Alpha", "Symbol"}


def _get_okt() -> Okt:
    global _okt
    if _okt is None:
        _okt = Okt()
    return _okt


def tokenize(text: str) -> list[str]:
    """Tokenize Korean text using Okt, returning unique stemmed content words."""
    tokens = _get_okt().pos(text, stem=True)
    seen: set[str] = set()
    result: list[str] = []
    for word, tag in tokens:
        if tag in _SKIP_TAGS:
            continue
        if word in string.punctuation:
            continue
        if word not in seen:
            seen.add(word)
            result.append(word)
    return result
