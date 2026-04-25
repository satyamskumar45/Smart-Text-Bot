import React, { createContext, useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import * as api from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [status, setStatus] = useState("loading");
  const navigate = useNavigate();

  useEffect(() => {
    api.getSession()
      .then((response) => {
        api.setAuthToken(response.access_token);
        setUser(response.user);
      })
      .catch(() => {
        setUser(null);
      })
      .finally(() => {
        setStatus("ready");
      });
  }, []);

  const login = React.useCallback(async ({ email, password, remember }) => {
    const result = await api.login(email, password, remember);
    api.setAuthToken(result.access_token);
    setUser(result.user);
    return result.user;
  }, []);

  const signup = React.useCallback(async ({ email, password, display_name, remember }) => {
    const result = await api.signup(email, password, display_name, remember);
    api.setAuthToken(result.access_token);
    setUser(result.user);
    return result.user;
  }, []);

  const logout = React.useCallback(async () => {
    await api.logout();
    api.setAuthToken(null);
    setUser(null);
    navigate("/auth/login", { replace: true });
  }, [navigate]);

  const startGuest = React.useCallback(async () => {
    const result = await api.startGuest();
    api.setAuthToken(result.access_token);
    setUser({ role: "guest", display_name: "Guest Learner" });
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
