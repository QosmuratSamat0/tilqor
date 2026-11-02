"""FR-03, FR-04, FR-05: task listing, admin permissions, blind translation and term variants."""

from random import Random

import pytest
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory

from apps.accounts.models import User
from apps.contributions.admin import activate_tasks, deactivate_tasks
from apps.contributions.models import ContributionVersion, Task, VariantPreference
from apps.contributions.selectors import visible_variants
from common.choices import Domain

pytestmark = pytest.mark.django_db
TASKS_URL = "/api/tasks/"


@pytest.fixture
def all_tasks(make_translation_task, make_term_task):
    tasks = {}
    for domain in Domain.values:
        tasks[(domain, Task.Type.TRANSLATION)] = make_translation_task(domain=domain)
        tasks[(domain, Task.Type.TERM)] = make_term_task(domain=domain)
    return tasks


def test_task_list_filters_across_all_domains_and_types(
    api_client, user_factory, all_tasks, make_translation_task
):
    inactive = make_translation_task(domain=Domain.IT, is_active=False)
    api_client.force_authenticate(user_factory())

    all_response = api_client.get(TASKS_URL)
    assert all_response.status_code == 200
    returned_ids = {row["id"] for row in all_response.data["results"]}
    assert returned_ids == {task.pk for task in all_tasks.values()}
    assert inactive.pk not in returned_ids

    for domain in Domain.values:
        resp = api_client.get(TASKS_URL, {"domain": domain})
        assert resp.status_code == 200
        assert {row["id"] for row in resp.data["results"]} == {
            all_tasks[(domain, Task.Type.TRANSLATION)].pk,
            all_tasks[(domain, Task.Type.TERM)].pk,
        }

    for task_type in Task.Type.values:
        resp = api_client.get(TASKS_URL, {"type": task_type})
        assert resp.status_code == 200
        assert {row["id"] for row in resp.data["results"]} == {
            all_tasks[(domain, task_type)].pk for domain in Domain.values
        }

    combined = api_client.get(TASKS_URL, {"domain": Domain.MEDICINE, "type": Task.Type.TERM})
    assert combined.status_code == 200
    assert [row["id"] for row in combined.data["results"]] == [
        all_tasks[(Domain.MEDICINE, Task.Type.TERM)].pk
    ]


def test_task_list_empty_state_and_invalid_filters(api_client, user_factory):
    api_client.force_authenticate(user_factory())

    empty_resp = api_client.get(TASKS_URL, {"domain": Domain.ENGINEERING})
    assert empty_resp.status_code == 200
    assert empty_resp.data == {"results": []}

    bad_domain = api_client.get(TASKS_URL, {"domain": "invalid"})
    assert bad_domain.status_code == 400
    assert "domain" in bad_domain.data

    bad_type = api_client.get(TASKS_URL, {"type": "invalid"})
    assert bad_type.status_code == 400
    assert "type" in bad_type.data


def test_inactive_task_is_hidden_and_refuses_submission_and_preference(
    api_client, user_factory, make_translation_task, make_term_task, add_version
):
    user = user_factory()
    api_client.force_authenticate(user)
    inactive_translation = make_translation_task(is_active=False)
    inactive_term = make_term_task(is_active=False)
    variant = add_version(inactive_term, text_kk="Есептегіш")

    assert api_client.get(f"{TASKS_URL}{inactive_translation.pk}/").status_code == 404
    submit_resp = api_client.post(
        f"{TASKS_URL}{inactive_translation.pk}/contributions/",
        {"text_kk": "Дәрігер науқасты қарады."},
    )
    assert submit_resp.status_code == 409
    assert "task" in submit_resp.data

    pref_resp = api_client.put(
        f"{TASKS_URL}{inactive_term.pk}/preference/",
        {"version_id": variant.pk},
    )
    assert pref_resp.status_code == 409
    assert "task" in pref_resp.data


def test_task_admin_permissions_and_actions(user_factory, make_translation_task):
    task = make_translation_task(is_active=True)
    modeladmin = admin.site._registry[Task]
    queryset = Task.objects.filter(pk=task.pk)

    for role in (User.Role.PARTICIPANT, User.Role.REVIEWER):
        user = user_factory(role=role, is_staff=True, is_superuser=True)
        request = RequestFactory().post("/admin/contributions/task/")
        request.user = user
        assert not modeladmin.has_add_permission(request)
        assert not modeladmin.has_change_permission(request, task)
        assert not modeladmin.has_delete_permission(request, task)
        with pytest.raises(PermissionDenied):
            deactivate_tasks(modeladmin, request, queryset)
        with pytest.raises(PermissionDenied):
            activate_tasks(modeladmin, request, queryset)

    for role in (User.Role.MODERATOR, User.Role.ADMIN):
        mod = user_factory(role=role, is_staff=True, is_superuser=True)
        request = RequestFactory().post("/admin/contributions/task/")
        request.user = mod
        assert modeladmin.has_add_permission(request)
        assert modeladmin.has_change_permission(request, task)
        assert modeladmin.has_delete_permission(request, task)
        deactivate_tasks(modeladmin, request, queryset)
        task.refresh_from_db()
        assert not task.is_active
        activate_tasks(modeladmin, request, queryset)
        task.refresh_from_db()
        assert task.is_active


def test_blind_translation_hides_variants_until_own_submission_and_filters_unsafe_rows(
    api_client, user_factory, make_translation_task, add_version
):
    task = make_translation_task()
    other_author = user_factory(username="secret_login", display_name="Айгүл")
    visible_other = add_version(
        task, text_kk="Бірінші дұрыс аударма.", author=other_author, status="accepted"
    )
    add_version(
        task,
        text_kk="Бақылау нұсқасы.",
        is_control=True,
        reference_decision="accept",
    )
    add_version(task, text_kk="Қабылданбаған нұсқа.", status="rejected")
    add_version(task, text_kk="Қайтарып алынған нұсқа.", status="accepted", is_withdrawn=True)

    participant = user_factory(username="participant_login", display_name="Ерлан")
    api_client.force_authenticate(participant)

    before = api_client.get(f"{TASKS_URL}{task.pk}/")
    assert before.status_code == 200
    assert before.data["variants"] == []

    create_resp = api_client.post(
        f"{TASKS_URL}{task.pk}/contributions/",
        {"text_kk": "Менің өз аудармам."},
    )
    assert create_resp.status_code == 201
    assert create_resp.data["version"]["status"] == "submitted"
    assert create_resp.data["version"]["number"] == 1
    assert create_resp.data["warnings"] == {}

    duplicate_submission = api_client.post(
        f"{TASKS_URL}{task.pk}/contributions/",
        {"text_kk": "Екінші рет жіберу."},
    )
    assert duplicate_submission.status_code == 409

    after = api_client.get(f"{TASKS_URL}{task.pk}/")
    assert after.status_code == 200
    variants = after.data["variants"]
    assert [v["id"] for v in variants] == [visible_other.pk]
    variant_data = variants[0]
    assert set(variant_data) == {"id", "text_kk", "status", "public_name", "created_at"}
    assert variant_data["public_name"] == "Айгүл"
    raw_json = after.content.decode("utf-8")
    assert "secret_login" not in raw_json
    assert other_author.email not in raw_json


def test_term_variants_visible_before_submission_without_counts_and_shuffled(
    api_client, user_factory, make_term_task, add_version
):
    task = make_term_task()
    created_ids = [
        add_version(task, text_kk=f"Термин нұсқасы {i}").pk for i in range(1, 9)
    ]
    add_version(task, text_kk="Қабылданбаған", status="rejected")
    add_version(task, text_kk="Бақылау", is_control=True, reference_decision="accept")
    add_version(task, text_kk="Қайтарылған", is_withdrawn=True)

    user = user_factory()
    api_client.force_authenticate(user)
    response = api_client.get(f"{TASKS_URL}{task.pk}/")
    assert response.status_code == 200
    variants = response.data["variants"]
    assert {v["id"] for v in variants} == set(created_ids)
    for item in variants:
        assert set(item) == {"id", "text_kk", "status", "public_name", "created_at"}

    seeded_one = [v.pk for v in visible_variants(task=task, user=user, rng=Random(42))]
    seeded_two = [v.pk for v in visible_variants(task=task, user=user, rng=Random(42))]
    assert seeded_one == seeded_two
    assert seeded_one != created_ids


def test_term_preference_create_replace_and_validation(
    api_client, user_factory, make_term_task, make_translation_task, add_version
):
    term_task = make_term_task()
    other_term_task = make_term_task()
    translation_task = make_translation_task()

    v1 = add_version(term_task, text_kk="Жасанды зерде")
    v2 = add_version(term_task, text_kk="Жасанды интеллект")
    rejected_v = add_version(term_task, text_kk="Қате нұсқа", status="rejected")
    control_v = add_version(
        term_task, text_kk="Бақылау нұсқа", is_control=True, reference_decision="accept"
    )
    foreign_v = add_version(other_term_task, text_kk="Басқа термин")

    user = user_factory()
    api_client.force_authenticate(user)

    first = api_client.put(f"{TASKS_URL}{term_task.pk}/preference/", {"version_id": v1.pk})
    assert first.status_code == 200
    assert first.data["version_id"] == v1.pk
    assert VariantPreference.objects.filter(user=user, task=term_task).count() == 1

    second = api_client.put(f"{TASKS_URL}{term_task.pk}/preference/", {"version_id": v2.pk})
    assert second.status_code == 200
    assert second.data["version_id"] == v2.pk
    assert VariantPreference.objects.filter(user=user, task=term_task).count() == 1

    v1.refresh_from_db()
    v2.refresh_from_db()
    assert v1.status == ContributionVersion.Status.SUBMITTED
    assert v2.status == ContributionVersion.Status.SUBMITTED

    for bad_id in (foreign_v.pk, rejected_v.pk, control_v.pk, 999999):
        bad_resp = api_client.put(
            f"{TASKS_URL}{term_task.pk}/preference/", {"version_id": bad_id}
        )
        assert bad_resp.status_code == 400
        assert "version_id" in bad_resp.data

    trans_resp = api_client.put(
        f"{TASKS_URL}{translation_task.pk}/preference/", {"version_id": v1.pk}
    )
    assert trans_resp.status_code == 400
    assert "task" in trans_resp.data
    assert VariantPreference.objects.get(user=user, task=term_task).version_id == v2.pk

