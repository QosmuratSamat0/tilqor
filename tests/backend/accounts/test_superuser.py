"""A Django superuser (createsuperuser) must be able to administer Tilqor."""
import pytest
from django.contrib.admin.sites import site
from django.test import RequestFactory

from apps.accounts.models import User
from apps.verification.models import QualitySettings

pytestmark = pytest.mark.django_db


def test_createsuperuser_gets_admin_role():
    user = User.objects.create_superuser("root", "root@example.com", "Kazakh-Tilqor-2026")

    assert user.role == User.Role.ADMIN
    assert user.is_admin_role and user.is_moderator and user.is_reviewer


def test_role_not_superuser_flag_decides_tilqor_permissions(make_user):
    user = make_user(username="staff_reviewer", role=User.Role.REVIEWER, is_superuser=True)

    assert user.is_reviewer
    assert not (user.is_moderator or user.is_admin_role)


def test_createsuperuser_keeps_an_explicit_role():
    user = User.objects.create_superuser(
        "mod", "mod@example.com", "Kazakh-Tilqor-2026", role=User.Role.MODERATOR
    )

    assert user.role == User.Role.MODERATOR


def test_superuser_can_edit_quality_settings_in_admin():
    user = User.objects.create_superuser("root", "root@example.com", "Kazakh-Tilqor-2026")
    request = RequestFactory().get("/admin/")
    request.user = user

    model_admin = site._registry[QualitySettings]

    assert model_admin.has_change_permission(request)
    assert model_admin.has_add_permission(request)


def test_regular_participant_is_not_admin(make_user):
    user = make_user(username="aru")

    assert not (user.is_admin_role or user.is_moderator or user.is_reviewer)
