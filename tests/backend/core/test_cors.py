import pytest
from django.test import override_settings

FRONTEND_ORIGIN = "https://tilqor.samatk.me"


@override_settings(CORS_ALLOWED_ORIGINS=[FRONTEND_ORIGIN])
def test_allowed_preflight_includes_credentials(client):
    response = client.options(
        "/api/auth/login/",
        HTTP_ORIGIN=FRONTEND_ORIGIN,
        HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
        HTTP_ACCESS_CONTROL_REQUEST_HEADERS="content-type,x-csrftoken",
    )

    assert response.status_code == 200
    assert response["Access-Control-Allow-Origin"] == FRONTEND_ORIGIN
    assert response["Access-Control-Allow-Credentials"] == "true"
    assert "x-csrftoken" in response["Access-Control-Allow-Headers"].lower().split(", ")
    assert "POST" in response["Access-Control-Allow-Methods"].split(", ")


@override_settings(CORS_ALLOWED_ORIGINS=[FRONTEND_ORIGIN])
@pytest.mark.parametrize("method", ["get", "options"])
def test_untrusted_origin_gets_no_cors_headers(client, method):
    response = getattr(client, method)(
        "/api/auth/csrf/",
        HTTP_ORIGIN="https://evil.example",
        HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
    )

    assert not any(key.lower().startswith("access-control-") for key in response.headers)


@override_settings(CORS_ALLOWED_ORIGINS=[])
def test_empty_allowlist_disables_cors(client):
    response = client.get("/api/auth/csrf/", HTTP_ORIGIN=FRONTEND_ORIGIN)

    assert "Access-Control-Allow-Origin" not in response
    assert "Access-Control-Allow-Credentials" not in response


@override_settings(CSRF_COOKIE_DOMAIN=".tilqor.samatk.me")
def test_csrf_cookie_can_be_read_on_frontend_subdomain(client, settings):
    response = client.get("/api/auth/csrf/")

    assert response.status_code == 204
    cookie = response.cookies["csrftoken"]
    assert cookie["domain"] == ".tilqor.samatk.me"
    assert not cookie["httponly"]
    assert cookie["samesite"] == "Lax"
    assert settings.SESSION_COOKIE_DOMAIN is None
    assert settings.SESSION_COOKIE_HTTPONLY is True
    assert settings.SESSION_COOKIE_SAMESITE == "Lax"
