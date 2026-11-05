"""Unit tests for apps.contributions.domain without the database."""

import unicodedata
from random import Random

import pytest

from apps.contributions.domain import (
    check_text,
    find_russian_connectors,
    has_kazakh_letters,
    normalize_text,
    shuffle_variants,
)

CONNECTORS = ["и", "но", "что", "потому что", "который", "или", "если"]


def test_normalize_text_nfc_and_whitespace_trimming():
    composed = "Әйел \u04dbнер"
    decomposed = unicodedata.normalize("NFD", composed)
    assert decomposed != composed
    assert normalize_text(f"  \t {decomposed} \n ") == composed


@pytest.mark.parametrize("raw", ["", "   ", "\n\t  "])
def test_empty_after_normalisation_is_rejected(raw):
    result = check_text(raw, max_length=200, russian_connectors=CONNECTORS)
    assert result.errors
    assert result.text == ""
    assert not result.warnings


def test_length_limit_boundary():
    exact = "ә" * 200
    too_long = "ә" * 201
    ok_result = check_text(f"  {exact}  ", max_length=200, russian_connectors=CONNECTORS)
    bad_result = check_text(too_long, max_length=200, russian_connectors=CONNECTORS)
    assert not ok_result.errors
    assert len(ok_result.text) == 200
    assert bad_result.errors


def test_duplicate_detection_uses_nfc_and_trimming():
    existing = ["Әділетті шешім \u04db"]
    decomposed_input = "  " + unicodedata.normalize("NFD", "Әділетті шешім \u04db") + "  "
    result = check_text(
        decomposed_input,
        max_length=200,
        existing_texts=existing,
        russian_connectors=CONNECTORS,
    )
    assert result.errors


@pytest.mark.parametrize("letter", list("әғқңөұүһіӘҒҚҢӨҰҮҺІ"))
def test_each_kazakh_letter_satisfies_check(letter):
    assert has_kazakh_letters(f"Сөз {letter}")
    result = check_text(f"Сөз {letter}", max_length=200, russian_connectors=CONNECTORS)
    assert not result.errors
    assert not result.warnings


def test_missing_kazakh_letters_produces_warning_not_error():
    result = check_text("Машина жасау саласы", max_length=200, russian_connectors=CONNECTORS)
    assert not result.errors
    assert len(result.warnings) == 1
    assert result.warnings == (("no_kazakh_letters", {}),)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Ол и мен келдік", ["и"]),
        ("Иә, бұл дұрыс шешім", []),
        ("иә", []),
        ("Кино және театр", []),
        ("Біз бардық, НО уақыт болмады", ["но"]),
        ("Ол айтты, потому что білді", ["что", "потому что"]),
        ("Қазақша таза сөйлем", []),
    ],
)
def test_russian_connector_whole_word_detection(text, expected):
    assert find_russian_connectors(text, CONNECTORS) == expected


def test_connector_warning_is_returned_without_rejecting():
    result = check_text(
        "Ол келді, но кешікті",
        max_length=200,
        russian_connectors=CONNECTORS,
    )
    assert not result.errors
    assert ("russian_connectors", {"connectors": ["но"]}) in result.warnings


def test_shuffle_variants_is_deterministic_with_seed_and_non_identity():
    items = [1, 2, 3, 4, 5, 6, 7, 8]
    first = shuffle_variants(items, Random(42))
    second = shuffle_variants(items, Random(42))
    assert first == second
    assert first != items
    assert sorted(first) == items
    assert items == [1, 2, 3, 4, 5, 6, 7, 8]
