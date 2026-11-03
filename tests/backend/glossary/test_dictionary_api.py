"""FR-17, FR-18, NFR-01, NFR-04, NFR-05: dictionary list, search, detail, and recommendation."""

import unicodedata

import pytest
from django.contrib import admin
from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory

from apps.contributions.models import ContributionVersion
from apps.glossary.admin_actions import recommend_variant
from apps.glossary.models import Term
from apps.glossary.services import recommend_term_variant
from common.choices import Domain

pytestmark = pytest.mark.django_db
DICTIONARY_URL = "/api/dictionary/"


def _admin_request(user, payload=None):
    request = RequestFactory().post("/admin/glossary/term/", payload or {})
    request.user = user
    request.session = {}
    request._messages = FallbackStorage(request)
    return request


def test_dictionary_list_only_includes_terms_with_eligible_variants_and_supports_anonymous(
    api_client, user_factory, make_term_with_task, make_version_on_task
):
    eligible_term, eligible_task = make_term_with_task(
        text_ru="Маршрутизатор", domain=Domain.IT, source="Termincom.kz", licence="CC BY 4.0"
    )
    eligible_v = make_version_on_task(eligible_task, text_kk="бағыттауыш")

    _, pending_task = make_term_with_task(text_ru="Компилятор", domain=Domain.IT)
    make_version_on_task(
        pending_task,
        text_kk="құрастырғыш",
        status=ContributionVersion.Status.SUBMITTED,
    )

    _, rejected_task = make_term_with_task(text_ru="Дебаггер", domain=Domain.IT)
    make_version_on_task(
        rejected_task,
        text_kk="жөндегіш",
        status=ContributionVersion.Status.REJECTED,
    )

    _, withdrawn_task = make_term_with_task(text_ru="Токен", domain=Domain.IT)
    make_version_on_task(withdrawn_task, text_kk="таңбалауыш", is_withdrawn=True)

    _, control_task = make_term_with_task(text_ru="Прокси", domain=Domain.IT)
    make_version_on_task(control_task, text_kk="делдал", is_control=True)

    _, unaccepted_author_task = make_term_with_task(text_ru="Сокет", domain=Domain.IT)
    unaccepted_author = user_factory(accepted_terms=False)
    make_version_on_task(
        unaccepted_author_task, text_kk="ұяшық", author=unaccepted_author
    )

    response = api_client.get(DICTIONARY_URL)
    assert response.status_code == 200
    assert response.data["count"] == 1
    results = response.data["results"]
    assert len(results) == 1
    assert results[0]["id"] == eligible_term.pk
    assert results[0]["text_ru"] == "Маршрутизатор"
    assert results[0]["recommended"] is None
    assert results[0]["alternatives"] == [
        {
            "id": eligible_v.pk,
            "text_kk": "бағыттауыш",
            "public_name": eligible_v.contribution.author.public_name,
        }
    ]


def test_unlicensed_sourced_term_is_excluded_from_dictionary_list_and_detail(
    api_client, make_term_with_task, make_version_on_task
):
    unlicensed_term, unlicensed_task = make_term_with_task(
        text_ru="Шлюз", domain=Domain.IT, source="External Dict", licence=""
    )
    make_version_on_task(unlicensed_task, text_kk="шлюз")

    list_resp = api_client.get(DICTIONARY_URL)
    assert list_resp.status_code == 200
    assert list_resp.data["results"] == []
    assert api_client.get(f"{DICTIONARY_URL}{unlicensed_term.pk}/").status_code == 404


def test_dictionary_search_matches_russian_and_filters_domain(
    api_client, make_term_with_task, make_version_on_task
):
    it_term, it_task = make_term_with_task(text_ru="Алгоритм поиска", domain=Domain.IT)
    make_version_on_task(it_task, text_kk="іздеу алгоритмі")
    make_version_on_task(
        it_task,
        text_kk="Жасырын тексерілмеген сөз",
        status=ContributionVersion.Status.SUBMITTED,
    )

    med_term, med_task = make_term_with_task(text_ru="Анестезия", domain=Domain.MEDICINE)
    make_version_on_task(med_task, text_kk="жансыздандыру")

    ru_resp = api_client.get(DICTIONARY_URL, {"q": "  АЛГОРИТМ  "})
    assert ru_resp.status_code == 200
    assert [item["id"] for item in ru_resp.data["results"]] == [it_term.pk]

    non_eligible_search = api_client.get(DICTIONARY_URL, {"q": "Жасырын"})
    assert non_eligible_search.status_code == 200
    assert non_eligible_search.data["results"] == []

    domain_resp = api_client.get(DICTIONARY_URL, {"domain": Domain.MEDICINE})
    assert domain_resp.status_code == 200
    assert [item["id"] for item in domain_resp.data["results"]] == [med_term.pk]

    bad_domain_resp = api_client.get(DICTIONARY_URL, {"domain": "invalid-domain"})
    assert bad_domain_resp.status_code == 400
    assert "domain" in bad_domain_resp.data


@pytest.mark.parametrize(
    "uppercase_query",
    [
        "ӘДІЛЕТ",
        "ҒЫЛЫМ",
        "ҚОҒАМ",
        "ҢҰСҚА",
        "ӨРІС",
        "ҰЛТ",
        "ҮЛЕС",
        "ҺАҚ",
        "ІЛІМ",
    ],
)
def test_dictionary_search_folds_uppercase_kazakh_letters_in_database(
    api_client, make_term_with_task, make_version_on_task, uppercase_query
):
    kazakh_all_letters = "Әділет Ғылым Қоғам Ңұсқа Өріс Ұлт Үлес Һақ Ілім"
    it_term, it_task = make_term_with_task(text_ru="Алгоритм поиска", domain=Domain.IT)
    make_version_on_task(it_task, text_kk=kazakh_all_letters)

    decomposed_q = unicodedata.normalize("NFD", f"  {uppercase_query}  ")
    kk_resp = api_client.get(DICTIONARY_URL, {"q": decomposed_q})
    assert kk_resp.status_code == 200
    assert [item["id"] for item in kk_resp.data["results"]] == [it_term.pk]


def test_dictionary_list_page_of_twenty_terms_uses_constant_queries(
    api_client, django_assert_max_num_queries, make_term_with_task, make_version_on_task
):
    for idx in range(25):
        _, task = make_term_with_task(text_ru=f"Термин страницы {idx}", source="", licence="")
        make_version_on_task(task, text_kk=f"бірінші нұсқа {idx}")
        make_version_on_task(task, text_kk=f"екінші нұсқа {idx}")

    with django_assert_max_num_queries(3):
        response = api_client.get(DICTIONARY_URL)
    assert response.status_code == 200
    assert response.data["count"] == 25
    assert len(response.data["results"]) == 20
    assert all(len(item["alternatives"]) == 2 for item in response.data["results"])


def test_dictionary_detail_shows_recommended_alternatives_and_pending_only_when_authenticated(
    api_client, user_factory, make_term_with_task, make_version_on_task
):
    moderator = user_factory(role="moderator")
    viewer = user_factory(role="participant")
    term, task = make_term_with_task(
        text_ru="Кэширование",
        definition="Промежуточное хранение данных.",
        domain=Domain.IT,
        source="Termincom.kz",
    )
    rec_v = make_version_on_task(task, text_kk="кэштеу")
    alt_v = make_version_on_task(task, text_kk="уақытша сақтау")
    sub_v = make_version_on_task(
        task, text_kk="ұсынылған нұсқа", status=ContributionVersion.Status.SUBMITTED
    )
    rev_v = make_version_on_task(
        task, text_kk="қаралудағы нұсқа", status=ContributionVersion.Status.IN_REVIEW
    )
    make_version_on_task(
        task, text_kk="қабылданбаған нұсқа", status=ContributionVersion.Status.REJECTED
    )
    make_version_on_task(task, text_kk="бақылау нұсқасы", is_control=True)
    make_version_on_task(task, text_kk="кері қайтарылған", is_withdrawn=True)

    recommend_term_variant(
        moderator=moderator,
        term_id=term.pk,
        version_id=rec_v.pk,
        reason="Ресми бекітілген термин.",
    )

    anon_resp = api_client.get(f"{DICTIONARY_URL}{term.pk}/")
    assert anon_resp.status_code == 200
    anon_data = anon_resp.json()
    assert anon_data["text_ru"] == "Кэширование"
    assert anon_data["definition"] == "Промежуточное хранение данных."
    assert anon_data["domain"] == Domain.IT
    assert anon_data["source"] == "Termincom.kz"
    assert anon_data["recommended"] == {
        "id": rec_v.pk,
        "text_kk": "кэштеу",
        "public_name": rec_v.contribution.author.public_name,
        "reason": "Ресми бекітілген термин.",
    }
    assert anon_data["alternatives"] == [
        {
            "id": alt_v.pk,
            "text_kk": "уақытша сақтау",
            "public_name": alt_v.contribution.author.public_name,
        }
    ]
    assert "pending" not in anon_data
    anon_raw = anon_resp.content.decode("utf-8")
    assert "ұсынылған нұсқа" not in anon_raw
    assert "қаралудағы нұсқа" not in anon_raw
    assert "@" not in anon_raw
    assert "email" not in anon_raw
    assert "username" not in anon_raw

    api_client.force_authenticate(viewer)
    auth_resp = api_client.get(f"{DICTIONARY_URL}{term.pk}/")
    assert auth_resp.status_code == 200
    auth_data = auth_resp.json()
    assert auth_data["alternatives"] == anon_data["alternatives"]
    assert auth_data["pending"] == [
        {
            "id": sub_v.pk,
            "text_kk": "ұсынылған нұсқа",
            "public_name": sub_v.contribution.author.public_name,
            "status": "submitted",
        },
        {
            "id": rev_v.pk,
            "text_kk": "қаралудағы нұсқа",
            "public_name": rev_v.contribution.author.public_name,
            "status": "in_review",
        },
    ]

    assert api_client.get(f"{DICTIONARY_URL}999999/").status_code == 404


def test_admin_action_and_service_recommend_variant_enforces_moderator_and_eligibility(
    user_factory, make_term_with_task, make_version_on_task
):
    moderator = user_factory(role="moderator", is_staff=True, is_superuser=True)
    reviewer = user_factory(role="reviewer", is_staff=True, is_superuser=True)
    participant = user_factory(role="participant", is_staff=True, is_superuser=True)

    term, task = make_term_with_task(text_ru="Интерфейс", domain=Domain.IT)
    other_term, other_task = make_term_with_task(text_ru="Сервер", domain=Domain.IT)

    eligible_v = make_version_on_task(task, text_kk="пайдаланушы интерфейсі")
    pending_v = make_version_on_task(
        task, text_kk="күтілудегі интерфейс", status=ContributionVersion.Status.SUBMITTED
    )
    foreign_v = make_version_on_task(other_task, text_kk="серверлік нұсқа")

    modeladmin = admin.site._registry[Term]
    selected = Term.objects.filter(pk=term.pk)

    for non_mod in (reviewer, participant):
        req = _admin_request(non_mod)
        assert not modeladmin.has_recommend_permission(req)
        assert not modeladmin.has_change_permission(req)
        with pytest.raises(PermissionDenied):
            recommend_variant(modeladmin, req, selected)

    for bad_version in (pending_v, foreign_v):
        bad_req = _admin_request(
            moderator,
            {
                "apply_recommendation": "1",
                "version": str(bad_version.pk),
                "reason": "Жарамсыз нұсқа",
            },
        )
        recommend_variant(modeladmin, bad_req, selected)
        term.refresh_from_db()
        assert term.recommended_version is None
        assert term.recommended_reason == ""
        messages_text = [m.message for m in get_messages(bad_req)]
        assert any("not an eligible accepted variant" in msg for msg in messages_text)

    ok_req = _admin_request(
        moderator,
        {
            "apply_recommendation": "1",
            "version": str(eligible_v.pk),
            "reason": "Түсінікті әрі дәл балама.",
        },
    )
    assert recommend_variant(modeladmin, ok_req, selected) is None
    term.refresh_from_db()
    assert term.recommended_version == eligible_v
    assert term.recommended_reason == "Түсінікті әрі дәл балама."
    assert term.recommended_by == moderator
    assert term.recommended_at is not None
