from django.conf import settings
from django.db import models

from common.choices import Domain


class Term(models.Model):
    """A Russian term whose Kazakh variants are proposed and verified by users."""

    text_ru = models.CharField(max_length=200)
    definition = models.TextField(blank=True)
    domain = models.CharField(max_length=20, choices=Domain.choices)
    source = models.CharField(max_length=255, blank=True)
    # Chosen by a moderator among accepted variants (FR-18).
    recommended_version = models.ForeignKey(
        "contributions.ContributionVersion",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="recommended_for",
    )
    recommended_reason = models.TextField(blank=True)
    recommended_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="recommended_terms",
    )
    recommended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["text_ru", "domain"], name="unique_term_per_domain"),
        ]
        ordering = ["text_ru"]

    def __str__(self):
        return self.text_ru


class ConnectorHint(models.Model):
    """A Russian connector with a Kazakh equivalent and sentence pair (FR-19)."""

    text_ru = models.CharField(max_length=255)
    text_kk = models.CharField(max_length=255)
    example_kk = models.TextField()
    example_ru = models.TextField()
    source = models.CharField(max_length=255, blank=True)
    licence = models.CharField(max_length=100, blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["text_ru", "text_kk"],
                name="unique_connector_hint",
            ),
        ]
        ordering = ["pk"]

    def __str__(self):
        return f"{self.text_ru} → {self.text_kk}"
