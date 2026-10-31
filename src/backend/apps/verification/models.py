from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import F, Q

from apps.verification.choices import Decision

WEIGHT_MIN = Decimal("0.50")
WEIGHT_MAX = Decimal("2.00")


class QualitySettings(models.Model):
    """A versioned set of quality-model parameters (FR-24). Only one version is active."""

    version = models.PositiveIntegerField(unique=True)
    threshold = models.DecimalField(max_digits=4, decimal_places=3, default=Decimal("0.660"))
    min_votes = models.PositiveSmallIntegerField(default=3)
    max_votes = models.PositiveSmallIntegerField(default=5)
    min_supporters = models.PositiveSmallIntegerField(default=2)
    weight_initial = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal("1.00"))
    weight_min = models.DecimalField(max_digits=3, decimal_places=2, default=WEIGHT_MIN)
    weight_max = models.DecimalField(max_digits=3, decimal_places=2, default=WEIGHT_MAX)
    match_step = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal("0.05"))
    mismatch_step = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal("0.10"))
    control_correct_step = models.DecimalField(
        max_digits=3, decimal_places=2, default=Decimal("0.05")
    )
    control_wrong_step = models.DecimalField(
        max_digits=3, decimal_places=2, default=Decimal("0.20")
    )
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "quality settings"
        constraints = [
            models.UniqueConstraint(
                fields=["is_active"], condition=Q(is_active=True), name="one_active_settings"
            ),
            models.CheckConstraint(
                condition=Q(min_votes__lte=F("max_votes")), name="min_votes_lte_max_votes"
            ),
            models.CheckConstraint(
                condition=Q(weight_min__lte=F("weight_initial"))
                & Q(weight_initial__lte=F("weight_max")),
                name="initial_weight_within_bounds",
            ),
            models.CheckConstraint(
                condition=Q(threshold__gt=0) & Q(threshold__lte=1), name="threshold_in_range"
            ),
        ]

    def __str__(self):
        return f"Quality settings v{self.version}" + (" (active)" if self.is_active else "")

    def clean(self):
        super().clean()
        errors = {}
        if not 3 <= self.min_votes <= self.max_votes <= 5:
            errors["min_votes"] = "Require 3 <= min_votes <= max_votes <= 5."
        if not 2 <= self.min_supporters <= self.min_votes:
            errors["min_supporters"] = "Require 2 <= min_supporters <= min_votes."
        if (
            not WEIGHT_MIN
            <= self.weight_min
            <= self.weight_initial
            <= self.weight_max
            <= WEIGHT_MAX
        ):
            errors["weight_initial"] = "Weights must be ordered within 0.50 to 2.00."
        if not Decimal("0.5") < self.threshold <= 1:
            errors["threshold"] = "Threshold must be greater than 0.5 and at most 1."
        for name in ("match_step", "mismatch_step", "control_correct_step", "control_wrong_step"):
            if getattr(self, name) < 0:
                errors[name] = "Steps cannot be negative."
        if errors:
            raise ValidationError(errors)
        self._check_immutable()

    def _check_immutable(self):
        if not self.pk or not self.reviews.exists():
            return
        previous = type(self).objects.get(pk=self.pk)
        for field in self._meta.concrete_fields:
            if field.name not in {"is_active", "created_at"} and (
                getattr(previous, field.attname) != getattr(self, field.attname)
            ):
                raise ValidationError("Used settings are immutable. Create a new settings version.")

    @transaction.atomic
    def save(self, *args, **kwargs):
        if self.pk:
            # Synchronize admin edits with the first review pinning this row.
            type(self).objects.select_for_update().filter(pk=self.pk).first()
        self._check_immutable()
        return super().save(*args, **kwargs)


class ReviewerProfile(models.Model):
    """A reviewer's current weight (reputation)."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviewer_profile"
    )
    weight = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal("1.00"))
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(weight__gte=WEIGHT_MIN) & Q(weight__lte=WEIGHT_MAX),
                name="weight_within_bounds",
            ),
        ]

    def __str__(self):
        return f"{self.user} ({self.weight})"


class Review(models.Model):
    """One reviewer's decision on one content version, with the weight used at that time."""

    version = models.ForeignKey(
        "contributions.ContributionVersion", on_delete=models.PROTECT, related_name="reviews"
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="reviews"
    )
    decision = models.CharField(max_length=20, choices=Decision.choices)
    reason = models.TextField(blank=True)
    weight_snapshot = models.DecimalField(max_digits=3, decimal_places=2)
    quality_settings = models.ForeignKey(
        QualitySettings, on_delete=models.PROTECT, related_name="reviews"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # Audit markers make standard finalization and immediate control feedback idempotent.
    reputation_applied_at = models.DateTimeField(null=True, blank=True)
    matched_final = models.BooleanField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["version", "reviewer"], name="one_review_per_reviewer_per_version"
            ),
            models.CheckConstraint(
                condition=~Q(decision__in=["reject", "edit"]) | ~Q(reason=""),
                name="reason_required_for_reject_and_edit",
            ),
        ]

    def __str__(self):
        return f"{self.reviewer} → {self.decision} on {self.version}"


class Finalization(models.Model):
    """One durable result per immutable version, including moderator overrides."""

    version = models.OneToOneField(
        "contributions.ContributionVersion",
        on_delete=models.PROTECT,
        related_name="finalization",
    )
    decision = models.CharField(
        max_length=20, choices=[(d, d.label) for d in Decision if d != Decision.DONT_KNOW]
    )
    quality_settings = models.ForeignKey(QualitySettings, on_delete=models.PROTECT)
    moderator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
