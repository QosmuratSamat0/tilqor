from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User


def is_reserved_username(username: str) -> bool:
    """Return True for reserved system seed usernames (`seed` and `seed_*`)."""
    lowered = username.strip().lower()
    return lowered == "seed" or lowered.startswith("seed_")


@transaction.atomic
def register_user(
    *,
    username: str,
    email: str,
    password: str,
    accept_terms: bool,
    display_name: str = "",
) -> User:
    """Create a participant account with recorded publication-terms acceptance (FR-01, FR-06)."""
    if is_reserved_username(username):
        raise ValidationError({"username": ["This username is reserved."]})
    if not accept_terms:
        raise ValidationError(
            {"accept_terms": ["You must accept the publication terms to register."]}
        )
    user = User(
        username=username,
        email=email,
        display_name=display_name,
        accepted_terms_at=timezone.now(),
        accepted_terms_version=settings.PUBLICATION_TERMS_VERSION,
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
