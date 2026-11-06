"""Generate explicitly synthetic records for pipeline checks, never the TIL-25 dataset."""

import argparse
import csv
from pathlib import Path
from random import Random

FIELDS = (
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
DEFAULT_OUT = Path(__file__).resolve().parents[1] / (
    "tests/backend/evaluation/fixtures/records_synthetic.csv"
)


def generate(path, seed):
    rng = Random(seed)
    decisions = ["accept"] * 75 + ["reject"] * 38 + ["edit"] * 37
    rng.shuffle(decisions)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        for index, decision in enumerate(decisions, 1):
            writer.writerow(
                {
                    "id": f"synthetic-{index:03d}",
                    "type": "translation" if index % 2 else "term",
                    "domain": rng.choice(["it", "medicine", "engineering", "everyday"]),
                    "text_ru": "synthetic",
                    "text_kk": "synthetic",
                    "reference_decision": decision,
                    "error_type": ""
                    if decision == "accept"
                    else rng.choice(["wrong_term", "russian_connector", "grammar"]),
                    "is_original": "true",
                    "source_url": "",
                    "licence": "synthetic-fixture-only",
                    "attribution": "synthetic",
                    "labelled_by": "synthetic",
                    "labelled_at": "",
                }
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--seed", type=int, default=20261103)
    args = parser.parse_args()
    generate(args.out, args.seed)
    print(f"Wrote 150 synthetic records to {args.out} (seed {args.seed})")
