"""FR-10 reason rules at the pure, API, service and database boundaries."""

from itertools import product

import pytest
from django.db import IntegrityError, transaction

from apps.verification.choices import ReviewReason
from apps.verification.domain.reasons import REASON_CODES, reason_error
from apps.verification.models import QualitySettings, Review
from apps.verification.services import submit_review
from apps.verification.services.errors import ReviewError

CASES = list(
    product(
        ("accept", "dont_know", "reject", "edit"),
        ("", "wrong_term", "russian_connector", "grammar", "other", "invalid"),
        ("", " \t\n", "Useful comment"),
    )
)


def valid(decision, code, comment):
    return (
        (decision in ("reject", "edit") and code in REASON_CODES)
        or (decision in ("accept", "dont_know") and code == "")
    ) and (code != "other" or bool(comment.strip()))


@pytest.mark.parametrize(("decision", "code", "comment"), CASES)
def test_pure_reason_matrix(decision, code, comment):
    assert (reason_error(decision, code, comment) is None) == valid(decision, code, comment)
    assert tuple(ReviewReason.values) == REASON_CODES


@pytest.mark.django_db
@pytest.mark.parametrize(("decision", "code", "comment"), CASES)
def test_api_service_and_database_reason_matrix(
    api_client,
    reviewer_factory,
    version,
    decision,
    code,
    comment,
):
    allowed = valid(decision, code, comment)
    api_client.force_authenticate(reviewer_factory())
    response = api_client.post(
        "/api/reviews/",
        {
            "version_id": version.pk,
            "decision": decision,
            "reason_code": code,
            "reason": comment,
        },
    )
    assert response.status_code == (201 if allowed else 400)
    if allowed:
        assert response.data["reason_code"] == code
        assert response.data["reason"] == comment.strip()
    else:
        error_field = (
            "reason" if code == "other" and decision in ("reject", "edit") else "reason_code"
        )
        assert response.data["codes"][error_field]
        with pytest.raises(ReviewError):
            submit_review(
                reviewer=reviewer_factory(),
                version_id=version.pk,
                decision=decision,
                reason_code=code,
                reason=comment,
            )

    def direct_write():
        return Review.objects.create(
            version=version,
            reviewer=reviewer_factory(),
            decision=decision,
            reason_code=code,
            reason=comment,
            weight_snapshot="1.00",
            quality_settings=QualitySettings.objects.get(is_active=True),
        )

    if allowed:
        assert direct_write().pk
    else:
        with pytest.raises(IntegrityError), transaction.atomic():
            direct_write()


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("payload", "field", "code"),
    [
        ({"decision": "reject"}, "reason_code", "reason_required"),
        ({"decision": "edit", "reason_code": "other"}, "reason", "comment_required"),
    ],
)
def test_reason_error_codes(api_client, reviewer_factory, version, payload, field, code):
    api_client.force_authenticate(reviewer_factory())
    response = api_client.post("/api/reviews/", {"version_id": version.pk, **payload})
    assert response.status_code == 400
    assert response.data["codes"] == {field: [code]}


@pytest.mark.django_db
def test_code_without_comment_is_exposed_to_author(api_client, reviewer_factory, make_version):
    version = make_version()
    for _ in range(3):
        submit_review(
            reviewer=reviewer_factory(),
            version_id=version.pk,
            decision="reject",
            reason_code="russian_connector",
        )
    api_client.force_authenticate(version.contribution.author)
    reasons = api_client.get("/api/contributions/me/").data[0]["versions"][0]["decision_reasons"]
    assert reasons == [{"code": "russian_connector", "comment": ""}]
