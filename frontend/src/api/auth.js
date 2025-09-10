import axios from "axios";

const BASE_URL = "http://identity:8000/api"; // Docker Compose service name

export const registerUser = async (username, email, password, password2) => {
  const res = await axios.post(`${BASE_URL}/auth/register/`, { username, email, password, password2 });
  return res.data;
};

export const loginUser = async (username, password) => {
  const res = await axios.post(`${BASE_URL}/auth/login/`, { username, password });
  return res.data;
};
