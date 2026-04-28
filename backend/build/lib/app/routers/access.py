from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import numpy as np

from app.dependencies import get_db
from app.models.donnee_faciale import DonneeFaciale
from app.models.log_acces import LogAcces
from app.models.notification import Notification
from app.security.dependencies import get_current_user
from app.face_recognition.engine import extract_face_encoding

router = APIRouter(
    prefix="/access",
    tags=["Contrôle d’accès"]
)


@router.post("/verify")
async def verify_access(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    # Lire l’image
    image_bytes = await file.read()

    # Extraire l'encodage facial
    encoding = extract_face_encoding(image_bytes)
    if encoding is None:
        raise HTTPException(
            status_code=400,
            detail="Aucun visage détecté"
        )

    # Donnée faciale de l'utilisateur
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

    # Comparaison
    db_encoding = np.frombuffer(face_data.encodage, dtype=np.float32)
    distance = np.linalg.norm(encoding - db_encoding)

    SEUIL = 0.5
    if distance < SEUIL:
        resultat = "ACCES_AUTORISE"
    else:
        resultat = "ACCES_REFUSE"

    # Log d'accès
    log = LogAcces(
        utilisateur_id=user["user_id"],
        resultat=resultat,
        distance=float(distance)
    )
    db.add(log)

    # Notification
    notification = Notification(
        utilisateur_id=user["user_id"],
        message=f"Accès bâtiment : {resultat}"
    )
    db.add(notification)

    db.commit()

    return {
        "resultat": resultat,
        "distance": float(distance)
    }
