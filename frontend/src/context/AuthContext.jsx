import { createContext, useState } from "react";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(JSON.parse(localStorage.getItem("user")) || null);
  const [access, setAccess] = useState(localStorage.getItem("access") || null);

  const login = (data) => {
    setUser(data.user);
    setAccess(data.access);
    localStorage.setItem("user", JSON.stringify(data.user));
    localStorage.setItem("access", data.access);
  };

  const logout = () => {
    setUser(null);
    setAccess(null);
    localStorage.clear();
  };

  return (
    <AuthContext.Provider value={{ user, access, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
