import { createContext, useContext, useEffect, useMemo, useState } from "react";
import * as api from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [status, setStatus] = useState("loading");

  useEffect(() => {
    let ignore = false;

    async function restoreSession() {
      const storedAuth = api.getStoredAuth();

      if (!storedAuth?.token) {
        setStatus("ready");
        return;
      }

      api.setAuthToken(storedAuth.token);
      setToken(storedAuth.token);
      setUser(storedAuth.user || null);

      try {
        const response = await api.getCurrentUser();
        if (ignore) {
          return;
        }
        const nextSession = {
          ...storedAuth,
          user: response.user,
        };
        api.persistAuthSession(nextSession);
        setUser(response.user);
      } catch (_error) {
        if (ignore) {
          return;
        }
        api.clearStoredAuth();
        api.setAuthToken(null);
        setToken(null);
        setUser(null);
      } finally {
        if (!ignore) {
          setStatus("ready");
        }
      }
    }

    restoreSession();

    const unsubscribe = api.subscribeToAuthChanges((session) => {
      if (ignore) {
        return;
      }

      if (!session?.token) {
        setToken(null);
        setUser(null);
        return;
      }

      setToken(session.token);
      setUser(session.user || null);
    });

    return () => {
      ignore = true;
      unsubscribe();
    };
  }, []);

  async function login(credentials) {
    const response = await api.login(credentials);
    const nextToken = response.access_token;
    const session = {
      token: nextToken,
      refreshToken: response.refresh_token || null,
      user: response.user,
    };

    api.setAuthToken(nextToken);
    api.persistAuthSession(session);
    setToken(nextToken);
    setUser(response.user);

    return response.user;
  }

  async function signup(payload) {
    const response = await api.signup(payload);
    const nextToken = response.access_token;
    const session = {
      token: nextToken,
      refreshToken: response.refresh_token || null,
      user: response.user,
    };

    api.setAuthToken(nextToken);
    api.persistAuthSession(session);
    setToken(nextToken);
    setUser(response.user);

    return response.user;
  }

  async function logout() {
    const storedAuth = api.getStoredAuth();

    try {
      await api.logout(storedAuth?.refreshToken);
    } catch (_error) {
      // Clear local auth state even if backend logout fails.
    } finally {
      api.clearStoredAuth();
      api.setAuthToken(null);
      setToken(null);
      setUser(null);
    }
  }

  const value = useMemo(
    () => ({
      user,
      token,
      status,
      isAuthenticated: Boolean(token && user),
      login,
      signup,
      logout,
    }),
    [user, token, status]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider.");
  }

  return context;
}
