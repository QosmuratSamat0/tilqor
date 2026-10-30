import pytest
from django.db import OperationalError
from django.urls import reverse


@pytest.mark.django_db
def test_health_reports_ok_when_database_is_reachable(client):
    response = client.get(reverse("health"))

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


def test_health_reports_503_when_database_is_unavailable(client, monkeypatch):
    def broken_cursor(*args, **kwargs):
        raise OperationalError("database is down")

    monkeypatch.setattr("core.views.connection.cursor", broken_cursor)

    response = client.get(reverse("health"))

    assert response.status_code == 503
    assert response.json() == {"status": "error", "database": "unavailable"}
