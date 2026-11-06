from collections import defaultdict

import pytest

from apps.evaluation.domain.simulation import Reviewer, Scenario, simulate
from apps.evaluation.domain.types import Record


def scenario(accuracy=0.7, dont_know=0.05):
    return Scenario(
        "test", 20261103, 0.1, tuple(Reviewer(str(i), accuracy, dont_know) for i in range(15))
    )


def test_fixed_seed_distinct_reviewers_and_counted_limit():
    records = [Record(str(i), "accept") for i in range(150)]
    first, second = simulate(records, scenario()), simulate(records, scenario())
    assert first == second
    assert len(first.control_record_ids) == 15
    assert first.records != records
    groups = defaultdict(list)
    for ballot in first.votes:
        groups[ballot.record_id].append(ballot)
    for ballots in groups.values():
        assert len({b.reviewer_id for b in ballots}) == len(ballots)
        assert sum(b.decision != "dont_know" for b in ballots) == 5
    assert any(b.decision == "dont_know" for b in first.votes)


def test_perfect_reviewer_is_always_correct():
    records = [Record(str(i), ["accept", "reject", "edit"][i % 3]) for i in range(30)]
    result = simulate(records, scenario(accuracy=1.0, dont_know=0))
    references = {r.id: r.reference_decision for r in records}
    assert all(ballot.decision == references[ballot.record_id] for ballot in result.votes)


def test_pool_exhaustion_is_explicit_not_a_biased_redraw():
    with pytest.raises(ValueError, match="pool exhausted"):
        simulate([Record("r", "accept")], scenario(dont_know=1))
