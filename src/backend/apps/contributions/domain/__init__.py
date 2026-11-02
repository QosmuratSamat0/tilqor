"""Pure domain logic for contributions (text checks and variant shuffling)."""

from .checks import (
    KAZAKH_LETTERS,
    CheckResult,
    check_text,
    find_russian_connectors,
    has_kazakh_letters,
    normalize_text,
    shuffle_variants,
)

__all__ = [
    "CheckResult",
    "KAZAKH_LETTERS",
    "check_text",
    "find_russian_connectors",
    "has_kazakh_letters",
    "normalize_text",
    "shuffle_variants",
]
