import json
from dataclasses import asdict

import pytest

from apps.evaluation.configuration import read_profiles, read_quality
from apps.evaluation.domain.types import Quality
from apps.evaluation.io import InputError, read_records, read_votes, write_json


@pytest.mark.parametrize(
    ("content", "line", "reason"),
    [
        ("id,reference_decision\nr,unknown\n", 2, "reference_decision"),
        ("id,reference_decision\n,accept\n", 2, "identifier"),
        ("id,reference_decision\nr,accept\nr,reject\n", 3, "duplicate"),
        ("id,reference_decision\nr\n", 2, "width"),
        ("id,id\nr,accept\n", 1, "headers"),
        ('id,reference_decision\n"r,accept\n', 2, "end of data"),
    ],
)
def test_bad_record_csv_has_path_and_physical_line(tmp_path, content, line, reason):
    path = tmp_path / "bad.csv"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(InputError, match=reason) as error:
        read_records(path)
    assert f"{path}:{line}:" in str(error.value)


def test_optional_columns_and_unknown_extra_columns(tmp_path):
    path = tmp_path / "records.csv"
    path.write_text("id,reference_decision,extra\nr,accept,ignored\n", encoding="utf-8")
    records = read_records(path)
    assert records[0].id == "r"
    assert "extra" not in records[0].attributes


@pytest.mark.parametrize(
    "rows",
    [
        "unknown,1,x,accept\n",
        "r,0,x,accept\n",
        "r,1.0,x,accept\n",
        "r,1,x,bad\n",
        "r,1,x,accept\nr,1,y,accept\n",
        "r,1,x,dont_know\nr,2,x,accept\n",
    ],
)
def test_vote_schema_rejects_unknown_ids_bad_sequences_and_duplicates(tmp_path, rows):
    path = tmp_path / "votes.csv"
    path.write_text("record_id,seq,reviewer_id,decision\n" + rows, encoding="utf-8")
    with pytest.raises(InputError) as error:
        read_votes(path, {"r"})
    assert str(path) in str(error.value)


@pytest.mark.parametrize(
    "changes",
    [
        {"threshold": "NaN"},
        {"threshold": "0.5"},
        {"min_votes": 2},
        {"max_votes": 6},
        {"min_supporters": 1},
        {"weight_min": "0.49"},
        {"weight_initial": "2.01"},
        {"match_step": "-0.05"},
        {"mismatch_step": "0.123"},
        {"max_votes": True},
        {"unknown": 1},
    ],
)
def test_quality_settings_are_strict_and_frozen(tmp_path, changes):
    path = tmp_path / "quality.json"
    write_json(path, {**asdict(Quality()), **changes})
    with pytest.raises(InputError, match="quality.json:1:"):
        read_quality(path)


def test_quality_round_trip_and_json_syntax_line(tmp_path):
    path = tmp_path / "quality.json"
    write_json(path, asdict(Quality()))
    assert read_quality(path) == Quality()
    path.write_text('{\n "threshold": broken\n}', encoding="utf-8")
    with pytest.raises(InputError, match="quality.json:2:"):
        read_quality(path)


def test_profile_validation(tmp_path):
    path = tmp_path / "profiles.json"
    data = {
        "name": "test",
        "seed": 1,
        "control_share": 0.1,
        "reviewers": [{"id": str(i), "accuracy": 1, "dont_know_rate": 0} for i in range(5)],
    }
    write_json(path, data)
    assert len(read_profiles(path).reviewers) == 5
    for change in ({"accuracy": 1.1}, {"dont_know_rate": -1}, {"id": "1"}):
        modified = json.loads(json.dumps(data))
        modified["reviewers"][0].update(change)
        write_json(path, modified)
        with pytest.raises(InputError):
            read_profiles(path)
