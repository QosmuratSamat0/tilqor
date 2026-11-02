from dataclasses import dataclass

from django.conf import settings
from django.db import transaction

from apps.contributions.domain import check_text
from apps.contributions.errors import (
    ContributionConflict,
    ContributionError,
    ContributionForbidden,
)
from apps.contributions.models import Contribution, ContributionVersion, Task, VariantPreference


@dataclass(frozen=True)
class SubmissionResult:
    contribution: Contribution
    version: ContributionVersion
    warnings: dict[str, list[str]]


def _locked_task(task_id: int) -> Task:
    try:
        return Task.objects.select_for_update().get(pk=task_id)
    except Task.DoesNotExist as exc:
        raise ContributionError("Unknown task.", field="task") from exc


def _max_length_for_task(task: Task) -> int:
    if task.type == Task.Type.TRANSLATION:
        return settings.CONTRIBUTION_MAX_LENGTH_TRANSLATION
    return settings.CONTRIBUTION_MAX_LENGTH_TERM


def _validate_task_text(task: Task, text_kk: str) -> tuple[str, dict[str, list[str]]]:
    existing_texts = list(
        ContributionVersion.objects.filter(contribution__task=task).values_list(
            "text_kk", flat=True
        )
    )
    checked = check_text(
        text_kk,
        max_length=_max_length_for_task(task),
        existing_texts=existing_texts,
        russian_connectors=settings.RUSSIAN_CONNECTORS,
    )
    if checked.errors:
        raise ContributionError(checked.errors[0], field="text_kk")
    warnings = {"text_kk": list(checked.warnings)} if checked.warnings else {}
    return checked.text, warnings


@transaction.atomic
def submit_contribution(*, author, task_id: int, text_kk: str) -> SubmissionResult:
    """Create a user's initial contribution and version 1 for an active task (FR-04, FR-05)."""
    task = _locked_task(task_id)
    if not task.is_active:
        raise ContributionConflict("Task is not active.", field="task")
    if Contribution.objects.filter(task=task, author=author).exists():
        raise ContributionConflict(
            "You have already submitted a contribution to this task.", field="task"
        )
    normalized_text, warnings = _validate_task_text(task, text_kk)
    contribution = Contribution.objects.create(task=task, author=author)
    version = ContributionVersion.objects.create(
        contribution=contribution,
        number=1,
        text_kk=normalized_text,
        status=ContributionVersion.Status.SUBMITTED,
    )
    return SubmissionResult(contribution=contribution, version=version, warnings=warnings)


@transaction.atomic
def submit_version(*, author, contribution_id: int, text_kk: str) -> SubmissionResult:
    """Create the next immutable version when the latest version has status=needs_edit (FR-13)."""
    try:
        contribution = (
            Contribution.objects.select_for_update(of=("self", "task"))
            .select_related("task")
            .get(pk=contribution_id)
        )
    except Contribution.DoesNotExist as exc:
        raise ContributionError("Unknown contribution.", field="contribution") from exc
    if contribution.author_id != author.pk:
        raise ContributionForbidden("Only the author may submit a new version.", field="author")
    if not contribution.task.is_active:
        raise ContributionConflict("Task is not active.", field="task")
    latest = contribution.versions.select_for_update().order_by("-number").first()
    if latest is None or latest.status != ContributionVersion.Status.NEEDS_EDIT:
        raise ContributionConflict(
            "A new version requires the latest version to have status needs_edit.",
            field="status",
        )
    normalized_text, warnings = _validate_task_text(contribution.task, text_kk)
    version = ContributionVersion.objects.create(
        contribution=contribution,
        number=latest.number + 1,
        text_kk=normalized_text,
        status=ContributionVersion.Status.SUBMITTED,
    )
    return SubmissionResult(contribution=contribution, version=version, warnings=warnings)


@transaction.atomic
def set_preference(*, user, task_id: int, version_id: int) -> VariantPreference:
    """Create or replace a user's single active variant preference on a term task (FR-05)."""
    task = _locked_task(task_id)
    if not task.is_active:
        raise ContributionConflict("Task is not active.", field="task")
    if task.type != Task.Type.TERM:
        raise ContributionError("Preferences can only be set on term tasks.", field="task")
    version = (
        ContributionVersion.objects.select_related("contribution")
        .filter(
            pk=version_id,
            contribution__task=task,
            is_control=False,
            is_withdrawn=False,
        )
        .exclude(status=ContributionVersion.Status.REJECTED)
        .first()
    )
    if version is None:
        raise ContributionError(
            "Version must belong to this task and be a listed variant.",
            field="version_id",
        )
    preference, _ = VariantPreference.objects.update_or_create(
        user=user,
        task=task,
        defaults={"version": version},
    )
    return preference
