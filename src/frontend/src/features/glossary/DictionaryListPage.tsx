import { useState, type FormEvent } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link, useSearchParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { api } from "../../shared/api/client";
import { queryKeys } from "../../shared/api/queryKeys";
import {
  Button,
  EmptyState,
  ErrorMessage,
  Field,
  Pagination,
  Select,
} from "../../shared/ui";
import styles from "./DictionaryPages.module.css";

export function DictionaryListPage() {
  const { t } = useTranslation();
  const [searchParams, setSearchParams] = useSearchParams();

  const q = searchParams.get("q") || "";
  const domain = searchParams.get("domain") || "";
  const page = Math.max(1, Number(searchParams.get("page") || "1") || 1);

  const [searchInput, setSearchInput] = useState(q);

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: queryKeys.dictionary.list({
      q: q || undefined,
      domain: domain || undefined,
      page,
    }),
    queryFn: () =>
      api.dictionary.list({
        q: q || undefined,
        domain: domain || undefined,
        page,
      }),
  });

  function handleSearchSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const next = new URLSearchParams(searchParams);
    if (searchInput.trim()) {
      next.set("q", searchInput.trim());
    } else {
      next.delete("q");
    }
    next.delete("page");
    setSearchParams(next);
  }

  function handleDomainChange(nextDomain: string) {
    const next = new URLSearchParams(searchParams);
    if (nextDomain) {
      next.set("domain", nextDomain);
    } else {
      next.delete("domain");
    }
    next.delete("page");
    setSearchParams(next);
  }

  function handlePageChange(nextPage: number) {
    const next = new URLSearchParams(searchParams);
    if (nextPage <= 1) {
      next.delete("page");
    } else {
      next.set("page", String(nextPage));
    }
    setSearchParams(next);
  }

  const domainOptions = [
    { value: "", label: t("domains.all") },
    { value: "it", label: t("domains.it") },
    { value: "medicine", label: t("domains.medicine") },
    { value: "engineering", label: t("domains.engineering") },
    { value: "everyday", label: t("domains.everyday") },
  ];

  return (
    <div>
      <header className={styles.header}>
        <div>
          <h1 className={styles.title}>{t("dictionary.title")}</h1>
          <p className={styles.subtitle}>{t("dictionary.subtitle")}</p>
        </div>
        <div className={styles.exports}>
          <a href="/api/exports/dataset.csv" className={styles.exportLink}>
            {t("dictionary.exportCsv")}
          </a>
          <a href="/api/exports/dataset.json" className={styles.exportLink}>
            {t("dictionary.exportJson")}
          </a>
        </div>
      </header>

      <form
        className={styles.searchBar}
        onSubmit={handleSearchSubmit}
        role="search"
      >
        <Field
          label={t("dictionary.searchLabel")}
          placeholder={t("dictionary.searchPlaceholder")}
          name="q"
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
        />
        <Select
          label={t("tasks.filterDomainLabel")}
          value={domain}
          options={domainOptions}
          onChange={(e) => handleDomainChange(e.target.value)}
        />
        <div className={styles.searchButtonWrap}>
          <Button type="submit" variant="primary">
            {t("dictionary.searchButton")}
          </Button>
        </div>
      </form>

      {isLoading ? <p role="status">{t("app.loading")}</p> : null}

      {isError ? (
        <div>
          <ErrorMessage>
            {error instanceof Error ? error.message : t("app.errorGeneric")}
          </ErrorMessage>
          <Button variant="secondary" onClick={() => void refetch()}>
            {t("app.retry")}
          </Button>
        </div>
      ) : null}

      {!isLoading && !isError && data ? (
        data.results.length === 0 ? (
          <EmptyState
            title={t("dictionary.emptyTitle")}
            description={t("dictionary.emptyDescription")}
          />
        ) : (
          <>
            <ul className={styles.termList}>
              {data.results.map((term) => (
                <li key={term.id} className={styles.termCard}>
                  <div className={styles.cardTop}>
                    <span className={styles.domainBadge}>
                      {t(`domains.${term.domain}`, {
                        defaultValue: term.domain,
                      })}
                    </span>
                    <Link to={`/dictionary/${term.id}`}>
                      {t("dictionary.openTermCard")} →
                    </Link>
                  </div>

                  <h2 className={styles.termRu}>{term.text_ru}</h2>
                  {term.definition ? (
                    <p className={styles.definition}>{term.definition}</p>
                  ) : null}

                  <div className={styles.recommendedBox}>
                    <div className={styles.sectionLabel}>
                      {t("dictionary.recommendedLabel")}
                    </div>
                    {term.recommended ? (
                      <>
                        <div className={styles.recommendedKk}>
                          {term.recommended.text_kk}
                        </div>
                        {term.recommended.reason ? (
                          <div className={styles.reasonText}>
                            <strong>{t("dictionary.reasonLabel")}</strong>{" "}
                            {term.recommended.reason}
                          </div>
                        ) : null}
                        <div className={styles.authorMeta}>
                          {t("dictionary.authorLabel", {
                            name: term.recommended.public_name,
                          })}
                        </div>
                      </>
                    ) : (
                      <div>{t("dictionary.noRecommended")}</div>
                    )}
                  </div>

                  {term.alternatives.length > 0 ? (
                    <div className={styles.alternativesSection}>
                      <div className={styles.sectionLabel}>
                        {t("dictionary.alternativesLabel")}
                      </div>
                      <ul className={styles.variantList}>
                        {term.alternatives.map((alt) => (
                          <li key={alt.id} className={styles.variantItem}>
                            <span className={styles.variantKk}>
                              {alt.text_kk}
                            </span>
                            <span className={styles.authorMeta}>
                              {t("dictionary.authorLabel", {
                                name: alt.public_name,
                              })}
                            </span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  ) : null}
                </li>
              ))}
            </ul>
            <Pagination
              page={page}
              hasNext={Boolean(data.next)}
              hasPrevious={Boolean(data.previous)}
              totalCount={data.count}
              onPageChange={handlePageChange}
            />
          </>
        )
      ) : null}
    </div>
  );
}

