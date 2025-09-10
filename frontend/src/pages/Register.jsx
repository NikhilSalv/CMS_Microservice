import { useState, useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import { registerUser } from "../api/auth";
import { useNavigate } from "react-router-dom";

export default function Register() {
  const [form, setForm] = useState({ username: "", email: "", password: "", password2: "" });
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = await registerUser(form.username, form.email, form.password, form.password2);
      login(data);  // store JWT in context/localStorage
      navigate("/profile");
    } catch (err) {
      console.error(err.response?.data || err.message);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Register</h2>
      <input name="username" placeholder="Username" onChange={handleChange} value={form.username} />
      <input name="email" placeholder="Email" onChange={handleChange} value={form.email} />
      <input name="password" type="password" placeholder="Password" onChange={handleChange} value={form.password} />
      <input name="password2" type="password" placeholder="Confirm Password" onChange={handleChange} value={form.password2} />
      <button type="submit">Register</button>
    </form>
  );
}
