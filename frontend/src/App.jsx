import { useState } from "react";
import Register from "./pages/Register";
import Admin from "./pages/Admin";
import User from "./pages/User";
import "./App.css";

function App() {
  const [view, setView] = useState("register");

  return (
    <main className={`register-page view-${view}`}>
      <section className="register-hero">
        <p className="eyebrow">Gestion d'accès</p>
        <h1>Plateforme de gestion d'accès</h1>
        <p className="hero-copy">
          Gérez les inscriptions, l'accès au bâtiment et les réservations de salles.
        </p>

        <div className="hero-tabs" aria-label="Navigation principale">
          <button
            className={view === "register" ? "hero-tab is-active" : "hero-tab"}
            type="button"
            onClick={() => setView("register")}
          >
            Inscription utilisateur
          </button>
          <button
            className={view === "user" ? "hero-tab is-active" : "hero-tab"}
            type="button"
            onClick={() => setView("user")}
          >
            Connexion utilisateur
          </button>
          <button
            className={view === "admin" ? "hero-tab is-active" : "hero-tab"}
            type="button"
            onClick={() => setView("admin")}
          >
            Connexion administrateur
          </button>
        </div>

        <div className="hero-steps" aria-label="Etapes d'inscription">
          <div className="hero-step">
            <p>Un utilisateur crée sa demande avec photo faciale.</p>
          </div>
          <div className="hero-step">
            <p>L'administrateur se connecte et gère les demandes, salles, utilisateurs, réservations et accès.</p>
          </div>
          <div className="hero-step">
            <p>Une fois validé, l'utilisateur réserve une salle et accède au bâtiment par reconnaissance faciale.</p>
          </div>
        </div>
      </section>

      {view === "register" ? <Register /> : null}
      {view === "user" ? <User /> : null}
      {view === "admin" ? <Admin /> : null}
    </main>
  );
}

export default App;
