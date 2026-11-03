"""FR-19, NFR-04: daily catalogue word of the day, top words, and connector hints."""

import pytest
from django.contrib import admin
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory

from apps.contributions.models import ContributionVersion
from apps.glossary.admin_actions import publish_connector_hints, unpublish_connector_hints
from apps.glossary.models import ConnectorHint
from apps.glossary.services import recommend_term_variant

pytestmark = pytest.mark.django_db
CATALOGUE_URL = "/api/catalogue/today/"


def _admin_request(user):
    request = RequestFactory().post("/admin/glossary/connectorhint/")
    request.user = user
    request.session = {}
    request._messages = FallbackStorage(request)
    return request


def test_catalogue_today_empty_state_and_invalid_date(api_client):
    empty_resp = api_client.get(CATALOGUE_URL, {"date": "2026-11-03"})
    assert empty_resp.status_code == 200
    assert empty_resp.json() == {
        "date": "2026-11-03",
        "word_of_the_day": None,
        "top_words": [],
        "connector_hints": [],
    }

    bad_date = api_client.get(CATALOGUE_URL, {"date": "2026-99-99"})
    assert bad_date.status_code == 400
    assert "date" in bad_date.json()


def test_catalogue_excludes_sourced_term_without_licence(
    api_client, make_term_with_task, make_version_on_task, add_preference
):
    _, unlicensed_task = make_term_with_task(
        text_ru="Нелицензированный термин", source="External Source", licence=""
    )
    unlicensed_v = make_version_on_task(unlicensed_task, text_kk="жабық нұсқа")
    add_preference(unlicensed_v)

    resp = api_client.get(CATALOGUE_URL, {"date": "2026-11-03"})
    assert resp.status_code == 200
    assert resp.json()["word_of_the_day"] is None
    assert resp.json()["top_words"] == []


def test_catalogue_word_of_the_day_is_deterministic_varies_by_date_and_ignores_ineligible(
    api_client, user_factory, make_term_with_task, make_version_on_task
):
    moderator = user_factory(role="moderator")
    eligible_terms = []
    for idx in range(6):
        term, task = make_term_with_task(text_ru=f"Термин каталога {idx}")
        first_v = make_version_on_task(task, text_kk=f"бірінші нұсқа {idx}")
        second_v = make_version_on_task(task, text_kk=f"ұсынылған нұсқа {idx}")
        if idx % 2 == 0:
            recommend_term_variant(
                moderator=moderator,
                term_id=term.pk,
                version_id=second_v.pk,
                reason="Таңдалған",
            )
            eligible_terms.append((term.pk, second_v.text_kk))
        else:
            eligible_terms.append((term.pk, first_v.text_kk))

    _, pending_task = make_term_with_task(text_ru="Неготовый термин")
    make_version_on_task(
        pending_task, text_kk="күтілуде", status=ContributionVersion.Status.SUBMITTED
    )
    _, rejected_task = make_term_with_task(text_ru="Отклонённый термин")
    make_version_on_task(
        rejected_task, text_kk="қабылданбаған", status=ContributionVersion.Status.REJECTED
    )
    _, control_task = make_term_with_task(text_ru="Контрольный термин")
    make_version_on_task(control_task, text_kk="бақылау", is_control=True)
    _, withdrawn_task = make_term_with_task(text_ru="Отозванный термин")
    make_version_on_task(withdrawn_task, text_kk="қайтарылған", is_withdrawn=True)

    resp_1 = api_client.get(CATALOGUE_URL, {"date": "2026-11-03"}).json()
    resp_2 = api_client.get(CATALOGUE_URL, {"date": "2026-11-03"}).json()
    assert resp_1["word_of_the_day"] == resp_2["word_of_the_day"]
    assert (
        resp_1["word_of_the_day"]["term_id"],
        resp_1["word_of_the_day"]["text_kk"],
    ) in eligible_terms

    chosen_across_days = {
        api_client.get(CATALOGUE_URL, {"date": f"2026-11-0{day}"})
        .json()["word_of_the_day"]["term_id"]
        for day in range(1, 9)
    }
    assert len(chosen_across_days) > 1


def test_catalogue_top_words_orders_by_preferences_and_caps_at_ten(
    api_client, user_factory, make_term_with_task, make_version_on_task, add_preference
):
    versions = []
    for idx in range(12):
        _, task = make_term_with_task(text_ru=f"Популярный термин {idx}")
        version = make_version_on_task(task, text_kk=f"нұсқа {idx}")
        versions.append(version)

    for _ in range(3):
        add_preference(versions[4])
    for _ in range(2):
        add_preference(versions[2])
        add_preference(versions[1])

    _, ineligible_task = make_term_with_task(text_ru="Скрытый термин")
    ineligible_v = make_version_on_task(
        ineligible_task,
        text_kk="күтілудегі",
        status=ContributionVersion.Status.SUBMITTED,
    )
    for _ in range(5):
        add_preference(ineligible_v)

    resp = api_client.get(CATALOGUE_URL, {"date": "2026-11-03"})
    assert resp.status_code == 200
    top_words = resp.json()["top_words"]
    assert len(top_words) == 10
    assert top_words[0]["id"] == versions[4].pk
    assert top_words[0]["preference_count"] == 3
    assert [top_words[1]["id"], top_words[2]["id"]] == [versions[1].pk, versions[2].pk]
    assert all(item["id"] != ineligible_v.pk for item in top_words)

    raw = resp.content.decode("utf-8")
    assert "@" not in raw
    assert "email" not in raw
    assert "username" not in raw


def test_catalogue_connector_hints_only_published_and_moderator_admin_actions(
    api_client, user_factory, make_connector_hint
):
    published_hint = make_connector_hint(
        text_ru="потому что", text_kk="себебі", is_published=True
    )
    draft_hint = make_connector_hint(
        text_ru="однако", text_kk="алайда", is_published=False
    )

    resp = api_client.get(CATALOGUE_URL, {"date": "2026-11-03"})
    assert resp.status_code == 200
    hints = resp.json()["connector_hints"]
    assert [h["id"] for h in hints] == [published_hint.pk]

    moderator = user_factory(role="moderator", is_staff=True, is_superuser=True)
    reviewer = user_factory(role="reviewer", is_staff=True, is_superuser=True)
    modeladmin = admin.site._registry[ConnectorHint]

    with pytest.raises(PermissionDenied):
        publish_connector_hints(
            modeladmin, _admin_request(reviewer), ConnectorHint.objects.filter(pk=draft_hint.pk)
        )

    publish_connector_hints(
        modeladmin, _admin_request(moderator), ConnectorHint.objects.filter(pk=draft_hint.pk)
    )
    draft_hint.refresh_from_db()
    assert draft_hint.is_published is True

    resp_after = api_client.get(CATALOGUE_URL, {"date": "2026-11-03"})
    assert [h["id"] for h in resp_after.json()["connector_hints"]] == [
        published_hint.pk,
        draft_hint.pk,
    ]

    unpublish_connector_hints(
        modeladmin, _admin_request(moderator), ConnectorHint.objects.filter(pk=draft_hint.pk)
    )
    draft_hint.refresh_from_db()
    assert draft_hint.is_published is False
