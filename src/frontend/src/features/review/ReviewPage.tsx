import { useState, type FormEvent } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import {
  api,
  ApiError,
  type DecisionEnum,
  type FieldErrors,
} from "../../shared/api/client";
import { queryKeys } from "../../shared/api/queryKeys";
import {
  Button,
  EmptyState,
  ErrorMessage,
  Field,
} from "../../shared/ui";
import { useAuth } from "../auth/AuthContext";
import styles from "./ReviewPage.module.css";

const DECISIONS: DecisionEnum[] = ["accept", "edit", "reject", "dont_know"];

export function ReviewPage() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const [decision, setDecision] = useState<DecisionEnum>("accept");
  const [reason, setReason] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const [detailError, setDetailError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const isReviewer =
    user &&
    (user.role === "reviewer" ||
      user.role === "moderator" ||
      user.role === "admin");

  const queueQuery = useQuery({
    queryKey: queryKeys.reviews.queue,
    queryFn: () => api.reviews.queue(),
    enabled: Boolean(isReviewer),
  });

  const statsQuery = useQuery({
    queryKey: queryKeys.reviews.stats,
    queryFn: () => api.reviews.myStats(),
    enabled: Boolean(isReviewer),
  });

  if (!isReviewer) {
    return (
      <EmptyState
        title={t("review.forbiddenTitle")}
        description={t("review.forbiddenDescription")}
      />
    );
  }

  const queue = queueQuery.data ?? [];
  const currentItem = queue[0] ?? null;
  const requiresReason = decision === "reject" || decision === "edit";

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!currentItem) return;

    setFieldErrors({});
    setDetailError(null);
    setSuccessMessage(null);

    if (requiresReason && !reason.trim()) {
      setFieldErrors({
        reason: [t("review.reasonRequiredError")],
      });
      return;
    }

    setSubmitting(true);
    try {
      await api.reviews.submit({
        version_id: currentItem.id,
        decision,
        reason: reason.trim(),
      });
      setReason("");
      setDecision("accept");
      setSuccessMessage(t("review.reviewSuccess"));
      await queryClient.invalidateQueries({
        queryKey: queryKeys.reviews.queue,
      });
      await queryClient.invalidateQueries({
        queryKey: queryKeys.reviews.stats,
      });
    } catch (err) {
      if (err instanceof ApiError) {
        setFieldErrors(err.fieldErrors);
        if (err.detail) {
          setDetailError(err.detail);
        } else if (!err.hasFieldErrors) {
          setDetailError(err.message);
        }
      } else {
        setDetailError(t("app.errorGeneric"));
      }
    } finally {
      setSubmitting(false);
    }
  }

  function decisionLabel(d: DecisionEnum): string {
    switch (d) {
      case "accept":
        return t("review.decisionAccept");
      case "edit":
        return t("review.decisionEdit");
      case "reject":
        return t("review.decisionReject");
      case "dont_know":
        return t("review.decisionDontKnow");
    }
  }

  const stats = statsQuery.data;
  const matchPercent =
    stats && stats.match_share !== null
      ? Math.round(Number(stats.match_share) * 100)
      : null;

  return (
    <div>
      <header className={styles.header}>
        <h1 className={styles.title}>{t("review.title")}</h1>
        <p className={styles.subtitle}>{t("review.subtitle")}</p>
      </header>

      <div className={styles.layout}>
        <div className={styles.mainColumn}>
          {successMessage ? (
            <div className={styles.successBanner} role="status">
              {successMessage}
            </div>
          ) : null}

          {queueQuery.isLoading ? (
            <p role="status">{t("app.loading")}</p>
          ) : queueQuery.isError ? (
            <div>
              <ErrorMessage>
                {queueQuery.error instanceof Error
                  ? queueQuery.error.message
                  : t("app.errorGeneric")}
              </ErrorMessage>
              <Button
                variant="secondary"
                onClick={() => void queueQuery.refetch()}
              >
                {t("app.retry")}
              </Button>
            </div>
          ) : !currentItem ? (
            <EmptyState
              title={t("review.queueEmptyTitle")}
              description={t("review.queueEmptyDescription")}
            />
          ) : (
            <section className={styles.card}>
              <div className={styles.badges}>
                <span className={styles.badge}>
                  {t(`domains.${currentItem.domain}`, {
                    defaultValue: currentItem.domain,
                  })}
                </span>
                <span className={styles.badge}>
                  {t(`taskTypes.${currentItem.task_type}`, {
                    defaultValue: currentItem.task_type,
                  })}
                </span>
                <span className={styles.badge}>
                  {t("review.versionNumber", { number: currentItem.number })}
                </span>
                <span className={styles.badge}>
                  {t("review.queueRemaining", { count: queue.length })}
                </span>
              </div>

              <div className={styles.compareBox}>
                <div className={styles.textBox}>
                  <div className={styles.boxLabel}>
                    {t("review.sourceTextLabel")}
                  </div>
                  <div className={styles.boxContent}>{currentItem.text_ru}</div>
                  {currentItem.definition ? (
                    <div className={styles.definition}>
                      {currentItem.definition}
                    </div>
                  ) : null}
                </div>

                <div className={styles.candidateBox}>
                  <div className={styles.boxLabel}>
                    {t("review.candidateTextLabel")}
                  </div>
                  <div className={styles.boxContent}>{currentItem.text_kk}</div>
                </div>
              </div>

              {detailError ? <ErrorMessage>{detailError}</ErrorMessage> : null}

              <form onSubmit={(e) => void handleSubmit(e)} noValidate>
                <fieldset className={styles.fieldset}>
                  <legend className={styles.legend}>
                    {t("review.decisionLabel")}
                  </legend>
                  <div className={styles.radioGrid}>
                    {DECISIONS.map((d) => {
                      const checked = decision === d;
                      return (
                        <label
                          key={d}
                          className={`${styles.radioOption} ${
                            checked ? styles.radioOptionSelected : ""
                          }`.trim()}
                        >
                          <input
                            type="radio"
                            name="decision"
                            value={d}
                            checked={checked}
                            onChange={() => {
                              setDecision(d);
                              if (d === "accept" || d === "dont_know") {
                                setFieldErrors({});
                              }
                            }}
                          />
                          <span>{decisionLabel(d)}</span>
                        </label>
                      );
                    })}
                  </div>
                </fieldset>

                <Field
                  multiline
                  label={t("review.reasonLabel")}
                  placeholder={t("review.reasonPlaceholder")}
                  name="reason"
                  required={requiresReason}
                  value={reason}
                  onChange={(e) => {
                    setReason(e.target.value);
                    if (e.target.value.trim() && fieldErrors.reason) {
                      setFieldErrors({});
                    }
                  }}
                  error={fieldErrors.reason}
                />

                <Button type="submit" variant="primary" disabled={submitting}>
                  {submitting
                    ? t("review.submittingReview")
                    : t("review.submitReviewButton")}
                </Button>
              </form>
            </section>
          )}
        </div>

        <aside className={styles.sideColumn}>
          <section className={styles.card} aria-label={t("review.statsTitle")}>
            <h2 className={styles.cardTitle}>{t("review.statsTitle")}</h2>
            {stats ? (
              <ul className={styles.statsList}>
                <li>{t("review.statsWeight", { weight: stats.weight })}</li>
                <li>
                  {t("review.statsFinalized", { count: stats.finalized_votes })}
                </li>
                <li>
                  {t("review.statsMatched", { count: stats.matched_votes })}
                </li>
                <li>
                  {matchPercent !== null
                    ? t("review.statsMatchShare", { percent: matchPercent })
                    : t("review.statsMatchShareEmpty")}
                </li>
              </ul>
            ) : (
              <p>{t("app.loading")}</p>
            )}
          </section>

          <section className={styles.card} aria-label={t("review.rulesTitle")}>
            <h2 className={styles.cardTitle}>{t("review.rulesTitle")}</h2>
            <ul className={styles.rulesList}>
              <li>{t("review.ruleBlind")}</li>
              <li>{t("review.ruleNoSelf")}</li>
              <li>{t("review.ruleReason")}</li>
              <li>{t("review.ruleControl")}</li>
            </ul>
          </section>
        </aside>
      </div>
    </div>
  );
}
