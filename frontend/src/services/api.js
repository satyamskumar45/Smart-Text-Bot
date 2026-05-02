import axios from "axios";

const API_BASE_URL = "https://smart-text-bot-backend-docker.onrender.com";

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

// Response interceptor: unwrap standard backend wrapper { success, data, error }
api.interceptors.response.use(
  (res) => {
    if (res?.data && typeof res.data === "object" && "success" in res.data) {
      return res.data.data;
    }
    return res.data;
  },
  (err) => Promise.reject(err?.response?.data || err)
);

// ================ AUTH HELPERS ================
export const signup = async (payload) => {
  return api.post("/auth/signup", payload).then((r) => r);
};

export const login = async (payload) => {
  return api.post("/auth/login", payload).then((r) => r);
};

export const logout = async (refreshToken) => {
  return api.post("/auth/logout", { refresh_token: refreshToken }).then((r) => r);
};

// Local session helpers used by AuthContext
let authToken = null;
const subscribers = new Set();

export const setAuthToken = (token) => {
  authToken = token;
  if (token) {
    api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common["Authorization"];
  }
  subscribers.forEach((s) => s({ token }));
};

export const persistAuthSession = (session) => {
  localStorage.setItem("smarttext_auth", JSON.stringify(session));
};

export const getStoredAuth = () => {
  try {
    const raw = localStorage.getItem("smarttext_auth");
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
};

export const clearStoredAuth = () => {
  localStorage.removeItem("smarttext_auth");
};

export const subscribeToAuthChanges = (fn) => {
  subscribers.add(fn);
  return () => subscribers.delete(fn);
};

export const getCurrentUser = async () => {
  return api.get("/auth/me").then((r) => ({ user: r?.user || r }));
};

// ================ DASHBOARD / ADMIN ================
export const fetchDashboard = async () => {
  return api.get("/dashboard").then((r) => r);
};

export const fetchAdminStats = async () => {
  return api.get("/admin/stats").then((r) => r);
};

export const fetchAdminUsers = async () => {
  return api.get("/admin/users").then((r) => r);
};

export const updateAdminUserRole = async (userId, role) => {
  return api.patch(`/admin/users/${userId}/role`, { role }).then((r) => r);
};

export const deleteAdminUser = async (userId) => {
  return api.delete(`/admin/users/${userId}`).then((r) => r);
};

// ================ AI FEATURES ================
export const chat = async (message) => {
  const payload = typeof message === "string" ? { message } : message;
  return api.post("/chat", payload).then((r) => r);
};

export const translate = async (textOrPayload, source = "auto", target = null) => {
  if (typeof textOrPayload === "string") {
    const payload = { text: textOrPayload, source_lang: source, target_lang: target };
    return api.post("/translate", payload).then((r) => r);
  }
  return api.post("/translate", textOrPayload).then((r) => r);
};

export const explainTranslation = async (original, translated, source = "auto", target = null) => {
  const payload = { original, translated, source_lang: source, target_lang: target };
  return api.post("/explain", payload).then((r) => r);
};

export const summarize = async (textOrPayload) => {
  const payload = typeof textOrPayload === "string" ? { text: textOrPayload } : textOrPayload;
  return api.post("/summarize", payload).then((r) => r);
};

export const summarizeText = summarize;

export const sentiment = async (textOrPayload) => {
  const payload = typeof textOrPayload === "string" ? { text: textOrPayload } : textOrPayload;
  return api.post("/sentiment", payload).then((r) => r);
};

export const contextTransform = async (textOrPayload, tone) => {
  const payload = typeof textOrPayload === "string" ? { text: textOrPayload, tone } : textOrPayload;
  return api.post("/context/transform", payload).then((r) => r);
};

export const scanImage = async (file) => {
  const form = new FormData();
  form.append("file", file);
  return api.post("/image-scan", form, { headers: { "Content-Type": "multipart/form-data" } }).then((r) => r);
};

export const pipeline = async (file, target_lang) => {
  const form = new FormData();
  form.append("file", file);
  if (target_lang) form.append("target_lang", target_lang);
  return api.post("/pipeline", form, { headers: { "Content-Type": "multipart/form-data" } }).then((r) => r);
};

export const writing = async (payload) => {
  return api.post("/grammar", payload).then((r) => r);
};

// ================ EXPORT DEFAULT ================
export default api;