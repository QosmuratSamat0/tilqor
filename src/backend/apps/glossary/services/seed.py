from pathlib import Path

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.contributions.models import Contribution, ContributionVersion, SourceSentence, Task
from apps.glossary.domain.seed import (
    parse_connectors_csv,
    parse_sentences_csv,
    parse_terms_csv,
)
from apps.glossary.models import ConnectorHint, Term


def _get_seed_user(index: int = 0) -> User:
    username = "seed" if index == 0 else f"seed_{index + 1}"
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            "email": f"{username}@tilqor.internal",
            "display_name": "seed",
            "role": User.Role.PARTICIPANT,
            "accepted_terms_at": timezone.now(),
            "accepted_terms_version": settings.PUBLICATION_TERMS_VERSION,
        },
    )
    updated_fields: list[str] = []
    if created or user.has_usable_password():
        user.set_unusable_password()
        updated_fields.append("password")
    if not user.accepted_terms:
        user.accepted_terms_at = timezone.now()
        user.accepted_terms_version = settings.PUBLICATION_TERMS_VERSION
        updated_fields.extend(["accepted_terms_at", "accepted_terms_version"])
    if updated_fields:
        user.save(update_fields=updated_fields)
    return user


@transaction.atomic
def load_seed_directory(seed_dir: Path) -> dict[str, int]:
    """Load terms.csv, sentences.csv and connectors.csv idempotently in one transaction."""
    term_rows = parse_terms_csv(
        seed_dir,
        max_variant_length=settings.CONTRIBUTION_MAX_LENGTH_TERM,
    )
    sentence_rows = parse_sentences_csv(seed_dir)
    connector_rows = parse_connectors_csv(seed_dir)

    created_counts = {
        "terms": 0,
        "term_variants": 0,
        "sentences": 0,
        "connectors": 0,
    }

    _get_seed_user(0)

    for row in term_rows:
        term, term_created = Term.objects.get_or_create(
            text_ru=row.text_ru,
            domain=row.domain,
            defaults={
                "definition": row.definition,
                "source": row.source,
                "licence": row.licence,
                "source_url": row.source_url,
            },
        )
        if term_created:
            created_counts["terms"] += 1

        task, _ = Task.objects.get_or_create(
            type=Task.Type.TERM,
            term=term,
            defaults={
                "domain": row.domain,
                "is_active": True,
            },
        )

        existing_texts = set(
            ContributionVersion.objects.filter(contribution__task=task).values_list(
                "text_kk", flat=True
            )
        )
        for idx, variant_text in enumerate(row.variants_kk):
            if variant_text in existing_texts:
                continue
            seed_user = _get_seed_user(idx)
            while Contribution.objects.filter(task=task, author=seed_user).exists():
                idx += 1
                seed_user = _get_seed_user(idx)
            contribution = Contribution.objects.create(task=task, author=seed_user)
            ContributionVersion.objects.create(
                contribution=contribution,
                number=1,
                text_kk=variant_text,
                status=ContributionVersion.Status.SUBMITTED,
                source=row.source,
                licence=row.licence,
            )
            existing_texts.add(variant_text)
            created_counts["term_variants"] += 1

    for row in sentence_rows:
        sentence, sentence_created = SourceSentence.objects.get_or_create(
            text_ru=row.text_ru,
            domain=row.domain,
            defaults={
                "source_url": row.source_url,
                "licence": row.licence,
                "attribution": row.attribution,
                "is_original": row.is_original,
            },
        )
        if sentence_created:
            created_counts["sentences"] += 1
        Task.objects.get_or_create(
            type=Task.Type.TRANSLATION,
            source_sentence=sentence,
            defaults={
                "domain": row.domain,
                "is_active": True,
            },
        )

    for row in connector_rows:
        _, connector_created = ConnectorHint.objects.get_or_create(
            text_ru=row.text_ru,
            text_kk=row.text_kk,
            defaults={
                "example_kk": row.example_kk,
                "example_ru": row.example_ru,
                "source": row.source,
                "licence": row.licence,
                "is_published": False,
            },
        )
        if connector_created:
            created_counts["connectors"] += 1

    return created_counts
