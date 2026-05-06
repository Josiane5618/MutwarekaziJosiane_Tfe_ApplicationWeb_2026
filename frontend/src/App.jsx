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
        <h1>Gestion d'accès à un bâtiment et réservation de salles</h1>

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

      </section>

      {view === "register" ? <Register /> : null}
      {view === "user" ? <User /> : null}
      {view === "admin" ? <Admin /> : null}
    </main>
  );
}

export default App;
