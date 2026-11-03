import { Link, NavLink, Outlet } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { setAppLanguage, type SupportedLanguage } from "../shared/i18n";
import { Button } from "../shared/ui";
import { AcceptTermsBanner } from "../features/auth/AcceptTermsBanner";
import { useAuth } from "../features/auth/AuthContext";
import styles from "./Layout.module.css";

export function Layout() {
  const { t, i18n } = useTranslation();
  const { user, logout } = useAuth();
  const currentLang: SupportedLanguage = i18n.language === "kk" ? "kk" : "ru";

  const isReviewer =
    user &&
    (user.role === "reviewer" ||
      user.role === "moderator" ||
      user.role === "admin");

  function handleLanguageChange(lang: SupportedLanguage) {
    setAppLanguage(lang);
  }

  return (
    <div className={styles.shell}>
      <header className={styles.header}>
        <div className={styles.headerInner}>
          <div className={styles.brandGroup}>
            <Link to="/" className={styles.brandLink}>
              {t("app.brand")}
            </Link>
            <nav className={styles.nav} aria-label={t("app.brand")}>
              <NavLink
                to="/"
                end
                className={({ isActive }) =>
                  `${styles.navLink} ${isActive ? styles.navLinkActive : ""}`.trim()
                }
              >
                {t("nav.home")}
              </NavLink>
              <NavLink
                to="/tasks"
                className={({ isActive }) =>
                  `${styles.navLink} ${isActive ? styles.navLinkActive : ""}`.trim()
                }
              >
                {t("nav.tasks")}
              </NavLink>
              <NavLink
                to="/dictionary"
                className={({ isActive }) =>
                  `${styles.navLink} ${isActive ? styles.navLinkActive : ""}`.trim()
                }
              >
                {t("nav.dictionary")}
              </NavLink>
              {user ? (
                <NavLink
                  to="/my"
                  className={({ isActive }) =>
                    `${styles.navLink} ${isActive ? styles.navLinkActive : ""}`.trim()
                  }
                >
                  {t("nav.my")}
                </NavLink>
              ) : null}
              {isReviewer ? (
                <NavLink
                  to="/review"
                  className={({ isActive }) =>
                    `${styles.navLink} ${isActive ? styles.navLinkActive : ""}`.trim()
                  }
                >
                  {t("nav.review")}
                </NavLink>
              ) : null}
            </nav>
          </div>

          <div className={styles.controls}>
            <div
              className={styles.langGroup}
              role="group"
              aria-label={t("app.languageLabel")}
            >
              <button
                type="button"
                onClick={() => handleLanguageChange("ru")}
                aria-pressed={currentLang === "ru"}
                className={`${styles.langButton} ${
                  currentLang === "ru" ? styles.langButtonActive : ""
                }`.trim()}
              >
                {t("app.langRu")}
              </button>
              <button
                type="button"
                onClick={() => handleLanguageChange("kk")}
                aria-pressed={currentLang === "kk"}
                className={`${styles.langButton} ${
                  currentLang === "kk" ? styles.langButtonActive : ""
                }`.trim()}
              >
                {t("app.langKk")}
              </button>
            </div>

            {user ? (
              <>
                <span className={styles.userInfo}>
                  {t("nav.signedInAs", {
                    name: user.display_name || user.username,
                  })}
                </span>
                <Button
                  variant="secondary"
                  size="small"
                  onClick={() => void logout()}
                >
                  {t("nav.logout")}
                </Button>
              </>
            ) : (
              <>
                <Link to="/login" className={styles.navLink}>
                  {t("nav.login")}
                </Link>
                <Link to="/register" className={styles.navLink}>
                  {t("nav.register")}
                </Link>
              </>
            )}
          </div>
        </div>
      </header>

      <AcceptTermsBanner />

      <main className={styles.main}>
        <Outlet />
      </main>

      <footer className={styles.footer}>{t("app.footerLicence")}</footer>
    </div>
  );
}
