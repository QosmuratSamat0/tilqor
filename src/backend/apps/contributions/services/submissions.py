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
from apps.contributions.selectors import listed_task_variants


@dataclass(frozen=True)
class SubmissionResult:
    contribution: Contribution
    version: ContributionVersion
    warnings: dict[str, list[dict]]


def _require_accepted_terms(user) -> None:
    if not getattr(user, "accepted_terms", False):
        raise ContributionForbidden(
            "You must accept the publication terms before submitting content.",
            field="accept_terms",
            code="terms_not_accepted",
        )


def _locked_task(task_id: int) -> Task:
    try:
        return Task.objects.select_for_update().get(pk=task_id)
    except Task.DoesNotExist as exc:
        raise ContributionError("Unknown task.", field="task", code="not_found") from exc


def _max_length_for_task(task: Task) -> int:
    if task.type == Task.Type.TRANSLATION:
        return settings.CONTRIBUTION_MAX_LENGTH_TRANSLATION
    return settings.CONTRIBUTION_MAX_LENGTH_TERM


FEEDBACK_MESSAGES = {
    "empty_text": "Text cannot be empty.",
    "text_too_long": "Text cannot exceed {max_length} characters.",
    "duplicate_variant": "This variant already exists for this task.",
    "no_kazakh_letters": "Text contains no Kazakh-specific letters (ә, ғ, қ, ң, ө, ұ, ү, һ, і).",
    "russian_connectors": "Text contains Russian connector(s): {connectors}.",
}


def _message(code, params):
    values = {
        key: ", ".join(value) if isinstance(value, list) else value for key, value in params.items()
    }
    return FEEDBACK_MESSAGES[code].format(**values)


def _validate_task_text(task: Task, text_kk: str) -> tuple[str, dict[str, list[dict]]]:
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
        code, params = checked.errors[0]
        raise ContributionError(_message(code, params), field="text_kk", code=code, params=params)
    warnings = (
        {
            "text_kk": [
                {"code": code, "params": params, "message": _message(code, params)}
                for code, params in checked.warnings
            ]
        }
        if checked.warnings
        else {}
    )
    return checked.text, warnings


@transaction.atomic
def submit_contribution(*, author, task_id: int, text_kk: str) -> SubmissionResult:
    """Create a user's initial contribution and version 1 for an active task (FR-04, FR-05)."""
    _require_accepted_terms(author)
    task = _locked_task(task_id)
    if not task.is_active:
        raise ContributionConflict("Task is not active.", field="task", code="task_inactive")
    if Contribution.objects.filter(task=task, author=author).exists():
        raise ContributionConflict(
            "You have already submitted a contribution to this task.",
            field="task",
            code="already_submitted",
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
        raise ContributionError(
            "Unknown contribution.", field="contribution", code="not_found"
        ) from exc
    if contribution.author_id != author.pk:
        raise ContributionForbidden(
            "Only the author may submit a new version.", field="author", code="author_required"
        )
    _require_accepted_terms(author)
    if not contribution.task.is_active:
        raise ContributionConflict("Task is not active.", field="task", code="task_inactive")
    latest = contribution.versions.select_for_update().order_by("-number").first()
    if latest is None or latest.status != ContributionVersion.Status.NEEDS_EDIT:
        raise ContributionConflict(
            "A new version requires the latest version to have status needs_edit.",
            field="status",
            code="version_not_editable",
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
        raise ContributionConflict("Task is not active.", field="task", code="task_inactive")
    if task.type != Task.Type.TERM:
        raise ContributionError(
            "Preferences can only be set on term tasks.", field="task", code="term_task_required"
        )
    version = listed_task_variants(task).filter(pk=version_id).first()
    if version is None:
        raise ContributionError(
            "Version must belong to this task and be a listed variant.",
            field="version_id",
            code="invalid_variant",
        )
    preference, _ = VariantPreference.objects.update_or_create(
        user=user,
        task=task,
        defaults={"version": version},
    )
    return preference
