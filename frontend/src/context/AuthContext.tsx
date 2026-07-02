import {
  createContext,
  useEffect,
  useState,
  type PropsWithChildren,
} from "react";
import axios from "axios";

import {
  clearStoredToken,
  getStoredToken,
  setStoredToken,
} from "../lib/storage";
import { getCurrentUser, loginUser, registerUser } from "../services/auth";
import type {
  AuthContextValue,
  AuthUser,
  LoginFormValues,
  RegisterFormValues,
} from "../types/auth";

export const AuthContext = createContext<AuthContextValue | undefined>(
  undefined,
);

export function AuthProvider({ children }: PropsWithChildren) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setToken] = useState<string | null>(getStoredToken());
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let active = true;

    async function hydrateAuth() {
      if (!token) {
        if (active) {
          setUser(null);
          setIsLoading(false);
        }
        return;
      }

      try {
        const profile = await getCurrentUser();
        if (active) {
          setUser(profile);
        }
      } catch (error) {
        clearStoredToken();
        if (active) {
          setToken(null);
          setUser(null);
        }
      } finally {
        if (active) {
          setIsLoading(false);
        }
      }
    }

    setIsLoading(true);
    void hydrateAuth();

    return () => {
      active = false;
    };
  }, [token]);

  async function login(values: LoginFormValues) {
    const authToken = await loginUser(values);

    // Persist token first so the hydration effect can resolve user state consistently.
    setStoredToken(authToken.access_token);
    setToken(authToken.access_token);
  }

  async function register(values: RegisterFormValues) {
    await registerUser(values);
  }

  function logout() {
    clearStoredToken();
    setToken(null);
    setUser(null);
  }

  const value: AuthContextValue = {
    user,
    token,
    isAuthenticated: Boolean(user && token),
    isLoading,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function getApiErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    return String(error.response?.data?.detail ?? error.message);
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "Something went wrong. Please try again.";
}
