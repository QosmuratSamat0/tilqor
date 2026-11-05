"""Strict frozen settings/profile schemas; never read model settings from the DB."""

from dataclasses import asdict
from decimal import Decimal, InvalidOperation

from .domain.simulation import Reviewer, Scenario
from .domain.types import Quality
from .io import fail, identifier, read_json


def fields(path, value, required, optional=()):
    if (
        not isinstance(value, dict)
        or set(required) - set(value)
        or (set(value) - set(required) - set(optional))
    ):
        fail(path, 1, f"expected fields {', '.join(sorted(required))}; optional {list(optional)}")


def number(path, name, value):
    try:
        if isinstance(value, bool) or not isinstance(value, (str, int, float, Decimal)):
            raise ValueError()
        result = Decimal(str(value))
        if not result.is_finite():
            raise ValueError()
        return result
    except (InvalidOperation, ValueError):
        fail(path, 1, f"{name} must be a finite number")


def integer(path, name, value):
    if isinstance(value, bool) or not isinstance(value, int):
        fail(path, 1, f"{name} must be an integer")
    return value


def probability(path, name, value):
    result = number(path, name, value)
    if not 0 <= result <= 1:
        fail(path, 1, f"{name} must be in [0, 1]")
    return float(result)


def read_quality(path):
    data = read_json(path)
    fields(path, data, asdict(Quality()))
    integers = {"min_votes", "max_votes", "min_supporters"}
    values = {
        key: integer(path, key, value) if key in integers else number(path, key, value)
        for key, value in data.items()
    }
    quality = Quality(**values)
    if not Decimal("0.5") < quality.threshold <= 1:
        fail(path, 1, "threshold must be greater than 0.5 and at most 1")
    if not 3 <= quality.min_votes <= quality.max_votes <= 5:
        fail(path, 1, "require 3 <= min_votes <= max_votes <= 5")
    if not 2 <= quality.min_supporters <= quality.min_votes:
        fail(path, 1, "require 2 <= min_supporters <= min_votes")
    if (
        not Decimal("0.50")
        <= quality.weight_min
        <= quality.weight_initial
        <= (quality.weight_max)
        <= Decimal("2.00")
    ):
        fail(path, 1, "weights must be ordered within [0.50, 2.00]")
    for key, value in values.items():
        if (
            key not in integers
            and key != "threshold"
            and (not 0 <= value <= Decimal("9.99") or value % Decimal("0.01"))
        ):
            fail(path, 1, f"{key} must be in [0, 9.99] with at most 2 decimal places")
    return quality


def read_profiles(path):
    return parse_profiles(read_json(path), path)


def parse_profiles(data, path):
    fields(path, data, ("name", "seed", "control_share", "reviewers"))
    identifier(path, 1, "name", data["name"])
    seed = integer(path, "seed", data["seed"])
    share = probability(path, "control_share", data["control_share"])
    if not isinstance(data["reviewers"], list):
        fail(path, 1, "reviewers must be an array")
    reviewers, seen = [], set()
    for index, entry in enumerate(data["reviewers"], 1):
        fields(path, entry, ("id", "accuracy", "dont_know_rate"), ("profile",))
        id = identifier(path, 1, f"reviewers[{index}].id", entry["id"])
        if id in seen:
            fail(path, 1, f"duplicate reviewer {id}")
        seen.add(id)
        profile = entry.get("profile", "")
        if not isinstance(profile, str):
            fail(path, 1, "profile must be a string")
        reviewers.append(
            Reviewer(
                id,
                probability(path, "accuracy", entry["accuracy"]),
                probability(path, "dont_know_rate", entry["dont_know_rate"]),
                profile,
            )
        )
    if sum(reviewer.dont_know_rate < 1 for reviewer in reviewers) < 5:
        fail(path, 1, "at least 5 distinct reviewers must be able to give counted votes")
    return Scenario(data["name"], seed, share, tuple(reviewers))
