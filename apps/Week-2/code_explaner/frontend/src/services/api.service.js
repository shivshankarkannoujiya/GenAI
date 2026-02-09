import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:3000/api/v1",
  headers: { "Content-Type": "application/json" },
});

export const getCodeExplanation = async (code, language) => {
  const response = await api.post("/explain", { code, language });
  return response.data;
};
