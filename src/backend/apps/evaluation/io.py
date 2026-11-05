"""UTF-8 CSV/JSON adapters, line-aware schema errors and canonical LF output."""

import csv
import hashlib
import json
import re
from collections import defaultdict
from dataclasses import asdict, is_dataclass
from decimal import Decimal
from pathlib import Path

from .domain.types import DECISIONS, Ballot, Record

RECORD_FIELDS = (
    "id",
    "type",
    "domain",
    "text_ru",
    "text_kk",
    "reference_decision",
    "error_type",
    "is_original",
    "source_url",
    "licence",
    "attribution",
    "labelled_by",
    "labelled_at",
)
VOTE_FIELDS = ("record_id", "seq", "reviewer_id", "decision")


class InputError(ValueError):
    pass


def fail(path, line, message):
    raise InputError(f"{path}:{line}: {message}")


def read_json(path):
    def invalid_constant(value):
        raise ValueError(f"non-finite JSON number {value}")

    try:
        with Path(path).open(encoding="utf-8-sig") as stream:
            return json.load(stream, parse_float=Decimal, parse_constant=invalid_constant)
    except json.JSONDecodeError as exc:
        fail(path, exc.lineno, exc.msg)
    except (OSError, UnicodeError, ValueError) as exc:
        fail(path, 1, str(exc))


def json_value(value):
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (set, frozenset)):
        return sorted(value)
    raise TypeError(f"Cannot encode {type(value).__name__}")


def write_json(path, value):
    Path(path).write_text(
        json.dumps(
            value, default=json_value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def csv_rows(path, required):
    try:
        with Path(path).open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream, skipinitialspace=True, strict=True)
            names = reader.fieldnames
            if not names or len(set(names)) != len(names) or not set(required) <= set(names):
                fail(path, 1, f"require unique headers including {', '.join(required)}")
            for row in reader:
                if None in row or any(value is None for value in row.values()):
                    fail(path, reader.line_num, "row width differs from header")
                yield reader.line_num, row
    except csv.Error as exc:
        fail(path, reader.reader.line_num, str(exc))
    except (OSError, UnicodeError) as exc:
        fail(path, 1, str(exc))


def identifier(path, line, name, value):
    if not isinstance(value, str) or not value or value != value.strip():
        fail(path, line, f"{name} must be a non-empty identifier without surrounding whitespace")
    return value


def read_records(path):
    records, seen = [], set()
    for line, row in csv_rows(path, ("id", "reference_decision")):
        id = identifier(path, line, "id", row["id"])
        if id in seen:
            fail(path, line, f"duplicate record id {id}")
        seen.add(id)
        if row["reference_decision"] not in DECISIONS:
            fail(path, line, "reference_decision must be accept, reject or edit")
        if row.get("type", "") not in ("", "translation", "term"):
            fail(path, line, "type must be translation or term when supplied")
        if row.get("error_type", "") not in ("", "wrong_term", "russian_connector", "grammar"):
            fail(path, line, "unknown error_type")
        records.append(
            Record(
                id,
                row["reference_decision"],
                row.get("domain", ""),
                row.get("error_type", ""),
                {key: row.get(key, "") for key in RECORD_FIELDS},
            )
        )
    if not records:
        fail(path, 2, "records file contains no records")
    return records


def read_votes(path, record_ids):
    groups, seen_seq, seen_reviewers = defaultdict(list), set(), set()
    for line, row in csv_rows(path, VOTE_FIELDS):
        record = identifier(path, line, "record_id", row["record_id"])
        reviewer = identifier(path, line, "reviewer_id", row["reviewer_id"])
        if record not in record_ids:
            fail(path, line, f"unknown record_id {record}")
        if not re.fullmatch(r"[1-9][0-9]*", row["seq"]):
            fail(path, line, "seq must be a positive integer")
        seq = int(row["seq"])
        if (record, seq) in seen_seq or (record, reviewer) in seen_reviewers:
            fail(path, line, "duplicate sequence or reviewer within record")
        if row["decision"] not in (*DECISIONS, "dont_know"):
            fail(path, line, "unknown decision")
        seen_seq.add((record, seq))
        seen_reviewers.add((record, reviewer))
        groups[record].append(Ballot(record, seq, reviewer, row["decision"]))
    return {id: sorted(ballots, key=lambda ballot: ballot.seq) for id, ballots in groups.items()}


def write_csv(path, fields, rows):
    with Path(path).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_records(path, records):
    write_csv(
        path,
        RECORD_FIELDS,
        (
            {
                **dict.fromkeys(RECORD_FIELDS, ""),
                **record.attributes,
                "id": record.id,
                "reference_decision": record.reference_decision,
                "domain": record.domain,
                "error_type": record.error_type,
            }
            for record in records
        ),
    )


def write_votes(path, ballots):
    write_csv(path, VOTE_FIELDS, (asdict(ballot) for ballot in ballots))
