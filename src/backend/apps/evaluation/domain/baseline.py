"""Sequential, unweighted strict majority; abstentions consume no counted slot."""

from collections import Counter

from .types import Outcome, ordered_ballots


def majority(record_id, ballots, *, min_votes=3, max_votes=5, is_control=False):
    if not 3 <= min_votes <= max_votes <= 5:
        raise ValueError("Require 3 <= min_votes <= max_votes <= 5.")
    counts, used = Counter(), []
    for ballot in ordered_ballots(record_id, ballots):
        used.append(ballot.seq)
        if ballot.decision == "dont_know":
            continue
        counts[ballot.decision] += 1
        total = sum(counts.values())
        if total >= min_votes:
            for decision, count in counts.items():
                if count * 2 > total:
                    return Outcome(record_id, decision, "decided", total, tuple(used), is_control)
        if total >= max_votes:
            break
    return Outcome(record_id, None, "unresolved", sum(counts.values()), tuple(used), is_control)
