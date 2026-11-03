import hashlib
from collections.abc import Iterable
from datetime import date

from apps.contributions.domain import normalize_text


def normalize_search_query(query: str | None) -> str:
    """Normalise search query text with NFC + trim and casefold for case-insensitive matching."""
    if not query:
        return ""
    return normalize_text(query).casefold()


def term_matches_query(
    *, query: str | None, text_ru: str, eligible_texts_kk: Iterable[str]
) -> bool:
    """Return True when `query` matches `text_ru` or any eligible Kazakh variant."""
    needle = normalize_search_query(query)
    if not needle:
        return True
    if needle in normalize_text(text_ru).casefold():
        return True
    return any(needle in normalize_text(text).casefold() for text in eligible_texts_kk)


def parse_iso_date(raw_date: str) -> str:
    """Validate and return an ISO YYYY-MM-DD date string, raising ValueError if invalid."""
    cleaned = raw_date.strip()
    if len(cleaned) != 10:
        raise ValueError("Invalid ISO date format.")
    return date.fromisoformat(cleaned).isoformat()


def word_of_the_day_index(iso_date: str, count: int) -> int | None:
    """Return deterministic index in `0..count-1` from `sha256(iso_date) mod count`."""
    if count <= 0:
        return None
    digest = hashlib.sha256(iso_date.encode("utf-8")).digest()
    return int.from_bytes(digest, "big") % count
