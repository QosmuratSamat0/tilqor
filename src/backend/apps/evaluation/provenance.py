"""Validate generated sidecars before using their control IDs or assumptions."""

import hashlib
import platform
import subprocess
from pathlib import Path

from .configuration import integer, parse_profiles
from .io import fail, read_json, sha256


def control_ids(path, values, records):
    if not isinstance(values, list) or any(not isinstance(id, str) for id in values):
        fail(path, 1, "control IDs must be a JSON array of strings")
    if len(set(values)) != len(values) or set(values) - {r.id for r in records}:
        fail(path, 1, "duplicate or unknown control record IDs")
    return frozenset(values)


def simulation_metadata(votes_path, records_path, records, label):
    path = votes_path.with_suffix(".meta.json")
    if not path.exists():
        if label == "simulation":
            fail(path, 1, "simulation requires the sidecar written by simulate_votes")
        return None, frozenset()
    data = read_json(path)
    required = {
        "format_version",
        "kind",
        "seed",
        "scenario",
        "source_records_sha256",
        "ordered_records_sha256",
        "votes_sha256",
        "profiles_sha256",
        "record_order",
        "control_record_ids",
    }
    if not isinstance(data, dict) or not required <= data.keys():
        fail(path, 1, "incomplete simulation metadata")
    if data["format_version"] != 1 or data["kind"] != "simulation":
        fail(path, 1, "unknown simulation metadata format")
    if label != "simulation":
        fail(path, 1, "simulated votes cannot be labelled real")
    if data["votes_sha256"] != sha256(votes_path):
        fail(path, 1, "votes SHA-256 differs from frozen simulation")
    if sha256(records_path) not in (data["source_records_sha256"], data["ordered_records_sha256"]):
        fail(path, 1, "records SHA-256 differs from frozen simulation")
    order = data["record_order"]
    if (
        not isinstance(order, list)
        or any(not isinstance(id, str) for id in order)
        or (len(set(order)) != len(records) or set(order) != {r.id for r in records})
    ):
        fail(path, 1, "generation order must contain each record exactly once")
    if sha256(records_path) == data["ordered_records_sha256"] and order != [r.id for r in records]:
        fail(path, 1, "record order differs from the frozen shuffled snapshot")
    seed = integer(path, "seed", data["seed"])
    scenario = parse_profiles(data["scenario"], path)
    if seed != scenario.seed:
        fail(path, 1, "metadata seed differs from reviewer assumptions")
    controls = control_ids(path, data["control_record_ids"], records)
    if len(controls) != int(len(records) * scenario.control_share + 0.5):
        fail(path, 1, "control count differs from declared share")
    return data, controls


def processing_conditions():
    root = Path(__file__).resolve().parents[4]
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, stderr=subprocess.DEVNULL, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        commit = None
    digest = hashlib.sha256()
    evaluation = Path(__file__).parent
    verification = evaluation.parent / "verification/domain"
    sources = [
        *evaluation.rglob("*.py"),
        verification / "decisions.py",
        verification / "reputation.py",
    ]
    for source in sorted(sources):
        digest.update(source.relative_to(root).as_posix().encode())
        digest.update(b"\0")
        digest.update(source.read_bytes())
    return {
        "git_commit": commit,
        "implementation_sha256": digest.hexdigest(),
        "python": platform.python_version(),
        "record_processing": "input CSV file order",
    }
