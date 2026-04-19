from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.utilisateur import Utilisateur
from app.schemas.user import UserRegister
from app.security.password import hash_password

router = APIRouter(
    prefix="/auth",
    tags=["Authentification"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register")
def register_user(
    user: UserRegister,
    db: Session = Depends(get_db)
):
    # Vérifier si l'email existe déjà
    existing_user = (
        db.query(Utilisateur)
        .filter(Utilisateur.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Cet email est déjà utilisé"
        )

    # Création de l'utilisateur (en attente de validation admin)
    new_user = Utilisateur(
        prenom=user.prenom,
        nom=user.nom,
        email=user.email,
        mot_de_passe_hash=hash_password(user.password),
        role="utilisateur",
        actif=False  # ✅ conforme au cahier des charges
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Demande d’inscription envoyée. En attente de validation.",
        "user_id": new_user.id
    }