import axios from "axios";

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";
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

// Request interceptor: log outgoing requests
api.interceptors.request.use(
  (cfg) => {
    try {
      // eslint-disable-next-line no-console
      console.debug("API Request:", cfg.method, cfg.url, cfg.data || cfg.params);
    } catch (e) {
      // ignore
    }
    return cfg;
  },
  (err) => {
    // eslint-disable-next-line no-console
    console.error("API request error:", err);
    return Promise.reject(err);
  }
);

// Response interceptor: centralize error logging and normalize error shape
api.interceptors.response.use(
  (res) => {
    try {
      // eslint-disable-next-line no-console
      console.debug("API Response:", res.status, res.config.url, res.data);
    } catch (e) {}

    if (res.data && typeof res.data === "object" && "success" in res.data) {
      return res.data.data || {};
    }

    if (res.data && typeof res.data === "object" && res.data.status === "success") {
      const { status, ...payload } = res.data;
      return payload;
    }

    return res.data;
  },
  async (error) => {
    const responseData = error.response ? error.response.data : null;
    const originalRequest = error.config;

    if (
      error.response?.status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !originalRequest.url?.includes("/auth/login") &&
      !originalRequest.url?.includes("/auth/signup") &&
      !originalRequest.url?.includes("/auth/refresh") &&
      !originalRequest.url?.includes("/auth/logout")
    ) {
      const storedAuth = getStoredAuth();

      if (storedAuth?.refreshToken) {
        originalRequest._retry = true;

        try {
          const refreshedSession = await refreshSession(storedAuth.refreshToken);
          const nextSession = {
            token: refreshedSession.access_token,
            refreshToken: refreshedSession.refresh_token || storedAuth.refreshToken,
            user: refreshedSession.user || storedAuth.user || null,
          };

          persistAuthSession(nextSession);
          originalRequest.headers = originalRequest.headers || {};
          originalRequest.headers.Authorization = `Bearer ${nextSession.token}`;

          return api(originalRequest);
        } catch (_refreshError) {
          clearStoredAuth();
        }
      }
    }

    // Normalize network / server errors to include response data when present
    const normalized = {
      message: responseData?.message || error.message || "Network or server error",
      status: error.response ? error.response.status : null,
      data: responseData,
    };
    // eslint-disable-next-line no-console
    console.error("API Error:", normalized);
    return Promise.reject(normalized);
  }
);

// ================= AUTH APIs =================
export const signup = (data) => api.post("/auth/signup", data);
export const login = (data) => api.post("/auth/login", data);
export const refreshSession = (refreshToken) => api.post("/auth/refresh", { refresh_token: refreshToken });
export const logout = (refreshToken) => api.post("/auth/logout", { refresh_token: refreshToken });
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
  try {
    localStorage.setItem("auth", JSON.stringify(data));
    // keep axios header in sync
    if (data && data.access_token) {
      setAuthToken(data.access_token);
    } else if (data && data.token) {
      setAuthToken(data.token);
    }
  } catch (e) {
    // eslint-disable-next-line no-console
    console.error("persistAuthSession error", e);
  }
};

export const getStoredAuth = () => {
  const data = localStorage.getItem("auth");
  if (!data) return null;
  try {
    return JSON.parse(data);
  } catch (e) {
    // eslint-disable-next-line no-console
    console.error("getStoredAuth: failed to parse stored auth", e);
    try {
      localStorage.removeItem("auth");
    } catch (remErr) {
      // ignore
    }
    return null;
  }
};

export const explainTranslation = (arg1, arg2, arg3, arg4) => {
  let payload;
  if (typeof arg1 === "object" && arg1 !== null) {
    payload = arg1;
  } else {
    // support explainTranslation(text, translated_text, source_lang, target_lang)
    payload = {
      text: arg1,
      translated_text: arg2,
      source_lang: arg3,
      target_lang: arg4,
    };
  }
  return api.post("/translate", payload);
};

export const clearStoredAuth = () => {
  localStorage.removeItem("auth");
  delete api.defaults.headers.common["Authorization"];
};

export const subscribeToAuthChanges = (callback) => {
  const wrapped = (evt) => callback(evt);
  window.addEventListener("storage", wrapped);
  return () => window.removeEventListener("storage", wrapped);
};

// ================= DASHBOARD =================
export const fetchDashboard = () => api.get("/dashboard");
export const fetchHistory = () => api.get("/history");
export const fetchFavorites = () => api.get("/history", { params: { favorites: "true" } });
export const toggleFavorite = (historyId, isFavorite) =>
  api.patch(`/history/${historyId}/favorite`, { is_favorite: isFavorite });

// ================= CHAT =================
export const chat = (data) => api.post("/chat", typeof data === "string" ? { message: data } : data);

// ================= AI FEATURES =================
export const translate = (data) => api.post("/translate", data);

// BOTH names supported to avoid breaking code
export const summarize = (data) => api.post("/summarize", typeof data === "string" ? { text: data } : data);
export const summarizeText = (data) => api.post("/summarize", typeof data === "string" ? { text: data } : data);

export const sentiment = (data) => api.post("/sentiment", typeof data === "string" ? { text: data } : data);

// ================= IMAGE OCR =================
export const scanImage = (file) => {
  const formData = file instanceof FormData ? file : new FormData();
  if (!(file instanceof FormData)) {
    formData.append("image", file);
  }

  return api.post("/image-scan", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
};

export const pipeline = (file, targetLang = "en") => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("target_lang", targetLang);

  return api.post("/pipeline", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
};

// ================= ADMIN =================
export const fetchAdminStats = () => api.get("/admin/stats");
export const fetchAdminUsers = () => api.get("/admin/users");

export const updateAdminUserRole = (userId, role) =>
  api.patch(`/admin/users/${userId}/role`, { role });

export const deleteAdminUser = (userId) =>
  api.delete(`/admin/users/${userId}`);

// ================= EXPORT DEFAULT =================
export default api;
