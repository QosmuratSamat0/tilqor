import { useState, type FormEvent } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  api,
  ApiError,
  type FieldErrors,
  type OwnContribution,
} from "../../shared/api/client";
import { queryKeys } from "../../shared/api/queryKeys";
import { errorFeedback, warningText } from "../../shared/i18n/feedback";
import {
  Button,
  EmptyState,
  ErrorMessage,
  Field,
  StatusBadge,
} from "../../shared/ui";
import styles from "./MyContributionsPage.module.css";

interface NewVersionFormProps {
  contribution: OwnContribution;
}

function NewVersionForm({ contribution }: NewVersionFormProps) {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const [textKk, setTextKk] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const [detailError, setDetailError] = useState<string | null>(null);
  const [warnings, setWarnings] = useState<string[]>([]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setFieldErrors({});
    setDetailError(null);
    setWarnings([]);

    try {
      const res = await api.contributions.submitVersion(
        contribution.id,
        textKk
      );
      setWarnings(Object.values(res.warnings ?? {}).flat().map((warning) => warningText(warning, t)));
      setTextKk("");
      await queryClient.invalidateQueries({
        queryKey: queryKeys.contributions.me,
      });
    } catch (err) {
      if (err instanceof ApiError) {
        const feedback = errorFeedback(err, t);
        setFieldErrors(feedback.fields);
        if (feedback.detail || !Object.keys(feedback.fields).some(
          (field) => field === "text_kk" || field === "contribution"
        )) setDetailError(feedback.message);
      } else {
        setDetailError(t("app.errorGeneric"));
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form
      className={styles.newVersionForm}
      onSubmit={(e) => void handleSubmit(e)}
      noValidate
    >
      <h3 className={styles.newVersionHeading}>
        {t("my.newVersionTitle")}
      </h3>
      {detailError ? <ErrorMessage>{detailError}</ErrorMessage> : null}
      {warnings.length > 0 ? (
        <div className={styles.warningsBox} role="alert">
          {warnings.join(" ")}
        </div>
      ) : null}
      <Field
        multiline
        label={t("my.newVersionLabel")}
        placeholder={t("my.newVersionPlaceholder")}
        name={`new_version_${contribution.id}`}
        required
        value={textKk}
        onChange={(e) => setTextKk(e.target.value)}
        error={fieldErrors.text_kk || fieldErrors.contribution}
      />
      <Button type="submit" variant="primary" size="small" disabled={submitting}>
        {submitting
          ? t("my.submittingNewVersion")
          : t("my.submitNewVersionButton")}
      </Button>
    </form>
  );
}

export function MyContributionsPage() {
  const { t } = useTranslation();
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: queryKeys.contributions.me,
    queryFn: () => api.contributions.me(),
  });

  return (
    <div>
      <header className={styles.header}>
        <h1 className={styles.title}>{t("my.title")}</h1>
        <p className={styles.subtitle}>{t("my.subtitle")}</p>
      </header>

      {isLoading ? <p role="status">{t("app.loading")}</p> : null}

      {isError ? (
        <div>
          <ErrorMessage>
            {error instanceof ApiError ? errorFeedback(error, t).message : t("app.errorGeneric")}
          </ErrorMessage>
          <Button variant="secondary" onClick={() => void refetch()}>
            {t("app.retry")}
          </Button>
        </div>
      ) : null}

      {!isLoading && !isError && data ? (
        data.length === 0 ? (
          <EmptyState
            title={t("my.emptyTitle")}
            description={t("my.emptyDescription")}
            action={<Link to="/tasks">{t("home.browseTasksCta")}</Link>}
          />
        ) : (
          <ul className={styles.list}>
            {data.map((contribution) => {
              const sortedVersions = [...contribution.versions].sort(
                (a, b) => a.number - b.number
              );
              const latestVersion =
                sortedVersions[sortedVersions.length - 1] ?? null;
              const canSubmitNewVersion =
                latestVersion?.status === "needs_edit";

              return (
                <li
                  key={contribution.id}
                  className={styles.contributionCard}
                >
                  <div className={styles.badges}>
                    <span className={styles.badge}>
                      {t(`domains.${contribution.domain}`, {
                        defaultValue: contribution.domain,
                      })}
                    </span>
                    <span className={styles.badge}>
                      {t(`taskTypes.${contribution.task_type}`, {
                        defaultValue: contribution.task_type,
                      })}
                    </span>
                  </div>
                  <div className={styles.sourceText}>
                    {contribution.text_ru}
                  </div>

                  <div className={styles.versionsTitle}>
                    {t("my.versionsTitle")}
                  </div>
                  <ul className={styles.versionsList}>
                    {sortedVersions.map((ver) => (
                      <li key={ver.id} className={styles.versionItem}>
                        <div className={styles.versionHeader}>
                          <span className={styles.versionNum}>
                            {t("my.versionItemLabel", { number: ver.number })}
                          </span>
                          <StatusBadge status={ver.status} />
                        </div>
                        <div className={styles.versionText}>{ver.text_kk}</div>
                        {ver.decision_reasons &&
                        ver.decision_reasons.length > 0 ? (
                          <div className={styles.reasonsBox}>
                            <strong>{t("my.reasonsTitle")}</strong>
                            <ul className={styles.reasonsList}>
                              {ver.decision_reasons.map((reason, idx) => (
                                <li key={idx}>
                                  {reason.code ? t(`review.reasonCode.${reason.code}`) : null}
                                  {reason.code && reason.comment ? ": " : null}
                                  {reason.comment}
                                </li>
                              ))}
                            </ul>
                          </div>
                        ) : null}
                      </li>
                    ))}
                  </ul>

                  {canSubmitNewVersion ? (
                    <NewVersionForm contribution={contribution} />
                  ) : null}
                </li>
              );
            })}
          </ul>
        )
      ) : null}
    </div>
  );
}

