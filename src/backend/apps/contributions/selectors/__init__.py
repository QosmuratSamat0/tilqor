from random import Random

from django.conf import settings
from django.db.models import Prefetch

from apps.contributions.domain import shuffle_variants
from apps.contributions.models import Contribution, ContributionVersion, Task
from apps.contributions.services.errors import ContributionError
from common.choices import Domain


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
    return queryset.order_by("pk")[: settings.TASK_LIST_PAGE_SIZE]


def visible_variants(
    *, task: Task, user, rng: Random | None = None
) -> list[ContributionVersion]:
    """Return variants visible to `user` for `task` (FR-04 blind flow, FR-05 shuffled terms)."""
    base = (
        ContributionVersion.objects.filter(
            contribution__task=task,
            is_control=False,
            is_withdrawn=False,
        )
        .exclude(status=ContributionVersion.Status.REJECTED)
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
    version_qs = ContributionVersion.objects.select_related("finalization").order_by("number")
    return (
        Contribution.objects.filter(author=user)
        .select_related("task__source_sentence", "task__term")
        .prefetch_related(Prefetch("versions", queryset=version_qs))
        .order_by("created_at", "pk")
    )
