import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "https://smart-text-bot-backend-docker.onrender.com";

console.log("API BASE URL:", API_BASE_URL);

const STORAGE_KEY = "smarttextbot.auth";
const AUTH_EVENT = "smarttextbot:auth-change";

const API = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

let refreshPromise = null;

function notifyAuthChanged() {
  if (typeof window !== "undefined") {
    window.dispatchEvent(new Event(AUTH_EVENT));
  }
}

function readStoredAuth() {
  if (typeof window === "undefined") {
    return null;
  }

  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw);
  } catch (_error) {
    window.localStorage.removeItem(STORAGE_KEY);
    return null;
  }
}

function extractPayload(response) {
  return response?.data?.data ?? response?.data;
}

function extractErrorMessage(error, fallbackMessage) {
  return (
    error?.response?.data?.message ||
    error?.response?.data?.error ||
    error?.message ||
    fallbackMessage
  );
}

function shouldBypassRefresh(config = {}) {
  if (config.skipAuthRefresh) {
    return true;
  }

  const url = config.url || "";
  return ["/auth/login", "/auth/signup", "/auth/refresh"].some((path) => url.includes(path));
}

export function setAuthToken(token) {
  if (token) {
    API.defaults.headers.common.Authorization = `Bearer ${token}`;
  } else {
    delete API.defaults.headers.common.Authorization;
  }
}

export function getStoredAuth() {
  return readStoredAuth();
}

export function persistAuthSession(session) {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
  notifyAuthChanged();
}

export function clearStoredAuth() {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.removeItem(STORAGE_KEY);
  notifyAuthChanged();
}

export function subscribeToAuthChanges(callback) {
  if (typeof window === "undefined") {
    return () => {};
  }

  const handler = () => callback(readStoredAuth());
  window.addEventListener(AUTH_EVENT, handler);
  window.addEventListener("storage", handler);

  return () => {
    window.removeEventListener(AUTH_EVENT, handler);
    window.removeEventListener("storage", handler);
  };
}

async function refreshAccessToken() {
  const storedAuth = readStoredAuth();
  if (!storedAuth?.refreshToken) {
    throw new Error("Missing refresh token.");
  }

  const response = await API.post(
    "/auth/refresh",
    { refresh_token: storedAuth.refreshToken },
    { skipAuthRefresh: true }
  );

  const payload = extractPayload(response);
  const nextSession = {
    ...storedAuth,
    token: payload.access_token,
    refreshToken: payload.refresh_token || storedAuth.refreshToken,
  };

  setAuthToken(nextSession.token);
  persistAuthSession(nextSession);
  return nextSession;
}

const initialSession = readStoredAuth();
if (initialSession?.token) {
  setAuthToken(initialSession.token);
}

API.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error?.config;

    if (
      error?.response?.status !== 401 ||
      !originalRequest ||
      originalRequest._retry ||
      shouldBypassRefresh(originalRequest)
    ) {
      return Promise.reject(error);
    }

    if (!refreshPromise) {
      refreshPromise = refreshAccessToken()
        .catch((refreshError) => {
          clearStoredAuth();
          setAuthToken(null);
          throw refreshError;
        })
        .finally(() => {
          refreshPromise = null;
        });
    }

    try {
      const session = await refreshPromise;
      originalRequest._retry = true;
      originalRequest.headers = {
        ...(originalRequest.headers || {}),
        Authorization: `Bearer ${session.token}`,
      };
      return API(originalRequest);
    } catch (refreshError) {
      return Promise.reject(refreshError);
    }
  }
);

export async function login({ email, password }) {
  try {
    const response = await API.post("/auth/login", { email, password }, { skipAuthRefresh: true });
    return extractPayload(response);
  } catch (error) {
    throw new Error(extractErrorMessage(error, "Unable to log in."));
  }
}

export async function signup({ email, password, name }) {
  try {
    const response = await API.post("/auth/signup", { email, password, name }, { skipAuthRefresh: true });
    return extractPayload(response);
  } catch (error) {
    throw new Error(extractErrorMessage(error, "Unable to create account."));
  }
}

export async function getCurrentUser() {
  try {
    const response = await API.get("/auth/me");
    return extractPayload(response);
  } catch (error) {
    throw new Error(extractErrorMessage(error, "Unable to fetch current user."));
  }
}

export async function logout(refreshToken) {
  try {
    const response = await API.post(
      "/auth/logout",
      refreshToken ? { refresh_token: refreshToken } : {},
      { skipAuthRefresh: true }
    );
    return extractPayload(response);
  } catch (error) {
    throw new Error(extractErrorMessage(error, "Unable to log out."));
  }
}

export async function fetchDashboard() {
  try {
    const response = await API.get("/dashboard");
    return extractPayload(response);
  } catch (error) {
    throw new Error(extractErrorMessage(error, "Unable to load dashboard."));
  }
}

export async function fetchAdminStats() {
  try {
    const response = await API.get("/admin/stats");
    return extractPayload(response);
  } catch (error) {
    throw new Error(extractErrorMessage(error, "Unable to load admin stats."));
  }
}

export async function fetchAdminUsers() {
  try {
    const response = await API.get("/admin/users");
    return extractPayload(response);
  } catch (error) {
    throw new Error(extractErrorMessage(error, "Unable to load users."));
  }
}

export async function updateAdminUserRole(userId, role) {
  try {
    const response = await API.patch(`/admin/users/${userId}/role`, { role });
    return extractPayload(response);
  } catch (error) {
    throw new Error(extractErrorMessage(error, "Unable to update user role."));
  }
}

export async function deleteAdminUser(userId) {
  try {
    const response = await API.delete(`/admin/users/${userId}`);
    return extractPayload(response);
  } catch (error) {
    throw new Error(extractErrorMessage(error, "Unable to delete user."));
  }
}

export const chat = async (message) => extractPayload(await API.post("/chat", { message }));

export const translate = async (text, fromLang = "en", toLang = "hi") =>
  extractPayload(await API.post("/translate", { text, source: fromLang, target: toLang }));

export const sentiment = async (text) =>
  extractPayload(await API.post("/sentiment", { text }));

export const summarizeText = async (text) =>
  extractPayload(await API.post("/summarize", { text }));

export const scanImage = async (image) => {
  const formData = new FormData();
  formData.append("image", image);
  return extractPayload(await API.post("/image-scan", formData));
};
