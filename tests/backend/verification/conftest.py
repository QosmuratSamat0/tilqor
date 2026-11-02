from itertools import count

import pytest

from apps.accounts.models import User
from apps.contributions.models import Contribution, ContributionVersion, SourceSentence, Task


@pytest.fixture
def reviewer_factory():
    sequence = count()

    def create(**kwargs):
        number = next(sequence)
        return User.objects.create(
            username=f"reviewer{number}",
            email=f"reviewer{number}@example.com",
            role=kwargs.pop("role", User.Role.REVIEWER),
            **kwargs,
        )

    return create


@pytest.fixture
def make_version(reviewer_factory):
    def create(**kwargs):
        author = kwargs.pop("author", None) or reviewer_factory()
        sentence = SourceSentence.objects.create(text_ru="Тест", domain="it", is_original=True)
        task = Task.objects.create(type="translation", domain="it", source_sentence=sentence)
        contribution = Contribution.objects.create(task=task, author=author)
        return ContributionVersion.objects.create(
            contribution=contribution,
            number=1,
            text_kk="Қазақша мәтін",
            **kwargs,
        )

    return create


@pytest.fixture
def version(make_version):
    return make_version()
