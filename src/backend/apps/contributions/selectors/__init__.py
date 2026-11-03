from random import Random

from django.db.models import Exists, OuterRef, Prefetch, Q

from apps.contributions.domain import shuffle_variants
from apps.contributions.errors import ContributionError
from apps.contributions.models import Contribution, ContributionVersion, Task
from apps.verification.models import Review
from common.choices import Domain


def eligible_versions():
    """Return accepted, non-withdrawn, non-control versions with valid terms and source licence."""
    translation_eligible = Q(contribution__task__type=Task.Type.TRANSLATION) & (
        Q(contribution__task__source_sentence__is_original=True)
        | ~Q(contribution__task__source_sentence__licence="")
    )
    term_source_eligible = (
        Q(contribution__task__term__source="")
        | ~Q(contribution__task__term__licence="")
    )
    is_seed_variant = (
        ~Q(source="")
        | Q(contribution__author__username="seed")
        | Q(contribution__author__username__startswith="seed_")
    )
    term_variant_eligible = ~is_seed_variant | ~Q(licence="")
    term_eligible = (
        Q(contribution__task__type=Task.Type.TERM)
        & term_source_eligible
        & term_variant_eligible
    )
    return (
        ContributionVersion.objects.filter(
            status=ContributionVersion.Status.ACCEPTED,
            is_withdrawn=False,
            is_control=False,
            contribution__author__accepted_terms_at__isnull=False,
        )
        .exclude(contribution__author__accepted_terms_version="")
        .filter(translation_eligible | term_eligible)
    )


def active_tasks(*, domain: str | None = None, task_type: str | None = None):
    """Return active tasks filtered by optional domain and type (FR-03)."""
    queryset = Task.objects.filter(is_active=True).select_related("source_sentence", "term")
    if domain is not None:
        if domain not in Domain.values:
            raise ContributionError("Invalid domain filter.", field="domain")
        queryset = queryset.filter(domain=domain)
    if task_type is not None:
        if task_type not in Task.Type.values:
            raise ContributionError("Invalid task type filter.", field="type")
        queryset = queryset.filter(type=task_type)
    return queryset.order_by("pk")


def listed_task_variants(task: Task):
    """Return the latest version per contribution on `task` that is eligible to be listed."""
    newer_version = ContributionVersion.objects.filter(
        contribution_id=OuterRef("contribution_id"),
        number__gt=OuterRef("number"),
    )
    return (
        ContributionVersion.objects.filter(
            contribution__task=task,
            is_control=False,
            is_withdrawn=False,
        )
        .annotate(has_newer=Exists(newer_version))
        .filter(has_newer=False)
        .exclude(status=ContributionVersion.Status.REJECTED)
    )


def visible_variants(
    *, task: Task, user, rng: Random | None = None
) -> list[ContributionVersion]:
    """Return variants visible to `user` for `task` (FR-04 blind flow, FR-05 shuffled terms)."""
    base = (
        listed_task_variants(task)
        .select_related("contribution__author")
        .order_by("created_at", "pk")
    )
    if task.type == Task.Type.TRANSLATION:
        if not Contribution.objects.filter(task=task, author=user).exists():
            return []
        return list(base.exclude(contribution__author=user))
    return shuffle_variants(list(base), rng or Random())


def task_detail(*, task_id: int, user, rng: Random | None = None) -> Task | None:
    """Return an active task with `visible_variants` attached, or None if unavailable."""
    task = (
        Task.objects.filter(pk=task_id, is_active=True)
        .select_related("source_sentence", "term")
        .first()
    )
    if task is None:
        return None
    task.visible_variants = visible_variants(task=task, user=user, rng=rng)
    return task


def own_contributions(user):
    """Return all contributions authored by `user` with their version history (FR-08, FR-13)."""
    review_qs = Review.objects.order_by("created_at", "pk")
    version_qs = (
        ContributionVersion.objects.select_related("finalization")
        .prefetch_related(Prefetch("reviews", queryset=review_qs))
        .order_by("number")
    )
    return (
        Contribution.objects.filter(author=user)
        .select_related("task__source_sentence", "task__term")
        .prefetch_related(Prefetch("versions", queryset=version_qs))
        .order_by("created_at", "pk")
    )
