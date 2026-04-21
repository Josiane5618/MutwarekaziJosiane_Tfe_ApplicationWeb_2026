from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.notification import Notification
from app.security.dependencies import get_current_user

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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