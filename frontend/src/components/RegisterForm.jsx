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

  const handleChange = e => {
    setForm({
      ...form,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async () => {
    if (!faceImage) {
      alert("La capture faciale est obligatoire !");
      return;
    }

    const data = new FormData();
    data.append("nom", form.nom);
    data.append("prenom", form.prenom);
    data.append("email", form.email);
    data.append("password", form.password);
    data.append("file", faceImage);

    const response = await registerUser(data);

    if (response.ok) {
      alert("Inscription envoyée. En attente de validation par l'administrateur.");
    } else {
      alert("Erreur lors de l'inscription");
    }
  };

  return (
    <div>
      <input name="nom" placeholder="Nom" onChange={handleChange} />
      <input name="prenom" placeholder="Prénom" onChange={handleChange} />
      <input name="email" placeholder="Email" onChange={handleChange} />
      <input name="password" type="password" placeholder="Mot de passe" onChange={handleChange} />

      <CameraCapture onCapture={setFaceImage} />

      <button onClick={handleSubmit}>S’inscrire</button>
    </div>
  );
}