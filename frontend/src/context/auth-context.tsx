import { createContext, useCallback, useEffect, useMemo, useState } from "react";

import { tokenStorage } from "@/api/client";
import { authService } from "@/services/auth-service";
import type { LoginCredentials, RegisterCredentials, User } from "@/types/auth";

interface AuthContextValue {
  user: User | null;
  isReady: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (credentials: RegisterCredentials) => Promise<void>;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isReady, setIsReady] = useState(false);

  const logout = useCallback(() => {
    tokenStorage.clear();
    setUser(null);
  }, []);

  useEffect(() => {
    const restoreSession = async () => {
      if (!tokenStorage.get()) {
        setIsReady(true);
        return;
      }

      try {
        setUser(await authService.getCurrentUser());
      } catch {
        tokenStorage.clear();
      } finally {
        setIsReady(true);
      }
    };

    void restoreSession();
  }, []);

  useEffect(() => {
    window.addEventListener("auth:unauthorized", logout);
    return () => window.removeEventListener("auth:unauthorized", logout);
  }, [logout]);

  const login = useCallback(async (credentials: LoginCredentials) => {
    const session = await authService.login(credentials);
    tokenStorage.set(session.access_token);
    try {
      setUser(await authService.getCurrentUser());
    } catch (error) {
      tokenStorage.clear();
      throw error;
    }
  }, []);

  const register = useCallback(
    async (credentials: RegisterCredentials) => {
      await authService.register(credentials);
      await login({ email: credentials.email, password: credentials.password });
    },
    [login],
  );

  const value = useMemo(
    () => ({ user, isReady, login, register, logout }),
    [isReady, login, logout, register, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
