import pytest

from config.settings import env_bool, env_list


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("true", True), ("1", True), ("Yes", True), ("false", False), ("0", False), ("", False)],
)
def test_env_bool_parses_common_values(monkeypatch, raw, expected):
    monkeypatch.setenv("TILQOR_TEST_FLAG", raw)

    assert env_bool("TILQOR_TEST_FLAG") is expected


def test_env_bool_uses_default_when_unset(monkeypatch):
    monkeypatch.delenv("TILQOR_TEST_FLAG", raising=False)

    assert env_bool("TILQOR_TEST_FLAG", default=True) is True


def test_env_list_splits_and_strips(monkeypatch):
    monkeypatch.setenv("TILQOR_TEST_HOSTS", " localhost, 127.0.0.1 ,,")

    assert env_list("TILQOR_TEST_HOSTS") == ["localhost", "127.0.0.1"]
