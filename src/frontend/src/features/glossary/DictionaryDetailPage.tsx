import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { api } from "../../shared/api/client";
import { queryKeys } from "../../shared/api/queryKeys";
import { Button, ErrorMessage, StatusBadge } from "../../shared/ui";
import styles from "./DictionaryPages.module.css";

export function DictionaryDetailPage() {
  const { id } = useParams<{ id: string }>();
  const termId = Number(id);
  const { t } = useTranslation();

  const {
    data: term,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: queryKeys.dictionary.detail(termId),
    queryFn: () => api.dictionary.detail(termId),
    enabled: Number.isFinite(termId) && termId > 0,
  });

  if (isLoading) {
    return <p role="status">{t("app.loading")}</p>;
  }

  if (isError || !term) {
    return (
      <div>
        <ErrorMessage>
          {error instanceof Error ? error.message : t("app.errorGeneric")}
        </ErrorMessage>
        <Button variant="secondary" onClick={() => void refetch()}>
          {t("app.retry")}
        </Button>
      </div>
    );
  }

  const pendingVariants = Array.isArray(term.pending) ? term.pending : [];

  return (
    <div>
      <Link to="/dictionary" className={styles.backLink}>
        ← {t("dictionary.backToDictionary")}
      </Link>

      <article className={styles.termCard}>
        <div className={styles.cardTop}>
          <span className={styles.domainBadge}>
            {t(`domains.${term.domain}`, { defaultValue: term.domain })}
          </span>
          {term.source ? (
            <span className={styles.authorMeta}>
              {t("dictionary.sourceLabel", { source: term.source })}
            </span>
          ) : null}
        </div>

        <h1 className={styles.termRu}>{term.text_ru}</h1>
        {term.definition ? (
          <p className={styles.definition}>{term.definition}</p>
        ) : null}

        <section
          className={styles.recommendedBox}
          aria-label={t("dictionary.recommendedLabel")}
        >
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
        </section>

        <section
          className={styles.alternativesSection}
          aria-label={t("dictionary.alternativesLabel")}
        >
          <div className={styles.sectionLabel}>
            {t("dictionary.alternativesLabel")}
          </div>
          {term.alternatives.length === 0 ? (
            <p className={styles.authorMeta}>
              {t("dictionary.alternativesEmpty")}
            </p>
          ) : (
            <ul className={styles.variantList}>
              {term.alternatives.map((alt) => (
                <li key={alt.id} className={styles.variantItem}>
                  <span className={styles.variantKk}>{alt.text_kk}</span>
                  <span className={styles.authorMeta}>
                    {t("dictionary.authorLabel", { name: alt.public_name })}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </section>

        {term.pending !== undefined ? (
          <section
            className={styles.pendingSection}
            aria-label={t("dictionary.pendingSectionTitle")}
          >
            <h2 className={styles.pendingTitle}>
              {t("dictionary.pendingSectionTitle")}
            </h2>
            <p className={styles.pendingNotice}>
              {t("dictionary.pendingSectionNotice")}
            </p>
            {pendingVariants.length === 0 ? (
              <p className={styles.authorMeta}>
                {t("dictionary.pendingEmpty")}
              </p>
            ) : (
              <ul className={styles.variantList}>
                {pendingVariants.map((item) => (
                  <li key={item.id} className={styles.variantItem}>
                    <span className={styles.variantKk}>{item.text_kk}</span>
                    <div>
                      <StatusBadge status={item.status} />{" "}
                      <span className={styles.authorMeta}>
                        {t("dictionary.authorLabel", {
                          name: item.public_name,
                        })}
                      </span>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </section>
        ) : null}
      </article>
    </div>
  );
}
