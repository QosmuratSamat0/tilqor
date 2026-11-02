"""OpenAPI 3.0 schema and Swagger UI checks (TIL-32)."""

import re

import yaml
from django.urls import URLPattern, URLResolver

from apps.contributions.models import Task
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
