import { useState, type FormEvent } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  api,
  ApiError,
  type FieldErrors,
} from "../../shared/api/client";
import { queryKeys } from "../../shared/api/queryKeys";
import {
  Button,
  ErrorMessage,
  Field,
  StatusBadge,
} from "../../shared/ui";
import styles from "./ContributePages.module.css";

export function TaskDetailPage() {
  const { id } = useParams<{ id: string }>();
  const taskId = Number(id);
  const { t } = useTranslation();
  const queryClient = useQueryClient();

  const [textKk, setTextKk] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [hasSubmittedOwn, setHasSubmittedOwn] = useState(false);
  const [warnings, setWarnings] = useState<string[]>([]);
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const [detailError, setDetailError] = useState<string | null>(null);
  const [chosenVersionId, setChosenVersionId] = useState<number | null>(null);
  const [preferenceSubmittingId, setPreferenceSubmittingId] = useState<
    number | null
  >(null);

  const {
    data: task,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: queryKeys.tasks.detail(taskId),
    queryFn: () => api.tasks.detail(taskId),
    enabled: Number.isFinite(taskId) && taskId > 0,
  });

  async function handleContributionSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setFieldErrors({});
    setDetailError(null);
    setWarnings([]);

    try {
      const response = await api.tasks.submitContribution(taskId, textKk);
      const collectedWarnings = Object.values(response.warnings ?? {}).flat();
      setWarnings(collectedWarnings);
      setHasSubmittedOwn(true);
      setTextKk("");
      await queryClient.invalidateQueries({
        queryKey: queryKeys.tasks.detail(taskId),
      });
      await queryClient.invalidateQueries({
        queryKey: queryKeys.contributions.me,
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

  async function handleChooseVariant(versionId: number) {
    setPreferenceSubmittingId(versionId);
    setDetailError(null);
    try {
      const pref = await api.tasks.setPreference(taskId, versionId);
      setChosenVersionId(pref.version_id);
    } catch (err) {
      if (err instanceof ApiError) {
        const msg =
          err.detail ||
          Object.values(err.fieldErrors).flat()[0] ||
          err.message;
        setDetailError(msg);
      } else {
        setDetailError(t("app.errorGeneric"));
      }
    } finally {
      setPreferenceSubmittingId(null);
    }
  }

  if (isLoading) {
    return <p role="status">{t("app.loading")}</p>;
  }

  if (isError || !task) {
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

  const isTranslation = task.type === "translation";
  const showTranslationVariants =
    isTranslation && (hasSubmittedOwn || task.variants.length > 0);

  return (
    <div>
      <Link to="/tasks" className={styles.backLink}>
        ← {t("tasks.backToList")}
      </Link>

      <section className={styles.detailCard}>
        <div className={styles.badges}>
          <span className={styles.domainBadge}>
            {t(`domains.${task.domain}`, { defaultValue: task.domain })}
          </span>
          <span className={styles.typeBadge}>
            {isTranslation
              ? t("contribute.translationBadge")
              : t("contribute.termBadge")}
          </span>
        </div>

        <div className={styles.sourceBox}>
          <div className={styles.sourceLabel}>
            {t("contribute.sourceTextLabel")}
          </div>
          <h1 className={styles.sourceText}>{task.text_ru}</h1>
          {task.definition ? (
            <div>
              <strong>{t("contribute.definitionLabel")}:</strong>{" "}
              {task.definition}
            </div>
          ) : null}
        </div>

        {detailError ? <ErrorMessage>{detailError}</ErrorMessage> : null}

        {hasSubmittedOwn ? (
          <div className={styles.successBox} role="status">
            {t("contribute.submittedSuccess")}
          </div>
        ) : null}

        {warnings.length > 0 ? (
          <div className={styles.warningsBox} role="alert">
            <strong>{t("contribute.warningsTitle")}</strong>
            <ul className={styles.warningsList}>
              {warnings.map((w, idx) => (
                <li key={idx}>{w}</li>
              ))}
            </ul>
          </div>
        ) : null}

        {isTranslation ? (
          <>
            {!showTranslationVariants ? (
              <p className={styles.blindNotice}>
                {t("contribute.blindNotice")}
              </p>
            ) : null}

            <form
              onSubmit={(e) => void handleContributionSubmit(e)}
              noValidate
            >
              <Field
                multiline
                label={t("contribute.translationInputLabel")}
                placeholder={t("contribute.translationPlaceholder")}
                name="text_kk"
                required
                value={textKk}
                onChange={(e) => setTextKk(e.target.value)}
                error={fieldErrors.text_kk || fieldErrors.task}
              />
              <Button type="submit" variant="primary" disabled={submitting}>
                {submitting
                  ? t("contribute.submitting")
                  : t("contribute.submitTranslation")}
              </Button>
            </form>
          </>
        ) : null}
      </section>

      {isTranslation && showTranslationVariants ? (
        <section
          className={styles.variantsSection}
          aria-label={t("contribute.otherVariantsTitle")}
        >
          <h2>{t("contribute.otherVariantsTitle")}</h2>
          {task.variants.length === 0 ? (
            <p>{t("contribute.otherVariantsEmpty")}</p>
          ) : (
            <ul className={styles.variantsList}>
              {task.variants.map((variant) => (
                <li key={variant.id} className={styles.variantItem}>
                  <div>
                    <div className={styles.variantText}>{variant.text_kk}</div>
                    <div className={styles.variantMeta}>
                      <StatusBadge status={variant.status} />
                      <span>
                        {t("contribute.variantAuthor", {
                          name: variant.public_name,
                        })}
                      </span>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>
      ) : null}

      {!isTranslation ? (
        <>
          <section
            className={styles.variantsSection}
            aria-label={t("contribute.termVariantsTitle")}
          >
            <h2>{t("contribute.termVariantsTitle")}</h2>
            <p className={styles.subtitle}>
              {t("contribute.termVariantsHint")}
            </p>
            {task.variants.length === 0 ? (
              <p>{t("contribute.otherVariantsEmpty")}</p>
            ) : (
              <ul className={styles.variantsList}>
                {task.variants.map((variant) => {
                  const isChosen = chosenVersionId === variant.id;
                  return (
                    <li
                      key={variant.id}
                      className={`${styles.variantItem} ${
                        isChosen ? styles.variantSelected : ""
                      }`.trim()}
                    >
                      <div>
                        <div className={styles.variantText}>
                          {variant.text_kk}
                        </div>
                        <div className={styles.variantMeta}>
                          <StatusBadge status={variant.status} />
                          <span>
                            {t("contribute.variantAuthor", {
                              name: variant.public_name,
                            })}
                          </span>
                        </div>
                      </div>
                      <div>
                        <Button
                          variant={isChosen ? "primary" : "secondary"}
                          size="small"
                          disabled={preferenceSubmittingId === variant.id}
                          onClick={() => void handleChooseVariant(variant.id)}
                        >
                          {isChosen
                            ? t("contribute.chosenVariantBadge")
                            : t("contribute.chooseVariantButton")}
                        </Button>
                      </div>
                    </li>
                  );
                })}
              </ul>
            )}
          </section>

          <section className={styles.detailCard}>
            <h2>{t("contribute.suggestOwnTermTitle")}</h2>
            <form
              onSubmit={(e) => void handleContributionSubmit(e)}
              noValidate
            >
              <Field
                label={t("contribute.termInputLabel")}
                placeholder={t("contribute.termPlaceholder")}
                name="text_kk"
                required
                value={textKk}
                onChange={(e) => setTextKk(e.target.value)}
                error={fieldErrors.text_kk || fieldErrors.task}
              />
              <Button type="submit" variant="primary" disabled={submitting}>
                {submitting
                  ? t("contribute.submitting")
                  : t("contribute.submitTermButton")}
              </Button>
            </form>
          </section>
        </>
      ) : null}
    </div>
  );
}
