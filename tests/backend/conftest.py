import pytest
from django.conf import settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import User

PASSWORD = "Kazakh-Tilqor-2026"


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def make_user(db):
    def _make_user(username="aru", role=User.Role.PARTICIPANT, accepted_terms=True, **extra):
        if accepted_terms:
            extra.setdefault("accepted_terms_at", timezone.now())
            extra.setdefault("accepted_terms_version", settings.PUBLICATION_TERMS_VERSION)
        user = User(username=username, email=f"{username}@example.com", role=role, **extra)
        user.set_password(PASSWORD)
        user.save()
        return user

    return _make_user
