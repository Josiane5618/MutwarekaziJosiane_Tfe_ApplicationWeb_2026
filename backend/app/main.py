
from fastapi import FastAPI

app = FastAPI(title="Projet Accès & Réservation")

@app.get("/")
def root():
    return {"message": "Backend démarré avec succès"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
