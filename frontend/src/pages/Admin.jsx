import { useEffect, useState } from "react";
import AdminLoginForm from "../components/AdminLoginForm";
import AdminReviewPanel from "../components/AdminReviewPanel";
import DashboardModal from "../components/DashboardModal";

const STORAGE_KEY = "admin_access_token";

export default function Admin() {
  const [token, setToken] = useState(() => localStorage.getItem(STORAGE_KEY));
  const [isModalOpen, setIsModalOpen] = useState(() => Boolean(localStorage.getItem(STORAGE_KEY)));

  useEffect(() => {
    if (token) {
      localStorage.setItem(STORAGE_KEY, token);
      return;
    }

    localStorage.removeItem(STORAGE_KEY);
  }, [token]);

  const handleLogin = nextToken => {
    setToken(nextToken);
    setIsModalOpen(true);
  };

  const handleLogout = () => {
    setToken("");
    setIsModalOpen(false);
  };

  return (
    <>
      <section className="register-panel">
        {token ? (
          <div className="session-panel">
            <div className="panel-header">
              <p className="section-label">Administration</p>
              <h2>Session administrateur active</h2>
              <p className="section-copy">
                Ouvrez le tableau de bord pour gérer les demandes, les salles,
                les utilisateurs, les réservations et les accès.
              </p>
            </div>

            <div className="credential-card">
              <p className="credential-label">Accès connecté</p>
              <p className="credential-value">Compte : admin@gestion-acces.dev</p>
            </div>

            <div className="request-actions">
              <button
                className="submit-button"
                type="button"
                onClick={() => setIsModalOpen(true)}
              >
                Ouvrir le tableau de bord
              </button>
              <button className="secondary-button" type="button" onClick={handleLogout}>
                Déconnexion
              </button>
            </div>
          </div>
        ) : (
          <AdminLoginForm onLogin={handleLogin} />
        )}
      </section>

      {token && isModalOpen ? (
        <DashboardModal
          label="Administration"
          title="Tableau de bord administrateur"
          subtitle="Gérez l'application dans un espace dédié."
          onClose={() => setIsModalOpen(false)}
        >
          <AdminReviewPanel token={token} onLogout={handleLogout} />
        </DashboardModal>
      ) : null}
    </>
  );
}
