import { useState } from "react";
import { loginUser } from "../api/api";

export default function AdminLoginForm({ onLogin }) {
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
          message: payload?.detail || "Connexion administrateur impossible."
        });
        return;
      }

      onLogin(payload.access_token);
      setFeedback({
        type: "success",
        message: "Connexion administrateur réussie."
      });
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
    <form className="register-form" onSubmit={handleSubmit} autoComplete="off">
      <div className="panel-header">
        <p className="section-label">Administration</p>
        <h2>Connexion administrateur</h2>
        <p className="section-copy">
          Connectez-vous pour gérer les demandes, les salles, les utilisateurs, les réservations et les accès.
        </p>
      </div>

      {feedback.message ? (
        <div className={`feedback feedback-${feedback.type}`} role="status">
          {feedback.message}
        </div>
      ) : null}

      <div className="form-grid">
        <label className="field field-full">
          <span>Email admin</span>
          <input
            name="email"
            type="email"
            value={form.email}
            onChange={handleChange}
            placeholder="email administrateur"
            autoComplete="off"
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
            placeholder="mot de passe administrateur"
            autoComplete="new-password"
            required
          />
        </label>
      </div>

      <button className="submit-button" type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Connexion..." : "Se connecter en admin"}
      </button>
    </form>
  );
}
