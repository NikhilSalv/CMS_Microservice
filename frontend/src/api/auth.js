import axios from "axios";

const API_BASE = "http://localhost:8000/api"; // identity service URL

export const registerUser = async (data) => {
  const response = await axios.post(`${API_BASE}/register/`, data);
  return response.data;
};

export const loginUser = async (data) => {
  const response = await axios.post(`${API_BASE}/auth/login/`, data,{
      headers: { "Content-Type": "application/json" },
    });
  return response.data;
};