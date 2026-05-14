from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.donnee_faciale import DonneeFaciale
from app.models.log_acces import LogAcces
from app.models.notification import Notification
from app.models.statuts import ResultatVerification, TypeNotification
from app.models.utilisateur import Utilisateur
from app.security.dependencies import get_current_user
from app.face_recognition.engine import extract_face_encoding
from app.utils.email_service import send_email

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

    # Comparaison (dechiffre l'encodage si necessaire)
    distance = face_data.comparer(encoding.tobytes())

    SEUIL = 0.5
    if distance < SEUIL:
        resultat = ResultatVerification.ACCES_AUTORISE.value
    else:
        resultat = ResultatVerification.ACCES_REFUSE.value

    # Log d'accès
    log = LogAcces(
        utilisateur_id=user["user_id"],
        resultat=resultat,
        score_confiance=float(distance),
        details=f"Distance faciale calculee : {float(distance):.3f}"
    )
    db.add(log)

    # Notification
    notification = Notification(
        utilisateur_id=user["user_id"],
        sujet=f"Accès bâtiment : {resultat}",
        message=f"Accès bâtiment : {resultat}",
        type=TypeNotification.ACCES_BATIMENT.value,
    )
    db.add(notification)

    db.commit()

    # Envoi de l'email correspondant
    utilisateur = (
        db.query(Utilisateur)
        .filter(Utilisateur.id == user["user_id"])
        .first()
    )

    if utilisateur:
        if resultat == ResultatVerification.ACCES_AUTORISE.value:
            sujet = "Accès au bâtiment autorisé"
            contenu = (
                "Votre tentative d'accès au bâtiment a été acceptée.\n"
                f"Score de correspondance : {float(distance):.3f}"
            )
        else:
            sujet = "Accès au bâtiment refusé"
            contenu = (
                "Une tentative d'accès au bâtiment a été refusée sur votre compte.\n"
                f"Score de correspondance : {float(distance):.3f}"
            )

        send_email(utilisateur.email, sujet, contenu)

    return {
        "resultat": resultat,
        "distance": float(distance)
    }
