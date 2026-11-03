from itertools import count
from pathlib import Path

import pytest
from django.conf import settings
from django.utils import timezone

from apps.accounts.models import User
from apps.contributions.models import (
    Contribution,
    ContributionVersion,
    SourceSentence,
    Task,
    VariantPreference,
)
from apps.glossary.models import ConnectorHint, Term
from apps.verification.models import Finalization, QualitySettings
from common.choices import Domain

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def seed_fixtures_dir() -> Path:
    return FIXTURES_DIR


@pytest.fixture
def user_factory(db):
    sequence = count(1)

    def create(role=User.Role.PARTICIPANT, accepted_terms=True, **kwargs):
        number = next(sequence)
        username = kwargs.pop("username", f"glossary_user_{number}")
        email = kwargs.pop("email", f"{username}@secret-mail.example")
        display_name = kwargs.pop("display_name", f"Contributor {number}")
        if accepted_terms:
            kwargs.setdefault("accepted_terms_at", timezone.now())
            kwargs.setdefault("accepted_terms_version", settings.PUBLICATION_TERMS_VERSION)
        return User.objects.create_user(
            username=username,
            email=email,
            password="Kazakh-Tilqor-2026",
            role=role,
            display_name=display_name,
            **kwargs,
        )

    return create


@pytest.fixture
def make_term_with_task(db):
    sequence = count(1)

    def create(
        text_ru=None,
        definition="Определение термина",
        domain=Domain.IT,
        source="Termincom.kz",
        licence=None,
        source_url="",
        is_active=True,
    ):
        number = next(sequence)
        if licence is None:
            licence = "CC BY 4.0" if source else ""
        term = Term.objects.create(
            text_ru=text_ru or f"Термин {number}",
            definition=definition,
            domain=domain,
            source=source,
            licence=licence,
            source_url=source_url,
        )
        task = Task.objects.create(
            type=Task.Type.TERM,
            domain=domain,
            term=term,
            is_active=is_active,
        )
        return term, task

    return create


@pytest.fixture
def make_sentence_with_task(db):
    sequence = count(1)

    def create(
        text_ru=None,
        domain=Domain.IT,
        is_original=True,
        licence="",
        attribution="",
        source_url="",
        is_active=True,
    ):
        number = next(sequence)
        sentence = SourceSentence.objects.create(
            text_ru=text_ru or f"Предложение {number}",
            domain=domain,
            is_original=is_original,
            licence=licence,
            attribution=attribution,
            source_url=source_url,
        )
        task = Task.objects.create(
            type=Task.Type.TRANSLATION,
            domain=domain,
            source_sentence=sentence,
            is_active=is_active,
        )
        return sentence, task

    return create


@pytest.fixture
def make_version_on_task(user_factory):
    def create(
        task,
        text_kk="Қазақша нұсқа",
        author=None,
        number=1,
        status=ContributionVersion.Status.ACCEPTED,
        is_control=False,
        is_withdrawn=False,
        source="",
        licence="",
        with_finalization=True,
    ):
        author = author or user_factory()
        contribution, _ = Contribution.objects.get_or_create(task=task, author=author)
        reference_decision = "accept" if is_control else ""
        version = ContributionVersion.objects.create(
            contribution=contribution,
            number=number,
            text_kk=text_kk,
            status=status,
            source=source,
            licence=licence,
            is_control=is_control,
            is_withdrawn=is_withdrawn,
            reference_decision=reference_decision,
        )
        if status == ContributionVersion.Status.ACCEPTED and with_finalization:
            q_settings = QualitySettings.objects.get(is_active=True)
            Finalization.objects.create(
                version=version,
                decision="accept",
                quality_settings=q_settings,
            )
        return version

    return create


@pytest.fixture
def add_preference(user_factory):
    def create(version, user=None):
        voter = user or user_factory()
        return VariantPreference.objects.create(
            task=version.contribution.task,
            user=voter,
            version=version,
        )

    return create


@pytest.fixture
def make_connector_hint(db):
    sequence = count(1)

    def create(
        text_ru=None,
        text_kk=None,
        example_kk="Мысал сөйлем.",
        example_ru="Пример предложения.",
        source="Tilqor",
        licence="CC BY 4.0",
        is_published=True,
    ):
        number = next(sequence)
        return ConnectorHint.objects.create(
            text_ru=text_ru or f"союз {number}",
            text_kk=text_kk or f"жалғаулық {number}",
            example_kk=example_kk,
            example_ru=example_ru,
            source=source,
            licence=licence,
            is_published=is_published,
        )

    return create
