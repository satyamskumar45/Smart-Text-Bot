import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "https://smart-text-bot-backend.onrender.com";
const USE_COOKIES = (import.meta.env.VITE_USE_COOKIES || "false") === "true";

const api = axios.create({
  baseURL: API_BASE_URL,
  // If you use cookie-based (httpOnly) sessions, set VITE_USE_COOKIES=true.
  // Otherwise, keep cookies off and use `Authorization: Bearer <token>`.
  withCredentials: USE_COOKIES,
  headers: {
    "Content-Type": "application/json",
  },
});

// ================= AUTH APIs =================
export const signup = (data) => api.post("/auth/signup", data);
export const login = (data) => api.post("/auth/login", data);
export const logout = () => api.post("/auth/logout");
export const getCurrentUser = () => api.get("/auth/me");

// ================= AUTH STORAGE =================
export const setAuthToken = (token) => {
  if (token) {
    api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common["Authorization"];
  }
};

export const persistAuthSession = (data) => {
  localStorage.setItem("auth", JSON.stringify(data));
};

export const getStoredAuth = () => {
  const data = localStorage.getItem("auth");
  return data ? JSON.parse(data) : null;
};

export const clearStoredAuth = () => {
  localStorage.removeItem("auth");
  delete api.defaults.headers.common["Authorization"];
};

export const subscribeToAuthChanges = (callback) => {
  window.addEventListener("storage", callback);
};

// ================= DASHBOARD =================
export const fetchDashboard = () => api.get("/dashboard");

// ================= CHAT =================
export const chat = (data) => api.post("/chat", data);

// ================= AI FEATURES =================
export const translate = (data) => api.post("/translate", data);

// BOTH names supported to avoid breaking code
export const summarize = (data) => api.post("/summarize", data);
export const summarizeText = (data) => api.post("/summarize", data);

export const sentiment = (data) => api.post("/sentiment", data);

// ================= IMAGE OCR =================
export const scanImage = (formData) =>
  api.post("/image/scan", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

// ================= ADMIN =================
export const fetchAdminStats = () => api.get("/admin/stats");
export const fetchAdminUsers = () => api.get("/admin/users");

export const updateAdminUserRole = (userId, role) =>
  api.put(`/admin/users/${userId}/role`, { role });

export const deleteAdminUser = (userId) =>
  api.delete(`/admin/users/${userId}`);

// ================= EXPORT DEFAULT =================
export default api;