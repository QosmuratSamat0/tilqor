"""Record-level paired comparisons; undefined denominators stay explicit."""

from collections import defaultdict
from random import Random


def ratio(numerator, denominator):
    return numerator / denominator if denominator else None


def score(records, outcomes):
    by_id = {record.id: record for record in records}
    scored = [outcome for outcome in outcomes if not outcome.is_control]
    decided = [outcome for outcome in scored if outcome.decision is not None]
    correct = sum(
        outcome.decision == by_id[outcome.record_id].reference_decision for outcome in decided
    )
    unresolved = len(scored) - len(decided)
    return {
        "all": len(scored),
        "decided": len(decided),
        "correct": correct,
        "unresolved": unresolved,
        "accuracy": ratio(correct, len(decided)),
        "correct_all": ratio(correct, len(scored)),
        "unresolved_rate": ratio(unresolved, len(scored)),
        "votes_per_decided_record": ratio(
            sum(outcome.counted_votes for outcome in decided), len(decided)
        ),
    }


def breakdown(records, outcomes, field):
    groups = defaultdict(list)
    for record in records:
        groups[getattr(record, field) or "(unspecified)"].append(record)
    by_id = {outcome.record_id: outcome for outcome in outcomes}
    return {
        key: score(group, [by_id[r.id] for r in group]) for key, group in sorted(groups.items())
    }


def control_accuracy(counts):
    return {
        reviewer: {**stat, "accuracy": ratio(stat["correct"], stat["counted"])}
        for reviewer, stat in sorted(counts.items())
    }


def percentile(ordered, quantile):
    position = (len(ordered) - 1) * quantile
    low = int(position)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def bootstrap_difference(records, weighted, baseline, *, seed, resamples=2000):
    """Resample paired records, recomputing each method's own correct/decided ratio.

    No rerunning or relearning reputation inside a resample. If any draw has a
    zero decided denominator, report an undefined interval rather than silently
    discarding draws and changing the bootstrap distribution.
    """
    if resamples < 1:
        raise ValueError("Bootstrap requires a positive resample count.")
    left, right = (
        {outcome.record_id: outcome for outcome in outcomes} for outcomes in (weighted, baseline)
    )
    rows = []
    for record in records:
        w, b = left[record.id], right[record.id]
        if not w.is_control and not b.is_control:
            rows.append(
                (
                    int(w.decision == record.reference_decision),
                    int(w.decision is not None),
                    int(b.decision == record.reference_decision),
                    int(b.decision is not None),
                )
            )
    result = {
        "seed": seed,
        "resamples": resamples,
        "confidence": 0.95,
        "method": "paired records; linear-interpolated percentile",
        "estimate": None,
        "lower": None,
        "upper": None,
        "undefined_resamples": 0,
        "reason": None,
    }
    if not rows or not sum(row[1] for row in rows) or not sum(row[3] for row in rows):
        return {**result, "reason": "accuracy difference undefined: no decided records"}
    result["estimate"] = sum(row[0] for row in rows) / sum(row[1] for row in rows) - sum(
        row[2] for row in rows
    ) / sum(row[3] for row in rows)
    rng, differences = Random(seed), []
    for _ in range(resamples):
        totals = [0, 0, 0, 0]
        for _ in rows:
            row = rows[rng.randrange(len(rows))]
            for index in range(4):
                totals[index] += row[index]
        if totals[1] and totals[3]:
            differences.append(totals[0] / totals[1] - totals[2] / totals[3])
        else:
            result["undefined_resamples"] += 1
    if result["undefined_resamples"]:
        result["reason"] = "some resamples have no decided records; interval is undefined"
        return result
    differences.sort()
    result.update(lower=percentile(differences, 0.025), upper=percentile(differences, 0.975))
    return result
