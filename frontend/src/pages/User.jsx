import { useEffect, useState } from "react";
import DashboardModal from "../components/DashboardModal";
import UserDashboard from "../components/UserDashboard";
import UserLoginForm from "../components/UserLoginForm";

const STORAGE_KEY = "user_access_token";

export default function User() {
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
              <p className="section-label">Utilisateur</p>
              <h2>Session utilisateur active</h2>
              <p className="section-copy">
                Ouvrez votre espace pour consulter les réservations, les
                notifications et réserver une salle.
              </p>
            </div>

            <div className="credential-card">
              <p className="credential-label">Accès connecté</p>
              <p className="credential-value">Votre compte est prêt.</p>
            </div>

            <div className="request-actions">
              <button
                className="submit-button"
                type="button"
                onClick={() => setIsModalOpen(true)}
              >
                Ouvrir l'espace utilisateur
              </button>
              <button className="secondary-button" type="button" onClick={handleLogout}>
                Déconnexion
              </button>
            </div>
          </div>
        ) : (
          <UserLoginForm onLogin={handleLogin} />
        )}
      </section>

      {token && isModalOpen ? (
        <DashboardModal
          label="Utilisateur"
          title="Espace utilisateur"
          subtitle="Consultez vos informations dans une vue dédiée."
          onClose={() => setIsModalOpen(false)}
        >
          <UserDashboard token={token} onLogout={handleLogout} />
        </DashboardModal>
      ) : null}
    </>
  );
}
