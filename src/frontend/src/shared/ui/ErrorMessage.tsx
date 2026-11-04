import type { ReactNode } from "react";
import styles from "./ErrorMessage.module.css";

export interface ErrorMessageProps {
  children: ReactNode;
}

export function ErrorMessage({ children }: ErrorMessageProps) {
  if (!children) return null;
  return (
    <div className={styles.errorMessage} role="alert">
      {children}
    </div>
  );
}

