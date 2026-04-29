import { useEffect, useState } from "react";
import UserDashboard from "../components/UserDashboard";
import UserLoginForm from "../components/UserLoginForm";

const STORAGE_KEY = "user_access_token";

export default function User() {
  const [token, setToken] = useState(() => localStorage.getItem(STORAGE_KEY));

  useEffect(() => {
    if (token) {
      localStorage.setItem(STORAGE_KEY, token);
      return;
    }

    localStorage.removeItem(STORAGE_KEY);
  }, [token]);

  return (
    <section className="register-panel">
      {token ? (
        <UserDashboard token={token} onLogout={() => setToken("")} />
      ) : (
        <UserLoginForm onLogin={setToken} />
      )}
    </section>
  );
}
