import { useEffect, useState } from "react";
import {
  createAdminSalle,
  deleteAdminSalle,
  getAdminAccessLogs,
  getAdminReservations,
  getAdminSalles,
  getAdminUsers,
  getPendingUsers,
  updateAdminSalle,
  updateAdminUser,
  validateUser
} from "../api/api";

const initialSalleForm = {
  nom: "",
  description: "",
  capacite: "",
  active: true
};

function formatDateTime(value) {
  if (!value) {
    return "Date indisponible";
  }

  return new Date(value).toLocaleString("fr-FR");
}

function formatReservationWindow(reservation) {
  return `${reservation.date} de ${reservation.heure_debut} à ${reservation.heure_fin}`;
}

function formatAccountStatus(status, active) {
  if (status === "ACTIF" || active) {
    return "Actif";
  }

  if (status === "REFUSE") {
    return "Refusé";
  }

  return "En attente";
}

function formatSalleStatus(status, active) {
  if (status === "ACTIVE" || active) {
    return "Active";
  }

  return "Inactive";
}

function formatReservationStatus(status) {
  return status === "ANNULEE" ? "Annulée" : "Confirmée";
}

function formatAccessResult(result) {
  return result === "ACCES_AUTORISE" ? "Accès autorisé" : "Accès refusé";
}

export default function AdminReviewPanel({ token, onLogout }) {
  const [dashboard, setDashboard] = useState({
    pendingUsers: [],
    users: [],
    salles: [],
    reservations: [],
    accessLogs: []
  });
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [updatingUserId, setUpdatingUserId] = useState(null);
  const [editingSalleId, setEditingSalleId] = useState(null);
  const [salleForm, setSalleForm] = useState(initialSalleForm);
  const [feedback, setFeedback] = useState({
    type: "",
    message: ""
  });

  const handleUnauthorized = () => {
    onLogout();
  };

  const loadDashboard = async ({ silent = false } = {}) => {
    if (!silent) {
      setIsLoading(true);
    }

    try {
      const responses = await Promise.all([
        getPendingUsers(token),
        getAdminUsers(token),
        getAdminSalles(token),
        getAdminReservations(token),
        getAdminAccessLogs(token)
      ]);

      const unauthorized = responses.some(
        response => response.status === 401 || response.status === 403
      );

      if (unauthorized) {
        handleUnauthorized();
        return;
      }

      const payloads = await Promise.all(
        responses.map(response => response.json().catch(() => null))
      );

      const failedPayload = responses.find(response => !response.ok);
      if (failedPayload) {
        setFeedback({
          type: "error",
          message: "Impossible de charger le tableau de bord administrateur."
        });
        return;
      }

      const [
        pendingUsersPayload,
        usersPayload,
        sallesPayload,
        reservationsPayload,
        accessLogsPayload
      ] = payloads;

      setDashboard({
        pendingUsers: pendingUsersPayload || [],
        users: usersPayload || [],
        salles: sallesPayload || [],
        reservations: reservationsPayload || [],
        accessLogs: accessLogsPayload || []
      });

      if (!silent) {
        setFeedback({
          type: "success",
          message: "Tableau de bord chargé avec succès."
        });
      }
    } catch {
      setFeedback({
        type: "error",
        message: "Impossible de joindre le backend."
      });
    } finally {
      if (!silent) {
        setIsLoading(false);
      }
    }
  };

  useEffect(() => {
    loadDashboard();
  }, [token]);

  const resetSalleForm = () => {
    setSalleForm(initialSalleForm);
    setEditingSalleId(null);
  };

  const handleDecision = async (userId, accept) => {
    setFeedback({ type: "", message: "" });
    setIsSubmitting(true);

    try {
      const response = await validateUser({
        token,
        userId,
        accept
      });
      const payload = await response.json().catch(() => null);

      if (response.status === 401 || response.status === 403) {
        handleUnauthorized();
        return;
      }

      if (!response.ok) {
        setFeedback({
          type: "error",
          message:
            payload?.detail || "La décision administrateur a échoué."
        });
        return;
      }

      setFeedback({
        type: "success",
        message:
          payload?.message ||
          "La demande a été traitée avec succès."
      });
      await loadDashboard({ silent: true });
    } catch {
      setFeedback({
        type: "error",
        message: "Impossible de joindre le backend."
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSalleChange = event => {
    const { name, value, type, checked } = event.target;
    setSalleForm(currentForm => ({
      ...currentForm,
      [name]: type === "checkbox" ? checked : value
    }));
  };

  const handleUserStatusToggle = async userToUpdate => {
    setFeedback({ type: "", message: "" });
    setUpdatingUserId(userToUpdate.id);

    try {
      const response = await updateAdminUser({
        token,
        userId: userToUpdate.id,
        data: {
          actif: !userToUpdate.actif
        }
      });
      const payload = await response.json().catch(() => null);

      if (response.status === 401 || response.status === 403) {
        handleUnauthorized();
        return;
      }

      if (!response.ok) {
        setFeedback({
          type: "error",
          message: payload?.detail || "Le compte n'a pas pu être modifié."
        });
        return;
      }

      setFeedback({
        type: "success",
        message: payload.actif
          ? "Compte utilisateur activé."
          : "Compte utilisateur désactivé."
      });
      await loadDashboard({ silent: true });
    } catch {
      setFeedback({
        type: "error",
        message: "Impossible de joindre le backend."
      });
    } finally {
      setUpdatingUserId(null);
    }
  };

  const handleSalleSubmit = async event => {
    event.preventDefault();
    setFeedback({ type: "", message: "" });
    setIsSubmitting(true);

    const payload = {
      nom: salleForm.nom.trim(),
      description: salleForm.description.trim() || null,
      capacite: salleForm.capacite ? Number(salleForm.capacite) : null,
      active: salleForm.active
    };

    try {
      const response = editingSalleId
        ? await updateAdminSalle({
            token,
            salleId: editingSalleId,
            data: payload
          })
        : await createAdminSalle({
            token,
            data: payload
          });
      const responsePayload = await response.json().catch(() => null);

      if (response.status === 401 || response.status === 403) {
        handleUnauthorized();
        return;
      }

      if (!response.ok) {
        setFeedback({
          type: "error",
          message:
            responsePayload?.detail ||
            "La salle n'a pas pu être enregistrée."
        });
        return;
      }

      setFeedback({
        type: "success",
        message: editingSalleId
          ? "Salle mise à jour avec succès."
          : "Salle créée avec succès."
      });
      resetSalleForm();
      await loadDashboard({ silent: true });
    } catch {
      setFeedback({
        type: "error",
        message: "Impossible de joindre le backend."
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSalleEdit = salle => {
    setEditingSalleId(salle.id);
    setSalleForm({
      nom: salle.nom || "",
      description: salle.description || "",
      capacite: salle.capacite ? String(salle.capacite) : "",
      active: Boolean(salle.active)
    });
    setFeedback({
      type: "success",
      message: `Modification de la salle ${salle.nom}.`
    });
  };

  const handleSalleDelete = async salleId => {
    setFeedback({ type: "", message: "" });
    setIsSubmitting(true);

    try {
      const response = await deleteAdminSalle({
        token,
        salleId
      });
      const payload = await response.json().catch(() => null);

      if (response.status === 401 || response.status === 403) {
        handleUnauthorized();
        return;
      }

      if (!response.ok) {
        setFeedback({
          type: "error",
          message:
            payload?.detail || "La salle n'a pas pu être désactivée."
        });
        return;
      }

      if (editingSalleId === salleId) {
        resetSalleForm();
      }

      setFeedback({
        type: "success",
        message:
          payload?.message || "Salle désactivée avec succès."
      });
      await loadDashboard({ silent: true });
    } catch {
      setFeedback({
        type: "error",
        message: "Impossible de joindre le backend."
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const {
    pendingUsers,
    users,
    salles,
    reservations,
    accessLogs
  } = dashboard;

  return (
    <div className="admin-panel">
      <div className="panel-header panel-header-row">
        <div>
          <p className="section-label">Administration</p>
          <h2>Tableau de bord administrateur</h2>
          <p className="section-copy">
            Gère les demandes, les salles, les utilisateurs, les réservations et
            les logs d'accès.
          </p>
        </div>

        <div className="toolbar toolbar-inline">
          <button
            className="secondary-button"
            type="button"
            onClick={() => loadDashboard()}
            disabled={isLoading || isSubmitting}
          >
            {isLoading ? "Actualisation..." : "Rafraîchir"}
          </button>
          <button className="secondary-button" type="button" onClick={onLogout}>
            Déconnexion
          </button>
        </div>
      </div>

      <section className="dashboard-grid">
        <article className="info-card">
          <p className="info-label">Demandes</p>
          <p className="info-title">{pendingUsers.length}</p>
          <p className="info-meta">Utilisateurs en attente de validation</p>
        </article>

        <article className="info-card">
          <p className="info-label">Utilisateurs</p>
          <p className="info-title">{users.length}</p>
          <p className="info-meta">Comptes disponibles dans le système</p>
        </article>

        <article className="info-card">
          <p className="info-label">Salles</p>
          <p className="info-title">{salles.length}</p>
          <p className="info-meta">Salles administrées par l'application</p>
        </article>

        <article className="info-card">
          <p className="info-label">Réservations</p>
          <p className="info-title">{reservations.length}</p>
          <p className="info-meta">Réservations enregistrées</p>
        </article>

        <article className="info-card">
          <p className="info-label">Logs d'accès</p>
          <p className="info-title">{accessLogs.length}</p>
          <p className="info-meta">Tentatives d'accès historisées</p>
        </article>
      </section>

      {feedback.message ? (
        <div className={`feedback feedback-${feedback.type}`} role="status">
          {feedback.message}
        </div>
      ) : null}

      {isLoading ? (
        <div className="empty-state">
          <p>Chargement du tableau de bord administrateur...</p>
        </div>
      ) : (
        <>
          <section className="admin-layout">
            <article className="request-card">
              <div className="panel-header">
                <p className="section-label">Demandes</p>
                <h2>Inscriptions en attente</h2>
              </div>

              {pendingUsers.length === 0 ? (
                <div className="empty-state">
                  <p>Aucune demande en attente pour le moment.</p>
                </div>
              ) : (
                <div className="request-list">
                  {pendingUsers.map(user => (
                    <article className="stack-item" key={user.id}>
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
                          disabled={isSubmitting}
                          onClick={() => handleDecision(user.id, true)}
                        >
                          Accepter
                        </button>
                        <button
                          className="danger-button"
                          type="button"
                          disabled={isSubmitting}
                          onClick={() => handleDecision(user.id, false)}
                        >
                          Refuser
                        </button>
                      </div>
                    </article>
                  ))}
                </div>
              )}
            </article>

            <article className="request-card">
              <div className="panel-header">
                <p className="section-label">Salles</p>
                <h2>{editingSalleId ? "Modifier une salle" : "Ajouter une salle"}</h2>
              </div>

              <form className="register-form" onSubmit={handleSalleSubmit}>
                <label className="field field-full">
                  <span>Nom</span>
                  <input
                    name="nom"
                    type="text"
                    value={salleForm.nom}
                    onChange={handleSalleChange}
                    placeholder="Salle polyvalente"
                    required
                  />
                </label>

                <label className="field field-full">
                  <span>Description</span>
                  <input
                    name="description"
                    type="text"
                    value={salleForm.description}
                    onChange={handleSalleChange}
                    placeholder="Etage, usage ou emplacement"
                  />
                </label>

                <div className="form-grid">
                  <label className="field">
                    <span>Capacité</span>
                    <input
                      name="capacite"
                      type="number"
                      min="1"
                      value={salleForm.capacite}
                      onChange={handleSalleChange}
                      placeholder="20"
                    />
                  </label>

                  <label className="field field-checkbox">
                    <span>Salle active</span>
                    <input
                      name="active"
                      type="checkbox"
                      checked={salleForm.active}
                      onChange={handleSalleChange}
                    />
                  </label>
                </div>

                <div className="request-actions">
                  <button
                    className="submit-button"
                    type="submit"
                    disabled={isSubmitting}
                  >
                    {editingSalleId ? "Mettre à jour" : "Ajouter la salle"}
                  </button>
                  {editingSalleId ? (
                    <button
                      className="secondary-button"
                      type="button"
                      onClick={resetSalleForm}
                    >
                      Annuler la modification
                    </button>
                  ) : null}
                </div>
              </form>
            </article>
          </section>

          <section className="dashboard-grid admin-secondary-grid">
            <article className="request-card">
              <div className="panel-header">
                <p className="section-label">Salles</p>
                <h2>Catalogue des salles</h2>
              </div>

              {salles.length === 0 ? (
                <div className="empty-state">
                    <p>Aucune salle enregistrée.</p>
                </div>
              ) : (
                <div className="stack-list">
                  {salles.map(salle => (
                    <div className="stack-item" key={salle.id}>
                      <div className="request-card-header">
                        <div>
                          <p className="request-name">{salle.nom}</p>
                          <p className="request-email">
                            {salle.description || "Aucune description"} · Capacité{" "}
                            {salle.capacite ?? "n/a"}
                          </p>
                        </div>
                        <span
                          className={
                            salle.statut_salle === "ACTIVE" || salle.active
                              ? "request-badge badge-success"
                              : "request-badge badge-muted"
                          }
                        >
                          {formatSalleStatus(salle.statut_salle, salle.active)}
                        </span>
                      </div>

                      <div className="request-actions">
                        <button
                          className="secondary-button"
                          type="button"
                          onClick={() => handleSalleEdit(salle)}
                        >
                          Modifier
                        </button>
                        <button
                          className="danger-button"
                          type="button"
                          disabled={isSubmitting || !salle.active}
                          onClick={() => handleSalleDelete(salle.id)}
                        >
                          Désactiver
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </article>

            <article className="request-card">
              <div className="panel-header">
                <p className="section-label">Utilisateurs</p>
                <h2>Comptes enregistrés</h2>
              </div>

              {users.length === 0 ? (
                <div className="empty-state">
                  <p>Aucun utilisateur trouvé.</p>
                </div>
              ) : (
                <div className="stack-list">
                  {users.map(user => (
                    <div className="stack-item" key={user.id}>
                      <div className="request-card-header">
                        <div>
                          <p className="request-name">
                            {user.prenom} {user.nom}
                          </p>
                          <p className="request-email">
                            {user.email} · Rôle {user.role}
                          </p>
                        </div>
                        <span
                          className={
                            user.statut_compte === "ACTIF" || user.actif
                              ? "request-badge badge-success"
                              : "request-badge badge-warning"
                          }
                        >
                          {formatAccountStatus(user.statut_compte, user.actif)}
                        </span>
                      </div>

                      <div className="request-actions">
                        <button
                          className={user.actif ? "danger-button" : "secondary-button"}
                          type="button"
                          disabled={
                            user.role === "admin" ||
                            updatingUserId === user.id ||
                            isSubmitting
                          }
                          onClick={() => handleUserStatusToggle(user)}
                        >
                          {updatingUserId === user.id
                            ? "Mise à jour..."
                            : user.actif
                              ? "Désactiver"
                              : "Activer"}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </article>
          </section>

          <section className="dashboard-grid admin-secondary-grid">
            <article className="request-card">
              <div className="panel-header">
                <p className="section-label">Réservations</p>
                <h2>Historique global</h2>
              </div>

              {reservations.length === 0 ? (
                <div className="empty-state">
                  <p>Aucune réservation enregistrée.</p>
                </div>
              ) : (
                <div className="stack-list">
                  {reservations.map(reservation => (
                    <div className="stack-item" key={reservation.id}>
                      <div className="request-card-header">
                        <p className="request-name">
                          {reservation.salle.nom} réservée par{" "}
                          {reservation.utilisateur.prenom} {reservation.utilisateur.nom}
                        </p>
                        <span
                          className={
                            reservation.statut === "ANNULEE"
                              ? "request-badge badge-muted"
                              : "request-badge badge-success"
                          }
                        >
                          {formatReservationStatus(reservation.statut)}
                        </span>
                      </div>
                      <p className="request-email">
                        {formatReservationWindow(reservation)}
                      </p>
                      <p className="request-meta">
                        {reservation.utilisateur.email}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </article>

            <article className="request-card">
              <div className="panel-header">
                <p className="section-label">Logs d'accès</p>
                <h2>Trace des contrôles</h2>
              </div>

              {accessLogs.length === 0 ? (
                <div className="empty-state">
                  <p>Aucun log d'accès disponible.</p>
                </div>
              ) : (
                <div className="stack-list">
                  {accessLogs.map(log => (
                    <div className="stack-item" key={log.id}>
                      <div className="request-card-header">
                        <div>
                          <p className="request-name">
                            {log.utilisateur.prenom} {log.utilisateur.nom}
                          </p>
                          <p className="request-email">{log.utilisateur.email}</p>
                        </div>
                        <span
                          className={
                            log.resultat === "ACCES_AUTORISE"
                              ? "request-badge badge-success"
                              : "request-badge badge-danger"
                          }
                        >
                          {formatAccessResult(log.resultat)}
                        </span>
                      </div>
                      <p className="request-meta">
                        {formatDateTime(log.date_acces)} · Distance faciale{" "}
                        {typeof log.distance === "number"
                          ? log.distance.toFixed(3)
                          : "n/a"}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </article>
          </section>
        </>
      )}
    </div>
  );
}
