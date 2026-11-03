import { useQuery } from "@tanstack/react-query";
import { Link, useSearchParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { api } from "../../shared/api/client";
import { queryKeys } from "../../shared/api/queryKeys";
import {
  Button,
  EmptyState,
  ErrorMessage,
  Pagination,
  Select,
} from "../../shared/ui";
import styles from "./ContributePages.module.css";

export function TaskListPage() {
  const { t } = useTranslation();
  const [searchParams, setSearchParams] = useSearchParams();

  const domain = searchParams.get("domain") || "";
  const type = searchParams.get("type") || "";
  const page = Math.max(1, Number(searchParams.get("page") || "1") || 1);

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: queryKeys.tasks.list({
      domain: domain || undefined,
      type: type || undefined,
      page,
    }),
    queryFn: () =>
      api.tasks.list({
        domain: domain || undefined,
        type: type || undefined,
        page,
      }),
  });

  function updateFilter(key: "domain" | "type", value: string) {
    const next = new URLSearchParams(searchParams);
    if (value) {
      next.set(key, value);
    } else {
      next.delete(key);
    }
    next.delete("page");
    setSearchParams(next);
  }

  function handlePageChange(nextPage: number) {
    const next = new URLSearchParams(searchParams);
    if (nextPage <= 1) {
      next.delete("page");
    } else {
      next.set("page", String(nextPage));
    }
    setSearchParams(next);
  }

  const domainOptions = [
    { value: "", label: t("domains.all") },
    { value: "it", label: t("domains.it") },
    { value: "medicine", label: t("domains.medicine") },
    { value: "engineering", label: t("domains.engineering") },
    { value: "everyday", label: t("domains.everyday") },
  ];

  const typeOptions = [
    { value: "", label: t("taskTypes.all") },
    { value: "translation", label: t("taskTypes.translation") },
    { value: "term", label: t("taskTypes.term") },
  ];

  return (
    <div>
      <header className={styles.header}>
        <h1 className={styles.title}>{t("tasks.title")}</h1>
        <p className={styles.subtitle}>{t("tasks.subtitle")}</p>
      </header>

      <div className={styles.filters}>
        <Select
          label={t("tasks.filterDomainLabel")}
          value={domain}
          options={domainOptions}
          onChange={(e) => updateFilter("domain", e.target.value)}
        />
        <Select
          label={t("tasks.filterTypeLabel")}
          value={type}
          options={typeOptions}
          onChange={(e) => updateFilter("type", e.target.value)}
        />
      </div>

      {isLoading ? <p role="status">{t("app.loading")}</p> : null}

      {isError ? (
        <div>
          <ErrorMessage>
            {error instanceof Error ? error.message : t("app.errorGeneric")}
          </ErrorMessage>
          <Button variant="secondary" onClick={() => void refetch()}>
            {t("app.retry")}
          </Button>
        </div>
      ) : null}

      {!isLoading && !isError && data ? (
        data.results.length === 0 ? (
          <EmptyState
            title={t("tasks.emptyTitle")}
            description={t("tasks.emptyDescription")}
          />
        ) : (
          <>
            <ul className={styles.taskList}>
              {data.results.map((task) => (
                <li key={task.id} className={styles.taskCard}>
                  <div className={styles.taskInfo}>
                    <div className={styles.badges}>
                      <span className={styles.domainBadge}>
                        {t(`domains.${task.domain}`, {
                          defaultValue: task.domain,
                        })}
                      </span>
                      <span className={styles.typeBadge}>
                        {t(`taskTypes.${task.type}`, {
                          defaultValue: task.type,
                        })}
                      </span>
                    </div>
                    <p className={styles.taskText}>{task.text_ru}</p>
                    {task.definition ? (
                      <p className={styles.taskDef}>{task.definition}</p>
                    ) : null}
                  </div>
                  <Link to={`/tasks/${task.id}`} className={styles.taskLink}>
                    {t("tasks.openTaskButton")}
                  </Link>
                </li>
              ))}
            </ul>
            <Pagination
              page={page}
              hasNext={Boolean(data.next)}
              hasPrevious={Boolean(data.previous)}
              totalCount={data.count}
              onPageChange={handlePageChange}
            />
          </>
        )
      ) : null}
    </div>
  );
}

