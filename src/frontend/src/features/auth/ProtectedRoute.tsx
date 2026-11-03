import type { ReactNode } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuth } from "./AuthContext";

export interface ProtectedRouteProps {
  children: ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { user, isLoading } = useAuth();
  const location = useLocation();
  const { t } = useTranslation();

  if (isLoading) {
    return <p role="status">{t("app.loading")}</p>;
  }

  if (!user) {
    const intended = `${location.pathname}${location.search}`;
    return <Navigate to="/login" state={{ from: intended }} replace />;
  }

  return <>{children}</>;
}
