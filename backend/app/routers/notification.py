from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.notification import Notification
from app.security.dependencies import get_current_user
from app.utils.dates import to_iso_utc

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


def serialize_notification(notification: Notification):
    return {
        "id": notification.id,
        "utilisateur_id": notification.utilisateur_id,
        "sujet": notification.sujet,
        "message": notification.message,
        "type": notification.type,
        "lu": notification.lu,
        "est_envoyee": notification.est_envoyee,
        "date_envoi": to_iso_utc(notification.date_envoi),
    }


@router.get("/")
def mes_notifications(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    notifications = (
        db.query(Notification)
        .filter(Notification.utilisateur_id == user["user_id"])
        .order_by(Notification.date_envoi.desc())
        .all()
    )
    return [serialize_notification(notification) for notification in notifications]
