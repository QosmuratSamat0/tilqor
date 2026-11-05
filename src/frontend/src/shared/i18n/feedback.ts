import type { TFunction } from "i18next";
import { ApiError, type Feedback, type FieldErrors } from "../api/client";

function translateFeedback(
  kind: "warning" | "error",
  code: string | null | undefined,
  params: Record<string, unknown>,
  message: string,
  t: TFunction,
): string {
  const values = Object.fromEntries(Object.entries(params).map(([key, value]) =>
    [key, Array.isArray(value) ? value.join(", ") : value]));
  return code ? t(`feedback.${kind}.${code}`, { ...values, defaultValue: message }) : message;
}

export function warningText(warning: Feedback, t: TFunction): string {
  return translateFeedback("warning", warning.code, warning.params, warning.message, t);
}

export function errorFeedback(error: ApiError, t: TFunction) {
  const fields: FieldErrors = Object.fromEntries(Object.entries(error.fieldErrors).map(
    ([field, messages]) => [field, messages.map((message, index) => translateFeedback(
      "error", error.fieldCodes[field]?.[index], error.params[field] ?? {}, message, t,
    ))],
  ));
  const detail = error.detail
    ? translateFeedback("error", error.code, error.params.detail ?? {}, error.detail, t)
    : null;
  return { fields, detail, message: detail ?? Object.values(fields).flat()[0] ?? error.message };
}
