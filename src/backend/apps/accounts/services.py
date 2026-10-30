from django.contrib.auth.password_validation import validate_password
from django.db import transaction

from apps.accounts.models import User


@transaction.atomic
def register_user(*, username, email, password, display_name=""):
    """Create a participant account. Raises django ValidationError for a weak password."""
    user = User(username=username, email=email, display_name=display_name)
    validate_password(password, user=user)
    user.set_password(password)
    user.save()
    return user
