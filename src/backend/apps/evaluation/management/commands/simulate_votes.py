from dataclasses import asdict
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.evaluation.configuration import read_profiles
from apps.evaluation.domain.simulation import simulate
from apps.evaluation.io import read_records, sha256, write_json, write_records, write_votes


class Command(BaseCommand):
    help = "Generate fixed-seed simulated votes, shuffled records and a provenance sidecar."
    requires_system_checks = []

    def add_arguments(self, parser):
        parser.add_argument("--records", required=True, type=Path)
        parser.add_argument("--profiles", required=True, type=Path)
        parser.add_argument("--out", required=True, type=Path)

    def handle(self, *args, **options):
        records_path, profiles_path, out = (options[key] for key in ("records", "profiles", "out"))
        ordered_path, metadata_path = out.with_suffix(".records.csv"), out.with_suffix(".meta.json")
        try:
            inputs = {records_path.resolve(), profiles_path.resolve()}
            outputs = {out.resolve(), ordered_path.resolve(), metadata_path.resolve()}
            if inputs & outputs or len(outputs) != 3:
                raise ValueError("Output paths must be distinct and cannot overwrite inputs.")
            records, scenario = read_records(records_path), read_profiles(profiles_path)
            result = simulate(records, scenario)
            out.parent.mkdir(parents=True, exist_ok=True)
            write_votes(out, result.votes)
            write_records(ordered_path, result.records)
            write_json(
                metadata_path,
                {
                    "format_version": 1,
                    "kind": "simulation",
                    "seed": scenario.seed,
                    "scenario": asdict(scenario),
                    "profiles_sha256": sha256(profiles_path),
                    "source_records_sha256": sha256(records_path),
                    "ordered_records_sha256": sha256(ordered_path),
                    "votes_sha256": sha256(out),
                    "record_order": [record.id for record in result.records],
                    "control_record_ids": sorted(result.control_record_ids),
                },
            )
        except (OSError, ValueError) as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(
            f"Simulation {scenario.name}: {len(result.records)} records, "
            f"{len(result.votes)} votes; "
            f"seed={scenario.seed}. Votes: {out}; replay records: {ordered_path}"
        )
