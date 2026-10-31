"""No database: decision, Decimal threshold, standard and control reputation rules.

The stateful rows of verification-plan §3 (permissions, retry, settings and
version history) are exercised in test_services.py and test_api.py.
"""

from decimal import Decimal

import pytest

from apps.verification.domain.decisions import Rules, Vote, evaluate
from apps.verification.domain.reputation import updated_weight

RULES = Rules(Decimal("0.66"), 3, 5, 2)


def votes(decisions, weights=None):
    weights = weights or ["1"] * len(decisions)
    return [
        Vote(i, decision, Decimal(weight))
        for i, (decision, weight) in enumerate(zip(decisions, weights, strict=True))
    ]


@pytest.mark.parametrize(
    "decisions,expected,escalated",
    [
        ([], None, False),
        (["accept"], None, False),
        (["accept", "accept"], None, False),
        (["accept", "accept", "reject"], "accept", False),
        (["reject", "reject", "edit"], "reject", False),
        (["edit", "edit", "accept"], "edit", False),
        (["accept", "reject", "edit"], None, False),
        (["accept", "reject", "edit", "accept"], None, False),
        (["accept", "reject", "edit", "accept", "reject"], None, True),
        (["accept", "reject", "edit", "accept", "accept"], None, True),
        (["accept", "accept", "reject", "accept"], "accept", False),
        (["accept", "accept", "reject", "edit", "accept"], None, True),
    ],
)
def test_decision_points(decisions, expected, escalated):
    result = evaluate(votes(decisions), RULES)
    assert (result.decision, result.escalated) == (expected, escalated)
    assert result.counted_votes == len(decisions)


def test_one_strong_reviewer_cannot_decide_alone():
    result = evaluate(votes(["accept", "reject", "edit"], ["2", "0.5", "0.5"]), RULES)
    assert result.decision is None


def test_abstention_does_not_affect_denominator_or_count():
    result = evaluate(
        votes(["accept", "accept", "reject", "dont_know"], ["1", "1", "1", "2"]), RULES
    )
    assert result.decision == "accept"
    assert result.counted_votes == 3
    assert evaluate(votes(["accept", "accept", "dont_know"]), RULES).decision is None


def test_share_is_not_rounded_before_comparison():
    # 0.659 rounds to 0.66, but must fail the threshold.
    result = evaluate(votes(["accept", "accept", "reject"], ["0.329", "0.330", "0.341"]), RULES)
    assert result.decision is None
    assert (
        evaluate(votes(["accept", "accept", "reject"], ["0.33", "0.33", "0.34"]), RULES).decision
        == "accept"
    )


def test_custom_rules_and_five_vote_outcome():
    rules = Rules(Decimal("0.60"), 4, 5, 3)
    assert evaluate(votes(["accept"] * 3), rules).decision is None
    assert (
        evaluate(votes(["accept", "reject", "edit", "accept", "accept"]), rules).decision
        == "accept"
    )


@pytest.mark.parametrize(
    "invalid_votes",
    [
        [Vote(1, "accept", Decimal("1")), Vote(1, "reject", Decimal("1"))],
        [Vote(1, "bad", Decimal("1"))],
        [Vote(1, "accept", Decimal("0"))],
        votes(["accept"] * 6),
    ],
)
def test_invalid_votes_are_refused(invalid_votes):
    with pytest.raises(ValueError):
        evaluate(invalid_votes, RULES)


@pytest.mark.parametrize(
    "weight,decision,final,control,expected",
    [
        ("1.00", "accept", "accept", False, "1.05"),
        ("1.00", "reject", "accept", False, "0.90"),
        ("1.00", "dont_know", "accept", False, "1.00"),
        ("2.00", "accept", "accept", False, "2.00"),
        ("0.50", "reject", "accept", False, "0.50"),
        ("1.99", "accept", "accept", False, "2.00"),
        ("0.51", "reject", "accept", False, "0.50"),
        ("1.00", "edit", "edit", True, "1.05"),
        ("1.00", "reject", "edit", True, "0.80"),
        ("1.00", "dont_know", "edit", True, "1.00"),
        ("0.60", "reject", "edit", True, "0.50"),
    ],
)
def test_reputation(weight, decision, final, control, expected):
    assert updated_weight(
        Decimal(weight),
        decision,
        final,
        correct_step=Decimal("0.05"),
        wrong_step=Decimal("0.20" if control else "0.10"),
        weight_min=Decimal("0.50"),
        weight_max=Decimal("2.00"),
    ) == Decimal(expected)
