import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User

PASSWORD = "Kazakh-Tilqor-2026"


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def make_user(db):
    def _make_user(username="aru", role=User.Role.PARTICIPANT, **extra):
        user = User(username=username, email=f"{username}@example.com", role=role, **extra)
        user.set_password(PASSWORD)
        user.save()
        return user

    return _make_user
