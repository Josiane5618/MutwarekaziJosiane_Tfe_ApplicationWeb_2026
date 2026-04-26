from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, time

from app.dependencies import get_db
from app.models.salle import Salle
from app.models.reservation import Reservation
from app.models.notification import Notification
from app.security.dependencies import get_current_user

router = APIRouter(
    prefix="/reservations",
    tags=["Réservations"]
)


@router.get("/salles")
def list_salles(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return db.query(Salle).filter(Salle.active == True).all()


@router.get("/mes-reservations")
def mes_reservations(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return (
        db.query(Reservation)
        .filter(Reservation.utilisateur_id == user["user_id"])
        .all()
    )


@router.post("/creer")
def creer_reservation(
    salle_id: int,
    date_reservation: date,
    heure_debut: time,
    heure_fin: time,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if heure_debut >= heure_fin:
        raise HTTPException(
            status_code=400,
            detail="L'heure de début doit être antérieure à l'heure de fin"
        )

    conflit = (
        db.query(Reservation)
        .filter(
            Reservation.salle_id == salle_id,
            Reservation.date == date_reservation,
            Reservation.heure_debut < heure_fin,
            Reservation.heure_fin > heure_debut
        )
        .first()
    )

    if conflit:
        raise HTTPException(
            status_code=409,
            detail="Créneau déjà réservé pour cette salle"
        )

    reservation = Reservation(
        utilisateur_id=user["user_id"],
        salle_id=salle_id,
        date=date_reservation,
        heure_debut=heure_debut,
        heure_fin=heure_fin
    )

    db.add(reservation)

    # ✅ Notification utilisateur
    notification = Notification(
        utilisateur_id=user["user_id"],
        message="Votre réservation de salle a été créée avec succès."
    )
    db.add(notification)

    db.commit()

    return {"message": "Réservation créée avec succès"}
