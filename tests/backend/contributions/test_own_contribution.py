"""Task detail exposes only the current user's latest submission, with bounded queries."""

import pytest
from django.contrib.auth.models import AnonymousUser

from apps.contributions.selectors import task_detail

pytestmark = pytest.mark.django_db


def test_own_summary_latest_status_and_privacy(
    api_client,
    user_factory,
    make_translation_task,
    add_version,
):
    author, viewer = user_factory(), user_factory()
    task = make_translation_task()
    version = add_version(task, author=author, status="needs_edit")
    add_version(task, author=author, number=2, status="in_review", text_kk="updated")
    assert task_detail(task_id=task.pk, user=AnonymousUser()).own_contribution is None
    # Existing authentication policy is retained; anonymous responses expose no own submission.
    anonymous = api_client.get(f"/api/tasks/{task.pk}/")
    assert anonymous.status_code == 403
    assert "own_contribution" not in anonymous.data
    api_client.force_authenticate(viewer)
    assert api_client.get(f"/api/tasks/{task.pk}/").data["own_contribution"] is None
    api_client.force_authenticate(author)
    assert api_client.get(f"/api/tasks/{task.pk}/").data["own_contribution"] == {
        "id": version.contribution_id,
        "status": "in_review",
        "latest_version_number": 2,
    }
    assert all(
        "own_contribution" not in row for row in api_client.get("/api/tasks/").data["results"]
    )


def test_detail_query_budget(
    api_client,
    django_assert_max_num_queries,
    user_factory,
    make_translation_task,
    make_term_task,
    add_version,
):
    author = user_factory()
    for task in (make_translation_task(), make_term_task()):
        add_version(task, author=author)
        for _ in range(4):
            add_version(task)
        api_client.force_authenticate(author)
        with django_assert_max_num_queries(3):
            response = api_client.get(f"/api/tasks/{task.pk}/")
        assert response.status_code == 200
    with django_assert_max_num_queries(2):
        assert api_client.get("/api/tasks/").status_code == 200
