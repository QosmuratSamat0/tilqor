import { useTranslation } from "react-i18next";
import styles from "./StatusBadge.module.css";

export type VersionStatus =
  | "submitted"
  | "in_review"
  | "accepted"
  | "rejected"
  | "needs_edit"
  | string;

const STATUS_ICONS: Record<string, string> = {
  submitted: "●",
  in_review: "⏳",
  accepted: "✓",
  rejected: "✕",
  needs_edit: "✎",
};

export interface StatusBadgeProps {
  status: VersionStatus;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const { t } = useTranslation();
  const icon = STATUS_ICONS[status] ?? "•";
  const label = t(`status.${status}`, { defaultValue: status });
  const statusClass = styles[status] ?? styles.submitted;

  return (
    <span className={`${styles.badge} ${statusClass}`} data-status={status}>
      <span className={styles.icon} aria-hidden="true">
        {icon}
      </span>
      <span>{label}</span>
    </span>
  );
}

