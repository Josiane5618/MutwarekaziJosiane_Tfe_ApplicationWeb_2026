from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.utilisateur import Utilisateur
from app.schemas.user import UserRegister, UserLogin
from app.security.dependencies import get_current_admin
from app.security.password import hash_password, verify_password
from app.security.jwt import create_access_token


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

    new_user = Utilisateur(
        prenom=user.prenom,
        nom=user.nom,
        email=user.email,
        mot_de_passe_hash=hash_password(user.password),
        role="utilisateur",
        actif=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Demande d’inscription envoyée. En attente de validation.",
        "user_id": new_user.id
    }


@router.post("/login")
def login_user(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    user = (
        db.query(Utilisateur)
        .filter(Utilisateur.email == credentials.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Identifiants incorrects"
        )

    if not user.actif:
        raise HTTPException(
            status_code=403,
            detail="Compte non validé par un administrateur"
        )

    if not verify_password(credentials.password, user.mot_de_passe_hash):
        raise HTTPException(
            status_code=401,
            detail="Identifiants incorrects"
        )

    token = create_access_token({
        "user_id": user.id,
        "role": user.role
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }