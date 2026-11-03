from collections import defaultdict

from django.db.models import Count, Exists, OuterRef
from django.utils import timezone

from apps.contributions.models import ContributionVersion, Task
from apps.contributions.selectors import eligible_versions
from apps.glossary.domain import parse_iso_date, term_matches_query, word_of_the_day_index
from apps.glossary.errors import GlossaryError
from apps.glossary.models import ConnectorHint, Term
from common.choices import Domain


def _serialize_variant(version: ContributionVersion) -> dict:
    return {
        "id": version.pk,
        "text_kk": version.text_kk,
        "public_name": version.contribution.author.public_name,
    }


def _build_term_payload(term: Term, eligible_list: list[ContributionVersion]) -> dict:
    eligible_by_id = {v.pk: v for v in eligible_list}
    rec_version = eligible_by_id.get(term.recommended_version_id)
    if rec_version is not None:
        recommended = {
            **_serialize_variant(rec_version),
            "reason": term.recommended_reason,
        }
        alternatives = [
            _serialize_variant(v) for v in eligible_list if v.pk != rec_version.pk
        ]
    else:
        recommended = None
        alternatives = [_serialize_variant(v) for v in eligible_list]

    return {
        "id": term.pk,
        "text_ru": term.text_ru,
        "definition": term.definition,
        "domain": term.domain,
        "source": term.source,
        "recommended": recommended,
        "alternatives": alternatives,
    }


def _eligible_terms_with_variants(*, domain: str | None = None):
    has_eligible = Exists(
        eligible_versions().filter(contribution__task__term_id=OuterRef("pk"))
    )
    queryset = Term.objects.annotate(has_eligible=has_eligible).filter(has_eligible=True)
    if domain:
        if domain not in Domain.values:
            raise GlossaryError("Invalid domain filter.", field="domain")
        queryset = queryset.filter(domain=domain)
    terms = list(queryset.order_by("pk"))
    variants_by_term: dict[int, list[ContributionVersion]] = defaultdict(list)
    if terms:
        versions = (
            eligible_versions()
            .filter(contribution__task__term__in=terms)
            .select_related("contribution__author")
            .order_by("pk")
        )
        for version in versions:
            variants_by_term[version.contribution.task.term_id].append(version)
    return terms, variants_by_term


def dictionary_terms(*, q: str | None = None, domain: str | None = None) -> list[dict]:
    """Return dictionary term payloads that have at least one eligible variant (FR-17)."""
    terms, variants_by_term = _eligible_terms_with_variants(domain=domain)
    results: list[dict] = []
    for term in terms:
        term_variants = variants_by_term.get(term.pk, [])
        if not term_variants:
            continue
        if not term_matches_query(
            query=q,
            text_ru=term.text_ru,
            eligible_texts_kk=[v.text_kk for v in term_variants],
        ):
            continue
        results.append(_build_term_payload(term, term_variants))
    return results


def dictionary_term_detail(*, term_id: int, include_pending: bool = False) -> dict | None:
    """Return a single dictionary entry with recommended, alternatives, and optional pending."""
    term = Term.objects.filter(pk=term_id).first()
    if term is None:
        return None
    eligible_list = list(
        eligible_versions()
        .filter(contribution__task__term_id=term.pk)
        .select_related("contribution__author")
        .order_by("pk")
    )
    payload = _build_term_payload(term, eligible_list)
    if include_pending:
        pending_qs = (
            ContributionVersion.objects.filter(
                contribution__task__term_id=term.pk,
                is_control=False,
                is_withdrawn=False,
                status__in=[
                    ContributionVersion.Status.SUBMITTED,
                    ContributionVersion.Status.IN_REVIEW,
                ],
            )
            .select_related("contribution__author")
            .order_by("pk")
        )
        payload["pending"] = [
            {
                **_serialize_variant(v),
                "status": v.status,
            }
            for v in pending_qs
        ]
    return payload


def daily_catalogue(*, raw_date: str | None = None) -> dict:
    """Return word of the day, top words and published connector hints for `raw_date` (FR-19)."""
    if raw_date is None or raw_date == "":
        iso_date = timezone.localdate().isoformat()
    else:
        try:
            iso_date = parse_iso_date(raw_date)
        except ValueError as exc:
            raise GlossaryError(
                "Invalid date format. Expected YYYY-MM-DD.",
                field="date",
            ) from exc

    terms, variants_by_term = _eligible_terms_with_variants()
    word_of_the_day = None
    idx = word_of_the_day_index(iso_date, len(terms))
    if idx is not None:
        chosen_term = terms[idx]
        chosen_variants = variants_by_term[chosen_term.pk]
        by_id = {v.pk: v for v in chosen_variants}
        chosen_v = by_id.get(chosen_term.recommended_version_id) or chosen_variants[0]
        word_of_the_day = {
            "id": chosen_term.pk,
            "term_id": chosen_term.pk,
            "text_ru": chosen_term.text_ru,
            "definition": chosen_term.definition,
            "domain": chosen_term.domain,
            "text_kk": chosen_v.text_kk,
            "public_name": chosen_v.contribution.author.public_name,
            "variant": _serialize_variant(chosen_v),
        }

    top_versions = (
        eligible_versions()
        .filter(contribution__task__type=Task.Type.TERM)
        .select_related("contribution__author", "contribution__task__term")
        .annotate(preference_count=Count("variantpreference"))
        .order_by("-preference_count", "pk")[:10]
    )
    top_words = [
        {
            "id": v.pk,
            "term_id": v.contribution.task.term_id,
            "text_ru": v.contribution.task.term.text_ru,
            "domain": v.contribution.task.term.domain,
            "text_kk": v.text_kk,
            "public_name": v.contribution.author.public_name,
            "preference_count": v.preference_count,
        }
        for v in top_versions
    ]

    connector_hints = [
        {
            "id": hint.pk,
            "text_ru": hint.text_ru,
            "text_kk": hint.text_kk,
            "example_kk": hint.example_kk,
            "example_ru": hint.example_ru,
            "source": hint.source,
            "licence": hint.licence,
        }
        for hint in ConnectorHint.objects.filter(is_published=True).order_by("pk")
    ]

    return {
        "date": iso_date,
        "word_of_the_day": word_of_the_day,
        "top_words": top_words,
        "connector_hints": connector_hints,
    }
