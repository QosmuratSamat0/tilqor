"""Stable FR-07 error codes and warning parameters across the API boundary."""

import pytest

from apps.contributions.domain import check_text


@pytest.mark.parametrize(
    ("text", "code", "params"),
    [
        ("  ", "empty_text", {}),
        ("x" * 201, "text_too_long", {"max_length": 200}),
        ("existing", "duplicate_variant", {}),
    ],
)
def test_check_errors_are_codes(text, code, params):
    assert check_text(text, max_length=200, existing_texts=["existing"]).errors == ((code, params),)


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("text", "code", "params"),
    [
        ("  ", "empty_text", {}),
        ("x" * 1001, "text_too_long", {"max_length": 1000}),
        ("existing", "duplicate_variant", {}),
    ],
)
def test_submission_error_codes(
    api_client, user_factory, make_translation_task, add_version, text, code, params
):
    task = make_translation_task()
    add_version(task, text_kk="existing")
    api_client.force_authenticate(user_factory())
    response = api_client.post(f"/api/tasks/{task.pk}/contributions/", {"text_kk": text})
    assert response.status_code == 400
    assert response.data["codes"] == {"text_kk": [code]}
    assert isinstance(response.data["text_kk"][0], str)
    assert response.data.get("params", {}).get("text_kk", {}) == params


@pytest.mark.django_db
def test_terms_and_already_submitted_codes(api_client, user_factory, make_translation_task):
    task = make_translation_task()
    api_client.force_authenticate(user_factory(accepted_terms=False))
    response = api_client.post(f"/api/tasks/{task.pk}/contributions/", {"text_kk": "text"})
    assert response.status_code == 403
    assert response.data["codes"] == {"accept_terms": ["terms_not_accepted"]}
    api_client.force_authenticate(user_factory())
    url = f"/api/tasks/{task.pk}/contributions/"
    assert api_client.post(url, {"text_kk": "text"}).status_code == 201
    response = api_client.post(url, {"text_kk": "text"})
    assert response.status_code == 409
    assert response.data["codes"] == {"task": ["already_submitted"]}


@pytest.mark.django_db
def test_warning_api_shape(api_client, user_factory, make_translation_task):
    task = make_translation_task()
    api_client.force_authenticate(user_factory())
    response = api_client.post(f"/api/tasks/{task.pk}/contributions/", {"text_kk": "text и но"})
    assert response.status_code == 201
    warnings = response.data["warnings"]["text_kk"]
    assert [warning["code"] for warning in warnings] == ["no_kazakh_letters", "russian_connectors"]
    assert warnings[0]["params"] == {}
    assert warnings[1]["params"] == {"connectors": ["и", "но"]}
    assert all(warning["message"] for warning in warnings)
