"""Plain evaluation inputs and outputs; independent of Django and persistence."""

from dataclasses import dataclass, field
from decimal import Decimal

from apps.verification.domain.decisions import Rules

DECISIONS = ("accept", "reject", "edit")


def ordered_ballots(record_id, ballots):
    """Keep sequence order and protect direct pure-domain callers from duplicate raters."""
    ordered = sorted(ballots, key=lambda ballot: ballot.seq)
    reviewers, sequences = set(), set()
    for ballot in ordered:
        if ballot.record_id != record_id or ballot.decision not in (*DECISIONS, "dont_know"):
            raise ValueError("Invalid ballot record or decision.")
        if ballot.seq < 1 or ballot.seq in sequences or ballot.reviewer_id in reviewers:
            raise ValueError("Duplicate reviewer/sequence or non-positive sequence.")
        reviewers.add(ballot.reviewer_id)
        sequences.add(ballot.seq)
    return ordered


@dataclass(frozen=True)
class Record:
    id: str
    reference_decision: str
    domain: str = ""
    error_type: str = ""
    attributes: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Ballot:
    record_id: str
    seq: int
    reviewer_id: str
    decision: str


@dataclass(frozen=True)
class Outcome:
    record_id: str
    decision: str | None
    status: str
    counted_votes: int
    used_seqs: tuple[int, ...]
    is_control: bool = False
    weight_snapshots: tuple[str, ...] = ()
    reputation_reference: str | None = None


@dataclass(frozen=True)
class Quality:
    threshold: Decimal = Decimal("0.66")
    min_votes: int = 3
    max_votes: int = 5
    min_supporters: int = 2
    weight_initial: Decimal = Decimal("1.00")
    weight_min: Decimal = Decimal("0.50")
    weight_max: Decimal = Decimal("2.00")
    match_step: Decimal = Decimal("0.05")
    mismatch_step: Decimal = Decimal("0.10")
    control_correct_step: Decimal = Decimal("0.05")
    control_wrong_step: Decimal = Decimal("0.20")

    @property
    def rules(self):
        return Rules(self.threshold, self.min_votes, self.max_votes, self.min_supporters)
