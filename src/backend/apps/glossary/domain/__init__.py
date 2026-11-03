import hashlib
from datetime import date


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
