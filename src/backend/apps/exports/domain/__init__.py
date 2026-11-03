import csv
import io
import json
from collections import Counter

EXPORT_COLUMNS = (
    "id",
    "type",
    "domain",
    "text_ru",
    "text_kk",
    "version",
    "source_url",
    "licence",
    "attribution",
    "is_original",
    "modifications",
    "contributor",
    "accepted_at",
)


def build_export_row(
    *,
    version_id: int,
    task_type: str,
    domain: str,
    text_ru: str,
    text_kk: str,
    version_number: int,
    source_url: str,
    licence: str,
    attribution: str,
    is_original: bool,
    modifications: int,
    contributor: str,
    accepted_at: str,
) -> dict:
    """Build a single dataset export record with all required provenance fields."""
    return {
        "id": version_id,
        "type": task_type,
        "domain": domain,
        "text_ru": text_ru,
        "text_kk": text_kk,
        "version": version_number,
        "source_url": source_url,
        "licence": licence,
        "attribution": attribution,
        "is_original": is_original,
        "modifications": modifications,
        "contributor": contributor,
        "accepted_at": accepted_at,
    }


def render_dataset_csv(records: list[dict]) -> bytes:
    """Render export records as UTF-8 CSV with BOM (NFR-01, FR-20)."""
    buffer = io.StringIO()
    buffer.write("\ufeff")
    writer = csv.DictWriter(
        buffer,
        fieldnames=EXPORT_COLUMNS,
        lineterminator="\r\n",
    )
    writer.writeheader()
    for row in records:
        writer.writerow(row)
    return buffer.getvalue().encode("utf-8")


def render_dataset_json(records: list[dict]) -> bytes:
    """Render export records as UTF-8 JSON without ASCII escaping (NFR-01, FR-20)."""
    payload = {"records": records}
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


def build_manifest(
    *,
    records: list[dict],
    generated_at: str,
    terms_version: str,
    dataset_licence: str,
) -> dict:
    """Build the dataset manifest with distinct (licence, attribution, source_url) counts."""
    counts: Counter[tuple[str, str, str]] = Counter()
    for row in records:
        key = (
            row["licence"],
            row["attribution"],
            row["source_url"],
        )
        counts[key] += 1

    conditions = [
        {
            "licence": licence,
            "attribution": attribution,
            "source_url": source_url,
            "count": count,
        }
        for (licence, attribution, source_url), count in sorted(counts.items())
    ]

    return {
        "generated_at": generated_at,
        "record_count": len(records),
        "terms_version": terms_version,
        "dataset_licence": dataset_licence,
        "conditions": conditions,
    }
