from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.glossary.domain.seed import SeedFormatError
from apps.glossary.services.seed import load_seed_directory


class Command(BaseCommand):
    help = "Load seed CSV files (terms.csv, sentences.csv, connectors.csv) idempotently."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dir",
            dest="seed_dir",
            default=str(settings.REPO_DIR / "data" / "seed"),
            help="Directory containing terms.csv, sentences.csv, and connectors.csv.",
        )

    def handle(self, *args, **options):
        seed_dir = Path(options["seed_dir"])
        if not seed_dir.is_dir():
            raise CommandError(f"Seed directory does not exist: {seed_dir}")
        try:
            counts = load_seed_directory(seed_dir)
        except SeedFormatError as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(
            self.style.SUCCESS(
                f"Seed loaded: {counts['terms']} terms, "
                f"{counts['term_variants']} variants, "
                f"{counts['sentences']} sentences, "
                f"{counts['connectors']} connectors."
            )
        )
