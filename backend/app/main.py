
from fastapi import FastAPI
from app.routers import auth
from sqlalchemy import text

from .database import Base, engine
from .models.utilisateur import Utilisateur  # ← OBLIGATOIRE

app = FastAPI()
app.include_router(auth.router)

@app.get("/db-test")
def db_test():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"database": "Connexion réussie"}
    except Exception as e:
        return {"error": str(e)}

# Création automatique des tables
Base.metadata.create_all(bind=engine)
