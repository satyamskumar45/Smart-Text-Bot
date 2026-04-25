import axios from "axios";

const API = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "https://smart-text-bot-backend.onrender.com",
  timeout: 25000,
  withCredentials: true,
});

let authToken = null;

export function setAuthToken(token) {
  authToken = token;
}

API.interceptors.request.use(
  (config) => {
    if (authToken) {
      config.headers = config.headers || {};
      config.headers.Authorization = `Bearer ${authToken}`;
    }
    console.log(`[API REQUEST] ${config.method?.toUpperCase()} ${config.url}`, config.data);
    return config;
  },
  (error) => Promise.reject(error)
);

API.interceptors.response.use(
  (response) => {
    const data = response.data;
    if (data && typeof data === "object" && "success" in data) {
      if (data.success) {
        return { ...response, data: data.data };
      }
      const err = new Error(data.error || "Unknown error");
      err.response = response;
      return Promise.reject(err);
    }
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    if (
      error.response &&
      error.response.status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      originalRequest.url !== "/auth/refresh" &&
      !["/auth/login", "/auth/signup", "/auth/guest", "/auth/session"].includes(originalRequest.url)
    ) {
      originalRequest._retry = true;
      try {
        const refreshResponse = await API.post("/auth/refresh");
        setAuthToken(refreshResponse.data.access_token);
        originalRequest.headers = originalRequest.headers || {};
        originalRequest.headers.Authorization = `Bearer ${refreshResponse.data.access_token}`;
        return API(originalRequest);
      } catch (refreshError) {
        setAuthToken(null);
        return Promise.reject(refreshError);
      }
    }

    if (error.response && error.response.data && typeof error.response.data === "object") {
      error.message = error.response.data.error || error.message;
    }
    return Promise.reject(error);
  }
);

export const login = (email, password, remember) =>
  API.post("/auth/login", { email, password, remember }).then((response) => response.data);

export const signup = (email, password, display_name, remember) =>
  API.post("/auth/signup", { email, password, display_name, remember }).then((response) => response.data);

export const logout = () => API.post("/auth/logout").then((response) => response.data);
export const getSession = () => API.get("/auth/session").then((response) => response.data);
export const startGuest = () => API.post("/auth/guest").then((response) => response.data);
export const fetchDashboard = () => API.get("/dashboard").then((response) => response.data);
export const fetchHistory = () => API.get("/history").then((response) => response.data);
export const fetchFavorites = () => API.get("/history/favorites").then((response) => response.data);
export const toggleFavorite = (historyId, favorite = true) =>
  API.patch(`/history/${historyId}/favorite`, { favorite }).then((response) => response.data);
export const fetchLearningProgress = () =>
  API.get("/learning/progress").then((response) => response.data);
export const saveLearningProgress = (payload) =>
  API.post("/learning/progress", payload).then((response) => response.data);

export const chat = (message, history = []) =>
  API.post("/chat", { message, history }).then((response) => response.data);

export const translate = (text, source_lang = "auto", target_lang = "en") =>
  API.post("/translate", { text, source_lang, target_lang }).then((response) => response.data);

export const explainTranslation = (original, translation, source_lang, target_lang) =>
  API.post("/explain", { original, translation, source_lang, target_lang }).then((response) => response.data);

export const sentiment = (text) => API.post("/sentiment", { text }).then((response) => response.data);
export const summarize = (text, mode = "short") =>
  API.post("/summarize", { text, mode }).then((response) => response.data);
export const summarizeDocument = (file, mode = "short") => {
  const form = new FormData();
  form.append("file", file);
  form.append("mode", mode);
  return API.post("/summarize", form).then((response) => response.data);
};
export const writing = (text, mode = "grammar", tone_style = "professional") =>
  API.post("/grammar", { text, mode, tone_style }).then((response) => response.data);
export const contextTransform = (text, tone) =>
  API.post("/context/transform", { text, tone }).then((response) => response.data);
export const imageScan = (imageFile) => {
  const form = new FormData();
  form.append("image", imageFile);
  return API.post("/image-scan", form).then((response) => response.data);
};
export const pipeline = (imageFile, target_lang = "en") => {
  const form = new FormData();
  form.append("file", imageFile);
  form.append("target_lang", target_lang);
  return API.post("/pipeline", form).then((response) => response.data);
};
export const writingAssistant = (text) =>
  API.post("/writing-assistant", { text }).then((response) => response.data);
export const docPipeline = (file) => {
  const form = new FormData();
  form.append("file", file);
  return API.post("/doc-pipeline", form).then((response) => response.data);
};
