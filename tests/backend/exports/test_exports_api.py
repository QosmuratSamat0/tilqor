"""FR-06, FR-20, NFR-01, NFR-04, NFR-12: CSV, JSON and manifest export tests."""

import csv
import io
import json
import unicodedata

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import User
from apps.contributions.models import Contribution, ContributionVersion, SourceSentence, Task
from apps.exports.domain import EXPORT_COLUMNS
from apps.glossary.models import Term
from apps.verification.models import Finalization, QualitySettings
from common.choices import Domain
from tests.backend.conftest import PASSWORD

pytestmark = pytest.mark.django_db

CSV_URL = "/api/exports/dataset.csv"
JSON_URL = "/api/exports/dataset.json"
MANIFEST_URL = "/api/exports/manifest.json"


def _create_user(username: str, *, display_name: str, accepted_terms: bool = True) -> User:
    kwargs = {
        "username": username,
        "email": f"{username}@private-domain.example",
        "password": "Kazakh-Tilqor-2026",
        "display_name": display_name,
    }
    if accepted_terms:
        kwargs["accepted_terms_at"] = timezone.now()
        kwargs["accepted_terms_version"] = settings.PUBLICATION_TERMS_VERSION
    return User.objects.create_user(**kwargs)


def _accept_version(version: ContributionVersion) -> Finalization:
    q_settings = QualitySettings.objects.get(is_active=True)
    return Finalization.objects.create(
        version=version,
        decision="accept",
        quality_settings=q_settings,
    )


def test_exports_csv_json_and_manifest_match_ids_provenance_and_exclude_ineligible(api_client):
    author_ok = _create_user("export_author_ok", display_name="Айгерім С.", accepted_terms=True)
    seed_user = _create_user("seed", display_name="Tilqor team", accepted_terms=True)
    author_no_terms = _create_user(
        "export_author_noterms", display_name="Terms Not Accepted", accepted_terms=False
    )

    kazakh_text = unicodedata.normalize(
        "NFC",
        "Әә Ғғ Ққ Ңң Өө Ұұ Үү Һһ Іі — Қазақ тіліндегі толық сөйлем үлгісі.",
    )
    russian_text = unicodedata.normalize(
        "NFC",
        "Проверка всех букв русского алфавита: Ёё, Йй, Щщ, Ъъ, Ыы, Ээ, Юю, Яя.",
    )

    licensed_sentence = SourceSentence.objects.create(
        text_ru=russian_text,
        domain=Domain.IT,
        source_url="https://example.org/corpus/42",
        licence="CC BY-SA 4.0",
        attribution="OpenKazakh Corpus",
        is_original=False,
    )
    translation_task = Task.objects.create(
        type=Task.Type.TRANSLATION,
        domain=Domain.IT,
        source_sentence=licensed_sentence,
    )
    trans_contrib = Contribution.objects.create(task=translation_task, author=author_ok)
    ContributionVersion.objects.create(
        contribution=trans_contrib,
        number=1,
        text_kk="Алғашқы түзетілген нұсқа",
        status=ContributionVersion.Status.NEEDS_EDIT,
    )
    eligible_trans_v2 = ContributionVersion.objects.create(
        contribution=trans_contrib,
        number=2,
        text_kk=kazakh_text,
        status=ContributionVersion.Status.ACCEPTED,
    )
    fin_trans = _accept_version(eligible_trans_v2)

    term = Term.objects.create(
        text_ru="Маршрутизатор",
        definition="Сетевое устройство.",
        domain=Domain.ENGINEERING,
        source="Termincom.kz",
        licence="CC BY-NC-SA 4.0",
        source_url="https://termincom.kz/router",
    )
    term_task = Task.objects.create(
        type=Task.Type.TERM,
        domain=Domain.ENGINEERING,
        term=term,
    )
    seed_term_contrib = Contribution.objects.create(task=term_task, author=seed_user)
    eligible_seed_term_v = ContributionVersion.objects.create(
        contribution=seed_term_contrib,
        number=1,
        text_kk="маршруттауыш",
        status=ContributionVersion.Status.ACCEPTED,
        source="Termincom.kz",
        licence="CC BY-NC-SA 4.0",
    )
    fin_seed_term = _accept_version(eligible_seed_term_v)

    term_contrib = Contribution.objects.create(task=term_task, author=author_ok)
    eligible_term_v1 = ContributionVersion.objects.create(
        contribution=term_contrib,
        number=1,
        text_kk="бағыттауыш",
        status=ContributionVersion.Status.ACCEPTED,
    )
    fin_term = _accept_version(eligible_term_v1)

    for idx, bad_kwargs in enumerate(
        [
            {"status": ContributionVersion.Status.SUBMITTED, "text_kk": "excluded_submitted"},
            {"status": ContributionVersion.Status.IN_REVIEW, "text_kk": "excluded_in_review"},
            {"status": ContributionVersion.Status.REJECTED, "text_kk": "excluded_rejected"},
            {"status": ContributionVersion.Status.NEEDS_EDIT, "text_kk": "excluded_needs_edit"},
            {
                "status": ContributionVersion.Status.ACCEPTED,
                "is_control": True,
                "reference_decision": "accept",
                "text_kk": "excluded_control",
            },
            {
                "status": ContributionVersion.Status.ACCEPTED,
                "is_withdrawn": True,
                "text_kk": "excluded_withdrawn",
            },
        ]
    ):
        s = SourceSentence.objects.create(
            text_ru=f"Исключённое предложение {idx}",
            domain=Domain.IT,
            is_original=True,
        )
        t = Task.objects.create(type=Task.Type.TRANSLATION, domain=Domain.IT, source_sentence=s)
        c = Contribution.objects.create(task=t, author=author_ok)
        ContributionVersion.objects.create(contribution=c, number=1, **bad_kwargs)

    unaccepted_sentence = SourceSentence.objects.create(
        text_ru="Предложение без согласия автора",
        domain=Domain.MEDICINE,
        is_original=True,
    )
    unaccepted_task = Task.objects.create(
        type=Task.Type.TRANSLATION,
        domain=Domain.MEDICINE,
        source_sentence=unaccepted_sentence,
    )
    unaccepted_contrib = Contribution.objects.create(
        task=unaccepted_task, author=author_no_terms
    )
    unaccepted_v = ContributionVersion.objects.create(
        contribution=unaccepted_contrib,
        number=1,
        text_kk="excluded_unaccepted_terms",
        status=ContributionVersion.Status.ACCEPTED,
    )
    _accept_version(unaccepted_v)

    csv_resp = api_client.get(CSV_URL)
    json_resp = api_client.get(JSON_URL)
    manifest_resp = api_client.get(MANIFEST_URL)

    assert csv_resp.status_code == 200
    assert json_resp.status_code == 200
    assert manifest_resp.status_code == 200

    assert csv_resp.content.startswith(b"\xef\xbb\xbf")
    csv_text = csv_resp.content.decode("utf-8-sig")
    csv_rows = list(csv.DictReader(io.StringIO(csv_text)))
    assert tuple(csv_rows[0].keys()) == EXPORT_COLUMNS

    json_text = json_resp.content.decode("utf-8")
    assert "\\u" not in json_text
    json_records = json.loads(json_text)["records"]

    expected_ids = [
        eligible_trans_v2.pk,
        eligible_seed_term_v.pk,
        eligible_term_v1.pk,
    ]
    assert [int(r["id"]) for r in csv_rows] == expected_ids
    assert [r["id"] for r in json_records] == expected_ids

    assert json_records[0] == {
        "id": eligible_trans_v2.pk,
        "type": "translation",
        "domain": Domain.IT,
        "text_ru": russian_text,
        "text_kk": kazakh_text,
        "version": 2,
        "source_url": "https://example.org/corpus/42",
        "licence": "CC BY-SA 4.0",
        "attribution": "OpenKazakh Corpus",
        "is_original": False,
        "modifications": 1,
        "contributor": "Айгерім С.",
        "accepted_at": fin_trans.created_at.isoformat(),
    }
    assert csv_rows[0]["text_ru"] == russian_text
    assert csv_rows[0]["text_kk"] == kazakh_text

    assert json_records[1] == {
        "id": eligible_seed_term_v.pk,
        "type": "term",
        "domain": Domain.ENGINEERING,
        "text_ru": "Маршрутизатор",
        "text_kk": "маршруттауыш",
        "version": 1,
        "source_url": "https://termincom.kz/router",
        "licence": "CC BY-NC-SA 4.0",
        "attribution": "Termincom.kz",
        "is_original": False,
        "modifications": 0,
        "contributor": "Termincom.kz",
        "accepted_at": fin_seed_term.created_at.isoformat(),
    }

    assert json_records[2] == {
        "id": eligible_term_v1.pk,
        "type": "term",
        "domain": Domain.ENGINEERING,
        "text_ru": "Маршрутизатор",
        "text_kk": "бағыттауыш",
        "version": 1,
        "source_url": "https://termincom.kz/router",
        "licence": settings.DATASET_LICENCE,
        "attribution": "Termincom.kz",
        "is_original": False,
        "modifications": 0,
        "contributor": "Айгерім С.",
        "accepted_at": fin_term.created_at.isoformat(),
    }
    assert all(r["contributor"] != "seed" for r in json_records)
    assert all(r["contributor"] != "seed" for r in csv_rows)

    manifest = manifest_resp.json()
    assert manifest["record_count"] == 3
    assert manifest["terms_version"] == settings.PUBLICATION_TERMS_VERSION
    assert manifest["dataset_licence"] == settings.DATASET_LICENCE
    assert manifest["conditions"] == [
        {
            "licence": "CC BY 4.0",
            "attribution": "Termincom.kz",
            "source_url": "https://termincom.kz/router",
            "count": 1,
        },
        {
            "licence": "CC BY-NC-SA 4.0",
            "attribution": "Termincom.kz",
            "source_url": "https://termincom.kz/router",
            "count": 1,
        },
        {
            "licence": "CC BY-SA 4.0",
            "attribution": "OpenKazakh Corpus",
            "source_url": "https://example.org/corpus/42",
            "count": 1,
        },
    ]

    for payload_str in (csv_text, json_text, manifest_resp.content.decode("utf-8")):
        assert "excluded_" not in payload_str
        assert "Алғашқы түзетілген нұсқа" not in payload_str
        assert "@" not in payload_str
        assert "email" not in payload_str
        assert "username" not in payload_str
        assert author_ok.username not in payload_str
        assert author_ok.email not in payload_str
        assert author_no_terms.username not in payload_str
        assert author_no_terms.email not in payload_str
        assert seed_user.email not in payload_str


def test_export_excludes_sourced_term_without_licence_and_third_party_variant_without_licence(
    api_client,
):
    participant = _create_user("part_user", display_name="Марат К.", accepted_terms=True)
    seed_user = _create_user("seed", display_name="Tilqor team", accepted_terms=True)

    unlicensed_term = Term.objects.create(
        text_ru="Закрытый термин",
        definition="Термин с источником без лицензии.",
        domain=Domain.IT,
        source="Unlicensed Dictionary",
        licence="",
    )
    unlicensed_task = Task.objects.create(
        type=Task.Type.TERM,
        domain=Domain.IT,
        term=unlicensed_term,
    )
    c1 = Contribution.objects.create(task=unlicensed_task, author=participant)
    v1 = ContributionVersion.objects.create(
        contribution=c1,
        number=1,
        text_kk="жабық термин",
        status=ContributionVersion.Status.ACCEPTED,
    )
    _accept_version(v1)

    licensed_term = Term.objects.create(
        text_ru="Открытый термин",
        definition="Термин с лицензией.",
        domain=Domain.IT,
        source="Termincom.kz",
        licence="CC BY-SA 4.0",
    )
    licensed_task = Task.objects.create(
        type=Task.Type.TERM,
        domain=Domain.IT,
        term=licensed_term,
    )
    c2 = Contribution.objects.create(task=licensed_task, author=seed_user)
    v2 = ContributionVersion.objects.create(
        contribution=c2,
        number=1,
        text_kk="лицензиясыз сыртқы нұсқа",
        status=ContributionVersion.Status.ACCEPTED,
        source="Termincom.kz",
        licence="",
    )
    _accept_version(v2)

    assert api_client.get(JSON_URL).json()["records"] == []
    assert api_client.get(MANIFEST_URL).json()["record_count"] == 0


def test_seedling_participant_variant_is_exported_with_own_public_name_and_cc_by(api_client):
    reg_resp = api_client.post(
        reverse("auth-register"),
        {
            "username": "seedling",
            "email": "seedling@example.com",
            "password": PASSWORD,
            "display_name": "Ерлан Б.",
            "accept_terms": True,
        },
        format="json",
    )
    assert reg_resp.status_code == 201
    seedling = User.objects.get(username="seedling")

    term = Term.objects.create(
        text_ru="Компилятор",
        definition="Программа перевода исходного кода.",
        domain=Domain.IT,
        source="Termincom.kz",
        licence="CC BY-SA 4.0",
    )
    task = Task.objects.create(type=Task.Type.TERM, domain=Domain.IT, term=term)
    contrib = Contribution.objects.create(task=task, author=seedling)
    version = ContributionVersion.objects.create(
        contribution=contrib,
        number=1,
        text_kk="құрастырғыш",
        status=ContributionVersion.Status.ACCEPTED,
    )
    _accept_version(version)

    records = api_client.get(JSON_URL).json()["records"]
    assert len(records) == 1
    assert records[0]["id"] == version.pk
    assert records[0]["contributor"] == "Ерлан Б."
    assert records[0]["licence"] == settings.DATASET_LICENCE
    assert records[0]["attribution"] == "Termincom.kz"
    assert records[0]["is_original"] is False
