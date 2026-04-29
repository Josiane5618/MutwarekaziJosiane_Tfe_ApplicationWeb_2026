import { useEffect, useState } from "react";
import { getPendingUsers, validateUser } from "../api/api";

export default function AdminReviewPanel({ token, onLogout }) {
  const [pendingUsers, setPendingUsers] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [feedback, setFeedback] = useState({
    type: "",
    message: ""
  });

  const loadPendingUsers = async () => {
    setIsLoading(true);

    try {
      const response = await getPendingUsers(token);
      const payload = await response.json().catch(() => null);

      if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
          onLogout();
        }

        setFeedback({
          type: "error",
          message:
            payload?.detail ||
            "Impossible de recuperer les demandes en attente."
        });
        setPendingUsers([]);
        return;
      }

      setPendingUsers(payload || []);
      setFeedback({
        type: "success",
        message: "Demandes chargees avec succes."
      });
    } catch {
      setFeedback({
        type: "error",
        message: "Impossible de joindre le backend."
      });
      setPendingUsers([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadPendingUsers();
  }, [token]);

  const handleDecision = async (userId, accept) => {
    setFeedback({ type: "", message: "" });

    try {
      const response = await validateUser({
        token,
        userId,
        accept
      });
      const payload = await response.json().catch(() => null);

      if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
          onLogout();
        }

        setFeedback({
          type: "error",
          message:
            payload?.detail || "La decision administrateur a echoue."
        });
        return;
      }

      setFeedback({
        type: "success",
        message:
          payload?.message ||
          "La demande a ete traitee avec succes."
      });
      await loadPendingUsers();
    } catch {
      setFeedback({
        type: "error",
        message: "Impossible de joindre le backend."
      });
    }
  };

  return (
    <div className="admin-panel">
      <div className="panel-header panel-header-row">
        <div>
          <p className="section-label">Administration</p>
          <h2>Demandes en attente</h2>
          <p className="section-copy">
            Acceptez ou refusez les inscriptions avant la connexion utilisateur.
          </p>
        </div>

        <button className="secondary-button" type="button" onClick={onLogout}>
          Deconnexion
        </button>
      </div>

      <div className="toolbar">
        <button
          className="secondary-button"
          type="button"
          onClick={loadPendingUsers}
          disabled={isLoading}
        >
          {isLoading ? "Actualisation..." : "Rafraichir"}
        </button>
      </div>

      {feedback.message ? (
        <div className={`feedback feedback-${feedback.type}`} role="status">
          {feedback.message}
        </div>
      ) : null}

      {isLoading ? (
        <div className="empty-state">
          <p>Chargement des demandes...</p>
        </div>
      ) : pendingUsers.length === 0 ? (
        <div className="empty-state">
          <p>Aucune demande en attente pour le moment.</p>
        </div>
      ) : (
        <div className="request-list">
          {pendingUsers.map(user => (
            <article className="request-card" key={user.id}>
              <div className="request-card-header">
                <div>
                  <p className="request-name">
                    {user.prenom} {user.nom}
                  </p>
                  <p className="request-email">{user.email}</p>
                </div>
                <span className="request-badge">En attente</span>
              </div>

              <div className="request-actions">
                <button
                  className="submit-button"
                  type="button"
                  onClick={() => handleDecision(user.id, true)}
                >
                  Accepter
                </button>
                <button
                  className="danger-button"
                  type="button"
                  onClick={() => handleDecision(user.id, false)}
                >
                  Refuser
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
