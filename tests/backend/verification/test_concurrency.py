"""Real PostgreSQL connections exercise row locks, not mocked thread ordering."""

from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from threading import Barrier

import pytest
from django.db import close_old_connections, connection, connections

from apps.accounts.models import User
from apps.verification.models import Finalization, QualitySettings, Review, ReviewerProfile
from apps.verification.services import finalize_version, submit_review
from apps.verification.services.errors import ReviewConflict

pytestmark = pytest.mark.django_db(transaction=True)


def simultaneous(requests):
    barrier = Barrier(len(requests))

    def run(request):
        close_old_connections()
        try:
            user_id, version_id, decision = request
            user = User.objects.get(pk=user_id)
            barrier.wait(timeout=15)
            try:
                return submit_review(
                    reviewer=user, version_id=version_id, decision=decision, reason="x"
                ).pk
            except ReviewConflict:
                return None
        finally:
            connections.close_all()

    with ThreadPoolExecutor(max_workers=len(requests)) as executor:
        return list(executor.map(run, requests, timeout=45))


@pytest.mark.parametrize("repeat", range(20))
def test_parallel_votes_and_retry_finalize_once(make_version, reviewer_factory, repeat):
    assert connection.vendor == "postgresql"
    QualitySettings.objects.get_or_create(version=1, defaults={"is_active": True})
    version = make_version()
    users = [reviewer_factory() for _ in range(5)]
    requests = [(user.pk, version.pk, "accept") for user in users]
    simultaneous([*requests, requests[0]])
    version.refresh_from_db()
    assert version.status == "accepted"
    assert version.reviews.count() == 3
    assert version.reviews.values("reviewer_id").distinct().count() == 3
    assert Finalization.objects.filter(version=version).count() == 1
    assert set(ReviewerProfile.objects.values_list("weight", flat=True)) == {Decimal("1.05")}
    finalize_version(version_id=version.pk)
    assert set(ReviewerProfile.objects.values_list("weight", flat=True)) == {Decimal("1.05")}


def test_parallel_votes_stop_at_five_without_outcome(make_version, reviewer_factory):
    QualitySettings.objects.get_or_create(
        version=1, defaults={"is_active": True, "threshold": Decimal("0.9")}
    )
    version = make_version()
    users = [reviewer_factory() for _ in range(5)]
    requests = [
        (user.pk, version.pk, decision)
        for user, decision in zip(
            users,
            ["accept", "reject", "edit", "accept", "reject"],
            strict=True,
        )
    ]
    results = simultaneous([*requests, requests[0]])
    assert sum(result is not None for result in results) == 5
    version.refresh_from_db()
    assert version.escalated and version.reviews.count() == 5
    assert not Finalization.objects.exists()
    assert not Review.objects.filter(reputation_applied_at__isnull=False).exists()


def test_shared_reviewers_across_parallel_rounds_keep_both_updates(make_version, reviewer_factory):
    QualitySettings.objects.get_or_create(version=1, defaults={"is_active": True})
    versions = [make_version(), make_version()]
    users = [reviewer_factory() for _ in range(3)]
    for version in versions:
        for user in users[:2]:
            submit_review(reviewer=user, version_id=version.pk, decision="accept")
    simultaneous([(users[2].pk, version.pk, "accept") for version in versions])
    assert Finalization.objects.count() == 2
    assert set(ReviewerProfile.objects.values_list("weight", flat=True)) == {Decimal("1.10")}
    assert set(
        Review.objects.filter(reviewer=users[2]).values_list("weight_snapshot", flat=True)
    ) == {
        Decimal("1.00"),
        Decimal("1.05"),
    }
