from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.utilisateur import Utilisateur
from app.models.notification import Notification
from app.security.dependencies import get_current_admin
from app.utils.email_service import send_email

router = APIRouter(
    prefix="/admin",
    tags=["Administration"]
)


@router.get("/pending-users")
def list_pending_users(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    users = (
        db.query(Utilisateur)
        .filter(
            Utilisateur.role == "utilisateur",
            Utilisateur.actif == False,
        )
        .order_by(Utilisateur.id.desc())
        .all()
    )

    return [
        {
            "id": user.id,
            "prenom": user.prenom,
            "nom": user.nom,
            "email": user.email,
            "role": user.role,
            "actif": user.actif,
        }
        for user in users
    ]


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

    user.actif = accept

    if accept:
        send_email(
            user.email,
            "Inscription acceptée",
            "Votre compte a été validé. Vous pouvez maintenant vous connecter."
        )
        notification_message = (
            "Votre compte a ete valide par un administrateur."
        )
    else:
        send_email(
            user.email,
            "Inscription refusée",
            "Votre demande d'inscription a été refusée."
        )
        notification_message = (
            "Votre demande d'inscription a ete refusee."
        )

    db.add(
        Notification(
            utilisateur_id=user.id,
            message=notification_message
        )
    )

    db.commit()
    return {"message": "Demande traitée avec succès"}
