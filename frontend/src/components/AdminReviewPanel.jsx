import { useEffect, useState } from "react";
import {
  createAdminSalle,
  deleteAdminSalle,
  getAdminAccessLogs,
  getAdminReservations,
  getAdminSalles,
  getAdminUserFaceImage,
  getAdminUsers,
  getPendingUsers,
  getRegistrationRequests,
  updateAdminSalle,
  updateAdminUser,
  validateUser
} from "../api/api";

const initialSalleForm = {
  nom: "",
  description: "",
  localisation: "",
  equipements: "",
  capacite: "",
  active: true
};

function formatDateTime(value) {
  if (!value) {
    return "Date indisponible";
  }

  return new Date(value).toLocaleString("fr-FR", {
    dateStyle: "medium",
    timeStyle: "short"
  });
}

function formatRequestDate(request) {
  if (!request?.date_soumission) {
    return "Date de demande indisponible";
  }

  return `Demande envoyée le ${formatDateTime(request.date_soumission)}`;
}

function formatRequestStatus(status) {
  if (status === "ACCEPTEE") {
    return "Acceptée";
  }

  if (status === "REFUSEE") {
    return "Refusée";
  }

  return "En attente";
}

function getRequestBadgeClass(status) {
  if (status === "ACCEPTEE") {
    return "request-badge badge-success";
  }

  if (status === "REFUSEE") {
    return "request-badge badge-danger";
  }

  return "request-badge badge-warning";
}

function formatReservationWindow(reservation) {
  const [year, month, day] = reservation.date.split("-").map(Number);
  const formattedDate = new Date(year, month - 1, day).toLocaleDateString(
    "fr-FR",
    {
      weekday: "long",
      day: "2-digit",
      month: "long",
      year: "numeric"
    }
  );
  const formattedStart = reservation.heure_debut.slice(0, 5).replace(":", " h ");
  const formattedEnd = reservation.heure_fin.slice(0, 5).replace(":", " h ");

  return `${formattedDate} de ${formattedStart} à ${formattedEnd}`;
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

function formatEmailResult(payload) {
  if (payload?.email_mode === "smtp" && payload?.email_envoye) {
    return "Email envoyé vers Mailpit ou le serveur SMTP configuré.";
  }

  if (payload?.email_mode === "smtp" && !payload?.email_envoye) {
    return "Email non envoyé : vérifiez Mailpit ou la configuration SMTP.";
  }

  return "Email affiché dans le terminal backend, car SMTP n'est pas activé.";
}

export default function AdminReviewPanel({ token, onLogout }) {
  const [dashboard, setDashboard] = useState({
    pendingUsers: [],
    registrationRequests: [],
    users: [],
    salles: [],
    reservations: [],
    accessLogs: []
  });
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [updatingUserId, setUpdatingUserId] = useState(null);
  const [editingSalleId, setEditingSalleId] = useState(null);
  const [activeTab, setActiveTab] = useState("demandes");
  const [salleForm, setSalleForm] = useState(initialSalleForm);
  const [feedback, setFeedback] = useState({
    type: "",
    message: ""
  });
  const [facePreview, setFacePreview] = useState({
    userId: null,
    imageUrl: "",
    isLoading: false
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
        getRegistrationRequests(token),
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
        registrationRequestsPayload,
        usersPayload,
        sallesPayload,
        reservationsPayload,
        accessLogsPayload
      ] = payloads;

      setDashboard({
        pendingUsers: pendingUsersPayload || [],
        registrationRequests: registrationRequestsPayload || [],
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

  useEffect(() => {
    return () => {
      if (facePreview.imageUrl) {
        URL.revokeObjectURL(facePreview.imageUrl);
      }
    };
  }, [facePreview.imageUrl]);

  const resetSalleForm = () => {
    setSalleForm(initialSalleForm);
    setEditingSalleId(null);
  };

  const handleFacePreview = async userId => {
    if (facePreview.userId === userId && facePreview.imageUrl) {
      setFacePreview({
        userId: null,
        imageUrl: "",
        isLoading: false
      });
      return;
    }

    setFeedback({ type: "", message: "" });
    setFacePreview({
      userId,
      imageUrl: "",
      isLoading: true
    });

    try {
      const response = await getAdminUserFaceImage({
        token,
        userId
      });

      if (response.status === 401 || response.status === 403) {
        handleUnauthorized();
        return;
      }

      if (!response.ok) {
        const payload = await response.json().catch(() => null);
        setFeedback({
          type: "error",
          message: payload?.detail || "Photo faciale indisponible."
        });
        setFacePreview({
          userId: null,
          imageUrl: "",
          isLoading: false
        });
        return;
      }

      const imageBlob = await response.blob();
      const imageUrl = URL.createObjectURL(imageBlob);

      setFacePreview({
        userId,
        imageUrl,
        isLoading: false
      });
    } catch {
      setFeedback({
        type: "error",
        message: "Impossible de charger la photo faciale."
      });
      setFacePreview({
        userId: null,
        imageUrl: "",
        isLoading: false
      });
    }
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
          `${payload?.message || "La demande a été traitée avec succès."} ${formatEmailResult(payload)}`
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

  const handleUserRoleToggle = async userToUpdate => {
    const nextRole = userToUpdate.role === "admin" ? "utilisateur" : "admin";
    const confirmationMessage =
      nextRole === "admin"
        ? `Promouvoir ${userToUpdate.prenom} ${userToUpdate.nom} au rôle d'administrateur ?`
        : `Retirer les droits d'administrateur à ${userToUpdate.prenom} ${userToUpdate.nom} ?`;

    if (!window.confirm(confirmationMessage)) {
      return;
    }

    setFeedback({ type: "", message: "" });
    setUpdatingUserId(userToUpdate.id);

    try {
      const response = await updateAdminUser({
        token,
        userId: userToUpdate.id,
        data: {
          role: nextRole
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
          message:
            payload?.detail || "Le rôle de l'utilisateur n'a pas pu être modifié."
        });
        return;
      }

      setFeedback({
        type: "success",
        message:
          nextRole === "admin"
            ? "Droits d'administrateur attribués."
            : "Droits d'administrateur retirés."
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
      localisation: salleForm.localisation.trim() || null,
      equipements: salleForm.equipements.trim() || null,
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
      localisation: salle.localisation || "",
      equipements: salle.equipements || "",
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
    registrationRequests,
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
          <p className="info-label">Historique</p>
          <p className="info-title">{registrationRequests.length}</p>
          <p className="info-meta">Demandes d'inscription suivies</p>
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
          <nav className="dashboard-tabs" aria-label="Navigation administrateur">
            <button
              className={activeTab === "demandes" ? "dashboard-tab is-active" : "dashboard-tab"}
              type="button"
              onClick={() => setActiveTab("demandes")}
            >
              Demandes
            </button>
            <button
              className={activeTab === "salles" ? "dashboard-tab is-active" : "dashboard-tab"}
              type="button"
              onClick={() => setActiveTab("salles")}
            >
              Salles
            </button>
            <button
              className={activeTab === "utilisateurs" ? "dashboard-tab is-active" : "dashboard-tab"}
              type="button"
              onClick={() => setActiveTab("utilisateurs")}
            >
              Utilisateurs
            </button>
            <button
              className={activeTab === "reservations" ? "dashboard-tab is-active" : "dashboard-tab"}
              type="button"
              onClick={() => setActiveTab("reservations")}
            >
              Réservations
            </button>
            <button
              className={activeTab === "logs" ? "dashboard-tab is-active" : "dashboard-tab"}
              type="button"
              onClick={() => setActiveTab("logs")}
            >
              Logs d'accès
            </button>
          </nav>

          {activeTab === "demandes" ? (
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
                          <p className="request-meta">
                            {formatRequestDate(user.demande_inscription)}
                          </p>
                        </div>
                        <span className="request-badge">En attente</span>
                      </div>

                      <div className="request-meta-grid">
                        <span
                          className={
                            user.donnees_faciales_enregistrees
                              ? "request-badge badge-success"
                              : "request-badge badge-warning"
                          }
                        >
                          {user.donnees_faciales_enregistrees
                            ? "Photo faciale enregistrée"
                            : "Photo faciale absente"}
                        </span>
                      </div>

                      {facePreview.userId === user.id && facePreview.imageUrl ? (
                        <figure className="face-preview">
                          <img
                            src={facePreview.imageUrl}
                            alt={`Photo faciale de ${user.prenom} ${user.nom}`}
                          />
                          <figcaption>Photo fournie lors de l'inscription</figcaption>
                        </figure>
                      ) : null}

                      <div className="request-actions">
                        <button
                          className="secondary-button"
                          type="button"
                          disabled={
                            isSubmitting ||
                            facePreview.isLoading ||
                            !user.donnees_faciales_enregistrees
                          }
                          onClick={() => handleFacePreview(user.id)}
                        >
                          {facePreview.userId === user.id && facePreview.imageUrl
                            ? "Masquer la photo"
                            : facePreview.userId === user.id && facePreview.isLoading
                              ? "Chargement..."
                              : "Voir la photo"}
                        </button>
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
          </section>
          ) : null}

          {activeTab === "salles" ? (
          <section className="admin-layout">
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
                    placeholder="Salle adaptée aux réunions et présentations"
                  />
                </label>

                <label className="field field-full">
                  <span>Localisation</span>
                  <input
                    name="localisation"
                    type="text"
                    value={salleForm.localisation}
                    onChange={handleSalleChange}
                    placeholder="Bâtiment A - local 203"
                  />
                </label>

                <label className="field field-full">
                  <span>Équipements</span>
                  <input
                    name="equipements"
                    type="text"
                    value={salleForm.equipements}
                    onChange={handleSalleChange}
                    placeholder="Projecteur, ordinateur, audiovisuel"
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
                          <p className="request-meta">
                            {salle.localisation || "Localisation non renseignée"}
                          </p>
                          <p className="request-meta">
                            Équipements : {salle.equipements || "non renseignés"}
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
          </section>
          ) : null}

          {activeTab === "demandes" ? (
          <section className="dashboard-grid admin-secondary-grid">
            <article className="request-card">
              <div className="panel-header">
                <p className="section-label">Demandes</p>
                <h2>Historique des inscriptions</h2>
              </div>

              {registrationRequests.length === 0 ? (
                <div className="empty-state">
                  <p>Aucune demande d'inscription enregistrée.</p>
                </div>
              ) : (
                <div className="stack-list">
                  {registrationRequests.map(request => (
                    <div className="stack-item" key={request.id}>
                      <div className="request-card-header">
                        <div>
                          <p className="request-name">
                            {request.utilisateur.prenom} {request.utilisateur.nom}
                          </p>
                          <p className="request-email">
                            {request.utilisateur.email}
                          </p>
                          <p className="request-meta">
                            Envoyée le {formatDateTime(request.date_soumission)}
                          </p>
                          <p className="request-meta">
                            Traitée le{" "}
                            {request.date_traitement
                              ? formatDateTime(request.date_traitement)
                              : "non traitée"}
                          </p>
                        </div>
                        <span className={getRequestBadgeClass(request.statut)}>
                          {formatRequestStatus(request.statut)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </article>
          </section>
          ) : null}

          {activeTab === "utilisateurs" ? (
          <section className="dashboard-grid admin-secondary-grid">
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
                          {user.date_creation ? (
                            <p className="request-meta">
                              Inscrit le {formatDateTime(user.date_creation)}
                            </p>
                          ) : null}
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

                      <div className="request-meta-grid">
                        <span
                          className={
                            user.donnees_faciales_enregistrees
                              ? "request-badge badge-success"
                              : "request-badge badge-warning"
                          }
                        >
                          {user.donnees_faciales_enregistrees
                            ? "Photo faciale enregistrée"
                            : "Photo faciale absente"}
                        </span>
                      </div>

                      {facePreview.userId === user.id && facePreview.imageUrl ? (
                        <figure className="face-preview">
                          <img
                            src={facePreview.imageUrl}
                            alt={`Photo faciale de ${user.prenom} ${user.nom}`}
                          />
                          <figcaption>Photo liée au compte utilisateur</figcaption>
                        </figure>
                      ) : null}

                      <div className="request-actions">
                        <button
                          className="secondary-button"
                          type="button"
                          disabled={
                            isSubmitting ||
                            facePreview.isLoading ||
                            !user.donnees_faciales_enregistrees
                          }
                          onClick={() => handleFacePreview(user.id)}
                        >
                          {facePreview.userId === user.id && facePreview.imageUrl
                            ? "Masquer la photo"
                            : facePreview.userId === user.id && facePreview.isLoading
                              ? "Chargement..."
                              : "Voir la photo"}
                        </button>
                        <button
                          className={user.actif ? "danger-button" : "secondary-button"}
                          type="button"
                          disabled={
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
                        <button
                          className={user.role === "admin" ? "danger-button" : "secondary-button"}
                          type="button"
                          disabled={
                            updatingUserId === user.id ||
                            isSubmitting ||
                            (!user.actif && user.role !== "admin")
                          }
                          onClick={() => handleUserRoleToggle(user)}
                          title={
                            !user.actif && user.role !== "admin"
                              ? "Le compte doit être actif pour devenir administrateur"
                              : ""
                          }
                        >
                          {user.role === "admin"
                            ? "Retirer droits admin"
                            : "Promouvoir admin"}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </article>
          </section>
          ) : null}

          {activeTab === "reservations" ? (
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
          </section>
          ) : null}

          {activeTab === "logs" ? (
          <section className="dashboard-grid admin-secondary-grid">
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
          ) : null}
        </>
      )}
    </div>
  );
}
