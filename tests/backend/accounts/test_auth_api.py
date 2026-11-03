"""FR-01, FR-06: registration, sign-in, sign-out and publication terms acceptance."""
import pytest
from django.conf import settings
from django.urls import reverse

from apps.accounts.models import User
from tests.backend.conftest import PASSWORD

pytestmark = pytest.mark.django_db


def register(client, **overrides):
    data = {
        "username": "aru",
        "email": "aru@example.com",
        "password": PASSWORD,
        "display_name": "Aru",
        "accept_terms": True,
    }
    data.update(overrides)
    return client.post(reverse("auth-register"), data, format="json")


def test_register_creates_participant_and_signs_in(api_client):
    response = register(api_client)

    assert response.status_code == 201
    assert response.json()["role"] == "participant"
    assert response.json()["accepted_terms"] is True
    assert response.json()["accepted_terms_version"] == settings.PUBLICATION_TERMS_VERSION
    assert "password" not in response.json()
    assert api_client.get(reverse("auth-me")).status_code == 200
    user = User.objects.get(username="aru")
    assert user.check_password(PASSWORD)
    assert user.accepted_terms is True
    assert user.accepted_terms_at is not None
    assert user.accepted_terms_version == settings.PUBLICATION_TERMS_VERSION


def test_register_requires_accept_terms_true(api_client):
    missing_payload = {
        "username": "aru",
        "email": "aru@example.com",
        "password": PASSWORD,
        "display_name": "Aru",
    }
    missing_resp = api_client.post(reverse("auth-register"), missing_payload, format="json")
    assert missing_resp.status_code == 400
    assert "accept_terms" in missing_resp.json()
    assert not User.objects.filter(username="aru").exists()

    false_resp = register(api_client, accept_terms=False)
    assert false_resp.status_code == 400
    assert "accept_terms" in false_resp.json()
    assert not User.objects.filter(username="aru").exists()


def test_accept_terms_endpoint_updates_existing_account_idempotently(api_client, make_user):
    user = make_user(username="legacy_user", accepted_terms=False)
    assert user.accepted_terms is False

    assert api_client.post(reverse("auth-accept-terms")).status_code == 403

    api_client.force_authenticate(user)
    me_before = api_client.get(reverse("auth-me")).json()
    assert me_before["accepted_terms"] is False
    assert me_before["accepted_terms_version"] == ""

    first_resp = api_client.post(reverse("auth-accept-terms"))
    assert first_resp.status_code == 200
    assert first_resp.json()["accepted_terms"] is True
    assert first_resp.json()["accepted_terms_version"] == settings.PUBLICATION_TERMS_VERSION

    user.refresh_from_db()
    first_accepted_at = user.accepted_terms_at
    assert first_accepted_at is not None

    second_resp = api_client.post(reverse("auth-accept-terms"))
    assert second_resp.status_code == 200
    user.refresh_from_db()
    assert user.accepted_terms_at == first_accepted_at
    assert user.accepted_terms_version == settings.PUBLICATION_TERMS_VERSION


def test_register_rejects_weak_password(api_client):
    response = register(api_client, password="12345")

    assert response.status_code == 400
    assert "password" in response.json()
    assert not User.objects.filter(username="aru").exists()


def test_register_rejects_duplicate_email(api_client, make_user):
    make_user(username="first")

    response = register(api_client, username="second", email="FIRST@example.com")

    assert response.status_code == 400
    assert "email" in response.json()


def test_login_with_valid_credentials_creates_session(api_client, make_user):
    make_user(username="aru")

    response = api_client.post(
        reverse("auth-login"), {"username": "aru", "password": PASSWORD}, format="json"
    )

    assert response.status_code == 200
    assert api_client.get(reverse("auth-me")).json()["username"] == "aru"


def test_login_with_invalid_credentials_does_not_create_session(api_client, make_user):
    make_user(username="aru")

    response = api_client.post(
        reverse("auth-login"), {"username": "aru", "password": "wrong-password"}, format="json"
    )

    assert response.status_code == 400
    assert api_client.get(reverse("auth-me")).status_code == 403


def test_after_logout_the_session_no_longer_works(api_client, make_user):
    make_user(username="aru")
    api_client.post(reverse("auth-login"), {"username": "aru", "password": PASSWORD}, format="json")

    assert api_client.post(reverse("auth-logout")).status_code == 204
    assert api_client.get(reverse("auth-me")).status_code == 403


def test_me_requires_authentication(api_client):
    assert api_client.get(reverse("auth-me")).status_code == 403


def test_csrf_endpoint_sets_cookie(api_client):
    response = api_client.get(reverse("auth-csrf"))

    assert response.status_code == 204
    assert "csrftoken" in response.cookies


def test_password_is_stored_as_hash(make_user):
    user = make_user(username="aru")

    assert user.password != PASSWORD
    assert user.password.startswith("pbkdf2_")
