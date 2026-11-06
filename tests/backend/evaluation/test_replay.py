from decimal import Decimal

import pytest

from apps.evaluation.domain.replay import replay
from apps.evaluation.domain.types import Quality, Record
from apps.verification.domain.decisions import Vote, evaluate


@pytest.mark.parametrize(
    ("decisions", "weights"),
    [
        (["accept", "accept"], ["1", "1"]),
        (["accept", "accept", "reject"], ["1", "1", "1"]),
        (["reject", "reject", "edit"], ["1", "1", "1"]),
        (["edit", "edit", "accept"], ["1", "1", "1"]),
        (["accept", "reject", "edit"], ["2", ".5", ".5"]),
        (["accept", "reject", "edit", "accept", "reject"], ["1"] * 5),
        (["accept", "dont_know", "accept", "reject"], ["1"] * 4),
    ],
)
def test_fr11_fixtures_reuse_production_evaluate(ballots, decisions, weights):
    expected = evaluate(
        [
            Vote(i, decision, Decimal(weight))
            for i, (decision, weight) in enumerate(zip(decisions, weights, strict=True))
        ],
        Quality().rules,
    )
    result = replay(
        [Record("r", "accept")],
        {"r": ballots(decisions)},
        initial_weights={str(i): Decimal(w) for i, w in enumerate(weights)},
    )
    actual = result.outcomes[0]
    assert actual.decision == expected.decision
    assert (actual.status == "escalated") == expected.escalated


def test_standard_updates_once_and_ignore_later_votes(ballots):
    result = replay(
        [Record("r", "accept")], {"r": ballots(["reject", "reject", "accept", "edit", "accept"])}
    )
    assert result.final_weights == {"0": "1.05", "1": "1.05", "2": "0.90", "3": "1.00", "4": "1.00"}
    assert result.outcomes[0].used_seqs == (1, 2, 3)
    assert result.outcomes[0].reputation_reference == "reject"  # Not the reference label.


def test_control_steps_and_next_record_snapshots(ballots):
    records = [Record("c", "accept"), Record("r", "accept")]
    result = replay(
        records,
        {
            "c": ballots(["accept", "reject", "dont_know"], "c"),
            "r": ballots(["accept", "accept", "reject"]),
        },
        controls={"c"},
    )
    assert result.outcomes[0].is_control
    assert result.outcomes[1].weight_snapshots == ("1.05", "0.80", "1.00")
    assert result.final_weights == {"0": "1.05", "1": "0.80", "2": "1.00"}
    assert result.controls["1"] == {"correct": 0, "counted": 1, "abstained": 0}


def test_escalation_uses_reference_moderator_assumption(ballots):
    result = replay(
        [Record("r", "edit")], {"r": ballots(["accept", "reject", "edit", "accept", "reject"])}
    )
    assert result.outcomes[0].decision is None
    assert result.outcomes[0].status == "escalated"
    assert result.final_weights["2"] == "1.05"
    assert result.final_weights["0"] == "0.90"


def test_bounds_and_whole_record_order(ballots):
    records = [Record(str(i), "accept") for i in range(40)]
    votes = {
        r.id: ballots(["accept", "accept", "reject", "accept", "reject"], r.id) for r in records
    }
    result = replay(records, votes)
    assert result.final_weights["0"] == "2.00"
    assert result.final_weights["2"] == "0.50"
    assert result.outcomes[1].weight_snapshots[:3] == ("1.05", "1.05", "0.90")


def test_incomplete_record_and_abstentions_do_not_change_reputation(ballots):
    result = replay([Record("r", "edit")], {"r": ballots(["accept", "dont_know", "edit"])})
    assert result.outcomes[0].status == "pending"
    assert set(result.final_weights.values()) == {"1.00"}


def test_control_uses_all_votes_and_only_control_updates(ballots):
    records = [Record(str(i), "accept") for i in range(40)]
    votes = {
        r.id: ballots(["accept", "accept", "accept", "reject", "reject"], r.id) for r in records
    }
    result = replay(records, votes, controls={r.id for r in records})
    assert all(outcome.counted_votes == 5 for outcome in result.outcomes)
    assert result.final_weights == {"0": "2.00", "1": "2.00", "2": "2.00", "3": "0.50", "4": "0.50"}
    assert result.controls["0"]["counted"] == 40


def test_calls_production_rule_at_each_counted_point_then_stops(ballots, monkeypatch):
    from apps.evaluation.domain import replay as module

    production_evaluate = module.evaluate
    seen = []

    def traced(votes, rules):
        seen.append(sum(v.decision != "dont_know" for v in votes))
        return production_evaluate(votes, rules)

    monkeypatch.setattr(module, "evaluate", traced)
    result = replay(
        [Record("r", "accept")],
        {"r": ballots(["accept", "reject", "edit", "dont_know", "accept", "reject", "accept"])},
    )
    assert seen == [3, 4, 5]
    assert result.outcomes[0].used_seqs == (1, 2, 3, 4, 5, 6)
    assert result.final_weights["6"] == "1.00"


def test_real_replay_does_not_invent_moderator_resolutions(ballots):
    result = replay(
        [Record("r", "edit")],
        {"r": ballots(["accept", "reject", "edit", "accept", "reject"])},
        assume_reference_resolution=False,
    )
    assert result.outcomes[0].status == "escalated"
    assert result.outcomes[0].reputation_reference is None
    assert set(result.final_weights.values()) == {"1.00"}
