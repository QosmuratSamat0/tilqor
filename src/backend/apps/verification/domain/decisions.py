from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal

COUNTED = ("accept", "reject", "edit")
STATUSES = {"accept": "accepted", "reject": "rejected", "edit": "needs_edit"}


@dataclass(frozen=True)
class Vote:
    reviewer_id: int
    decision: str
    weight: Decimal


@dataclass(frozen=True)
class Rules:
    threshold: Decimal
    min_votes: int
    max_votes: int
    min_supporters: int


@dataclass(frozen=True)
class Result:
    decision: str | None
    counted_votes: int
    escalated: bool


def evaluate(votes: list[Vote], rules: Rules) -> Result:
    """Compare exact weighted sums; abstentions consume neither weight nor slots."""
    seen = set()
    weights = defaultdict(Decimal)
    supporters = defaultdict(set)
    for vote in votes:
        if vote.reviewer_id in seen:
            raise ValueError("A reviewer may vote only once per version.")
        seen.add(vote.reviewer_id)
        if vote.decision == "dont_know":
            continue
        if vote.decision not in COUNTED or vote.weight <= 0:
            raise ValueError("Invalid counted vote.")
        weights[vote.decision] += vote.weight
        supporters[vote.decision].add(vote.reviewer_id)
    count = sum(len(ids) for ids in supporters.values())
    if count > rules.max_votes:
        raise ValueError("The counted-vote limit has been reached.")
    if count >= rules.min_votes:
        total = sum(weights.values(), Decimal("0"))
        for decision in COUNTED:
            if (
                len(supporters[decision]) >= rules.min_supporters
                and weights[decision] >= total * rules.threshold
            ):
                return Result(decision, count, False)
    return Result(None, count, count >= rules.max_votes)
