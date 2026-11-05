"""Nominal Krippendorff alpha, using exact rational coincidence counts.

Reference: Krippendorff (2011), Computing Krippendorff's Alpha-Reliability,
section C, pp. 4-5 (bibliography updated 2013). Units are rows, raters columns.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class Alpha:
    value: float | None
    reason: str | None
    pairable_units: int
    pairable_values: int
    observed_disagreement: float | None = None
    expected_disagreement: float | None = None


def nominal_alpha(units) -> Alpha:
    coincidences = defaultdict(Fraction)
    pairable_units = 0
    for unit in units:
        counts = Counter(value for value in unit if value is not None and value != "dont_know")
        size = sum(counts.values())
        if size < 2:
            continue
        pairable_units += 1
        for left, count in counts.items():
            for right, other in counts.items():
                coincidences[left, right] += Fraction(count * (other - (left == right)), size - 1)
    margins = defaultdict(Fraction)
    for (left, _), value in coincidences.items():
        margins[left] += value
    total = sum(margins.values(), Fraction())
    if pairable_units < 2 or total < 2:
        return Alpha(None, "fewer than 2 pairable units/values", pairable_units, int(total))
    observed = (
        sum((value for (left, right), value in coincidences.items() if left != right), Fraction())
        / total
    )
    expected = (total * total - sum(value * value for value in margins.values())) / (
        total * (total - 1)
    )
    if expected == 0:
        return Alpha(
            None,
            "only one category used; expected disagreement is 0",
            pairable_units,
            int(total),
            float(observed),
            0.0,
        )
    return Alpha(
        float(1 - observed / expected),
        None,
        pairable_units,
        int(total),
        float(observed),
        float(expected),
    )
