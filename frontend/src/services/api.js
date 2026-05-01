import axios from "axios";
const API = axios.create({ baseURL:"http://localhost:5000" });

export const chat = (msg)=>API.post("/chat",{message:msg});
export const translate = (text)=>API.post("/translate",{text});
export const sentiment = (text)=>API.post("/sentiment",{text});
