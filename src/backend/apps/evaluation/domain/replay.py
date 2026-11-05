"""Whole-record replay reusing the production decision and reputation functions."""

from dataclasses import dataclass

from apps.verification.domain.decisions import Vote, evaluate
from apps.verification.domain.reputation import updated_weight

from .types import Outcome, Quality, ordered_ballots


@dataclass(frozen=True)
class Replay:
    outcomes: list[Outcome]
    final_weights: dict[str, str]
    controls: dict[str, dict[str, int]]


def replay(records, ballots_by_record, quality=None, controls=frozenset(), *, initial_weights=None):
    """Moderators resolve escalations with reference labels: a simulation assumption.

    Incomplete records (< max counted votes, no outcome) do not finalize or update
    standard reputation. Control votes always use the reference and no standard update.
    initial_weights is for pure rule fixtures; commands always start everyone at the
    frozen quality.weight_initial and never load persisted reviewer profiles.
    """
    quality = quality or Quality()
    reviewers = sorted(
        {ballot.reviewer_id for ballots in ballots_by_record.values() for ballot in ballots}
    )
    identities = {reviewer: index for index, reviewer in enumerate(reviewers)}
    weights = dict.fromkeys(reviewers, quality.weight_initial)
    if initial_weights:
        if set(initial_weights) - set(reviewers):
            raise ValueError("Unknown initial reviewer.")
        if any(
            not quality.weight_min <= weight <= quality.weight_max
            for weight in initial_weights.values()
        ):
            raise ValueError("Initial weight outside frozen bounds.")
        weights.update(initial_weights)
    control_counts = {
        reviewer: {"correct": 0, "counted": 0, "abstained": 0} for reviewer in reviewers
    }
    outcomes = []

    def update(ballot, final_decision, *, control=False):
        weights[ballot.reviewer_id] = updated_weight(
            weights[ballot.reviewer_id],
            ballot.decision,
            final_decision,
            correct_step=quality.control_correct_step if control else quality.match_step,
            wrong_step=quality.control_wrong_step if control else quality.mismatch_step,
            weight_min=quality.weight_min,
            weight_max=quality.weight_max,
        )

    for record in records:
        is_control = record.id in controls
        consumed, snapshots, votes = [], [], []
        counted, decision, escalated = 0, None, False
        for ballot in ordered_ballots(record.id, ballots_by_record.get(record.id, [])):
            consumed.append(ballot)
            weight = weights[ballot.reviewer_id]
            snapshots.append(format(weight, ".2f"))
            votes.append(Vote(identities[ballot.reviewer_id], ballot.decision, weight))
            if is_control:
                stat = control_counts[ballot.reviewer_id]
                if ballot.decision == "dont_know":
                    stat["abstained"] += 1
                else:
                    stat["counted"] += 1
                    stat["correct"] += ballot.decision == record.reference_decision
                update(ballot, record.reference_decision, control=True)
            if ballot.decision == "dont_know":
                continue
            counted += 1
            if not is_control and counted >= quality.min_votes:
                result = evaluate(votes, quality.rules)
                decision, escalated = result.decision, result.escalated
                if decision is not None or escalated:
                    break
            if counted >= quality.max_votes:
                break
        final = record.reference_decision if is_control or escalated else decision
        if not is_control and final is not None:
            for ballot in consumed:
                update(ballot, final)
        status = (
            "control"
            if is_control
            else ("decided" if decision is not None else "escalated" if escalated else "pending")
        )
        outcomes.append(
            Outcome(
                record.id,
                decision,
                status,
                counted,
                tuple(ballot.seq for ballot in consumed),
                is_control,
                tuple(snapshots),
                final,
            )
        )
    return Replay(
        outcomes, {key: format(value, ".2f") for key, value in weights.items()}, control_counts
    )
