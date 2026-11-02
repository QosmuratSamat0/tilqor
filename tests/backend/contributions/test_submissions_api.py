"""FR-07, FR-08, FR-13, NFR-01: automatic checks, Unicode fidelity, own submissions and versions."""

import unicodedata

import pytest

from apps.contributions.models import Contribution, ContributionVersion
from apps.verification.models import Finalization, QualitySettings
from apps.verification.services import resolve_version, submit_review

pytestmark = pytest.mark.django_db
TASKS_URL = "/api/tasks/"
CONTRIBUTIONS_URL = "/api/contributions/"


@pytest.mark.parametrize(
    ("method", "url", "payload"),
    [
        ("get", "/api/tasks/", None),
        ("get", "/api/tasks/1/", None),
        ("post", "/api/tasks/1/contributions/", {"text_kk": "Қазақша"}),
        ("put", "/api/tasks/1/preference/", {"version_id": 1}),
        ("get", "/api/contributions/me/", None),
        ("post", "/api/contributions/1/versions/", {"text_kk": "Қазақша"}),
    ],
)
def test_anonymous_requests_are_refused(api_client, method, url, payload):
    caller = getattr(api_client, method)
    response = caller(url, payload) if payload is not None else caller(url)
    assert response.status_code == 403


def test_automatic_checks_reject_empty_too_long_and_duplicate_without_saving(
    api_client, user_factory, make_translation_task, make_term_task, add_version
):
    translation_task = make_translation_task()
    term_task = make_term_task()
    existing_text = "Науқасқа емдеу курсы тағайындалды \u04db"
    add_version(translation_task, text_kk=existing_text)

    user = user_factory()
    api_client.force_authenticate(user)

    for invalid_text in [
        "",
        "   \n\t ",
        "ә" * 1001,
        existing_text,
        "  " + unicodedata.normalize("NFD", existing_text) + "  ",
    ]:
        resp = api_client.post(
            f"{TASKS_URL}{translation_task.pk}/contributions/",
            {"text_kk": invalid_text},
        )
        assert resp.status_code == 400
        assert "text_kk" in resp.data
        assert not Contribution.objects.filter(task=translation_task, author=user).exists()

    term_too_long = api_client.post(
        f"{TASKS_URL}{term_task.pk}/contributions/",
        {"text_kk": "қ" * 201},
    )
    assert term_too_long.status_code == 400
    assert "text_kk" in term_too_long.data
    assert not Contribution.objects.filter(task=term_task, author=user).exists()


def test_warnings_returned_with_text_kk_and_record_is_saved(
    api_client, user_factory, make_translation_task
):
    task = make_translation_task()
    user = user_factory()
    api_client.force_authenticate(user)

    response = api_client.post(
        f"{TASKS_URL}{task.pk}/contributions/",
        {"text_kk": "  Бизнес жоспар и максат но ناتиже  "},
    )
    assert response.status_code == 201
    assert "text_kk" in response.data["warnings"]
    assert len(response.data["warnings"]["text_kk"]) == 2
    version = ContributionVersion.objects.get(pk=response.data["version"]["id"])
    assert version.text_kk == "Бизнес жоспар и максат но ناتиже"


def test_kazakh_and_russian_unicode_survives_round_trip(
    api_client, user_factory, make_translation_task
):
    kazakh_sample = "Әә Ғғ Ққ Ңң Өө Ұұ Үү Һһ Іі — Қазақ тілі мен русский текст"
    task = make_translation_task(text_ru="Проверка всех букв: ё, й, щ, ъ, ы, э, ю, я.")
    user = user_factory()
    api_client.force_authenticate(user)

    post_resp = api_client.post(
        f"{TASKS_URL}{task.pk}/contributions/",
        {"text_kk": f"  {unicodedata.normalize('NFD', kazakh_sample)}  "},
    )
    assert post_resp.status_code == 201
    assert post_resp.data["version"]["text_kk"] == kazakh_sample

    me_resp = api_client.get(f"{CONTRIBUTIONS_URL}me/")
    assert me_resp.status_code == 200
    assert me_resp.data[0]["versions"][0]["text_kk"] == kazakh_sample
    assert me_resp.data[0]["text_ru"] == "Проверка всех букв: ё, й, щ, ъ, ы, э, ю, я."


def test_own_submissions_show_all_statuses_and_matching_reasons_without_reviewer_leak(
    api_client, user_factory, make_translation_task, add_version
):
    author = user_factory(username="author_one")
    other_user = user_factory(username="author_two")
    moderator = user_factory(username="mod_secret", role="moderator")
    reviewers = [
        user_factory(username=f"rev_secret_{i}", role="reviewer") for i in range(5)
    ]
    settings = QualitySettings.objects.get(is_active=True)

    submitted_v = add_version(
        make_translation_task(), text_kk="Жіберілген мәтін", author=author
    )
    in_review_v = add_version(
        make_translation_task(), text_kk="Тексерілудегі мәтін", author=author
    )
    submit_review(
        reviewer=reviewers[0],
        version_id=in_review_v.pk,
        decision="reject",
        reason="Әлі шешім жоқ",
    )

    accepted_v = add_version(
        make_translation_task(),
        text_kk="Қабылданған мәтін",
        author=author,
        status="accepted",
    )
    Finalization.objects.create(
        version=accepted_v,
        decision="accept",
        quality_settings=settings,
        reason="",
    )

    auto_rejected_v = add_version(
        make_translation_task(), text_kk="Автоматты қабылданбаған мәтін", author=author
    )
    submit_review(
        reviewer=reviewers[0],
        version_id=auto_rejected_v.pk,
        decision="edit",
        reason="Бұл edit себебі көрінбеуі тиіс.",
    )
    submit_review(
        reviewer=reviewers[1],
        version_id=auto_rejected_v.pk,
        decision="reject",
        reason="Сөз тәртібі қате.",
    )
    submit_review(
        reviewer=reviewers[2],
        version_id=auto_rejected_v.pk,
        decision="reject",
        reason="Мағынасы бұрмаланған.",
    )

    mod_needs_edit_v = add_version(
        make_translation_task(), text_kk="Модератор шешкен мәтін", author=author
    )
    for reviewer, decision, reason in zip(
        reviewers,
        ["accept", "reject", "edit", "accept", "edit"],
        ["", "Қате аударма", "Жалғауын түзету керек.", "", "Стилін жөндеу қажет."],
        strict=True,
    ):
        submit_review(
            reviewer=reviewer,
            version_id=mod_needs_edit_v.pk,
            decision=decision,
            reason=reason,
        )
    resolve_version(
        moderator=moderator,
        version_id=mod_needs_edit_v.pk,
        decision="edit",
        reason="Модератор: терминді нақтылаңыз.",
    )

    add_version(make_translation_task(), text_kk="Басқа автордың аудармасы", author=other_user)

    api_client.force_authenticate(author)
    response = api_client.get(f"{CONTRIBUTIONS_URL}me/")
    assert response.status_code == 200
    assert len(response.data) == 5

    by_status = {row["versions"][0]["status"]: row["versions"][0] for row in response.data}
    assert set(by_status) == {"submitted", "in_review", "accepted", "rejected", "needs_edit"}
    assert by_status["submitted"]["id"] == submitted_v.pk
    assert by_status["submitted"]["decision_reasons"] == []
    assert by_status["in_review"]["decision_reasons"] == []
    assert by_status["accepted"]["decision_reasons"] == []
    assert by_status["rejected"]["decision_reasons"] == [
        "Сөз тәртібі қате.",
        "Мағынасы бұрмаланған.",
    ]
    assert by_status["needs_edit"]["decision_reasons"] == [
        "Модератор: терминді нақтылаңыз.",
        "Жалғауын түзету керек.",
        "Стилін жөндеу қажет.",
    ]

    raw_json = response.content.decode("utf-8")
    for secret_user in [moderator, *reviewers]:
        assert secret_user.username not in raw_json
        assert secret_user.email not in raw_json
    assert "Бұл edit себебі көрінбеуі тиіс." not in raw_json

    for row in response.data:
        for version_row in row["versions"]:
            assert set(version_row) == {
                "id",
                "number",
                "text_kk",
                "status",
                "decision_reasons",
                "created_at",
            }

    api_client.force_authenticate(other_user)
    other_resp = api_client.get(f"{CONTRIBUTIONS_URL}me/")
    assert len(other_resp.data) == 1
    assert other_resp.data[0]["versions"][0]["text_kk"] == "Басқа автордың аудармасы"


def test_own_submissions_prefetch_avoids_n_plus_one_queries(
    api_client, django_assert_max_num_queries, user_factory, make_translation_task, add_version
):
    author = user_factory()
    reviewers = [user_factory(role="reviewer") for _ in range(3)]
    settings = QualitySettings.objects.get(is_active=True)

    for idx in range(3):
        task = make_translation_task()
        v1 = add_version(
            task,
            text_kk=f"Бірінші нұсқа {idx}",
            author=author,
            number=1,
            status="needs_edit",
        )
        Finalization.objects.create(
            version=v1,
            decision="edit",
            quality_settings=settings,
            reason=f"Себеп {idx}",
        )
        v2 = add_version(
            task,
            text_kk=f"Екінші нұсқа {idx}",
            author=author,
            number=2,
        )
        for rev_idx, reviewer in enumerate(reviewers):
            submit_review(
                reviewer=reviewer,
                version_id=v2.pk,
                decision="reject",
                reason=f"Пікір {idx}-{rev_idx}",
            )

    api_client.force_authenticate(author)
    with django_assert_max_num_queries(4):
        response = api_client.get(f"{CONTRIBUTIONS_URL}me/")
    assert response.status_code == 200
    assert len(response.data) == 3
    assert all(len(item["versions"]) == 2 for item in response.data)


def test_new_version_after_needs_edit_preserves_history_and_enforces_rules(
    api_client, user_factory, make_translation_task, add_version
):
    author = user_factory()
    non_author = user_factory()
    moderator = user_factory(role="moderator")
    reviewers = [user_factory(role="reviewer") for _ in range(5)]

    task = make_translation_task()
    v1 = add_version(task, text_kk="Бірінші нұсқа мәтіні.", author=author)
    for reviewer, decision in zip(
        reviewers, ["accept", "reject", "edit", "accept", "reject"], strict=True
    ):
        submit_review(reviewer=reviewer, version_id=v1.pk, decision=decision, reason="Себеп")
    resolve_version(
        moderator=moderator,
        version_id=v1.pk,
        decision="edit",
        reason="Терминді нақтылау керек.",
    )
    v1.refresh_from_db()
    assert v1.status == ContributionVersion.Status.NEEDS_EDIT

    contribution = v1.contribution
    url = f"{CONTRIBUTIONS_URL}{contribution.pk}/versions/"

    api_client.force_authenticate(non_author)
    assert api_client.post(url, {"text_kk": "Бөтен адамның түзетуі."}).status_code == 403

    api_client.force_authenticate(author)
    dup_resp = api_client.post(url, {"text_kk": "Бірінші нұсқа мәтіні."})
    assert dup_resp.status_code == 400
    assert "text_kk" in dup_resp.data
    assert contribution.versions.count() == 1

    ok_resp = api_client.post(url, {"text_kk": "Түзетілген екінші нұсқа мәтіні."})
    assert ok_resp.status_code == 201
    assert ok_resp.data["number"] == 2
    assert ok_resp.data["status"] == "submitted"
    assert ok_resp.data["text_kk"] == "Түзетілген екінші нұсқа мәтіні."

    v2 = ContributionVersion.objects.get(pk=ok_resp.data["id"])
    assert v2.reviews.count() == 0
    v1.refresh_from_db()
    assert v1.status == ContributionVersion.Status.NEEDS_EDIT
    assert v1.reviews.count() == 5
    assert v1.finalization.reason == "Терминді нақтылау керек."

    me_resp = api_client.get(f"{CONTRIBUTIONS_URL}me/")
    versions_data = me_resp.data[0]["versions"]
    assert [(v["number"], v["status"], v["decision_reasons"]) for v in versions_data] == [
        (1, "needs_edit", ["Терминді нақтылау керек.", "Себеп"]),
        (2, "submitted", []),
    ]

    for non_editable_status in ("submitted", "in_review", "accepted", "rejected"):
        other_task = make_translation_task()
        other_v = add_version(
            other_task,
            text_kk=f"Мәтін {non_editable_status}",
            author=author,
            status=non_editable_status,
        )
        conflict_resp = api_client.post(
            f"{CONTRIBUTIONS_URL}{other_v.contribution_id}/versions/",
            {"text_kk": "Жаңа мәтін нұсқасы."},
        )
        assert conflict_resp.status_code == 409
