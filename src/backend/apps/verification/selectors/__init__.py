from decimal import Decimal

from django.db.models import Count, Exists, OuterRef

from apps.contributions.models import ContributionVersion
from apps.verification.models import QualitySettings, Review, ReviewerProfile


def review_queue(user):
    """Only unresolved independent reviews; callers expose an explicit field allowlist."""
    reviewed = Review.objects.filter(version_id=OuterRef("pk"), reviewer=user)
    return (
        ContributionVersion.objects.filter(
            status__in=["submitted", "in_review"],
            escalated=False,
            is_withdrawn=False,
            finalization__isnull=True,
        )
        .exclude(contribution__author=user)
        .annotate(already_reviewed=Exists(reviewed))
        .filter(already_reviewed=False)
        .select_related("contribution__task__source_sentence", "contribution__task__term")
        # Stable interleaving includes controls without identifying them in responses.
        .order_by("created_at", "pk")
    )


def reviewer_stats(user):
    profile = ReviewerProfile.objects.filter(user=user).first()
    if profile:
        weight = profile.weight
    else:
        settings = QualitySettings.objects.filter(is_active=True).first()
        weight = settings.weight_initial if settings else Decimal("1.00")
    counts = dict(
        Review.objects.filter(reviewer=user, matched_final__isnull=False)
        .values_list("matched_final")
        .annotate(total=Count("pk"))
    )
    matched = counts.get(True, 0)
    total = matched + counts.get(False, 0)
    return {
        "weight": weight,
        "matched_votes": matched,
        "finalized_votes": total,
        "match_share": Decimal(matched) / Decimal(total) if total else None,
    }
