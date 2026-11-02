from decimal import ROUND_HALF_UP, Decimal


def updated_weight(
    weight: Decimal,
    decision: str,
    final_decision: str,
    *,
    correct_step: Decimal,
    wrong_step: Decimal,
    weight_min: Decimal,
    weight_max: Decimal,
) -> Decimal:
    if decision == "dont_know":
        return weight
    delta = correct_step if decision == final_decision else -wrong_step
    return min(weight_max, max(weight_min, weight + delta)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
