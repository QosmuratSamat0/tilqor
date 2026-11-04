import type { components } from "./schema";
import { apiUrl } from "./apiUrl";

export type CurrentUser = components["schemas"]["CurrentUser"];
export type RegisterRequest = components["schemas"]["RegisterRequest"];
export type LoginRequest = components["schemas"]["LoginRequest"];
export type RoleEnum = components["schemas"]["RoleEnum"];
export type DomainEnum = components["schemas"]["DomainEnum"];
export type TypeEnum = components["schemas"]["TypeEnum"];
export type StatusEnum = components["schemas"]["StatusEnum"];
export type DecisionEnum = components["schemas"]["DecisionEnum"];

export type DailyCatalogue = components["schemas"]["DailyCatalogue"];
export type WordOfTheDay = components["schemas"]["WordOfTheDay"];
export type TopWord = components["schemas"]["TopWord"];
export type ConnectorHint = components["schemas"]["ConnectorHint"];

export type Task = components["schemas"]["Task"];
export type TaskDetail = components["schemas"]["TaskDetail"];
export type Variant = components["schemas"]["Variant"];
export type PaginatedTaskList = components["schemas"]["PaginatedTaskList"];
export type ContributionSubmission = components["schemas"]["ContributionSubmission"];
export type Preference = components["schemas"]["Preference"];

export type OwnContribution = components["schemas"]["OwnContribution"];
export type OwnVersion = components["schemas"]["OwnVersion"];
export type VersionSubmission = components["schemas"]["VersionSubmission"];

export type QueueItem = components["schemas"]["Queue"];
export type Review = components["schemas"]["Review"];
export type ReviewInputRequest = components["schemas"]["ReviewInputRequest"];
export type Stats = components["schemas"]["Stats"];

export type DictionaryTerm = components["schemas"]["DictionaryTerm"];
export type DictionaryTermDetail = components["schemas"]["DictionaryTermDetail"];
export type DictionaryVariant = components["schemas"]["DictionaryVariant"];
export type RecommendedVariant = components["schemas"]["RecommendedVariant"];
export type PendingVariant = components["schemas"]["PendingVariant"];
export type PaginatedDictionaryTermList =
  components["schemas"]["PaginatedDictionaryTermList"];

export type FieldErrors = Record<string, string[]>;
export type DetailError = components["schemas"]["DetailError"];

const UNSAFE_METHODS = new Set(["POST", "PUT", "PATCH", "DELETE"]);

export function getCookie(name: string): string | null {
  if (typeof document === "undefined" || !document.cookie) {
    return null;
  }
  const cookies = document.cookie.split(";");
  for (const raw of cookies) {
    const trimmed = raw.trim();
    if (trimmed.startsWith(`${name}=`)) {
      return decodeURIComponent(trimmed.slice(name.length + 1));
    }
  }
  return null;
}

export class ApiError extends Error {
  public readonly status: number;
  public readonly detail: string | null;
  public readonly fieldErrors: FieldErrors;

  constructor(
    status: number,
    message: string,
    options?: { detail?: string | null; fieldErrors?: FieldErrors }
  ) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = options?.detail ?? null;
    this.fieldErrors = options?.fieldErrors ?? {};
  }

  public get hasFieldErrors(): boolean {
    return Object.keys(this.fieldErrors).length > 0;
  }
}

export function parseErrorPayload(
  status: number,
  payload: unknown
): ApiError {
  if (payload && typeof payload === "object" && !Array.isArray(payload)) {
    const record = payload as Record<string, unknown>;
    if (typeof record.detail === "string" && Object.keys(record).length === 1) {
      return new ApiError(status, record.detail, { detail: record.detail });
    }

    const fieldErrors: FieldErrors = {};
    for (const [key, value] of Object.entries(record)) {
      if (Array.isArray(value)) {
        const messages = value.filter((item): item is string => typeof item === "string");
        if (messages.length > 0) {
          fieldErrors[key] = messages;
        }
      } else if (typeof value === "string") {
        fieldErrors[key] = [value];
      }
    }

    if (Object.keys(fieldErrors).length > 0) {
      const firstField = Object.keys(fieldErrors)[0];
      const summary = fieldErrors[firstField][0] || `HTTP ${status}`;
      return new ApiError(status, summary, {
        detail: typeof record.detail === "string" ? record.detail : null,
        fieldErrors,
      });
    }
  }

  return new ApiError(status, `Request failed with status ${status}`);
}

export interface RequestOptions {
  method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  body?: unknown;
  params?: Record<string, string | number | undefined | null>;
  headers?: Record<string, string>;
  signal?: AbortSignal;
}

function buildUrl(
  path: string,
  params?: Record<string, string | number | undefined | null>
): string {
  if (!params) return path;
  const searchParams = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== "") {
      searchParams.set(key, String(value));
    }
  }
  const queryString = searchParams.toString();
  return queryString ? `${path}?${queryString}` : path;
}

export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {}
): Promise<T> {
  const method = (options.method ?? "GET").toUpperCase();
  const headers: Record<string, string> = {
    Accept: "application/json",
    ...options.headers,
  };

  if (options.body !== undefined) {
    headers["Content-Type"] = "application/json";
  }

  if (UNSAFE_METHODS.has(method)) {
    const csrfToken = getCookie("csrftoken");
    if (csrfToken) {
      headers["X-CSRFToken"] = csrfToken;
    }
  }

  const response = await fetch(apiUrl(buildUrl(path, options.params)), {
    method,
    credentials: "include",
    headers,
    body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
    signal: options.signal,
  });

  if (response.status === 204) {
    return undefined as T;
  }

  let data: unknown = null;
  const contentType = response.headers.get("content-type") ?? "";
  if (contentType.includes("application/json")) {
    try {
      data = await response.json();
    } catch {
      data = null;
    }
  }

  if (!response.ok) {
    throw parseErrorPayload(response.status, data);
  }

  return data as T;
}

export const api = {
  auth: {
    csrf: () => apiRequest<void>("/api/auth/csrf/", { method: "GET" }),
    me: () => apiRequest<CurrentUser>("/api/auth/me/", { method: "GET" }),
    login: (body: LoginRequest) =>
      apiRequest<CurrentUser>("/api/auth/login/", { method: "POST", body }),
    register: (body: RegisterRequest) =>
      apiRequest<CurrentUser>("/api/auth/register/", { method: "POST", body }),
    logout: () => apiRequest<void>("/api/auth/logout/", { method: "POST" }),
    acceptTerms: () =>
      apiRequest<CurrentUser>("/api/auth/accept-terms/", { method: "POST" }),
  },
  catalogue: {
    today: (date?: string) =>
      apiRequest<DailyCatalogue>("/api/catalogue/today/", {
        method: "GET",
        params: { date },
      }),
  },
  tasks: {
    list: (params?: { domain?: string; type?: string; page?: number }) =>
      apiRequest<PaginatedTaskList>("/api/tasks/", {
        method: "GET",
        params,
      }),
    detail: (taskId: number) =>
      apiRequest<TaskDetail>(`/api/tasks/${taskId}/`, { method: "GET" }),
    submitContribution: (taskId: number, text_kk: string) =>
      apiRequest<ContributionSubmission>(`/api/tasks/${taskId}/contributions/`, {
        method: "POST",
        body: { text_kk },
      }),
    setPreference: (taskId: number, version_id: number) =>
      apiRequest<Preference>(`/api/tasks/${taskId}/preference/`, {
        method: "PUT",
        body: { version_id },
      }),
  },
  contributions: {
    me: () =>
      apiRequest<OwnContribution[]>("/api/contributions/me/", { method: "GET" }),
    submitVersion: (contributionId: number, text_kk: string) =>
      apiRequest<VersionSubmission>(
        `/api/contributions/${contributionId}/versions/`,
        {
          method: "POST",
          body: { text_kk },
        }
      ),
  },
  reviews: {
    queue: () => apiRequest<QueueItem[]>("/api/reviews/queue/", { method: "GET" }),
    submit: (body: ReviewInputRequest) =>
      apiRequest<Review>("/api/reviews/", { method: "POST", body }),
    myStats: () =>
      apiRequest<Stats>("/api/reviews/me/stats/", { method: "GET" }),
  },
  dictionary: {
    list: (params?: { q?: string; domain?: string; page?: number }) =>
      apiRequest<PaginatedDictionaryTermList>("/api/dictionary/", {
        method: "GET",
        params,
      }),
    detail: (termId: number) =>
      apiRequest<DictionaryTermDetail>(`/api/dictionary/${termId}/`, {
        method: "GET",
      }),
  },
};

