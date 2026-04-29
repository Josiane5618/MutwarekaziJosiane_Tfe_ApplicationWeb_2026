import { useEffect, useState } from "react";
import AdminLoginForm from "../components/AdminLoginForm";
import AdminReviewPanel from "../components/AdminReviewPanel";

const STORAGE_KEY = "admin_access_token";

export default function Admin() {
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
        <AdminReviewPanel token={token} onLogout={() => setToken("")} />
      ) : (
        <AdminLoginForm onLogin={setToken} />
      )}
    </section>
  );
}
