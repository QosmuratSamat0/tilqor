"""Part 6 (TIL-30 seed data): load_seed command idempotency, term licences, and validation."""

import shutil

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.accounts.models import User
from apps.contributions.models import Contribution, ContributionVersion, SourceSentence, Task
from apps.glossary.models import ConnectorHint, Term

pytestmark = pytest.mark.django_db


def test_load_seed_creates_terms_tasks_submitted_variants_sentences_and_unpublished_connectors(
    seed_fixtures_dir,
):
    call_command("load_seed", "--dir", str(seed_fixtures_dir))

    seed_user = User.objects.get(username="seed")
    assert seed_user.role == User.Role.PARTICIPANT
    assert not seed_user.has_usable_password()
    assert seed_user.accepted_terms is True
    assert seed_user.public_name == "seed"

    assert Term.objects.count() == 3
    assert Task.objects.filter(type=Task.Type.TERM, is_active=True).count() == 3
    assert SourceSentence.objects.count() == 2
    assert Task.objects.filter(type=Task.Type.TRANSLATION, is_active=True).count() == 2
    assert ConnectorHint.objects.count() == 2
    assert ConnectorHint.objects.filter(is_published=True).count() == 0

    cache_term = Term.objects.get(text_ru="кэш")
    assert cache_term.source == "Termincom.kz"
    assert cache_term.licence == "CC BY-SA 4.0"

    inhibitor_term = Term.objects.get(text_ru="ингибитор")
    assert inhibitor_term.source == ""
    assert inhibitor_term.licence == ""

    versions = list(ContributionVersion.objects.select_related("contribution__task__term"))
    assert len(versions) == 5
    assert all(v.status == ContributionVersion.Status.SUBMITTED for v in versions)
    for version in versions:
        term = version.contribution.task.term
        assert version.source == term.source
        assert version.licence == term.licence

    counts_before = (
        Term.objects.count(),
        SourceSentence.objects.count(),
        ConnectorHint.objects.count(),
        Task.objects.count(),
        Contribution.objects.count(),
        ContributionVersion.objects.count(),
    )

    call_command("load_seed", "--dir", str(seed_fixtures_dir))

    counts_after = (
        Term.objects.count(),
        SourceSentence.objects.count(),
        ConnectorHint.objects.count(),
        Task.objects.count(),
        Contribution.objects.count(),
        ContributionVersion.objects.count(),
    )
    assert counts_after == counts_before


def test_load_seed_stops_with_file_and_line_number_and_rolls_back_on_broken_row(
    seed_fixtures_dir, tmp_path
):
    for filename in ("terms.csv", "sentences.csv", "connectors.csv"):
        shutil.copy(seed_fixtures_dir / filename, tmp_path / filename)

    with (tmp_path / "sentences.csv").open("a", encoding="utf-8") as handle:
        handle.write("Битая строка без лицензии,it,https://example.org,,,false\n")

    with pytest.raises(CommandError) as exc_info:
        call_command("load_seed", "--dir", str(tmp_path))

    message = str(exc_info.value)
    assert "sentences.csv" in message
    assert "line 4" in message
    assert "licence" in message

    assert Term.objects.count() == 0
    assert SourceSentence.objects.count() == 0
    assert ConnectorHint.objects.count() == 0
    assert Task.objects.count() == 0
    assert ContributionVersion.objects.count() == 0


def test_load_seed_rejects_sourced_term_without_licence_and_saves_nothing(
    seed_fixtures_dir, tmp_path
):
    for filename in ("terms.csv", "sentences.csv", "connectors.csv"):
        shutil.copy(seed_fixtures_dir / filename, tmp_path / filename)

    with (tmp_path / "terms.csv").open("a", encoding="utf-8") as handle:
        handle.write("протокол,Набор правил обмена данными.,it,хаттама,Termincom.kz,\n")

    with pytest.raises(CommandError) as exc_info:
        call_command("load_seed", "--dir", str(tmp_path))

    message = str(exc_info.value)
    assert "terms.csv" in message
    assert "line 5" in message
    assert "licence" in message

    assert Term.objects.count() == 0
    assert SourceSentence.objects.count() == 0
    assert ConnectorHint.objects.count() == 0
    assert Task.objects.count() == 0
    assert ContributionVersion.objects.count() == 0
