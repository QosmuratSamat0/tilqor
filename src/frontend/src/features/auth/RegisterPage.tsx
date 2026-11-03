import { useId, useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { ApiError, type FieldErrors } from "../../shared/api/client";
import { Button, ErrorMessage, Field } from "../../shared/ui";
import { useAuth } from "./AuthContext";
import styles from "./AuthPages.module.css";

export function RegisterPage() {
  const { t } = useTranslation();
  const { register } = useAuth();
  const navigate = useNavigate();
  const termsId = useId();
  const termsErrorId = `${termsId}-error`;

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [password, setPassword] = useState("");
  const [acceptTerms, setAcceptTerms] = useState(false);

  const [submitting, setSubmitting] = useState(false);
  const [detailError, setDetailError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});

  const termsError = fieldErrors.accept_terms?.join(" ");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setDetailError(null);
    setFieldErrors({});

    if (!acceptTerms) {
      setFieldErrors({
        accept_terms: [t("auth.acceptTermsRequired")],
      });
      return;
    }

    setSubmitting(true);
    try {
      await register({
        username,
        email,
        password,
        display_name: displayName || undefined,
        accept_terms: acceptTerms,
      });
      navigate("/", { replace: true });
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

  return (
    <section className={styles.wrapper}>
      <h1 className={styles.title}>{t("auth.registerTitle")}</h1>
      <p className={styles.subtitle}>{t("auth.registerSubtitle")}</p>

      {detailError ? <ErrorMessage>{detailError}</ErrorMessage> : null}

      <form onSubmit={(e) => void handleSubmit(e)} noValidate>
        <Field
          label={t("auth.usernameLabel")}
          name="username"
          autoComplete="username"
          required
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          error={fieldErrors.username}
        />

        <Field
          label={t("auth.emailLabel")}
          name="email"
          type="email"
          autoComplete="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          error={fieldErrors.email}
        />

        <Field
          label={t("auth.displayNameLabel")}
          hint={t("auth.displayNameHint")}
          name="display_name"
          autoComplete="name"
          value={displayName}
          onChange={(e) => setDisplayName(e.target.value)}
          error={fieldErrors.display_name}
        />

        <Field
          label={t("auth.passwordLabel")}
          name="password"
          type="password"
          autoComplete="new-password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          error={fieldErrors.password}
        />

        <div className={styles.checkboxGroup}>
          <label htmlFor={termsId} className={styles.checkboxLabel}>
            <input
              id={termsId}
              name="accept_terms"
              type="checkbox"
              checked={acceptTerms}
              onChange={(e) => {
                setAcceptTerms(e.target.checked);
                if (e.target.checked && fieldErrors.accept_terms) {
                  setFieldErrors((prev) => {
                    const next = { ...prev };
                    delete next.accept_terms;
                    return next;
                  });
                }
              }}
              aria-invalid={Boolean(termsError) || undefined}
              aria-describedby={termsError ? termsErrorId : undefined}
              className={styles.checkboxInput}
              required
            />
            <span>{t("auth.acceptTermsLabel")} *</span>
          </label>
          {termsError ? (
            <span id={termsErrorId} role="alert" className={styles.checkboxError}>
              {termsError}
            </span>
          ) : null}
        </div>

        <div className={styles.actions}>
          <Button type="submit" variant="primary" disabled={submitting}>
            {submitting ? t("auth.registerSubmitting") : t("auth.registerButton")}
          </Button>
        </div>
      </form>

      <div className={styles.switchPrompt}>
        {t("auth.haveAccountPrompt")}{" "}
        <Link to="/login">{t("auth.goToLogin")}</Link>
      </div>
    </section>
  );
}

