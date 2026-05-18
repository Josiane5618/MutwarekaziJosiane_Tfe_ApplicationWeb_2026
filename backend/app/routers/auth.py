from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from datetime import datetime

from app.dependencies import get_db
from app.models.demande_inscription import DemandeInscription
from app.models.donnee_faciale import DonneeFaciale
from app.models.statuts import StatutDemandeInscription
from app.models.utilisateur import Utilisateur
from app.schemas.user import UserLogin
from app.face_recognition.engine import extract_face_encoding
from app.security.biometric_cipher import encrypt_encoding
from app.security.dependencies import get_current_user
from app.security.password import (
    hash_password,
    verify_password,
    validate_password_strength,
    PasswordTooWeakError,
)
from app.security.jwt import create_access_token
from app.utils.dates import to_iso_utc

router = APIRouter(
    prefix="/auth",
    tags=["Authentification"]
)


class ProfileUpdate(BaseModel):
    prenom: str = Field(..., min_length=1)
    nom: str = Field(..., min_length=1)
    email: EmailStr
    password: Optional[str] = Field(default=None, min_length=1)

    @field_validator("password")
    @classmethod
    def _password_doit_etre_robuste(cls, value):
        if value is None or value == "":
            return value
        try:
            validate_password_strength(value)
        except PasswordTooWeakError as exc:
            raise ValueError(str(exc)) from exc
        return value


@router.post("/register")
async def register_user(
    prenom: str = Form(...),
    nom: str = Form(...),
    email: EmailStr = Form(...),
    password: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    existing_user = (
        db.query(Utilisateur)
        .filter(Utilisateur.email == email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Cet email est déjà utilisé"
        )

    try:
        validate_password_strength(password)
    except PasswordTooWeakError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    image_bytes = await file.read()
    encoding = extract_face_encoding(image_bytes)

    if encoding is None:
        raise HTTPException(
            status_code=400,
            detail="Aucun visage détecté lors de l'inscription"
        )

    new_user = Utilisateur(
        prenom=prenom,
        nom=nom,
        email=email,
        mot_de_passe_hash=hash_password(password),
        role="utilisateur",
        actif=False
    )

    db.add(new_user)
    db.flush()

    face_data = DonneeFaciale(
        utilisateur_id=new_user.id,
        image_path=image_bytes,
        encodage_facial=encrypt_encoding(encoding.tobytes()),
        est_chiffre=True,
    )
    db.add(face_data)

    demande = DemandeInscription(
        utilisateur_id=new_user.id,
        statut=StatutDemandeInscription.EN_ATTENTE.value,
    )
    db.add(demande)

    db.commit()
    db.refresh(new_user)

    return {
        "message": "Demande d’inscription envoyée. En attente de validation.",
        "user_id": new_user.id,
        "demande_id": demande.id,
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

    user.derniere_connexion = datetime.utcnow()
    db.commit()

    token = create_access_token({
        "user_id": user.id,
        "role": user.role
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/me")
def get_me(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    current_user = (
        db.query(Utilisateur)
        .filter(Utilisateur.id == user["user_id"])
        .first()
    )

    if not current_user:
        raise HTTPException(
            status_code=404,
            detail="Utilisateur introuvable"
        )

    return {
        "id": current_user.id,
        "prenom": current_user.prenom,
        "nom": current_user.nom,
        "email": current_user.email,
        "role": current_user.role,
        "actif": current_user.actif,
        "statut_compte": current_user.statut_compte,
        "date_creation": to_iso_utc(current_user.date_creation),
    }


@router.put("/me")
def update_me(
    payload: ProfileUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    current_user = (
        db.query(Utilisateur)
        .filter(Utilisateur.id == user["user_id"])
        .first()
    )

    if not current_user:
        raise HTTPException(
            status_code=404,
            detail="Utilisateur introuvable"
        )

    existing_email_user = (
        db.query(Utilisateur)
        .filter(
            Utilisateur.email == payload.email,
            Utilisateur.id != current_user.id
        )
        .first()
    )

    if existing_email_user:
        raise HTTPException(
            status_code=409,
            detail="Cet email est déjà utilisé"
        )

    current_user.prenom = payload.prenom.strip()
    current_user.nom = payload.nom.strip()
    current_user.email = payload.email

    if payload.password:
        current_user.mot_de_passe_hash = hash_password(payload.password)

    db.commit()
    db.refresh(current_user)

    return {
        "id": current_user.id,
        "prenom": current_user.prenom,
        "nom": current_user.nom,
        "email": current_user.email,
        "role": current_user.role,
        "actif": current_user.actif,
        "statut_compte": current_user.statut_compte,
        "date_creation": to_iso_utc(current_user.date_creation),
    }
