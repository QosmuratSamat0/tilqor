from decimal import Decimal

from django.conf import settings
from django.db import models
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
