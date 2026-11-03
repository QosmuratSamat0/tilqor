import { useId, type InputHTMLAttributes, type TextareaHTMLAttributes } from "react";
import styles from "./Field.module.css";

interface BaseFieldProps {
  label: string;
  hint?: string;
  error?: string | string[];
  id?: string;
}

export type InputFieldProps = BaseFieldProps &
  InputHTMLAttributes<HTMLInputElement> & {
    multiline?: false;
  };

export type TextareaFieldProps = BaseFieldProps &
  TextareaHTMLAttributes<HTMLTextAreaElement> & {
    multiline: true;
  };

export type FieldProps = InputFieldProps | TextareaFieldProps;

export function Field(props: FieldProps) {
  const generatedId = useId();
  const id = props.id || generatedId;
  const errorText = Array.isArray(props.error)
    ? props.error.filter(Boolean).join(" ")
    : props.error;
  const hasError = Boolean(errorText);
  const errorId = `${id}-error`;
  const hintId = `${id}-hint`;

  const describedBy = [props.hint ? hintId : null, hasError ? errorId : null]
    .filter(Boolean)
    .join(" ") || undefined;

  return (
    <div className={styles.field}>
      <label htmlFor={id} className={styles.label}>
        {props.label}
        {props.required ? <span className={styles.required} aria-hidden="true">*</span> : null}
      </label>
      {props.hint ? (
        <span id={hintId} className={styles.hint}>
          {props.hint}
        </span>
      ) : null}
      {props.multiline ? (
        <textarea
          {...( filterTextareaProps(props) )}
          id={id}
          aria-invalid={hasError || undefined}
          aria-describedby={describedBy}
          className={`${styles.textarea} ${hasError ? styles.invalid : ""} ${props.className || ""}`.trim()}
        />
      ) : (
        <input
          {...( filterInputProps(props) )}
          id={id}
          aria-invalid={hasError || undefined}
          aria-describedby={describedBy}
          className={`${styles.input} ${hasError ? styles.invalid : ""} ${props.className || ""}`.trim()}
        />
      )}
      {hasError ? (
        <span id={errorId} role="alert" className={styles.error}>
          {errorText}
        </span>
      ) : null}
    </div>
  );
}

function filterInputProps(props: InputFieldProps): InputHTMLAttributes<HTMLInputElement> {
  const { label: _l, hint: _h, error: _e, multiline: _m, ...rest } = props;
  void _l;
  void _h;
  void _e;
  void _m;
  return rest;
}

function filterTextareaProps(props: TextareaFieldProps): TextareaHTMLAttributes<HTMLTextAreaElement> {
  const { label: _l, hint: _h, error: _e, multiline: _m, ...rest } = props;
  void _l;
  void _h;
  void _e;
  void _m;
  return rest;
}
