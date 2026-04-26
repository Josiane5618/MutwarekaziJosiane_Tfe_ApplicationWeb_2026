from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import EmailStr

from app.dependencies import get_db
from app.models.donnee_faciale import DonneeFaciale
from app.models.utilisateur import Utilisateur
from app.schemas.user import UserLogin
from app.face_recognition.engine import extract_face_encoding
from app.security.password import hash_password, verify_password
from app.security.jwt import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Authentification"]
)


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
        image=image_bytes,
        encodage=encoding.tobytes()
    )
    db.add(face_data)
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
