import { useTranslation } from "react-i18next";
import { Button } from "./Button";
import styles from "./Pagination.module.css";

export interface PaginationProps {
  page: number;
  hasNext: boolean;
  hasPrevious: boolean;
  totalCount?: number;
  onPageChange: (page: number) => void;
}

export function Pagination({
  page,
  hasNext,
  hasPrevious,
  totalCount,
  onPageChange,
}: PaginationProps) {
  const { t } = useTranslation();

  if (!hasNext && !hasPrevious && page <= 1) {
    return null;
  }

  return (
    <nav className={styles.pagination} aria-label={t("pagination.ariaLabel")}>
      <span className={styles.info}>
        {t("pagination.pageInfo", { page })}
        {typeof totalCount === "number"
          ? ` (${t("pagination.totalCount", { count: totalCount })})`
          : ""}
      </span>
      <div className={styles.controls}>
        <Button
          variant="secondary"
          size="small"
          disabled={!hasPrevious || page <= 1}
          onClick={() => onPageChange(Math.max(1, page - 1))}
        >
          {t("pagination.previous")}
        </Button>
        <Button
          variant="secondary"
          size="small"
          disabled={!hasNext}
          onClick={() => onPageChange(page + 1)}
        >
          {t("pagination.next")}
        </Button>
      </div>
    </nav>
  );
}

