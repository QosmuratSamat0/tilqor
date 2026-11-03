/* eslint-disable react-refresh/only-export-components */
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { useQueryClient } from "@tanstack/react-query";
import {
  api,
  ApiError,
  type CurrentUser,
  type LoginRequest,
  type RegisterRequest,
} from "../../shared/api/client";

export interface AuthContextValue {
  user: CurrentUser | null;
  isLoading: boolean;
  login: (credentials: LoginRequest) => Promise<CurrentUser>;
  register: (payload: RegisterRequest) => Promise<CurrentUser>;
  logout: () => Promise<void>;
  acceptTerms: () => Promise<CurrentUser>;
  refreshUser: () => Promise<CurrentUser | null>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export interface AuthProviderProps {
  children: ReactNode;
  initialUser?: CurrentUser | null;
  skipInitialFetch?: boolean;
}

export function AuthProvider({
  children,
  initialUser = null,
  skipInitialFetch = false,
}: AuthProviderProps) {
  const [user, setUser] = useState<CurrentUser | null>(initialUser);
  const [isLoading, setIsLoading] = useState<boolean>(!skipInitialFetch);
  const queryClient = useQueryClient();

  const refreshUser = useCallback(async (): Promise<CurrentUser | null> => {
    try {
      const current = await api.auth.me();
      setUser(current);
      return current;
    } catch (err) {
      if (err instanceof ApiError && (err.status === 401 || err.status === 403)) {
        setUser(null);
        return null;
      }
      setUser(null);
      return null;
    }
  }, []);

  useEffect(() => {
    if (skipInitialFetch) {
      setIsLoading(false);
      return;
    }
    let active = true;
    async function bootstrap() {
      try {
        await api.auth.csrf().catch(() => undefined);
        const current = await api.auth.me();
        if (active) {
          setUser(current);
        }
      } catch {
        if (active) {
          setUser(null);
        }
      } finally {
        if (active) {
          setIsLoading(false);
        }
      }
    }
    void bootstrap();
    return () => {
      active = false;
    };
  }, [skipInitialFetch]);

  const login = useCallback(
    async (credentials: LoginRequest): Promise<CurrentUser> => {
      await api.auth.csrf().catch(() => undefined);
      const loggedIn = await api.auth.login(credentials);
      setUser(loggedIn);
      await api.auth.csrf().catch(() => undefined);
      await queryClient.invalidateQueries();
      return loggedIn;
    },
    [queryClient]
  );

  const register = useCallback(
    async (payload: RegisterRequest): Promise<CurrentUser> => {
      await api.auth.csrf().catch(() => undefined);
      const registered = await api.auth.register(payload);
      setUser(registered);
      await api.auth.csrf().catch(() => undefined);
      await queryClient.invalidateQueries();
      return registered;
    },
    [queryClient]
  );

  const logout = useCallback(async (): Promise<void> => {
    await api.auth.logout();
    setUser(null);
    await api.auth.csrf().catch(() => undefined);
    queryClient.clear();
  }, [queryClient]);

  const acceptTerms = useCallback(async (): Promise<CurrentUser> => {
    const updated = await api.auth.acceptTerms();
    setUser(updated);
    return updated;
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        login,
        register,
        logout,
        acceptTerms,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return ctx;
}
