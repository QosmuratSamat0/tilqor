from django.db import models

from common.choices import Domain


class Term(models.Model):
    """A Russian term whose Kazakh variants are proposed and verified by users."""

    text_ru = models.CharField(max_length=200)
    definition = models.TextField(blank=True)
    domain = models.CharField(max_length=20, choices=Domain.choices)
    # Chosen by a moderator among accepted variants (FR-18).
    recommended_version = models.ForeignKey(
        "contributions.ContributionVersion",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="recommended_for",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["text_ru", "domain"], name="unique_term_per_domain"),
        ]
        ordering = ["text_ru"]

    def __str__(self):
        return self.text_ru
