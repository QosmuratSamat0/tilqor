"""Pure domain unit tests for glossary word of the day and seed CSV parsing."""

import pytest

from apps.glossary.domain import (
    parse_iso_date,
    word_of_the_day_index,
)
from apps.glossary.domain.seed import (
    SeedFormatError,
    parse_connectors_csv,
    parse_sentences_csv,
    parse_terms_csv,
)


def test_parse_iso_date_and_word_of_the_day_index():
    assert parse_iso_date("2026-11-03") == "2026-11-03"
    for invalid in ("2026/11/03", "2026-11-3", "not-a-date", "2026-02-30", ""):
        with pytest.raises(ValueError):
            parse_iso_date(invalid)

    assert word_of_the_day_index("2026-11-03", 0) is None
    assert word_of_the_day_index("2026-11-03", -1) is None

    idx_first = word_of_the_day_index("2026-11-03", 10)
    idx_repeat = word_of_the_day_index("2026-11-03", 10)
    assert idx_first == idx_repeat
    assert 0 <= idx_first < 10

    distinct_indices = {word_of_the_day_index(f"2026-11-0{day}", 10) for day in range(1, 9)}
    assert len(distinct_indices) > 1


def test_parse_seed_csv_files_and_report_line_numbers_on_invalid_rows(tmp_path):
    (tmp_path / "terms.csv").write_text(
        "text_ru,definition,domain,variants_kk,source,licence\n"
        "кэш,Определение,invalid_domain,жад,Termincom,CC BY 4.0\n",
        encoding="utf-8",
    )
    with pytest.raises(SeedFormatError) as exc_info:
        parse_terms_csv(tmp_path)
    assert exc_info.value.filename == "terms.csv"
    assert exc_info.value.line_number == 2
    assert "domain" in exc_info.value.reason

    (tmp_path / "terms.csv").write_text(
        "text_ru,definition,domain,variants_kk,source,licence\n"
        "кэш,Определение,it,жад,Termincom.kz,\n",
        encoding="utf-8",
    )
    with pytest.raises(SeedFormatError) as term_lic_exc:
        parse_terms_csv(tmp_path)
    assert term_lic_exc.value.filename == "terms.csv"
    assert term_lic_exc.value.line_number == 2
    assert "licence" in term_lic_exc.value.reason

    (tmp_path / "terms.csv").write_text(
        "text_ru,definition,domain,variants_kk,source,licence\n"
        "кэш,Определение,it,жад,,CC BY 4.0\n",
        encoding="utf-8",
    )
    with pytest.raises(SeedFormatError) as team_lic_exc:
        parse_terms_csv(tmp_path)
    assert team_lic_exc.value.filename == "terms.csv"
    assert team_lic_exc.value.line_number == 2
    assert "empty licence" in team_lic_exc.value.reason

    (tmp_path / "sentences.csv").write_text(
        "text_ru,domain,source_url,licence,attribution,is_original\n"
        "Первое предложение,it,,,,true\n"
        "Второе без лицензии,it,,,,false\n",
        encoding="utf-8",
    )
    with pytest.raises(SeedFormatError) as sent_exc:
        parse_sentences_csv(tmp_path)
    assert sent_exc.value.filename == "sentences.csv"
    assert sent_exc.value.line_number == 3
    assert "licence" in sent_exc.value.reason

    (tmp_path / "connectors.csv").write_text(
        "text_ru,text_kk,example_kk,example_ru,source,licence\n"
        "потому что,себебі,,Пример,Tilqor,CC BY 4.0\n",
        encoding="utf-8",
    )
    with pytest.raises(SeedFormatError) as conn_exc:
        parse_connectors_csv(tmp_path)
    assert conn_exc.value.filename == "connectors.csv"
    assert conn_exc.value.line_number == 2
    assert "example_kk" in conn_exc.value.reason
