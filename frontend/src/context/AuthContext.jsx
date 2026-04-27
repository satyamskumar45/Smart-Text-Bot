import React, { createContext, useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import * as api from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const storedSession = api.getStoredSession();
  const [user, setUser] = useState(storedSession?.user || null);
  const [status, setStatus] = useState("ready");
  const navigate = useNavigate();

  useEffect(() => {
    let cancelled = false;

    if (storedSession?.access_token) {
      api.setAuthToken(storedSession.access_token);
    }

    if (!storedSession) {
      setStatus("ready");
      return undefined;
    }

    api.getSession()
      .then((response) => {
        if (cancelled) return;
        api.setAuthToken(response.access_token);
        api.persistSession({
          access_token: response.access_token,
          user: response.user,
          remember: storedSession.remember ?? response.user?.role !== "guest",
        });
        setUser(response.user);
      })
      .catch(() => {
        if (cancelled) return;
        api.clearStoredSession();
        api.setAuthToken(null);
        setUser(null);
      })
      .finally(() => {
        if (!cancelled) {
          setStatus("ready");
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const login = React.useCallback(async ({ email, password, remember }) => {
    const result = await api.login(email, password, remember);
    api.setAuthToken(result.access_token);
    api.persistSession({ access_token: result.access_token, user: result.user, remember });
    setUser(result.user);
    return result.user;
  }, []);

  const signup = React.useCallback(async ({ email, password, display_name, remember }) => {
    const result = await api.signup(email, password, display_name, remember);
    api.setAuthToken(result.access_token);
    api.persistSession({ access_token: result.access_token, user: result.user, remember });
    setUser(result.user);
    return result.user;
  }, []);

  const logout = React.useCallback(async () => {
    await api.logout();
    api.clearStoredSession();
    api.setAuthToken(null);
    setUser(null);
    navigate("/auth/login", { replace: true });
  }, [navigate]);

  const startGuest = React.useCallback(async () => {
    const result = await api.startGuest();
    api.setAuthToken(result.access_token);
    const guestUser = result.user || { role: "guest", display_name: "Guest Learner" };
    api.persistSession({ access_token: result.access_token, user: guestUser, remember: true });
    setUser(guestUser);
    return result;
  }, []);

  return (
    <AuthContext.Provider value={{ user, status, login, signup, logout, startGuest }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
