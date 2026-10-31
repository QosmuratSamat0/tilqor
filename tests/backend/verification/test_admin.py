import pytest
from django.contrib import admin
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory

from apps.contributions.models import ContributionVersion
from apps.verification.admin_actions import resolve_escalated
from apps.verification.models import Finalization, QualitySettings
from apps.verification.services import submit_review

pytestmark = pytest.mark.django_db


def admin_request(user, payload=None):
    request = RequestFactory().post("/admin/contributions/contributionversion/", payload or {})
    request.user = user
    request.session = {}
    request._messages = FallbackStorage(request)
    return request


def test_admin_resolution_requires_reason_and_records_actor(version, reviewer_factory):
    for decision in ("accept", "reject", "edit", "accept", "reject"):
        submit_review(
            reviewer=reviewer_factory(), version_id=version.pk, decision=decision, reason="x"
        )
    moderator = reviewer_factory(role="moderator", is_staff=True, is_superuser=True)
    modeladmin = admin.site._registry[ContributionVersion]
    selected = ContributionVersion.objects.filter(pk=version.pk)
    for payload in ({}, {"apply_resolution": "1", "decision": "edit", "reason": " "}):
        response = resolve_escalated(modeladmin, admin_request(moderator, payload), selected)
        assert response.status_code == 200
        assert not Finalization.objects.exists()
    payload = {"apply_resolution": "1", "decision": "edit", "reason": "Moderator explanation"}
    assert resolve_escalated(modeladmin, admin_request(moderator, payload), selected) is None
    result = Finalization.objects.get(version=version)
    assert result.moderator == moderator and result.reason == "Moderator explanation"
    version.refresh_from_db()
    assert version.status == "needs_edit"


def test_reviewer_cannot_use_admin_override(version, reviewer_factory):
    reviewer = reviewer_factory(is_staff=True, is_superuser=True)
    request = admin_request(reviewer)
    modeladmin = admin.site._registry[ContributionVersion]
    assert not modeladmin.has_resolve_permission(request)
    with pytest.raises(PermissionDenied):
        resolve_escalated(modeladmin, request, ContributionVersion.objects.filter(pk=version.pk))


def test_only_admin_role_can_edit_settings(reviewer_factory):
    modeladmin = admin.site._registry[QualitySettings]
    for role in ("reviewer", "moderator", "admin"):
        request = admin_request(reviewer_factory(role=role, is_staff=True, is_superuser=True))
        assert modeladmin.has_change_permission(request) == (role == "admin")
        assert modeladmin.has_add_permission(request) == (role == "admin")


def test_control_creation_requires_counted_reference(version, reviewer_factory):
    user = reviewer_factory(role="moderator", is_staff=True, is_superuser=True)
    modeladmin = admin.site._registry[ContributionVersion]
    form_type = modeladmin.get_form(admin_request(user))
    form = form_type(
        data={
            "contribution": version.contribution_id,
            "number": 2,
            "text_kk": "Бақылау",
            "is_control": True,
            "reference_decision": "dont_know",
        }
    )
    assert not form.is_valid()
    assert "reference_decision" in form.errors
