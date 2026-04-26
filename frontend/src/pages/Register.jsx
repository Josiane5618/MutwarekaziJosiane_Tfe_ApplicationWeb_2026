import RegisterForm from "../components/RegisterForm";

export default function Register() {
  return (
    <main className="register-page">
      <section className="register-hero">
        <p className="eyebrow">Gestion d'acces</p>
        <h1>Creer un compte avec verification faciale</h1>
        <p className="hero-copy">
          Cette interface permet d'envoyer une demande d'inscription avec photo
          faciale. Une fois la demande validee par un administrateur, le compte
          pourra etre utilise pour la connexion et la verification d'acces.
        </p>

        <div className="hero-steps" aria-label="Etapes d'inscription">
          <div className="hero-step">
            <span>1</span>
            <p>Renseigner vos informations personnelles.</p>
          </div>
          <div className="hero-step">
            <span>2</span>
            <p>Capturer votre visage depuis la webcam.</p>
          </div>
          <div className="hero-step">
            <span>3</span>
            <p>Envoyer la demande pour validation administrateur.</p>
          </div>
        </div>
      </section>

      <section className="register-panel">
        <RegisterForm />
      </section>
    </main>
  );
}
