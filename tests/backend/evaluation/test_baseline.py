import pytest

from apps.evaluation.domain.baseline import majority


@pytest.mark.parametrize(
    ("decisions", "expected", "count"),
    [
        (["accept", "reject", "accept"], "accept", 3),
        (["accept", "reject", "edit", "reject"], None, 4),
        (["accept", "reject", "edit", "reject", "edit"], None, 5),
        (["accept", "reject", "edit", "accept", "accept"], "accept", 5),
        (["accept", "dont_know", "accept", "reject"], "accept", 3),
        (["accept", "accept"], None, 2),
    ],
)
def test_sequential_majority(ballots, decisions, expected, count):
    result = majority("r", ballots(decisions))
    assert (result.decision, result.counted_votes) == (expected, count)


def test_two_two_at_four_continues_if_minimum_is_four(ballots):
    # With min=3 any A,A,B or A,B,B prefix already decides; a 2-2 prefix
    # is reachable when the frozen minimum is four. Test the tie explicitly.
    result = majority("r", ballots(["accept", "reject", "accept", "reject"]), min_votes=4)
    assert result.decision is None


def test_later_votes_are_not_used(ballots):
    result = majority("r", ballots(["edit", "edit", "accept", "reject", "reject"]))
    assert result.decision == "edit"
    assert result.used_seqs == (1, 2, 3)
