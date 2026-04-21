from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import numpy as np

from app.database import SessionLocal
from app.models.donnee_faciale import DonneeFaciale
from app.security.dependencies import get_current_user
from app.face_recognition.engine import extract_face_encoding

router = APIRouter(
    prefix="/access",
    tags=["Contrôle d’accès"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/verify")
async def verify_access(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    image_bytes = await file.read()

    encoding = extract_face_encoding(image_bytes)
    if encoding is None:
        raise HTTPException(status_code=400, detail="Aucun visage détecté")

    face_data = (
        db.query(DonneeFaciale)
        .filter(DonneeFaciale.utilisateur_id == user["user_id"])
        .first()
    )

    if not face_data:
        raise HTTPException(
            status_code=404,
            detail="Aucune donnée faciale enregistrée pour cet utilisateur"
        )

    db_encoding = np.frombuffer(face_data.encodage, dtype=np.float32)
    distance = np.linalg.norm(encoding - db_encoding)

    SEUIL = 0.5

    if distance < SEUIL:
        return {"resultat": "ACCES_AUTORISE", "distance": float(distance)}
    else:
        return {"resultat": "ACCES_REFUSE", "distance": float(distance)}