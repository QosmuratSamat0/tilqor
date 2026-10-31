from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import transaction

from apps.contributions.models import ContributionVersion
from apps.verification.models import Finalization, QualitySettings, Review, ReviewerProfile
from apps.verification.services import finalize_version, resolve_version, submit_review
from apps.verification.services.errors import ReviewConflict, ReviewError, ReviewForbidden

pytestmark = pytest.mark.django_db


def cast(version, reviewer, decision="accept", reason="Explanation"):
    return submit_review(reviewer=reviewer, version_id=version.pk, decision=decision, reason=reason)


def escalate(version, reviewer_factory):
    return [
        cast(version, reviewer_factory(), decision)
        for decision in (
            "accept",
            "reject",
            "edit",
            "accept",
            "reject",
        )
    ]


def test_first_counted_vote_changes_status_abstention_does_not(version, reviewer_factory):
    abstention = cast(version, reviewer_factory(), "dont_know")
    version.refresh_from_db()
    assert version.status == "submitted"
    assert abstention.reputation_applied_at is None
    cast(version, reviewer_factory())
    version.refresh_from_db()
    assert version.status == "in_review"
    assert not Finalization.objects.exists()


@pytest.mark.parametrize(
    "outcome,status",
    [
        ("accept", "accepted"),
        ("reject", "rejected"),
        ("edit", "needs_edit"),
    ],
)
def test_finalization_once_with_frozen_snapshots(version, reviewer_factory, outcome, status):
    users = [reviewer_factory() for _ in range(4)]
    cast(version, users[0], "dont_know")
    for user, decision in zip(
        users[1:], [outcome, "edit" if outcome != "edit" else "accept", outcome], strict=True
    ):
        cast(version, user, decision)
    version.refresh_from_db()
    assert version.status == status
    assert list(ReviewerProfile.objects.order_by("user_id").values_list("weight", flat=True)) == [
        Decimal("1.00"),
        Decimal("1.05"),
        Decimal("0.90"),
        Decimal("1.05"),
    ]
    for _ in range(2):
        finalize_version(version_id=version.pk)
    assert Finalization.objects.filter(version=version).count() == 1
    assert Review.objects.filter(reputation_applied_at__isnull=False).count() == 3
    assert set(Review.objects.values_list("weight_snapshot", flat=True)) == {Decimal("1.00")}
    assert ReviewerProfile.objects.get(user=users[1]).weight == Decimal("1.05")


@pytest.mark.parametrize("role", ["participant"])
def test_role_and_self_review(version, reviewer_factory, role):
    with pytest.raises(ReviewForbidden):
        cast(version, reviewer_factory(role=role))
    with pytest.raises(ReviewForbidden):
        cast(version, version.contribution.author)
    assert not Review.objects.exists()
    assert not ReviewerProfile.objects.exists()


def test_duplicate_and_validation_fail_without_writes(version, reviewer_factory):
    reviewer = reviewer_factory()
    cast(version, reviewer)
    with pytest.raises(ReviewConflict):
        cast(version, reviewer, "dont_know")
    for decision, reason in [("reject", " "), ("edit", ""), ("bad", "")]:
        with pytest.raises(ReviewError):
            cast(version, reviewer_factory(), decision, reason)
    assert version.reviews.count() == 1
    assert ReviewerProfile.objects.count() == 1


def test_escalation_and_moderator_resolution(version, reviewer_factory):
    reviews = escalate(version, reviewer_factory)
    version.refresh_from_db()
    assert version.escalated and version.status == "in_review"
    with pytest.raises(ReviewConflict):
        cast(version, reviewer_factory())
    with pytest.raises(ReviewForbidden):
        resolve_version(
            moderator=reviewer_factory(), version_id=version.pk, decision="reject", reason="x"
        )
    moderator = reviewer_factory(role="moderator")
    with pytest.raises(ReviewError):
        resolve_version(moderator=moderator, version_id=version.pk, decision="reject", reason=" ")
    result = resolve_version(
        moderator=moderator, version_id=version.pk, decision="reject", reason="Incorrect"
    )
    assert result.reason == "Incorrect" and result.moderator == moderator
    for _ in range(2):
        assert (
            resolve_version(
                moderator=moderator, version_id=version.pk, decision="reject", reason="Incorrect"
            ).pk
            == result.pk
        )
        finalize_version(version_id=version.pk)
    version.refresh_from_db()
    assert version.status == "rejected" and not version.escalated
    assert ReviewerProfile.objects.get(user=reviews[0].reviewer).weight == Decimal("0.90")
    assert ReviewerProfile.objects.get(user=reviews[1].reviewer).weight == Decimal("1.05")


@pytest.mark.parametrize(
    "decision,expected", [("accept", "1.05"), ("reject", "0.80"), ("dont_know", "1.00")]
)
def test_control_steps_once_no_standard_updates(make_version, reviewer_factory, decision, expected):
    version = make_version(is_control=True, reference_decision="accept")
    reviewer = reviewer_factory()
    review = cast(version, reviewer, decision)
    assert ReviewerProfile.objects.get(user=reviewer).weight == Decimal(expected)
    with pytest.raises(ReviewConflict):
        cast(version, reviewer, decision)
    for _ in range(5):
        if not Finalization.objects.filter(version=version).exists():
            cast(version, reviewer_factory(), "accept")
    finalize_version(version_id=version.pk)
    assert ReviewerProfile.objects.get(user=reviewer).weight == Decimal(expected)
    version.refresh_from_db()
    assert version.status == "in_review"  # Control-only data never becomes publishable.
    review.refresh_from_db()
    assert review.weight_snapshot == Decimal("1.00")


def test_settings_are_pinned_and_new_version_has_fresh_round(version, reviewer_factory):
    first = cast(version, reviewer_factory(), "edit")
    settings = first.quality_settings
    settings.is_active = False
    settings.save(update_fields=["is_active"])
    replacement = QualitySettings.objects.create(
        version=2, is_active=True, weight_initial=Decimal("1.20")
    )
    second = cast(version, reviewer_factory(), "edit")
    cast(version, reviewer_factory(), "accept")
    assert second.quality_settings_id == settings.pk
    assert second.weight_snapshot == Decimal("1.00")
    version.refresh_from_db()
    assert version.status == "needs_edit"
    new = ContributionVersion.objects.create(
        contribution=version.contribution, number=2, text_kk="Жаңа нұсқа"
    )
    assert new.status == "submitted" and not new.reviews.exists()
    new_review = cast(new, first.reviewer)
    assert new_review.quality_settings == replacement
    assert version.reviews.count() == 3
    assert Finalization.objects.get(version=version).decision == "edit"


def test_settings_cannot_mutate_used_round(version, reviewer_factory):
    settings = cast(version, reviewer_factory()).quality_settings
    settings.threshold = Decimal("0.8")
    with pytest.raises(ValidationError):
        settings.save()


@pytest.mark.parametrize(
    "weight,decision,expected",
    [
        ("2.00", "accept", "2.00"),
        ("0.50", "reject", "0.50"),
    ],
)
def test_standard_weight_bounds_in_database(version, reviewer_factory, weight, decision, expected):
    reviewer = reviewer_factory()
    ReviewerProfile.objects.create(user=reviewer, weight=Decimal(weight))
    cast(version, reviewer, decision)
    cast(version, reviewer_factory())
    cast(version, reviewer_factory())
    assert ReviewerProfile.objects.get(user=reviewer).weight == Decimal(expected)


@pytest.mark.parametrize(
    "weight,decision,expected",
    [
        ("2.00", "accept", "2.00"),
        ("0.50", "reject", "0.50"),
    ],
)
def test_control_weight_bounds_in_database(
    make_version, reviewer_factory, weight, decision, expected
):
    version = make_version(is_control=True, reference_decision="accept")
    reviewer = reviewer_factory()
    ReviewerProfile.objects.create(user=reviewer, weight=Decimal(weight))
    cast(version, reviewer, decision)
    assert ReviewerProfile.objects.get(user=reviewer).weight == Decimal(expected)


def test_configured_steps_and_bounds_are_used(make_version, reviewer_factory):
    settings = QualitySettings.objects.get(is_active=True)
    settings.match_step, settings.mismatch_step = Decimal("0.07"), Decimal("0.11")
    settings.control_correct_step, settings.control_wrong_step = Decimal("0.08"), Decimal("0.30")
    settings.weight_min, settings.weight_max = Decimal("0.70"), Decimal("1.60")
    settings.save()
    version = make_version()
    users = [reviewer_factory() for _ in range(3)]
    for user, decision in zip(users, ["accept", "accept", "reject"], strict=True):
        cast(version, user, decision)
    assert ReviewerProfile.objects.get(user=users[0]).weight == Decimal("1.07")
    assert ReviewerProfile.objects.get(user=users[2]).weight == Decimal("0.89")
    control = make_version(is_control=True, reference_decision="accept")
    cast(control, users[0])
    cast(control, users[2], "reject")
    assert ReviewerProfile.objects.get(user=users[0]).weight == Decimal("1.15")
    assert ReviewerProfile.objects.get(user=users[2]).weight == Decimal("0.70")


@pytest.mark.parametrize(
    "changes",
    [
        {"min_votes": 2},
        {"max_votes": 6},
        {"min_supporters": 1},
        {"weight_initial": Decimal("2.1")},
        {"threshold": Decimal("0.5")},
        {"match_step": Decimal("-0.1")},
    ],
)
def test_settings_validation(changes):
    settings = QualitySettings(version=2, **changes)
    with pytest.raises(ValidationError):
        settings.full_clean()


def test_round_rolls_back_if_weight_update_fails(version, reviewer_factory, monkeypatch):
    from apps.verification.services import reviews

    cast(version, reviewer_factory())
    cast(version, reviewer_factory())
    original = reviews._apply_weight

    def fail_after_update(*args, **kwargs):
        original(*args, **kwargs)
        raise RuntimeError("simulated write failure")

    monkeypatch.setattr(reviews, "_apply_weight", fail_after_update)
    with pytest.raises(RuntimeError), transaction.atomic():
        cast(version, reviewer_factory(), "reject")
    version.refresh_from_db()
    assert version.reviews.count() == 2 and version.status == "in_review"
    assert not Finalization.objects.exists()
    assert set(ReviewerProfile.objects.values_list("weight", flat=True)) == {Decimal("1.00")}
