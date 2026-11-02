from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from apps.contributions.models import Contribution, ContributionVersion, Task
from apps.glossary.models import Term
from apps.verification.models import QualitySettings, Review, ReviewerProfile
from apps.verification.services import submit_review

pytestmark = pytest.mark.django_db
ROOT = "/api/reviews/"


@pytest.mark.parametrize("role", [None, "participant"])
def test_review_endpoints_require_reviewer(api_client, reviewer_factory, version, role):
    if role:
        api_client.force_authenticate(reviewer_factory(role=role))
    for response in [
        api_client.get(ROOT + "queue/"),
        api_client.get(ROOT + "me/stats/"),
        api_client.post(ROOT, {"version_id": version.pk, "decision": "accept"}),
    ]:
        assert response.status_code == 403
    assert not Review.objects.exists()


@pytest.mark.parametrize("role", ["reviewer", "moderator", "admin"])
def test_allowed_roles_and_response_allowlist(api_client, reviewer_factory, version, role):
    api_client.force_authenticate(reviewer_factory(role=role))
    response = api_client.post(ROOT, {"version_id": version.pk, "decision": "accept"})
    assert response.status_code == 201
    assert set(response.data) == {
        "id",
        "version_id",
        "decision",
        "reason",
        "weight_snapshot",
        "created_at",
    }
    assert response.data["weight_snapshot"] == "1.00"


def test_queue_hides_author_votes_and_control_metadata(api_client, reviewer_factory, make_version):
    reviewer = reviewer_factory()
    own = make_version(author=reviewer)
    pending = make_version()
    control = make_version(is_control=True, reference_decision="edit")
    reviewed = make_version()
    submit_review(reviewer=reviewer, version_id=reviewed.pk, decision="dont_know")
    for status in ("accepted", "rejected", "needs_edit"):
        make_version(status=status)
    make_version(status="in_review", escalated=True)
    make_version(is_withdrawn=True)
    api_client.force_authenticate(reviewer)
    response = api_client.get(ROOT + "queue/")
    assert response.status_code == 200
    assert {row["id"] for row in response.data} == {pending.pk, control.pk}
    assert own.pk not in {row["id"] for row in response.data}
    for row in response.data:
        assert set(row) == {
            "id",
            "number",
            "text_kk",
            "task_type",
            "domain",
            "text_ru",
            "definition",
        }
    assert response.data[0]["text_kk"] == "Қазақша мәтін"


def test_queue_includes_term_context(api_client, reviewer_factory):
    term = Term.objects.create(text_ru="Термин", definition="Meaning", domain="it")
    task = Task.objects.create(type="term", domain="it", term=term)
    contribution = Contribution.objects.create(task=task, author=reviewer_factory())
    ContributionVersion.objects.create(contribution=contribution, number=1, text_kk="Атау")
    api_client.force_authenticate(reviewer_factory())
    row = api_client.get(ROOT + "queue/").data[0]
    assert (row["task_type"], row["text_ru"], row["definition"]) == ("term", "Термин", "Meaning")


def test_self_duplicate_and_invalid_votes(api_client, reviewer_factory, version):
    api_client.force_authenticate(version.contribution.author)
    payload = {"version_id": version.pk, "decision": "accept"}
    assert api_client.post(ROOT, payload).status_code == 403
    api_client.force_authenticate(reviewer_factory())
    for changes in [
        {"decision": "bad"},
        {"decision": "reject"},
        {"decision": "edit", "reason": " "},
        {"version_id": 0},
        {"version_id": 999999},
    ]:
        assert api_client.post(ROOT, {**payload, **changes}).status_code == 400
    assert api_client.post(ROOT, payload).status_code == 201
    assert api_client.post(ROOT, payload).status_code == 409
    assert version.reviews.count() == 1


def test_sixth_vote_conflicts(api_client, reviewer_factory, version):
    for decision in ("accept", "reject", "edit", "accept", "reject"):
        submit_review(
            reviewer=reviewer_factory(), version_id=version.pk, decision=decision, reason="x"
        )
    api_client.force_authenticate(reviewer_factory())
    response = api_client.post(ROOT, {"version_id": version.pk, "decision": "accept"})
    assert response.status_code == 409
    assert version.reviews.count() == 5


def test_control_submission_does_not_expose_control_status(
    api_client, reviewer_factory, make_version
):
    version = make_version(is_control=True, reference_decision="reject")
    api_client.force_authenticate(reviewer_factory())
    response = api_client.post(ROOT, {"version_id": version.pk, "decision": "accept"})
    assert response.status_code == 201
    assert (
        not {"is_control", "reference_decision", "matched_final", "reputation_applied_at"}
        & response.data.keys()
    )


def test_stats_use_only_own_finalized_counted_votes(api_client, reviewer_factory, make_version):
    reviewer = reviewer_factory()
    api_client.force_authenticate(reviewer)
    assert api_client.get(ROOT + "me/stats/").data == {
        "weight": "1.00",
        "matched_votes": 0,
        "finalized_votes": 0,
        "match_share": None,
    }
    assert not ReviewerProfile.objects.exists()  # A read does not create a review profile.
    for decision in ("accept", "reject", "dont_know"):
        version = make_version()
        submit_review(reviewer=reviewer, version_id=version.pk, decision=decision, reason="x")
        # A prior match raises this reviewer's weight to 1.05: two new accepts
        # then fall just below 0.66 against their rejection, so collect a third.
        for _ in range(2 if decision == "accept" else 3):
            submit_review(reviewer=reviewer_factory(), version_id=version.pk, decision="accept")
    pending = make_version()
    submit_review(reviewer=reviewer, version_id=pending.pk, decision="reject", reason="x")
    data = api_client.get(ROOT + "me/stats/").data
    assert data == {
        "weight": "0.95",
        "matched_votes": 1,
        "finalized_votes": 2,
        "match_share": "0.50000000",
    }


def test_initial_weight_comes_from_active_settings(api_client, reviewer_factory, version):
    settings = QualitySettings.objects.get(is_active=True)
    settings.weight_initial = Decimal("1.20")
    settings.save()
    reviewer = reviewer_factory()
    api_client.force_authenticate(reviewer)
    assert api_client.get(ROOT + "me/stats/").data["weight"] == "1.20"
    response = api_client.post(ROOT, {"version_id": version.pk, "decision": "accept"})
    assert response.data["weight_snapshot"] == "1.20"


def test_session_review_requires_csrf(reviewer_factory, version):
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(reviewer_factory())
    response = client.post(ROOT, {"version_id": version.pk, "decision": "accept"})
    assert response.status_code == 403
    assert not Review.objects.exists()
