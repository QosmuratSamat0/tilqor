import json
from io import StringIO
from pathlib import Path

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.evaluation.domain.types import Ballot, Record
from apps.evaluation.io import write_json, write_records, write_votes
from apps.evaluation.report import DISCLAIMER

ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "tests/backend/evaluation/fixtures/records_synthetic.csv"
PROFILES = ROOT / "data/evaluation/simulation/mixed.json"
QUALITY = ROOT / "data/evaluation/quality.json"


def simulate(tmp_path):
    out = tmp_path / "votes.csv"
    call_command(
        "simulate_votes",
        "--records",
        str(FIXTURE),
        "--profiles",
        str(PROFILES),
        "--out",
        str(out),
        stdout=StringIO(),
    )
    return out, out.with_suffix(".records.csv")


def evaluate(votes, records, out, label="simulation", extra=()):
    call_command(
        "evaluate",
        "--records",
        str(records),
        "--votes",
        str(votes),
        "--quality",
        str(QUALITY),
        "--label",
        label,
        "--out",
        str(out),
        *extra,
        stdout=StringIO(),
    )
    return json.loads((out / "results.json").read_text(encoding="utf-8"))


def test_synthetic_end_to_end_without_database_and_reproducible_bytes(tmp_path):
    votes, records = simulate(tmp_path)
    before = {
        suffix: votes.with_suffix(suffix).read_bytes()
        for suffix in (".csv", ".records.csv", ".meta.json")
    }
    simulate(tmp_path)
    assert before == {suffix: votes.with_suffix(suffix).read_bytes() for suffix in before}
    output = tmp_path / "run"
    result = evaluate(votes, records, output)
    artifacts = [(output / name).read_bytes() for name in ("report.md", "results.json")]
    evaluate(votes, records, output)
    assert artifacts == [(output / name).read_bytes() for name in ("report.md", "results.json")]
    report = (output / "report.md").read_text(encoding="utf-8")
    assert report.startswith(DISCLAIMER + "\n")
    assert "# Synthetic records + simulation — pipeline check, not a result" in report
    assert all(
        "Simulation" in line
        for line in report.splitlines()
        if line.startswith("| ")
        and not line.startswith("| weighted")
        and not line.startswith("| baseline")
        and "method |" in line
    )
    for section in report.split("\n## ")[1:]:
        if "\n|" in section:
            assert section.startswith("Simulation:")
    assert len(result["records"]) == 150
    assert len(result["control_record_ids"]) == 15
    assert result["metrics"]["methods"]["weighted"]["all"] == 135
    assert result["metrics"]["accuracy_difference_ci"]["resamples"] == 2000
    assert result["metrics"]["alpha"]["pairable_values"] == 675
    assert result["processing"]["git_commit"]
    assert all(len(source["sha256"]) == 64 for source in result["inputs"].values())


def test_evaluate_requires_explicit_label(tmp_path):
    with pytest.raises(CommandError, match="label"):
        call_command(
            "evaluate",
            records=FIXTURE,
            votes=tmp_path / "votes.csv",
            quality=QUALITY,
            out=tmp_path / "run",
            stdout=StringIO(),
        )


def test_command_bad_csv_reports_file_and_line(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("id,reference_decision\nr,bad\n", encoding="utf-8")
    with pytest.raises(CommandError, match="bad.csv:2:"):
        call_command(
            "simulate_votes",
            "--records",
            str(path),
            "--profiles",
            str(PROFILES),
            "--out",
            str(tmp_path / "votes.csv"),
            stdout=StringIO(),
        )


def test_sidecar_integrity_and_label_protection(tmp_path):
    votes, records = simulate(tmp_path)
    with pytest.raises(CommandError, match="cannot be labelled real"):
        evaluate(votes, records, tmp_path / "bad", label="real")
    votes.write_bytes(votes.read_bytes() + b"\n")
    with pytest.raises(CommandError, match="votes SHA-256"):
        evaluate(votes, records, tmp_path / "bad")


def test_real_input_and_raw_agreement_includes_unused_votes(tmp_path):
    records, votes = tmp_path / "records.csv", tmp_path / "votes.csv"
    write_records(records, [Record("r", "accept"), Record("s", "reject"), Record("c", "edit")])
    write_votes(
        votes,
        [
            Ballot(id, i + 1, str(i), decision)
            for id, decisions in [
                ("r", ["accept"] * 3 + ["reject"] * 2),
                ("s", ["reject"] * 3),
                ("c", ["edit"] * 5),
            ]
            for i, decision in enumerate(decisions)
        ],
    )
    controls = tmp_path / "controls.json"
    write_json(controls, ["c"])
    result = evaluate(
        votes, records, tmp_path / "real", label="real", extra=("--controls", str(controls))
    )
    assert result["metrics"]["alpha"]["pairable_values"] == 8
    assert result["metrics"]["methods"]["weighted"]["all"] == 2
    assert result["assumptions"]["scenario"] is None
    assert result["records"][0]["weighted"]["counted_votes"] == 3


def test_source_record_file_order_is_honored_even_without_using_shuffled_snapshot(tmp_path):
    votes, _ = simulate(tmp_path)
    result = evaluate(votes, FIXTURE, tmp_path / "original-order")
    assert result["records"][0]["id"] == "synthetic-001"
    assert result["assumptions"]["generation_order"][0] != "synthetic-001"
