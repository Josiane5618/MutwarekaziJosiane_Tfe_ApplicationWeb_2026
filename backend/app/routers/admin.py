from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.utilisateur import Utilisateur
from app.security.dependencies import get_current_admin
from app.utils.email_service import send_email

router = APIRouter(
    prefix="/admin",
    tags=["Administration"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.put("/validate-user/{user_id}")
def validate_user(
    user_id: int,
    accept: bool,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    if accept:
        user.statut = "ACTIF"
        send_email(
            user.email,
            "Inscription acceptée",
            "Votre compte a été validé. Vous pouvez maintenant vous connecter."
        )
    else:
        user.statut = "REFUSE"
        send_email(
            user.email,
            "Inscription refusée",
            "Votre demande d'inscription a été refusée."
        )

    db.commit()
    return {"message": "Demande traitée avec succès"}