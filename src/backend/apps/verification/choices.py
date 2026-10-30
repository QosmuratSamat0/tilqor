from django.db import models


class Decision(models.TextChoices):
    """A reviewer's decision on one content version (FR-10)."""

    ACCEPT = "accept", "Accept"
    REJECT = "reject", "Reject"
    EDIT = "edit", "Needs edit"
    DONT_KNOW = "dont_know", "Don't know"


COUNTED_DECISIONS = (Decision.ACCEPT, Decision.REJECT, Decision.EDIT)
DECISIONS_REQUIRING_REASON = (Decision.REJECT, Decision.EDIT)
