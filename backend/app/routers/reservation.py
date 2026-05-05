from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, time

from app.dependencies import get_db
from app.models.salle import Salle
from app.models.reservation import Reservation
from app.models.notification import Notification
from app.models.statuts import StatutReservation
from app.security.dependencies import get_current_user

router = APIRouter(
    prefix="/reservations",
    tags=["Réservations"]
)


def serialize_reservation(reservation: Reservation):
    return {
        "id": reservation.id,
        "utilisateur_id": reservation.utilisateur_id,
        "salle_id": reservation.salle_id,
        "date": reservation.date.isoformat(),
        "heure_debut": reservation.heure_debut.isoformat(),
        "heure_fin": reservation.heure_fin.isoformat(),
        "statut": reservation.statut,
    }


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
    reservations = (
        db.query(Reservation)
        .filter(Reservation.utilisateur_id == user["user_id"])
        .all()
    )
    return [serialize_reservation(reservation) for reservation in reservations]


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
            Reservation.statut == StatutReservation.CONFIRMEE.value,
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
        heure_fin=heure_fin,
        statut=StatutReservation.CONFIRMEE.value,
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


@router.put("/{reservation_id}")
def modifier_reservation(
    reservation_id: int,
    salle_id: int,
    date_reservation: date,
    heure_debut: time,
    heure_fin: time,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    reservation = (
        db.query(Reservation)
        .filter(
            Reservation.id == reservation_id,
            Reservation.utilisateur_id == user["user_id"]
        )
        .first()
    )

    if not reservation:
        raise HTTPException(
            status_code=404,
            detail="Réservation introuvable"
        )

    if reservation.statut == StatutReservation.ANNULEE.value:
        raise HTTPException(
            status_code=400,
            detail="Une réservation annulée ne peut pas être modifiée"
        )

    if heure_debut >= heure_fin:
        raise HTTPException(
            status_code=400,
            detail="L'heure de début doit être antérieure à l'heure de fin"
        )

    conflit = (
        db.query(Reservation)
        .filter(
            Reservation.id != reservation_id,
            Reservation.salle_id == salle_id,
            Reservation.date == date_reservation,
            Reservation.statut == StatutReservation.CONFIRMEE.value,
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

    reservation.salle_id = salle_id
    reservation.date = date_reservation
    reservation.heure_debut = heure_debut
    reservation.heure_fin = heure_fin

    notification = Notification(
        utilisateur_id=user["user_id"],
        message="Votre réservation de salle a été modifiée avec succès."
    )
    db.add(notification)

    db.commit()

    return {"message": "Réservation modifiée avec succès"}


@router.delete("/{reservation_id}")
def annuler_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    reservation = (
        db.query(Reservation)
        .filter(
            Reservation.id == reservation_id,
            Reservation.utilisateur_id == user["user_id"]
        )
        .first()
    )

    if not reservation:
        raise HTTPException(
            status_code=404,
            detail="Réservation introuvable"
        )

    if reservation.statut == StatutReservation.ANNULEE.value:
        raise HTTPException(
            status_code=400,
            detail="Cette réservation est déjà annulée"
        )

    reservation.statut = StatutReservation.ANNULEE.value

    notification = Notification(
        utilisateur_id=user["user_id"],
        message="Votre réservation de salle a été annulée."
    )
    db.add(notification)

    db.commit()

    return {"message": "Réservation annulée avec succès"}
