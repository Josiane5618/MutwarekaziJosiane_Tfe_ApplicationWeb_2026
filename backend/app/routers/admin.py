from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.utilisateur import Utilisateur
from app.security.dependencies import get_current_admin

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

@router.get("/pending-users")
def list_pending_users(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    return (
        db.query(Utilisateur)
        .filter(Utilisateur.actif == False)
        .all()
    )