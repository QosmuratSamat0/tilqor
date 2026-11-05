import pytest

from apps.evaluation.domain.metrics import bootstrap_difference, breakdown, score
from apps.evaluation.domain.types import Outcome, Record


def outcome(id, decision, count=3, control=False):
    return Outcome(id, decision, "decided" if decision else "unresolved", count, (), control)


def test_handmade_metrics_exclude_controls():
    records = [
        Record("1", "accept", "it", "grammar"),
        Record("2", "reject", "it"),
        Record("3", "edit", "medicine"),
        Record("c", "accept"),
    ]
    outcomes = [
        outcome("1", "accept"),
        outcome("2", "edit", 5),
        outcome("3", None, 5),
        outcome("c", "reject", control=True),
    ]
    result = score(records, outcomes)
    assert (result["all"], result["decided"], result["correct"], result["unresolved"]) == (
        3,
        2,
        1,
        1,
    )
    assert result["accuracy"] == 0.5
    assert result["correct_all"] == pytest.approx(1 / 3)
    assert result["unresolved_rate"] == pytest.approx(1 / 3)
    assert result["votes_per_decided_record"] == 4
    assert breakdown(records, outcomes, "domain")["medicine"]["accuracy"] is None
    assert breakdown(records, outcomes, "error_type")["grammar"]["correct"] == 1


def test_paired_bootstrap_is_deterministic_and_keeps_identical_methods_at_zero():
    records = [Record(str(i), "accept") for i in range(8)]
    weighted = [outcome(r.id, "accept" if int(r.id) % 2 else "reject") for r in records]
    baseline = [outcome(r.id, "accept") for r in records]
    first = bootstrap_difference(records, weighted, baseline, seed=42)
    assert first == bootstrap_difference(records, weighted, baseline, seed=42)
    assert first["estimate"] == -0.5
    assert first["lower"] <= first["estimate"] <= first["upper"]
    same = bootstrap_difference(records, weighted, weighted, seed=42)
    assert (same["lower"], same["upper"]) == (0.0, 0.0)


def test_empty_or_undefined_denominators_do_not_become_nan():
    assert score([], [])["accuracy"] is None
    result = bootstrap_difference(
        [Record("r", "accept")], [outcome("r", None)], [outcome("r", "accept")], seed=42
    )
    assert result["estimate"] is None and result["reason"]
