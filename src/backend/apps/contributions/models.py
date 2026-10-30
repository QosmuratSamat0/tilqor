from django.conf import settings
from django.db import models
from django.db.models import Q

from apps.verification.choices import Decision
from common.choices import Domain


class SourceSentence(models.Model):
    """A Russian source sentence with its provenance (FR-06)."""

    text_ru = models.TextField()
    domain = models.CharField(max_length=20, choices=Domain.choices)
    is_original = models.BooleanField(
        default=False, help_text="Written by the team; no external licence needed."
    )
    source_url = models.URLField(blank=True)
    licence = models.CharField(max_length=100, blank=True)
    attribution = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(is_original=True) | ~Q(licence=""),
                name="source_sentence_original_or_licensed",
            ),
        ]

    def __str__(self):
        return self.text_ru[:60]


class Task(models.Model):
    """A micro-task: translate a sentence or choose / suggest a term variant."""

    class Type(models.TextChoices):
        TRANSLATION = "translation", "Translate a sentence ru → kk"
        TERM = "term", "Choose or suggest a term variant"

    type = models.CharField(max_length=20, choices=Type.choices)
    domain = models.CharField(max_length=20, choices=Domain.choices)
    source_sentence = models.ForeignKey(
        SourceSentence, null=True, blank=True, on_delete=models.PROTECT, related_name="tasks"
    )
    term = models.ForeignKey(
        "glossary.Term", null=True, blank=True, on_delete=models.PROTECT, related_name="tasks"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(type="translation", source_sentence__isnull=False, term__isnull=True)
                    | Q(type="term", term__isnull=False, source_sentence__isnull=True)
                ),
                name="task_target_matches_type",
            ),
        ]

    def __str__(self):
        return f"{self.get_type_display()} #{self.pk}"


class Contribution(models.Model):
    """One author's answer to one task; edits create new versions (FR-13)."""

    task = models.ForeignKey(Task, on_delete=models.PROTECT, related_name="contributions")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="contributions"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["task", "author"], name="one_contribution_per_task"),
        ]

    def __str__(self):
        return f"Contribution #{self.pk} to task #{self.task_id}"


class ContributionVersion(models.Model):
    """An immutable version of a contribution that is reviewed (FR-13)."""

    class Status(models.TextChoices):
        SUBMITTED = "submitted", "Submitted"
        IN_REVIEW = "in_review", "In review"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"
        NEEDS_EDIT = "needs_edit", "Needs edit"

    contribution = models.ForeignKey(
        Contribution, on_delete=models.PROTECT, related_name="versions"
    )
    number = models.PositiveIntegerField()
    text_kk = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUBMITTED)
    # Escalation flag on in_review versions; not a separate status (requirements, section 4).
    escalated = models.BooleanField(default=False)
    # Publication eligibility; withdrawal keeps the decision and history (FR-21).
    is_withdrawn = models.BooleanField(default=False)
    # Control items have a known reference decision (FR-15).
    is_control = models.BooleanField(default=False)
    reference_decision = models.CharField(max_length=20, choices=Decision.choices, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["contribution", "number"], name="unique_version_number"
            ),
            models.CheckConstraint(
                condition=Q(is_control=False) | ~Q(reference_decision=""),
                name="control_version_has_reference_decision",
            ),
        ]
        ordering = ["contribution", "number"]

    def __str__(self):
        return f"v{self.number} of contribution #{self.contribution_id}"


class VariantPreference(models.Model):
    """A participant's single active choice among the variants of a term task (FR-05)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="variant_preferences"
    )
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="preferences")
    version = models.ForeignKey(ContributionVersion, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "task"], name="one_preference_per_task"),
        ]
