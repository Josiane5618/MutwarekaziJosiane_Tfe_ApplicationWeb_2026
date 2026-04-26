from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.notification import Notification
from app.security.dependencies import get_current_user

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


@router.get("/")
def mes_notifications(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return (
        db.query(Notification)
        .filter(Notification.utilisateur_id == user["user_id"])
        .order_by(Notification.date_creation.desc())
        .all()
    )
