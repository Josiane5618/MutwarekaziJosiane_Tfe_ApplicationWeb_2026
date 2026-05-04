import { useState } from "react";
import { loginUser } from "../api/api";

export default function UserLoginForm({ onLogin }) {
  const [form, setForm] = useState({
    email: "",
    password: ""
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [feedback, setFeedback] = useState({
    type: "",
    message: ""
  });

  const handleChange = event => {
    setForm({
      ...form,
      [event.target.name]: event.target.value
    });
  };

  const handleSubmit = async event => {
    event.preventDefault();
    setFeedback({ type: "", message: "" });
    setIsSubmitting(true);

    try {
      const response = await loginUser(form);
      const payload = await response.json().catch(() => null);

      if (!response.ok) {
        setFeedback({
          type: "error",
          message:
            payload?.detail || "Connexion utilisateur impossible."
        });
        return;
      }

      onLogin(payload.access_token);
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
    <form className="register-form" onSubmit={handleSubmit} autoComplete="on">
      <div className="panel-header">
        <p className="section-label">Utilisateur</p>
        <h2>Connexion utilisateur</h2>
        <p className="section-copy">
          Connectez-vous après validation administrateur pour accéder aux
          réservations et notifications.
        </p>
      </div>

      {feedback.message ? (
        <div className={`feedback feedback-${feedback.type}`} role="status">
          {feedback.message}
        </div>
      ) : null}

      <div className="form-grid">
        <label className="field field-full">
          <span>Email</span>
          <input
            name="email"
            type="email"
            value={form.email}
            onChange={handleChange}
            placeholder="vous@example.com"
            autoComplete="username"
            required
          />
        </label>

        <label className="field field-full">
          <span>Mot de passe</span>
          <input
            name="password"
            type="password"
            value={form.password}
            onChange={handleChange}
            placeholder="Votre mot de passe"
            autoComplete="current-password"
            required
          />
        </label>
      </div>

      <button className="submit-button" type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Connexion..." : "Se connecter"}
      </button>
    </form>
  );
}
