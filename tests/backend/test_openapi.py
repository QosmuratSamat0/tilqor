"""OpenAPI 3.0 schema and Swagger UI checks (TIL-32)."""

import re

import pytest
import yaml
from django.urls import URLPattern, URLResolver

from apps.accounts.models import User
from apps.contributions.models import Contribution, ContributionVersion, SourceSentence, Task
from common.choices import Domain
from config.urls import urlpatterns

EXCLUDED_API_PATHS = {"/api/schema/", "/api/docs/"}


def _collect_api_paths(patterns, prefix="") -> set[str]:
    paths: set[str] = set()
    for entry in patterns:
        segment = str(entry.pattern)
        current = f"{prefix}{segment}"
        if isinstance(entry, URLResolver):
            paths |= _collect_api_paths(entry.url_patterns, current)
        elif isinstance(entry, URLPattern):
            normalized = "/" + current.lstrip("/")
            normalized = re.sub(r"<(?:\w+:)?(\w+)>", r"{\1}", normalized)
            if normalized.startswith("/api/") and normalized not in EXCLUDED_API_PATHS:
                paths.add(normalized)
    return paths


def _collect_response_schema_refs(schema: dict) -> set[str]:
    refs: set[str] = set()

    def walk(node):
        if isinstance(node, dict):
            ref = node.get("$ref")
            if isinstance(ref, str) and ref.startswith("#/components/schemas/"):
                refs.add(ref.rsplit("/", 1)[-1])
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    for path_item in schema["paths"].values():
        for operation in path_item.values():
            if isinstance(operation, dict) and "responses" in operation:
                walk(operation["responses"])
    return refs


def test_schema_endpoint_is_public_and_valid_yaml_and_json(api_client):
    yaml_resp = api_client.get("/api/schema/")
    assert yaml_resp.status_code == 200
    schema = yaml.safe_load(yaml_resp.content)
    assert schema["openapi"].startswith("3.0.")
    assert schema["info"]["title"] == "Tilqor API"
    assert schema["info"]["version"] == "0.1.0"

    json_resp = api_client.get("/api/schema/", {"format": "json"})
    assert json_resp.status_code == 200
    assert json_resp.json()["paths"] == schema["paths"]


def test_swagger_ui_is_public(api_client):
    response = api_client.get("/api/docs/")
    assert response.status_code == 200
    assert "swagger-ui" in response.content.decode("utf-8").lower()


def test_schema_contains_all_api_paths_tags_params_and_session_security(api_client):
    schema = yaml.safe_load(api_client.get("/api/schema/").content)
    expected_paths = _collect_api_paths(urlpatterns)
    assert expected_paths
    assert set(schema["paths"]) == expected_paths

    security_schemes = schema["components"]["securitySchemes"]
    assert "cookieAuth" in security_schemes
    assert security_schemes["cookieAuth"]["type"] == "apiKey"
    assert security_schemes["cookieAuth"]["in"] == "cookie"

    tasks_params = {
        param["name"]: param for param in schema["paths"]["/api/tasks/"]["get"]["parameters"]
    }
    assert set(tasks_params) == {"domain", "type", "page"}
    assert set(tasks_params["domain"]["schema"]["enum"]) == set(Domain.values)
    assert set(tasks_params["type"]["schema"]["enum"]) == set(Task.Type.values)


def test_no_response_component_exposes_password(api_client):
    schema = yaml.safe_load(api_client.get("/api/schema/").content)
    schemas = schema["components"]["schemas"]
    response_refs = _collect_response_schema_refs(schema)
    assert response_refs

    for name in response_refs:
        properties = schemas[name].get("properties", {})
        assert "password" not in properties, f"Response schema {name} must not expose password"

    for name, component in schemas.items():
        if not name.endswith("Request"):
            properties = component.get("properties", {})
            assert "password" not in properties


def test_error_components_and_endpoint_error_references(api_client):
    schema = yaml.safe_load(api_client.get("/api/schema/").content)
    schemas = schema["components"]["schemas"]

    assert "DetailError" in schemas
    assert "FieldErrors" in schemas
    assert schemas["DetailError"]["properties"]["detail"]["type"] == "string"
    assert schemas["DetailError"]["example"] == {
        "detail": "Authentication credentials were not provided."
    }
    assert schemas["FieldErrors"]["additionalProperties"] == {
        "type": "array",
        "items": {"type": "string"},
    }
    assert schemas["FieldErrors"]["example"] == {"text_kk": ["Text cannot be empty."]}

    contrib_400 = schema["paths"]["/api/tasks/{task_id}/contributions/"]["post"]["responses"][
        "400"
    ]["content"]["application/json"]
    assert contrib_400["schema"] == {"$ref": "#/components/schemas/FieldErrors"}
    assert "FieldErrorsExample" in contrib_400["examples"]

    reviews_409 = schema["paths"]["/api/reviews/"]["post"]["responses"]["409"]["content"][
        "application/json"
    ]
    assert reviews_409["schema"] == {"$ref": "#/components/schemas/DetailError"}
    assert "DetailErrorExample" in reviews_409["examples"]


@pytest.mark.django_db
def test_real_error_responses_match_documented_shapes(api_client, make_user):
    anon_resp = api_client.get("/api/tasks/")
    assert anon_resp.status_code == 403
    anon_body = anon_resp.json()
    assert set(anon_body) == {"detail"}
    assert isinstance(anon_body["detail"], str) and anon_body["detail"]

    author = make_user(username="author_err", role=User.Role.PARTICIPANT)
    reviewer = make_user(username="reviewer_err", role=User.Role.REVIEWER)
    sentence = SourceSentence.objects.create(text_ru="Пример", domain=Domain.IT, is_original=True)
    task = Task.objects.create(
        type=Task.Type.TRANSLATION, domain=Domain.IT, source_sentence=sentence
    )

    api_client.force_authenticate(author)
    bad_submit = api_client.post(f"/api/tasks/{task.pk}/contributions/", {"text_kk": "   "})
    assert bad_submit.status_code == 400
    bad_body = bad_submit.json()
    assert isinstance(bad_body, dict) and bad_body
    assert all(
        isinstance(key, str)
        and isinstance(values, list)
        and values
        and all(isinstance(item, str) for item in values)
        for key, values in bad_body.items()
    )

    contribution = Contribution.objects.create(task=task, author=author)
    version = ContributionVersion.objects.create(
        contribution=contribution, number=1, text_kk="Қазақша аударма"
    )
    api_client.force_authenticate(reviewer)
    first_vote = api_client.post(
        "/api/reviews/", {"version_id": version.pk, "decision": "accept"}
    )
    assert first_vote.status_code == 201
    dup_vote = api_client.post("/api/reviews/", {"version_id": version.pk, "decision": "accept"})
    assert dup_vote.status_code == 409
    dup_body = dup_vote.json()
    assert set(dup_body) == {"detail"}
    assert isinstance(dup_body["detail"], str) and dup_body["detail"]
