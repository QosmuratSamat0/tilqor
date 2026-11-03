from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, F, Q
from django.utils import timezone

from apps.contributions.models import Task
from apps.contributions.selectors import eligible_versions
from apps.exports.domain import build_export_row, build_manifest


def _is_seed_version(version) -> bool:
    username = version.contribution.author.username
    return bool(version.source) or username == "seed" or username.startswith("seed_")


def export_records() -> list[dict]:
    """Return ordered dataset export rows for all eligible versions (FR-20, NFR-12)."""
    queryset = (
        eligible_versions()
        .select_related(
            "contribution__author",
            "contribution__task__source_sentence",
            "contribution__task__term",
            "finalization",
        )
        .annotate(
            earlier_versions=Count(
                "contribution__versions",
                filter=Q(contribution__versions__number__lt=F("number")),
            )
        )
        .order_by("pk")
    )

    rows: list[dict] = []
    for version in queryset:
        task = version.contribution.task
        if task.type == Task.Type.TRANSLATION:
            sentence = task.source_sentence
            text_ru = sentence.text_ru
            source_url = sentence.source_url
            licence = sentence.licence or settings.DATASET_LICENCE
            attribution = sentence.attribution
            is_original = sentence.is_original
            contributor = version.contribution.author.public_name
        else:
            term = task.term
            text_ru = term.text_ru
            source_url = term.source_url
            licence = version.licence or settings.DATASET_LICENCE
            attribution = version.source or term.source
            is_original = not bool(term.source or version.source)
            if _is_seed_version(version):
                contributor = version.source or term.source
            else:
                contributor = version.contribution.author.public_name

        try:
            accepted_dt = version.finalization.created_at
        except ObjectDoesNotExist:
            accepted_dt = version.created_at

        rows.append(
            build_export_row(
                version_id=version.pk,
                task_type=task.type,
                domain=task.domain,
                text_ru=text_ru,
                text_kk=version.text_kk,
                version_number=version.number,
                source_url=source_url,
                licence=licence,
                attribution=attribution,
                is_original=is_original,
                modifications=version.earlier_versions,
                contributor=contributor,
                accepted_at=accepted_dt.isoformat(),
            )
        )
    return rows


def export_manifest() -> dict:
    """Return the dataset export manifest with provenance summary (FR-20, NFR-12)."""
    records = export_records()
    return build_manifest(
        records=records,
        generated_at=timezone.now().isoformat(),
        terms_version=settings.PUBLICATION_TERMS_VERSION,
        dataset_licence=settings.DATASET_LICENCE,
    )
