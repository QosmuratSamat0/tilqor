"""Pure text validation and variant ordering rules with no Django dependencies."""

import re
import unicodedata
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from random import Random

KAZAKH_LETTERS = frozenset("әғқңөұүһі")


@dataclass(frozen=True)
class CheckResult:
    text: str
    errors: tuple[str, ...]
    warnings: tuple[str, ...]


def normalize_text(text: str) -> str:
    """Apply Unicode NFC normalization and strip leading/trailing whitespace (NFR-01)."""
    return unicodedata.normalize("NFC", text).strip()


def has_kazakh_letters(text: str) -> bool:
    """Return True if the text contains at least one Kazakh-specific letter in any case."""
    normalized = normalize_text(text).lower()
    return any(char in KAZAKH_LETTERS for char in normalized)


def find_russian_connectors(text: str, connectors: Iterable[str]) -> list[str]:
    """Return connectors found as whole words (case-insensitive) in the text."""
    normalized = normalize_text(text)
    found: list[str] = []
    for connector in connectors:
        target = normalize_text(connector)
        if not target:
            continue
        parts = [re.escape(part) for part in target.split()]
        pattern = r"(?<!\w)" + r"\s+".join(parts) + r"(?!\w)"
        if re.search(pattern, normalized, flags=re.IGNORECASE):
            found.append(target)
    return found


def check_text(
    text: str,
    *,
    max_length: int,
    existing_texts: Iterable[str] = (),
    russian_connectors: Iterable[str] = (),
) -> CheckResult:
    """Validate submission text and collect non-blocking quality warnings (FR-07)."""
    normalized = normalize_text(text)
    errors: list[str] = []
    warnings: list[str] = []

    if not normalized:
        errors.append("Text cannot be empty.")
    elif len(normalized) > max_length:
        errors.append(f"Text cannot exceed {max_length} characters.")

    normalized_existing = {normalize_text(item) for item in existing_texts}
    if normalized and normalized in normalized_existing:
        errors.append("This variant already exists for this task.")

    if normalized and not errors:
        if not has_kazakh_letters(normalized):
            warnings.append(
                "Text contains no Kazakh-specific letters (ә, ғ, қ, ң, ө, ұ, ү, һ, і)."
            )
        matched_connectors = find_russian_connectors(normalized, russian_connectors)
        if matched_connectors:
            joined = ", ".join(matched_connectors)
            warnings.append(f"Text contains Russian connector(s): {joined}.")

    return CheckResult(
        text=normalized,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


def shuffle_variants[T](variants: Sequence[T], rng: Random) -> list[T]:
    """Return a copy of variants shuffled with the provided random generator (FR-05)."""
    items = list(variants)
    rng.shuffle(items)
    return items
