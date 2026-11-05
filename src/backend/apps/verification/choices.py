from django.db import models


class Decision(models.TextChoices):
    """A reviewer's decision on one content version (FR-10)."""

    ACCEPT = "accept", "Accept"
    REJECT = "reject", "Reject"
    EDIT = "edit", "Needs edit"
    DONT_KNOW = "dont_know", "Don't know"


COUNTED_DECISIONS = (Decision.ACCEPT, Decision.REJECT, Decision.EDIT)
DECISIONS_REQUIRING_REASON = (Decision.REJECT, Decision.EDIT)


class ReviewReason(models.TextChoices):
    WRONG_TERM = "wrong_term", "Wrong term"
    RUSSIAN_CONNECTOR = "russian_connector", "Russian connector"
    GRAMMAR = "grammar", "Grammar"
    OTHER = "other", "Other"
