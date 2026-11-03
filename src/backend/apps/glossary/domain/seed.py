import csv
from dataclasses import dataclass
from pathlib import Path

from apps.contributions.domain import normalize_text
from common.choices import Domain

VALID_DOMAINS = set(Domain.values)
TRUE_VALUES = {"1", "true", "yes"}
FALSE_VALUES = {"0", "false", "no", ""}


class SeedFormatError(ValueError):
    def __init__(self, filename: str, line_number: int, reason: str):
        self.filename = filename
        self.line_number = line_number
        self.reason = reason
        super().__init__(f"{filename}: line {line_number}: {reason}")


@dataclass(frozen=True)
class TermSeedRow:
    text_ru: str
    definition: str
    domain: str
    variants_kk: tuple[str, ...]
    source: str


@dataclass(frozen=True)
class SentenceSeedRow:
    text_ru: str
    domain: str
    source_url: str
    licence: str
    attribution: str
    is_original: bool


@dataclass(frozen=True)
class ConnectorSeedRow:
    text_ru: str
    text_kk: str
    example_kk: str
    example_ru: str
    source: str
    licence: str


def _open_csv_rows(directory: Path, filename: str, required_columns: set[str]):
    path = directory / filename
    if not path.is_file():
        raise SeedFormatError(filename, 1, f"File '{filename}' does not exist in {directory}.")
    text = path.read_text(encoding="utf-8-sig")
    reader = csv.DictReader(text.splitlines())
    if not reader.fieldnames:
        raise SeedFormatError(filename, 1, "Missing CSV header row.")
    header = {col.strip() for col in reader.fieldnames if col}
    missing = sorted(required_columns - header)
    if missing:
        raise SeedFormatError(
            filename, 1, f"Missing required columns: {', '.join(missing)}."
        )
    for line_no, raw_row in enumerate(reader, start=2):
        if None in raw_row:
            raise SeedFormatError(filename, line_no, "Row has more columns than header.")
        if any(v is None for v in raw_row.values()):
            raise SeedFormatError(filename, line_no, "Row has fewer columns than header.")
        yield line_no, {k.strip(): normalize_text(v) for k, v in raw_row.items() if k}


def parse_terms_csv(directory: Path, *, max_variant_length: int = 200) -> list[TermSeedRow]:
    filename = "terms.csv"
    required = {"text_ru", "definition", "domain", "variants_kk", "source"}
    rows: list[TermSeedRow] = []
    for line_no, row in _open_csv_rows(directory, filename, required):
        text_ru = row["text_ru"]
        domain = row["domain"]
        if not text_ru:
            raise SeedFormatError(filename, line_no, "text_ru cannot be empty.")
        if len(text_ru) > 200:
            raise SeedFormatError(filename, line_no, "text_ru exceeds 200 characters.")
        if domain not in VALID_DOMAINS:
            raise SeedFormatError(filename, line_no, f"Invalid domain '{domain}'.")

        raw_variants = [
            normalize_text(item)
            for item in row["variants_kk"].split(";")
            if normalize_text(item)
        ]
        deduped_variants: list[str] = []
        for variant in raw_variants:
            if len(variant) > max_variant_length:
                raise SeedFormatError(
                    filename,
                    line_no,
                    f"Variant exceeds {max_variant_length} characters.",
                )
            if variant not in deduped_variants:
                deduped_variants.append(variant)

        rows.append(
            TermSeedRow(
                text_ru=text_ru,
                definition=row["definition"],
                domain=domain,
                variants_kk=tuple(deduped_variants),
                source=row["source"],
            )
        )
    return rows


def parse_sentences_csv(directory: Path) -> list[SentenceSeedRow]:
    filename = "sentences.csv"
    required = {"text_ru", "domain", "source_url", "licence", "attribution", "is_original"}
    rows: list[SentenceSeedRow] = []
    for line_no, row in _open_csv_rows(directory, filename, required):
        text_ru = row["text_ru"]
        domain = row["domain"]
        raw_original = row["is_original"].lower()
        if not text_ru:
            raise SeedFormatError(filename, line_no, "text_ru cannot be empty.")
        if domain not in VALID_DOMAINS:
            raise SeedFormatError(filename, line_no, f"Invalid domain '{domain}'.")
        if raw_original in TRUE_VALUES:
            is_original = True
        elif raw_original in FALSE_VALUES:
            is_original = False
        else:
            raise SeedFormatError(
                filename, line_no, f"Invalid boolean value '{row['is_original']}' for is_original."
            )

        licence = row["licence"]
        if not is_original and not licence:
            raise SeedFormatError(
                filename,
                line_no,
                "Non-original sentence must specify a licence.",
            )

        rows.append(
            SentenceSeedRow(
                text_ru=text_ru,
                domain=domain,
                source_url=row["source_url"],
                licence=licence,
                attribution=row["attribution"],
                is_original=is_original,
            )
        )
    return rows


def parse_connectors_csv(directory: Path) -> list[ConnectorSeedRow]:
    filename = "connectors.csv"
    required = {"text_ru", "text_kk", "example_kk", "example_ru", "source", "licence"}
    rows: list[ConnectorSeedRow] = []
    for line_no, row in _open_csv_rows(directory, filename, required):
        for field_name in ("text_ru", "text_kk", "example_kk", "example_ru"):
            if not row[field_name]:
                raise SeedFormatError(filename, line_no, f"{field_name} cannot be empty.")
        rows.append(
            ConnectorSeedRow(
                text_ru=row["text_ru"],
                text_kk=row["text_kk"],
                example_kk=row["example_kk"],
                example_ru=row["example_ru"],
                source=row["source"],
                licence=row["licence"],
            )
        )
    return rows
