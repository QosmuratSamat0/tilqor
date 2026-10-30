"""FR-01: registration, sign-in and sign-out."""
import pytest
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
    }
    data.update(overrides)
    return client.post(reverse("auth-register"), data, format="json")


def test_register_creates_participant_and_signs_in(api_client):
    response = register(api_client)

    assert response.status_code == 201
    assert response.json()["role"] == "participant"
    assert "password" not in response.json()
    assert api_client.get(reverse("auth-me")).status_code == 200
    assert User.objects.get(username="aru").check_password(PASSWORD)


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
