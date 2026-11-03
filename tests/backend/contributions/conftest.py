from itertools import count

import pytest
from django.conf import settings
from django.utils import timezone

from apps.accounts.models import User
from apps.contributions.models import Contribution, ContributionVersion, SourceSentence, Task
from apps.glossary.models import Term
from common.choices import Domain


@pytest.fixture
def user_factory(db):
    sequence = count()

    def create(role=User.Role.PARTICIPANT, accepted_terms=True, **kwargs):
        number = next(sequence)
        username = kwargs.pop("username", f"user{number}")
        email = kwargs.pop("email", f"{username}@example.com")
        if accepted_terms:
            kwargs.setdefault("accepted_terms_at", timezone.now())
            kwargs.setdefault("accepted_terms_version", settings.PUBLICATION_TERMS_VERSION)
        return User.objects.create_user(
            username=username,
            email=email,
            password="Kazakh-Tilqor-2026",
            role=role,
            **kwargs,
        )

    return create


@pytest.fixture
def make_translation_task(db):
    sequence = count()

    def create(domain=Domain.IT, text_ru=None, is_active=True):
        number = next(sequence)
        sentence = SourceSentence.objects.create(
            text_ru=text_ru or f"Исходное предложение {number}",
            domain=domain,
            is_original=True,
        )
        return Task.objects.create(
            type=Task.Type.TRANSLATION,
            domain=domain,
            source_sentence=sentence,
            is_active=is_active,
        )

    return create


@pytest.fixture
def make_term_task(db):
    sequence = count()

    def create(domain=Domain.IT, text_ru=None, definition="Определение", is_active=True):
        number = next(sequence)
        term = Term.objects.create(
            text_ru=text_ru or f"Термин {number}",
            definition=definition,
            domain=domain,
        )
        return Task.objects.create(
            type=Task.Type.TERM,
            domain=domain,
            term=term,
            is_active=is_active,
        )

    return create


@pytest.fixture
def add_version(user_factory):
    def create(task, text_kk="Қазақша нұсқа", author=None, number=1, **kwargs):
        author = author or user_factory()
        contribution, _ = Contribution.objects.get_or_create(task=task, author=author)
        return ContributionVersion.objects.create(
            contribution=contribution,
            number=number,
            text_kk=text_kk,
            **kwargs,
        )

    return create
