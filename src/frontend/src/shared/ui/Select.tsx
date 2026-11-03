import { useId, type SelectHTMLAttributes } from "react";
import styles from "./Select.module.css";

export interface SelectOption {
  value: string;
  label: string;
}

export interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label: string;
  options: SelectOption[];
  error?: string | string[];
}

export function Select({
  label,
  options,
  error,
  id: providedId,
  className = "",
  ...rest
}: SelectProps) {
  const generatedId = useId();
  const id = providedId || generatedId;
  const errorText = Array.isArray(error) ? error.filter(Boolean).join(" ") : error;
  const hasError = Boolean(errorText);
  const errorId = `${id}-error`;

  return (
    <div className={styles.field}>
      <label htmlFor={id} className={styles.label}>
        {label}
      </label>
      <select
        id={id}
        aria-invalid={hasError || undefined}
        aria-describedby={hasError ? errorId : undefined}
        className={`${styles.select} ${hasError ? styles.invalid : ""} ${className}`.trim()}
        {...rest}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {hasError ? (
        <span id={errorId} role="alert" className={styles.error}>
          {errorText}
        </span>
      ) : null}
    </div>
  );
}
