// src/components/RegisterForm.js
import React, { useState } from "react";
import { registerUser } from "../api/auth";

function RegisterForm() {
  const [formData, setFormData] = useState({ username: "", password: "" });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = await registerUser(formData);
      console.log("User registered:", data);
    } catch (error) {
      console.error("Registration error:", error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input name="username" onChange={handleChange} />
      <input name="password" type="password" onChange={handleChange} />
      <button type="submit">Register</button>
    </form>
  );
}

export default RegisterForm;
