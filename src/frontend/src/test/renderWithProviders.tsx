import type { ReactNode } from "react";
import { render } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import "../shared/i18n";
import { AuthProvider } from "../features/auth/AuthContext";
import type { CurrentUser } from "../shared/api/client";

export interface RenderOptions {
  route?: string;
  path?: string;
  user?: CurrentUser | null;
}

export function renderWithProviders(
  ui: ReactNode,
  { route = "/", path = "*", user = null }: RenderOptions = {}
) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <AuthProvider initialUser={user} skipInitialFetch>
        <MemoryRouter
          initialEntries={[route]}
          future={{ v7_startTransition: true, v7_relativeSplatPath: true }}
        >
          <Routes>
            <Route path={path} element={ui} />
            <Route path="*" element={ui} />
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}
