import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  api,
  type DomainEnum,
  type OwnContribution,
} from "../../shared/api/client";
import { queryKeys } from "../../shared/api/queryKeys";
import { useAuth } from "../auth/AuthContext";
import { DailyShowcase } from "../daily/DailyShowcase";
import styles from "./HomePage.module.css";

const DOMAINS: DomainEnum[] = ["it", "medicine", "engineering", "everyday"];
export const DAILY_TARGET = 10;

const almatyDateFormatter = new Intl.DateTimeFormat("en-CA", {
  timeZone: "Asia/Almaty",
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
});

export function toAlmatyDateKey(value: Date | string): string {
  const date = typeof value === "string" ? new Date(value) : value;
  if (Number.isNaN(date.getTime())) {
    return "";
  }
  return almatyDateFormatter.format(date);
}

export function countTodayContributions(
  contributions: OwnContribution[],
  now: Date = new Date()
): number {
  const todayKey = toAlmatyDateKey(now);
  return contributions.filter((contribution) => {
    const firstVersion =
      contribution.versions.find((v) => v.number === 1) ??
      contribution.versions[0];
    const timestamp = firstVersion?.created_at ?? contribution.created_at;
    return toAlmatyDateKey(timestamp) === todayKey;
  }).length;
}

export function HomePage() {
  const { t } = useTranslation();
  const { user } = useAuth();

  const { data: myContributions } = useQuery({
    queryKey: queryKeys.contributions.me,
    queryFn: () => api.contributions.me(),
    enabled: Boolean(user),
  });

  const doneCount = myContributions
    ? countTodayContributions(myContributions)
    : 0;
  const clampedProgress = Math.min(
    100,
    Math.round((doneCount / DAILY_TARGET) * 100)
  );

  return (
    <div>
      <section className={styles.hero}>
        <div>
          <h1 className={styles.heroTitle}>{t("home.heroTitle")}</h1>
          <p className={styles.heroSubtitle}>{t("home.heroSubtitle")}</p>
          <div className={styles.ctaGroup}>
            <Link
              to="/tasks"
              className={`${styles.ctaLink} ${styles.ctaPrimary}`}
            >
              {t("home.browseTasksCta")}
            </Link>
            <Link
              to="/dictionary"
              className={`${styles.ctaLink} ${styles.ctaSecondary}`}
            >
              {t("home.openDictionaryCta")}
            </Link>
          </div>
        </div>

        <aside className={styles.goalCard} aria-label={t("home.dailyGoalTitle")}>
          <h2 className={styles.goalTitle}>{t("home.dailyGoalTitle")}</h2>
          {user ? (
            <>
              <p>
                {t("home.dailyGoalProgress", {
                  done: doneCount,
                  target: DAILY_TARGET,
                })}
              </p>
              <div
                className={styles.progressTrack}
                role="progressbar"
                aria-valuenow={Math.min(doneCount, DAILY_TARGET)}
                aria-valuemin={0}
                aria-valuemax={DAILY_TARGET}
              >
                <div
                  className={styles.progressBar}
                  style={{ width: `${clampedProgress}%` }}
                />
              </div>
            </>
          ) : (
            <p>{t("home.dailyGoalAnonHint")}</p>
          )}
          <div>
            <Link to="/tasks">{t("home.dailyGoalAction")}</Link>
          </div>
        </aside>
      </section>

      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>{t("home.domainsTitle")}</h2>
        <div className={styles.domainsGrid}>
          {DOMAINS.map((domain) => (
            <Link
              key={domain}
              to={`/tasks?domain=${domain}`}
              className={styles.domainCard}
            >
              <span className={styles.domainName}>{t(`domains.${domain}`)}</span>
              <span className={styles.domainAction}>
                {t("home.domainCardAction")} →
              </span>
            </Link>
          ))}
        </div>
      </section>

      <section className={styles.section}>
        <DailyShowcase />
      </section>
    </div>
  );
}
