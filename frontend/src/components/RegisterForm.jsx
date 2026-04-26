import { registerUser } from "../api/api";
import { useState } from "react";
import CameraCapture from "./CameraCapture";

export default function RegisterForm() {
  const [form, setForm] = useState({
    nom: "",
    prenom: "",
    email: "",
    password: ""
  });

  const [faceImage, setFaceImage] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [feedback, setFeedback] = useState({
    type: "",
    message: ""
  });

  const handleChange = e => {
    setForm({
      ...form,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setFeedback({ type: "", message: "" });

    if (!faceImage) {
      setFeedback({
        type: "error",
        message: "La capture faciale est obligatoire avant l'envoi."
      });
      return;
    }

    setIsSubmitting(true);

    const data = new FormData();
    data.append("nom", form.nom);
    data.append("prenom", form.prenom);
    data.append("email", form.email);
    data.append("password", form.password);
    data.append("file", faceImage, "face-capture.jpg");

    try {
      const response = await registerUser(data);
      const payload = await response.json().catch(() => null);

      if (!response.ok) {
        setFeedback({
          type: "error",
          message: payload?.detail || "Erreur lors de l'inscription."
        });
        return;
      }

      setFeedback({
        type: "success",
        message:
          payload?.message ||
          "Inscription envoyee. En attente de validation par l'administrateur."
      });

      setForm({
        nom: "",
        prenom: "",
        email: "",
        password: ""
      });
      setFaceImage(null);
    } catch {
      setFeedback({
        type: "error",
        message:
          "Impossible de joindre le backend. Verifie que l'API est bien lancee."
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form className="register-form" onSubmit={handleSubmit}>
      <div className="panel-header">
        <p className="section-label">Demande d'inscription</p>
        <h2>Informations utilisateur</h2>
        <p className="section-copy">
          Remplissez le formulaire puis capturez votre visage pour envoyer la
          demande.
        </p>
      </div>

      {feedback.message ? (
        <div className={`feedback feedback-${feedback.type}`} role="status">
          {feedback.message}
        </div>
      ) : null}

      <div className="form-grid">
        <label className="field">
          <span>Prenom</span>
          <input
            name="prenom"
            placeholder="Josiane"
            value={form.prenom}
            onChange={handleChange}
            required
          />
        </label>

        <label className="field">
          <span>Nom</span>
          <input
            name="nom"
            placeholder="Mutwarekazi"
            value={form.nom}
            onChange={handleChange}
            required
          />
        </label>

        <label className="field field-full">
          <span>Email</span>
          <input
            name="email"
            type="email"
            placeholder="vous@example.com"
            value={form.email}
            onChange={handleChange}
            required
          />
        </label>

        <label className="field field-full">
          <span>Mot de passe</span>
          <input
            name="password"
            type="password"
            placeholder="Minimum recommande: un mot de passe fort"
            value={form.password}
            onChange={handleChange}
            required
          />
        </label>
      </div>

      <CameraCapture onCapture={setFaceImage} hasCapture={Boolean(faceImage)} />

      <button className="submit-button" type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Envoi en cours..." : "Envoyer la demande"}
      </button>
    </form>
  );
}
