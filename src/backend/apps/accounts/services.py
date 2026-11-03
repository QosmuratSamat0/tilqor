from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User


@transaction.atomic
def register_user(*, username, email, password, display_name="", accept_terms=True):
    """Create a participant account with recorded publication-terms acceptance (FR-01, FR-06)."""
    now = timezone.now() if accept_terms else None
    version = settings.PUBLICATION_TERMS_VERSION if accept_terms else ""
    user = User(
        username=username,
        email=email,
        display_name=display_name,
        accepted_terms_at=now,
        accepted_terms_version=version,
    )
    validate_password(password, user=user)
    user.set_password(password)
    user.save()
    return user


@transaction.atomic
def accept_publication_terms(*, user: User) -> User:
    """Record acceptance of the current publication terms idempotently (FR-06)."""
    locked = User.objects.select_for_update().get(pk=user.pk)
    if (
        locked.accepted_terms_at is None
        or locked.accepted_terms_version != settings.PUBLICATION_TERMS_VERSION
    ):
        locked.accepted_terms_at = timezone.now()
        locked.accepted_terms_version = settings.PUBLICATION_TERMS_VERSION
        locked.save(update_fields=["accepted_terms_at", "accepted_terms_version"])
    return locked
