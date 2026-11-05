import json
from dataclasses import asdict
from pathlib import Path

import django
from django.core.management.base import BaseCommand, CommandError

from apps.evaluation.configuration import read_quality
from apps.evaluation.domain.alpha import nominal_alpha
from apps.evaluation.domain.baseline import majority
from apps.evaluation.domain.metrics import (
    bootstrap_difference,
    breakdown,
    control_accuracy,
    score,
)
from apps.evaluation.domain.replay import replay
from apps.evaluation.io import read_json, read_records, read_votes, sha256, write_json
from apps.evaluation.provenance import control_ids, processing_conditions, simulation_metadata
from apps.evaluation.report import report_markdown


class Command(BaseCommand):
    help = "Compare frozen weighted replay and sequential majority on the same ordered votes."
    requires_system_checks = []

    def add_arguments(self, parser):
        for flag in ("records", "votes", "quality", "out"):
            parser.add_argument(f"--{flag}", required=True, type=Path)
        parser.add_argument("--label", required=True, choices=("simulation", "real"))
        parser.add_argument("--controls", type=Path, help="Real-vote control IDs as a JSON array.")
        parser.add_argument("--seed", type=int, help="Bootstrap seed; defaults to simulation seed.")

    def handle(self, *args, **options):
        try:
            result = self.evaluate(options)
            out = options["out"]
            protected = {options[key].resolve() for key in ("records", "votes", "quality")}
            if options["controls"]:
                protected.add(options["controls"].resolve())
            if any((out / name).resolve() in protected for name in ("results.json", "report.md")):
                raise ValueError("Outputs cannot overwrite input files.")
            out.mkdir(parents=True, exist_ok=True)
            write_json(out / "results.json", result)
            (out / "report.md").write_text(report_markdown(result), encoding="utf-8", newline="\n")
        except (OSError, ValueError) as exc:
            raise CommandError(str(exc)) from exc
        stats = result["metrics"]["methods"]
        self.stdout.write(
            f"{options['label']}: weighted {stats['weighted']['correct']}/"
            f"{stats['weighted']['decided']}; baseline {stats['baseline']['correct']}/"
            f"{stats['baseline']['decided']}. Wrote {out / 'report.md'} and results.json"
        )

    def evaluate(self, options):
        records_path, votes_path, quality_path = (
            options[key] for key in ("records", "votes", "quality")
        )
        records = read_records(records_path)
        ballots = read_votes(votes_path, {record.id for record in records})
        quality = read_quality(quality_path)
        label = options["label"]
        metadata, controls = simulation_metadata(votes_path, records_path, records, label)
        if options["controls"]:
            if label != "real":
                raise ValueError(
                    "--controls is only for real votes; simulation controls are frozen."
                )
            controls = control_ids(options["controls"], read_json(options["controls"]), records)
        seed = (
            options["seed"]
            if options["seed"] is not None
            else (metadata["seed"] if metadata else 20261103)
        )
        weighted = replay(
            records, ballots, quality, controls, assume_reference_resolution=label == "simulation"
        )
        # FR-25 baseline uses fixed 3..5 points, independently of weighted configuration.
        baseline = [
            majority(r.id, ballots.get(r.id, []), is_control=r.id in controls) for r in records
        ]
        methods = {"weighted": weighted.outcomes, "baseline": baseline}
        scores = {name: score(records, outcomes) for name, outcomes in methods.items()}
        w, b = scores["weighted"], scores["baseline"]
        if w["accuracy"] is None or b["accuracy"] is None:
            h1 = "undefined: at least one method has no decided non-control records."
        elif w["accuracy"] < b["accuracy"]:
            h1 = "not supported: weighted accuracy is lower than baseline."
        elif w["accuracy"] > b["accuracy"]:
            h1 = "supported in this run: weighted accuracy is higher than baseline."
        else:
            h1 = "accuracy is equal; the strict improvement claim is not supported."
        h2 = (
            "undefined: no non-control records."
            if not w["all"]
            else f"weighted leaves {w['unresolved']} unresolved vs {b['unresolved']} for baseline; "
            + (
                "higher moderator cost observed."
                if w["unresolved"] > b["unresolved"]
                else "higher moderator cost not observed."
            )
        )
        inputs = {
            key: {"path": str(options[key]), "sha256": sha256(options[key])}
            for key in ("records", "votes", "quality")
        }
        if metadata:
            meta_path = votes_path.with_suffix(".meta.json")
            inputs["simulation_metadata"] = {"path": str(meta_path), "sha256": sha256(meta_path)}
        if options["controls"]:
            inputs["controls"] = {
                "path": str(options["controls"]),
                "sha256": sha256(options["controls"]),
            }
        synthetic = all(
            r.id.startswith("synthetic-")
            and r.attributes.get("text_ru") == r.attributes.get("text_kk") == "synthetic"
            for r in records
        )
        title = (
            f"Synthetic records + {label if label == 'simulation' else 'real votes'} "
            "— pipeline check, not a result"
            if synthetic
            else f"{label.title()} — weighted quality model vs majority baseline"
        )
        return {
            "format_version": 1,
            "label": label,
            "title": title,
            "synthetic": synthetic,
            "scenario": metadata["scenario"]["name"] if metadata else "real",
            "seed": metadata["seed"] if metadata else seed,
            "settings": json.loads(json.dumps(asdict(quality), default=str)),
            "inputs": inputs,
            "processing": {**processing_conditions(), "django": django.get_version()},
            "control_record_ids": sorted(controls),
            "assumptions": {
                "scenario": metadata["scenario"] if metadata else None,
                "moderator_reference_resolution": label == "simulation",
                "generation_order": metadata["record_order"] if metadata else None,
            },
            "hypotheses": {"H1": h1, "H2": h2},
            "metrics": {
                "methods": scores,
                "alpha": asdict(
                    nominal_alpha(
                        [
                            [ballot.decision for ballot in ballots.get(r.id, [])]
                            for r in records
                            if r.id not in controls
                        ]
                    )
                ),
                "control_accuracy": control_accuracy(weighted.controls),
                "accuracy_difference_ci": bootstrap_difference(
                    records,
                    weighted.outcomes,
                    baseline,
                    seed=seed,
                ),
                "breakdowns": {
                    field: {
                        name: breakdown(records, outcomes, field)
                        for name, outcomes in methods.items()
                    }
                    for field in ("error_type", "domain")
                },
            },
            "final_weights": weighted.final_weights,
            "records": [
                {
                    "id": r.id,
                    "reference_decision": r.reference_decision,
                    "domain": r.domain,
                    "error_type": r.error_type,
                    "is_control": r.id in controls,
                    **{name: asdict(outcomes[index]) for name, outcomes in methods.items()},
                }
                for index, r in enumerate(records)
            ],
        }
