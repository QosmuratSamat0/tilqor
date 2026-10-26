import os

from config.settings import load_env_file


def test_load_env_file_reads_values_and_skips_comments(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("# comment\nTILQOR_TEST_A=1\n\nTILQOR_TEST_B = two \n", encoding="utf-8")
    monkeypatch.delenv("TILQOR_TEST_A", raising=False)
    monkeypatch.delenv("TILQOR_TEST_B", raising=False)

    load_env_file(env_file)

    assert os.environ["TILQOR_TEST_A"] == "1"
    assert os.environ["TILQOR_TEST_B"] == "two"


def test_load_env_file_does_not_override_existing_variables(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("TILQOR_TEST_A=from-file\n", encoding="utf-8")
    monkeypatch.setenv("TILQOR_TEST_A", "from-environment")

    load_env_file(env_file)

    assert os.environ["TILQOR_TEST_A"] == "from-environment"


def test_load_env_file_ignores_missing_file(tmp_path):
    load_env_file(tmp_path / "missing.env")
