from django.db import transaction
from django.utils import timezone

from apps.contributions.domain import normalize_text
from apps.contributions.selectors import eligible_versions
from apps.glossary.errors import GlossaryError, GlossaryForbidden, GlossaryNotFound
from apps.glossary.models import Term


@transaction.atomic
def recommend_term_variant(*, moderator, term_id: int, version_id: int, reason: str) -> Term:
    """Assign an eligible variant as the recommended translation for a term (FR-18)."""
    if not getattr(moderator, "is_authenticated", False) or not moderator.is_moderator:
        raise GlossaryForbidden("Moderator role is required.")

    cleaned_reason = normalize_text(reason)
    if not cleaned_reason:
        raise GlossaryError("Recommendation reason cannot be empty.", field="reason")

    term = Term.objects.select_for_update().filter(pk=term_id).first()
    if term is None:
        raise GlossaryNotFound("Term not found.")

    version = (
        eligible_versions()
        .filter(pk=version_id, contribution__task__term_id=term.pk)
        .first()
    )
    if version is None:
        raise GlossaryError(
            "Selected variant is not an eligible accepted variant for this term.",
            field="version",
        )

    term.recommended_version = version
    term.recommended_reason = cleaned_reason
    term.recommended_by = moderator
    term.recommended_at = timezone.now()
    term.save(
        update_fields=[
            "recommended_version",
            "recommended_reason",
            "recommended_by",
            "recommended_at",
        ]
    )
    return term
