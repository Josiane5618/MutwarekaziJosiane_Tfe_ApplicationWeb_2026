import { useState } from "react";
import Register from "./pages/Register";
import Admin from "./pages/Admin";
import User from "./pages/User";
import "./App.css";

function App() {
  const [view, setView] = useState("register");

  return (
    <main className="register-page">
      <section className="register-hero">
        <p className="eyebrow">Gestion d'acces</p>
        <h1>Creer un compte et le valider cote administrateur</h1>
        <p className="hero-copy">
          Le projet permet maintenant d'envoyer une inscription faciale puis de
          la traiter depuis une interface administrateur locale.
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
            Validation administrateur
          </button>
        </div>

        <div className="hero-steps" aria-label="Etapes d'inscription">
          <div className="hero-step">
            <span>1</span>
            <p>Un utilisateur cree sa demande avec photo faciale.</p>
          </div>
          <div className="hero-step">
            <span>2</span>
            <p>L'administrateur se connecte et examine les demandes.</p>
          </div>
          <div className="hero-step">
            <span>3</span>
            <p>Une fois valide, l'utilisateur se connecte et reserve une salle.</p>
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
