import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Button } from "../../shared/ui";
import { useAuth } from "./AuthContext";
import styles from "./AcceptTermsBanner.module.css";

export function AcceptTermsBanner() {
  const { user, acceptTerms } = useAuth();
  const { t } = useTranslation();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!user || user.accepted_terms) {
    return null;
  }

  async function handleAccept() {
    setSubmitting(true);
    setError(null);
    try {
      await acceptTerms();
    } catch (err) {
      setError(err instanceof Error ? err.message : t("app.errorGeneric"));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className={styles.banner} role="region" aria-label={t("auth.termsBannerAction")}>
      <div className={styles.inner}>
        <p className={styles.text}>{t("auth.termsBannerText")}</p>
        <Button
          variant="primary"
          size="small"
          disabled={submitting}
          onClick={() => void handleAccept()}
        >
          {submitting ? t("auth.termsBannerSubmitting") : t("auth.termsBannerAction")}
        </Button>
        {error ? (
          <div className={styles.error} role="alert">
            {error}
          </div>
        ) : null}
      </div>
    </div>
  );
}

