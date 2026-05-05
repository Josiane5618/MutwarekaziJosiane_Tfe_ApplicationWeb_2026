import { useEffect, useState } from "react";
import {
  cancelReservation,
  createReservation,
  getCurrentUser,
  getMyReservations,
  getNotifications,
  getSalles,
  updateCurrentUser,
  updateReservation,
  verifyBuildingAccess
} from "../api/api";
import CameraCapture from "./CameraCapture";

function formatAccountStatus(status, active) {
  if (status === "ACTIF" || active) {
    return "Actif";
  }

  if (status === "REFUSE") {
    return "Refusé";
  }

  return "En attente";
}

function formatReservationStatus(status) {
  return status === "ANNULEE" ? "Annulée" : "Confirmée";
}

function getTodayInputValue() {
  const today = new Date();
  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, "0");
  const day = String(today.getDate()).padStart(2, "0");

  return `${year}-${month}-${day}`;
}

export default function UserDashboard({ token, onLogout }) {
  const [user, setUser] = useState(null);
  const [salles, setSalles] = useState([]);
  const [reservations, setReservations] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isProfileSubmitting, setIsProfileSubmitting] = useState(false);
  const [cancelingReservationId, setCancelingReservationId] = useState(null);
  const [editingReservationId, setEditingReservationId] = useState(null);
  const [updatingReservationId, setUpdatingReservationId] = useState(null);
  const [isAccessSubmitting, setIsAccessSubmitting] = useState(false);
  const [accessFaceImage, setAccessFaceImage] = useState(null);
  const [accessResult, setAccessResult] = useState(null);
  const [accessNotice, setAccessNotice] = useState({
    type: "",
    message: ""
  });
  const [feedback, setFeedback] = useState({
    type: "",
    message: ""
  });
  const [reservationForm, setReservationForm] = useState({
    salleId: "",
    dateReservation: "",
    heureDebut: "",
    heureFin: ""
  });
  const [profileForm, setProfileForm] = useState({
    prenom: "",
    nom: "",
    email: "",
    password: ""
  });
  const [editReservationForm, setEditReservationForm] = useState({
    salleId: "",
    dateReservation: "",
    heureDebut: "",
    heureFin: ""
  });
  const sallesById = Object.fromEntries(
    salles.map(salle => [String(salle.id), salle])
  );
  const todayInputValue = getTodayInputValue();

  const handleUnauthorized = () => {
    onLogout();
  };

  const loadDashboard = async ({ silent = false } = {}) => {
    if (!silent) {
      setIsLoading(true);
      setFeedback({ type: "", message: "" });
    }

    try {
      const responses = await Promise.all([
        getCurrentUser(token),
        getSalles(token),
        getMyReservations(token),
        getNotifications(token)
      ]);

      const unauthorized = responses.some(
        response => response.status === 401 || response.status === 403
      );

      if (unauthorized) {
        handleUnauthorized();
        return;
      }

      const [userPayload, sallesPayload, reservationsPayload, notificationsPayload] =
        await Promise.all(
          responses.map(response => response.json().catch(() => null))
        );

      const failedResponse = responses.find(response => !response.ok);
      if (failedResponse) {
        setFeedback({
          type: "error",
          message: "Impossible de charger l'espace utilisateur."
        });
        return;
      }

      setUser(userPayload);
      setProfileForm({
        prenom: userPayload?.prenom || "",
        nom: userPayload?.nom || "",
        email: userPayload?.email || "",
        password: ""
      });
      setSalles(sallesPayload || []);
      setReservations(reservationsPayload || []);
      setNotifications(notificationsPayload || []);

      if (!reservationForm.salleId && sallesPayload?.length) {
        setReservationForm(currentForm => ({
          ...currentForm,
          salleId: String(sallesPayload[0].id)
        }));
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

  const handleReservationChange = event => {
    setReservationForm({
      ...reservationForm,
      [event.target.name]: event.target.value
    });
  };

  const handleProfileChange = event => {
    setProfileForm({
      ...profileForm,
      [event.target.name]: event.target.value
    });
  };

  const handleEditReservationChange = event => {
    setEditReservationForm({
      ...editReservationForm,
      [event.target.name]: event.target.value
    });
  };

  const startReservationEdit = reservation => {
    if (reservation.statut === "ANNULEE") {
      setFeedback({
        type: "error",
        message: "Une réservation annulée ne peut pas être modifiée."
      });
      return;
    }

    setEditingReservationId(reservation.id);
    setEditReservationForm({
      salleId: String(reservation.salle_id),
      dateReservation: reservation.date,
      heureDebut: reservation.heure_debut,
      heureFin: reservation.heure_fin
    });
    setFeedback({ type: "", message: "" });
  };

  const stopReservationEdit = () => {
    setEditingReservationId(null);
    setEditReservationForm({
      salleId: "",
      dateReservation: "",
      heureDebut: "",
      heureFin: ""
    });
  };

  const handleAccessCapture = image => {
    setAccessFaceImage(image);
    setAccessResult(null);
    setAccessNotice({ type: "", message: "" });
  };

  const handleCancelReservation = async reservationId => {
    setFeedback({ type: "", message: "" });
    setCancelingReservationId(reservationId);

    try {
      const response = await cancelReservation({
        token,
        reservationId
      });
      const payload = await response.json().catch(() => null);

      if (response.status === 401 || response.status === 403) {
        handleUnauthorized();
        return;
      }

      if (!response.ok) {
        setFeedback({
          type: "error",
          message: payload?.detail || "La réservation n'a pas pu être annulée."
        });
        return;
      }

      setFeedback({
        type: "success",
        message: payload?.message || "Réservation annulée avec succès."
      });

      await loadDashboard({ silent: true });
    } catch {
      setFeedback({
        type: "error",
        message: "Impossible de joindre le backend."
      });
    } finally {
      setCancelingReservationId(null);
    }
  };

  const handleProfileSubmit = async event => {
    event.preventDefault();
    setFeedback({ type: "", message: "" });
    setIsProfileSubmitting(true);

    const payload = {
      prenom: profileForm.prenom.trim(),
      nom: profileForm.nom.trim(),
      email: profileForm.email.trim()
    };

    if (profileForm.password.trim()) {
      payload.password = profileForm.password;
    }

    try {
      const response = await updateCurrentUser({
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
          message: responsePayload?.detail || "Le profil n'a pas pu être modifié."
        });
        return;
      }

      setUser(responsePayload);
      setProfileForm({
        prenom: responsePayload.prenom || "",
        nom: responsePayload.nom || "",
        email: responsePayload.email || "",
        password: ""
      });
      setFeedback({
        type: "success",
        message: "Profil mis à jour avec succès."
      });
    } catch {
      setFeedback({
        type: "error",
        message: "Impossible de joindre le backend."
      });
    } finally {
      setIsProfileSubmitting(false);
    }
  };

  const handleUpdateReservation = async event => {
    event.preventDefault();
    setFeedback({ type: "", message: "" });
    setUpdatingReservationId(editingReservationId);

    try {
      const response = await updateReservation({
        token,
        reservationId: editingReservationId,
        salleId: editReservationForm.salleId,
        dateReservation: editReservationForm.dateReservation,
        heureDebut: editReservationForm.heureDebut,
        heureFin: editReservationForm.heureFin
      });
      const payload = await response.json().catch(() => null);

      if (response.status === 401 || response.status === 403) {
        handleUnauthorized();
        return;
      }

      if (!response.ok) {
        setFeedback({
          type: "error",
          message: payload?.detail || "La réservation n'a pas pu être modifiée."
        });
        return;
      }

      setFeedback({
        type: "success",
        message: payload?.message || "Réservation modifiée avec succès."
      });
      stopReservationEdit();
      await loadDashboard({ silent: true });
    } catch {
      setFeedback({
        type: "error",
        message: "Impossible de joindre le backend."
      });
    } finally {
      setUpdatingReservationId(null);
    }
  };

  const handleReservationSubmit = async event => {
    event.preventDefault();
    setFeedback({ type: "", message: "" });
    setIsSubmitting(true);

    try {
      const response = await createReservation({
        token,
        salleId: reservationForm.salleId,
        dateReservation: reservationForm.dateReservation,
        heureDebut: reservationForm.heureDebut,
        heureFin: reservationForm.heureFin
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
            payload?.detail || "La réservation n'a pas pu être créée."
        });
        return;
      }

      setFeedback({
        type: "success",
        message: payload?.message || "Réservation créée avec succès."
      });

      setReservationForm(currentForm => ({
        ...currentForm,
        dateReservation: "",
        heureDebut: "",
        heureFin: ""
      }));

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

  const handleAccessSubmit = async event => {
    event.preventDefault();
    setFeedback({ type: "", message: "" });
    setAccessResult(null);
    setAccessNotice({ type: "", message: "" });

    if (!accessFaceImage) {
      setAccessNotice({
        type: "error",
        message: "Capturez votre visage avant de demander l'accès."
      });
      setFeedback({
        type: "error",
        message: "Capturez votre visage avant de demander l'accès."
      });
      return;
    }

    setIsAccessSubmitting(true);

    try {
      const response = await verifyBuildingAccess({
        token,
        file: accessFaceImage
      });
      const payload = await response.json().catch(() => null);

      if (response.status === 401 || response.status === 403) {
        handleUnauthorized();
        return;
      }

      if (!response.ok) {
        setAccessNotice({
          type: "error",
          message: payload?.detail || "La vérification faciale a échoué."
        });
        setFeedback({
          type: "error",
          message: payload?.detail || "La vérification faciale a échoué."
        });
        return;
      }

      setAccessResult(payload);
      setAccessNotice({
        type: payload?.resultat === "ACCES_AUTORISE" ? "success" : "error",
        message:
          payload?.resultat === "ACCES_AUTORISE"
            ? "Identité confirmée."
            : "Le visage ne correspond pas au profil enregistré."
      });
      setFeedback({
        type: payload?.resultat === "ACCES_AUTORISE" ? "success" : "error",
        message:
          payload?.resultat === "ACCES_AUTORISE"
            ? "Accès bâtiment autorisé."
            : "Accès bâtiment refusé."
      });

      await loadDashboard({ silent: true });
    } catch {
      setAccessNotice({
        type: "error",
        message: "Impossible de joindre le backend."
      });
      setFeedback({
        type: "error",
        message: "Impossible de joindre le backend."
      });
    } finally {
      setIsAccessSubmitting(false);
    }
  };

  return (
    <div className="user-dashboard">
      <div className="panel-header panel-header-row">
        <div>
          <p className="section-label">Utilisateur</p>
          <h2>Espace connecté</h2>
          <p className="section-copy">
            Consultez vos réservations, vos notifications et vérifiez l'accès bâtiment.
          </p>
        </div>

        <div className="toolbar toolbar-inline">
          <button className="secondary-button" type="button" onClick={() => loadDashboard()}>
            Rafraîchir
          </button>
          <button className="secondary-button" type="button" onClick={onLogout}>
            Déconnexion
          </button>
        </div>
      </div>

      {feedback.message ? (
        <div className={`feedback feedback-${feedback.type}`} role="status">
          {feedback.message}
        </div>
      ) : null}

      {isLoading ? (
        <div className="empty-state">
          <p>Chargement de votre espace...</p>
        </div>
      ) : (
        <>
          <section className="dashboard-grid">
            <article className="info-card profile-summary-card">
              <p className="info-label">Profil</p>
              <p className="info-title">
                {user?.prenom} {user?.nom}
              </p>
              <p className="info-meta">{user?.email}</p>
              <p className="info-meta">Rôle : {user?.role}</p>
              <p className="info-meta">
                Statut : {formatAccountStatus(user?.statut_compte, user?.actif)}
              </p>
            </article>

            <article className="info-card">
              <p className="info-label">Notifications</p>
              <p className="info-title">{notifications.length}</p>
              <p className="info-meta">Messages disponibles</p>
            </article>

            <article className="info-card">
              <p className="info-label">Réservations</p>
              <p className="info-title">{reservations.length}</p>
              <p className="info-meta">Réservations enregistrées</p>
            </article>
          </section>

          <article className="request-card">
            <div className="panel-header">
              <p className="section-label">Profil</p>
              <h2>Mettre à jour le profil</h2>
            </div>

            <form className="profile-form" onSubmit={handleProfileSubmit}>
              <label className="field">
                <span>Prénom</span>
                <input
                  name="prenom"
                  value={profileForm.prenom}
                  onChange={handleProfileChange}
                  required
                />
              </label>

              <label className="field">
                <span>Nom</span>
                <input
                  name="nom"
                  value={profileForm.nom}
                  onChange={handleProfileChange}
                  required
                />
              </label>

              <label className="field">
                <span>Email</span>
                <input
                  name="email"
                  type="email"
                  value={profileForm.email}
                  onChange={handleProfileChange}
                  required
                />
              </label>

              <label className="field">
                <span>Nouveau mot de passe</span>
                <input
                  name="password"
                  type="password"
                  value={profileForm.password}
                  onChange={handleProfileChange}
                  placeholder="Laisser vide pour conserver l'actuel"
                />
              </label>

              <button
                className="submit-button compact-submit"
                type="submit"
                disabled={isProfileSubmitting}
              >
                {isProfileSubmitting ? "Enregistrement..." : "Enregistrer le profil"}
              </button>
            </form>
          </article>

          <article className="request-card access-card">
            <div className="panel-header">
              <p className="section-label">Accès bâtiment</p>
              <h2>Vérification faciale</h2>
              <p className="section-copy">
                Capturez votre visage pour confirmer votre identité avant l'accès.
              </p>
            </div>

            <form className="access-form" onSubmit={handleAccessSubmit}>
              <CameraCapture
                onCapture={handleAccessCapture}
                hasCapture={Boolean(accessFaceImage)}
              />

              <div className="access-result-panel">
                {accessNotice.message ? (
                  <div className={`access-notice access-notice-${accessNotice.type}`}>
                    {accessNotice.message}
                  </div>
                ) : null}

                {accessResult ? (
                  <>
                    <span
                      className={
                        accessResult.resultat === "ACCES_AUTORISE"
                          ? "request-badge badge-success"
                          : "request-badge badge-danger"
                      }
                    >
                      {accessResult.resultat === "ACCES_AUTORISE"
                        ? "Accès autorisé"
                        : "Accès refusé"}
                    </span>
                    <p className="request-meta">
                      Distance faciale :{" "}
                      {typeof accessResult.distance === "number"
                        ? accessResult.distance.toFixed(3)
                      : "n/a"}
                    </p>
                  </>
                ) : !accessNotice.message ? (
                  <p className="request-meta">
                    Le résultat apparaîtra ici après vérification.
                  </p>
                ) : null}
              </div>

              <button
                className="submit-button compact-submit"
                type="submit"
                disabled={isAccessSubmitting}
              >
                {isAccessSubmitting ? "Vérification..." : "Demander l'accès bâtiment"}
              </button>
            </form>
          </article>

          <section className="reservation-layout">
            <article className="request-card">
              <div className="panel-header">
                <p className="section-label">Réservation</p>
                <h2>Créer une réservation</h2>
              </div>

              <form className="register-form" onSubmit={handleReservationSubmit}>
                <label className="field field-full">
                  <span>Salle</span>
                  <select
                    className="field-select"
                    name="salleId"
                    value={reservationForm.salleId}
                    onChange={handleReservationChange}
                    required
                  >
                    <option value="" disabled>
                      Sélectionnez une salle
                    </option>
                    {salles.map(salle => (
                      <option key={salle.id} value={salle.id}>
                        {salle.nom} - capacité {salle.capacite ?? "n/a"}
                      </option>
                    ))}
                  </select>
                </label>

                <div className="form-grid reservation-form-grid">
                  <label className="field field-full reservation-date-field">
                    <span>Date</span>
                    <input
                      name="dateReservation"
                      type="date"
                      min={todayInputValue}
                      value={reservationForm.dateReservation}
                      onChange={handleReservationChange}
                      required
                    />
                  </label>

                  <label className="field">
                    <span>Heure de début</span>
                    <input
                      name="heureDebut"
                      type="time"
                      value={reservationForm.heureDebut}
                      onChange={handleReservationChange}
                      required
                    />
                  </label>

                  <label className="field">
                    <span>Heure de fin</span>
                    <input
                      name="heureFin"
                      type="time"
                      value={reservationForm.heureFin}
                      onChange={handleReservationChange}
                      required
                    />
                  </label>
                </div>

                <button className="submit-button compact-submit" type="submit" disabled={isSubmitting}>
                  {isSubmitting ? "Réservation..." : "Créer la réservation"}
                </button>
              </form>
            </article>

            <article className="request-card">
              <div className="panel-header">
                <p className="section-label">Historique</p>
                <h2>Mes réservations</h2>
              </div>

              {reservations.length === 0 ? (
                <div className="empty-state">
                  <p>Aucune réservation pour le moment.</p>
                </div>
              ) : (
                <div className="stack-list">
                  {reservations.map(reservation => (
                    <div className="stack-item" key={reservation.id}>
                      {editingReservationId === reservation.id ? (
                        <form className="edit-reservation-form" onSubmit={handleUpdateReservation}>
                          <label className="field">
                            <span>Salle</span>
                            <select
                              className="field-select"
                              name="salleId"
                              value={editReservationForm.salleId}
                              onChange={handleEditReservationChange}
                              required
                            >
                              {salles.map(salle => (
                                <option key={salle.id} value={salle.id}>
                                  {salle.nom}
                                </option>
                              ))}
                            </select>
                          </label>

                          <label className="field">
                            <span>Date</span>
                            <input
                              name="dateReservation"
                              type="date"
                              min={todayInputValue}
                              value={editReservationForm.dateReservation}
                              onChange={handleEditReservationChange}
                              required
                            />
                          </label>

                          <label className="field">
                            <span>Début</span>
                            <input
                              name="heureDebut"
                              type="time"
                              value={editReservationForm.heureDebut}
                              onChange={handleEditReservationChange}
                              required
                            />
                          </label>

                          <label className="field">
                            <span>Fin</span>
                            <input
                              name="heureFin"
                              type="time"
                              value={editReservationForm.heureFin}
                              onChange={handleEditReservationChange}
                              required
                            />
                          </label>

                          <div className="request-actions">
                            <button
                              className="submit-button"
                              type="submit"
                              disabled={updatingReservationId === reservation.id}
                            >
                              {updatingReservationId === reservation.id
                                ? "Modification..."
                                : "Enregistrer"}
                            </button>
                            <button
                              className="secondary-button"
                              type="button"
                              onClick={stopReservationEdit}
                            >
                              Annuler l'édition
                            </button>
                          </div>
                        </form>
                      ) : (
                        <div className="request-card-header">
                          <div>
                            <p className="request-name">
                              {sallesById[String(reservation.salle_id)]?.nom ||
                                `Salle #${reservation.salle_id}`}
                            </p>
                            <p className="request-email">
                              {reservation.date} de {reservation.heure_debut} à{" "}
                              {reservation.heure_fin}
                            </p>
                          </div>

                          <div className="request-actions">
                            <span
                              className={
                                reservation.statut === "ANNULEE"
                                  ? "request-badge badge-muted"
                                  : "request-badge badge-success"
                              }
                            >
                              {formatReservationStatus(reservation.statut)}
                            </span>
                            <button
                              className="secondary-button"
                              type="button"
                              disabled={reservation.statut === "ANNULEE"}
                              onClick={() => startReservationEdit(reservation)}
                            >
                              Modifier
                            </button>
                            <button
                              className="danger-button"
                              type="button"
                              disabled={
                                cancelingReservationId === reservation.id ||
                                reservation.statut === "ANNULEE"
                              }
                              onClick={() => handleCancelReservation(reservation.id)}
                            >
                              {reservation.statut === "ANNULEE"
                                ? "Annulée"
                                : cancelingReservationId === reservation.id
                                  ? "Annulation..."
                                  : "Annuler"}
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </article>
          </section>

          <article className="request-card user-notifications-card">
            <div className="panel-header">
              <p className="section-label">Notifications</p>
              <h2>Messages reçus</h2>
            </div>

            {notifications.length === 0 ? (
              <div className="empty-state">
                <p>Aucune notification disponible.</p>
              </div>
            ) : (
              <div className="stack-list">
                {notifications.map(notification => (
                  <div className="stack-item" key={notification.id}>
                    <p className="request-name">{notification.message}</p>
                    <p className="request-email">
                      {new Date(notification.date_creation).toLocaleString()}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </article>
        </>
      )}
    </div>
  );
}
