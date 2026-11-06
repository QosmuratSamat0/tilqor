"""Fixed-seed assumptions about reviewers, not measurements of real reviewer ability."""

from dataclasses import dataclass
from random import Random

from .types import DECISIONS, Ballot, Record


@dataclass(frozen=True)
class Reviewer:
    id: str
    accuracy: float
    dont_know_rate: float
    profile: str = ""


@dataclass(frozen=True)
class Scenario:
    name: str
    seed: int
    control_share: float
    reviewers: tuple[Reviewer, ...]


@dataclass(frozen=True)
class Simulation:
    records: list[Record]
    votes: list[Ballot]
    control_record_ids: frozenset[str]


def simulate(records, scenario):
    """Sample without replacement; fail if a finite reviewer pool cannot supply 5 votes.

    Retrying the draw or silently replacing abstentions would condition away difficult
    records and change the declared don't-know assumption, so exhaustion is explicit.
    Control count rounds N*share to the nearest integer (half up).
    """
    rng = Random(scenario.seed)
    ordered = list(records)
    rng.shuffle(ordered)
    control_count = int(len(ordered) * scenario.control_share + 0.5)
    controls = frozenset(r.id for r in rng.sample(ordered, control_count))
    votes = []
    for record in ordered:
        counted = 0
        reviewers = list(scenario.reviewers)
        rng.shuffle(reviewers)
        for seq, reviewer in enumerate(reviewers, 1):
            if rng.random() < reviewer.dont_know_rate:
                decision = "dont_know"
            elif rng.random() < reviewer.accuracy:
                decision = record.reference_decision
            else:
                decision = rng.choice([d for d in DECISIONS if d != record.reference_decision])
            votes.append(Ballot(record.id, seq, reviewer.id, decision))
            counted += decision != "dont_know"
            if counted == 5:
                break
        if counted < 5:
            raise ValueError(
                f"Record {record.id}: reviewer pool exhausted before 5 counted votes; "
                "increase the pool or revise the declared abstention rates."
            )
    return Simulation(ordered, votes, controls)
