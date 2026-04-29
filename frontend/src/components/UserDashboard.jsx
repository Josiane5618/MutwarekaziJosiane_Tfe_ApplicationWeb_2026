import { useEffect, useState } from "react";
import {
  createReservation,
  getCurrentUser,
  getMyReservations,
  getNotifications,
  getSalles
} from "../api/api";

export default function UserDashboard({ token, onLogout }) {
  const [user, setUser] = useState(null);
  const [salles, setSalles] = useState([]);
  const [reservations, setReservations] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
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
  const sallesById = Object.fromEntries(
    salles.map(salle => [String(salle.id), salle])
  );

  const handleUnauthorized = () => {
    onLogout();
  };

  const loadDashboard = async () => {
    setIsLoading(true);
    setFeedback({ type: "", message: "" });

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
      setIsLoading(false);
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
            payload?.detail || "La reservation n'a pas pu etre creee."
        });
        return;
      }

      setFeedback({
        type: "success",
        message: payload?.message || "Reservation creee avec succes."
      });

      setReservationForm(currentForm => ({
        ...currentForm,
        dateReservation: "",
        heureDebut: "",
        heureFin: ""
      }));

      await loadDashboard();
    } catch {
      setFeedback({
        type: "error",
        message: "Impossible de joindre le backend."
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="user-dashboard">
      <div className="panel-header panel-header-row">
        <div>
          <p className="section-label">Utilisateur</p>
          <h2>Espace connecte</h2>
          <p className="section-copy">
            Consultez vos reservations, vos notifications et reservez une salle.
          </p>
        </div>

        <div className="toolbar toolbar-inline">
          <button className="secondary-button" type="button" onClick={loadDashboard}>
            Rafraichir
          </button>
          <button className="secondary-button" type="button" onClick={onLogout}>
            Deconnexion
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
            <article className="info-card">
              <p className="info-label">Profil</p>
              <p className="info-title">
                {user?.prenom} {user?.nom}
              </p>
              <p className="info-meta">{user?.email}</p>
              <p className="info-meta">Role: {user?.role}</p>
            </article>

            <article className="info-card">
              <p className="info-label">Notifications</p>
              <p className="info-title">{notifications.length}</p>
              <p className="info-meta">Messages disponibles</p>
            </article>

            <article className="info-card">
              <p className="info-label">Reservations</p>
              <p className="info-title">{reservations.length}</p>
              <p className="info-meta">Reservations enregistrees</p>
            </article>
          </section>

          <section className="reservation-layout">
            <article className="request-card">
              <div className="panel-header">
                <p className="section-label">Reservation</p>
                <h2>Creer une reservation</h2>
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
                      Selectionnez une salle
                    </option>
                    {salles.map(salle => (
                      <option key={salle.id} value={salle.id}>
                        {salle.nom} - capacite {salle.capacite ?? "n/a"}
                      </option>
                    ))}
                  </select>
                </label>

                <div className="form-grid">
                  <label className="field">
                    <span>Date</span>
                    <input
                      name="dateReservation"
                      type="date"
                      value={reservationForm.dateReservation}
                      onChange={handleReservationChange}
                      required
                    />
                  </label>

                  <label className="field">
                    <span>Heure de debut</span>
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

                <button className="submit-button" type="submit" disabled={isSubmitting}>
                  {isSubmitting ? "Reservation..." : "Creer la reservation"}
                </button>
              </form>
            </article>

            <article className="request-card">
              <div className="panel-header">
                <p className="section-label">Historique</p>
                <h2>Mes reservations</h2>
              </div>

              {reservations.length === 0 ? (
                <div className="empty-state">
                  <p>Aucune reservation pour le moment.</p>
                </div>
              ) : (
                <div className="stack-list">
                  {reservations.map(reservation => (
                    <div className="stack-item" key={reservation.id}>
                      <p className="request-name">
                        {sallesById[String(reservation.salle_id)]?.nom ||
                          `Salle #${reservation.salle_id}`}
                      </p>
                      <p className="request-email">
                        {reservation.date} de {reservation.heure_debut} a{" "}
                        {reservation.heure_fin}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </article>
          </section>

          <article className="request-card">
            <div className="panel-header">
              <p className="section-label">Notifications</p>
              <h2>Messages recus</h2>
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
