import { useState, type FormEvent } from "react";
import { Link, useLocation, useNavigate, useSearchParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { ApiError, type FieldErrors } from "../../shared/api/client";
import { Button, ErrorMessage, Field } from "../../shared/ui";
import { useAuth } from "./AuthContext";
import styles from "./AuthPages.module.css";

interface LocationState {
  from?: string;
}

export function LoginPage() {
  const { t } = useTranslation();
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [detailError, setDetailError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});

  const state = location.state as LocationState | null;
  const redirectTarget = state?.from || searchParams.get("next") || "/";

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setDetailError(null);
    setFieldErrors({});

    try {
      await login({ username, password });
      navigate(redirectTarget, { replace: true });
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
      <h1 className={styles.title}>{t("auth.loginTitle")}</h1>
      <p className={styles.subtitle}>{t("auth.loginSubtitle")}</p>

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
          label={t("auth.passwordLabel")}
          name="password"
          type="password"
          autoComplete="current-password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          error={fieldErrors.password}
        />

        <div className={styles.actions}>
          <Button type="submit" variant="primary" disabled={submitting}>
            {submitting ? t("auth.loginSubmitting") : t("auth.loginButton")}
          </Button>
        </div>
      </form>

      <div className={styles.switchPrompt}>
        {t("auth.noAccountPrompt")}{" "}
        <Link to="/register">{t("auth.goToRegister")}</Link>
      </div>
    </section>
  );
}
