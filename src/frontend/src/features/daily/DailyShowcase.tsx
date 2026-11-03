import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { api } from "../../shared/api/client";
import { queryKeys } from "../../shared/api/queryKeys";
import { Button, ErrorMessage } from "../../shared/ui";
import styles from "./DailyShowcase.module.css";

export function DailyShowcase() {
  const { t } = useTranslation();
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: queryKeys.catalogue.today(),
    queryFn: () => api.catalogue.today(),
  });

  if (isLoading) {
    return <p role="status">{t("app.loading")}</p>;
  }

  if (isError || !data) {
    return (
      <div>
        <ErrorMessage>
          {error instanceof Error ? error.message : t("app.errorGeneric")}
        </ErrorMessage>
        <Button variant="secondary" size="small" onClick={() => void refetch()}>
          {t("app.retry")}
        </Button>
      </div>
    );
  }

  const { word_of_the_day: wotd, top_words: topWords, connector_hints: hints } = data;

  return (
    <div className={styles.grid}>
      <article className={styles.card}>
        <h2 className={styles.cardTitle}>{t("home.wordOfTheDayTitle")}</h2>
        {wotd ? (
          <>
            <span className={styles.domainTag}>
              {t(`domains.${wotd.domain}`, { defaultValue: wotd.domain })}
            </span>
            <div className={styles.termPair}>
              <span className={styles.termKk}>{wotd.text_kk}</span>
              <span className={styles.termRu}>{wotd.text_ru}</span>
            </div>
            {wotd.definition ? (
              <p className={styles.definition}>{wotd.definition}</p>
            ) : null}
            <span className={styles.meta}>
              {t("home.wordOfTheDayAuthor", { author: wotd.public_name })}
            </span>
            <div>
              <Link to={`/dictionary/${wotd.term_id}`}>
                {t("home.openTermDetail")}
              </Link>
            </div>
          </>
        ) : (
          <p className={styles.definition}>{t("home.wordOfTheDayEmpty")}</p>
        )}
      </article>

      <article className={styles.card}>
        <h2 className={styles.cardTitle}>{t("home.topWordsTitle")}</h2>
        {topWords.length > 0 ? (
          <ul className={styles.list}>
            {topWords.map((item) => (
              <li key={item.id} className={styles.listItem}>
                <div className={styles.listHeader}>
                  <Link to={`/dictionary/${item.term_id}`}>
                    {item.text_kk} — {item.text_ru}
                  </Link>
                  <span className={styles.meta}>
                    {t("home.topWordVotes", { count: item.preference_count })}
                  </span>
                </div>
                <span className={styles.meta}>
                  {t(`domains.${item.domain}`, { defaultValue: item.domain })} ·{" "}
                  {item.public_name}
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <p className={styles.definition}>{t("home.topWordsEmpty")}</p>
        )}
      </article>

      <article className={styles.card}>
        <h2 className={styles.cardTitle}>{t("home.connectorHintsTitle")}</h2>
        {hints.length > 0 ? (
          <ul className={styles.list}>
            {hints.map((hint) => (
              <li key={hint.id} className={styles.listItem}>
                <div className={styles.listHeader}>
                  <span>{hint.text_kk}</span>
                  <span className={styles.meta}>{hint.text_ru}</span>
                </div>
                {hint.example_kk || hint.example_ru ? (
                  <div className={styles.exampleBox}>
                    <strong>{t("home.connectorExampleLabel")}</strong>{" "}
                    {hint.example_kk}
                    {hint.example_ru ? ` (${hint.example_ru})` : ""}
                  </div>
                ) : null}
              </li>
            ))}
          </ul>
        ) : (
          <p className={styles.definition}>{t("home.connectorHintsEmpty")}</p>
        )}
      </article>
    </div>
  );
}
