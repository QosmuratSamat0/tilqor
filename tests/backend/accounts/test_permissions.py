"""FR-02: role permissions are checked on the server."""
import pytest
from django.contrib.auth.models import AnonymousUser
from rest_framework.test import APIRequestFactory

from apps.accounts.models import User
from common.permissions import IsModerator, IsReviewer

pytestmark = pytest.mark.django_db

ROLES = User.Role


def has(permission_class, user):
    request = APIRequestFactory().get("/")
    request.user = user
    return permission_class().has_permission(request, view=None)


@pytest.mark.parametrize(
    ("role", "reviewer", "moderator"),
    [
        (ROLES.PARTICIPANT, False, False),
        (ROLES.REVIEWER, True, False),
        (ROLES.MODERATOR, True, True),
        (ROLES.ADMIN, True, True),
    ],
)
def test_role_permissions(make_user, role, reviewer, moderator):
    user = make_user(username=f"user_{role}", role=role)

    assert has(IsReviewer, user) is reviewer
    assert has(IsModerator, user) is moderator


def test_anonymous_user_has_no_role_permissions():
    assert has(IsReviewer, AnonymousUser()) is False
    assert has(IsModerator, AnonymousUser()) is False


def test_new_user_is_a_participant(make_user):
    assert make_user(username="newbie").role == ROLES.PARTICIPANT


def test_public_name_never_exposes_email(make_user):
    user = make_user(username="aru", display_name="")

    assert user.public_name == "aru"
    assert "@" not in user.public_name
