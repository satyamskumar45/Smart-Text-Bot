import axios from "axios";

const API_BASE_URL =
  (typeof process !== "undefined" && process.env?.REACT_APP_API_URL) ||
  (typeof import.meta !== "undefined" && import.meta.env?.VITE_API_BASE_URL) ||
  "http://localhost:5000";

const API = axios.create({
  baseURL: API_BASE_URL,
});

export const chat = (message) =>
  API.post("/chat", { message }).then((response) => response.data);

export const translate = (text, fromLang = "en", toLang = "hi") =>
  API.post("/translate", { text, source: fromLang, target: toLang }).then((response) => response.data);

export const sentiment = (text) =>
  API.post("/sentiment", { text }).then((response) => response.data);

export const summarizeText = (text) =>
  API.post("/api/summarize", { text }).then((response) => response.data);

export const scanImage = (image) => {
  const formData = new FormData();
  formData.append("image", image);
  return API.post("/api/image-scan", formData).then((response) => response.data);
};
