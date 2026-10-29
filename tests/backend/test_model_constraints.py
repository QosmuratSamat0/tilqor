"""Database constraints that protect data quality."""
from decimal import Decimal

import pytest
from django.db import IntegrityError, transaction

from apps.contributions.models import Contribution, ContributionVersion, SourceSentence, Task
from apps.glossary.models import Term
from apps.verification.models import QualitySettings, Review, ReviewerProfile
from common.choices import Domain

pytestmark = pytest.mark.django_db


@pytest.fixture
def sentence():
    return SourceSentence.objects.create(
        text_ru="Пациенту назначили курс лечения.", domain=Domain.MEDICINE, is_original=True
    )


@pytest.fixture
def version(sentence, make_user):
    task = Task.objects.create(
        type=Task.Type.TRANSLATION, domain=Domain.MEDICINE, source_sentence=sentence
    )
    contribution = Contribution.objects.create(task=task, author=make_user(username="author"))
    return ContributionVersion.objects.create(
        contribution=contribution, number=1, text_kk="Науқасқа емдеу курсы тағайындалды."
    )


def active_settings():
    return QualitySettings.objects.get(is_active=True)


def assert_integrity_error(create):
    with pytest.raises(IntegrityError), transaction.atomic():
        create()


def test_default_quality_settings_match_requirements():
    settings = active_settings()

    assert settings.version == 1
    assert settings.threshold == Decimal("0.660")
    assert (settings.min_votes, settings.max_votes, settings.min_supporters) == (3, 5, 2)
    assert (settings.weight_min, settings.weight_initial, settings.weight_max) == (
        Decimal("0.50"),
        Decimal("1.00"),
        Decimal("2.00"),
    )


def test_only_one_active_settings_version():
    assert_integrity_error(lambda: QualitySettings.objects.create(version=2, is_active=True))


def test_settings_reject_min_votes_above_max_votes():
    assert_integrity_error(
        lambda: QualitySettings.objects.create(version=3, min_votes=6, max_votes=5)
    )


def test_external_sentence_requires_licence():
    assert_integrity_error(
        lambda: SourceSentence.objects.create(text_ru="Текст", domain=Domain.IT, licence="")
    )


def test_translation_task_requires_source_sentence():
    assert_integrity_error(
        lambda: Task.objects.create(type=Task.Type.TRANSLATION, domain=Domain.IT)
    )


def test_term_task_requires_term(sentence):
    assert_integrity_error(
        lambda: Task.objects.create(
            type=Task.Type.TERM, domain=Domain.IT, source_sentence=sentence
        )
    )
    term = Term.objects.create(text_ru="кэш", domain=Domain.IT)
    assert Task.objects.create(type=Task.Type.TERM, domain=Domain.IT, term=term).pk


def test_reviewer_weight_must_stay_within_bounds(make_user):
    user = make_user(username="reviewer")

    assert_integrity_error(
        lambda: ReviewerProfile.objects.create(user=user, weight=Decimal("2.50"))
    )
    assert ReviewerProfile.objects.create(user=user, weight=Decimal("2.00")).pk


def test_one_review_per_reviewer_per_version(version, make_user):
    reviewer = make_user(username="reviewer")

    def review():
        return Review.objects.create(
            version=version,
            reviewer=reviewer,
            decision="accept",
            weight_snapshot=Decimal("1.00"),
            quality_settings=active_settings(),
        )

    review()
    assert_integrity_error(review)


def test_reject_requires_a_reason(version, make_user):
    reviewer = make_user(username="reviewer")

    assert_integrity_error(
        lambda: Review.objects.create(
            version=version,
            reviewer=reviewer,
            decision="reject",
            reason="",
            weight_snapshot=Decimal("1.00"),
            quality_settings=active_settings(),
        )
    )


def test_version_numbers_are_unique_per_contribution(version):
    assert_integrity_error(
        lambda: ContributionVersion.objects.create(
            contribution=version.contribution, number=1, text_kk="басқа нұсқа"
        )
    )


def test_control_version_needs_a_reference_decision(version):
    assert_integrity_error(
        lambda: ContributionVersion.objects.create(
            contribution=version.contribution, number=2, text_kk="бақылау", is_control=True
        )
    )
