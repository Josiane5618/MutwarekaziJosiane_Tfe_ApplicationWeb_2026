from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, time

from app.dependencies import get_db
from app.models.salle import Salle
from app.models.reservation import Reservation
from app.models.notification import Notification
from app.models.statuts import StatutReservation, TypeNotification
from app.models.utilisateur import Utilisateur
from app.security.dependencies import get_current_user
from app.config import SMTP_ENABLED
from app.utils.email_service import send_email

router = APIRouter(
    prefix="/reservations",
    tags=["Réservations"]
)


def serialize_reservation(reservation: Reservation):
    return {
        "id": reservation.id,
        "utilisateur_id": reservation.utilisateur_id,
        "salle_id": reservation.salle_id,
        "date": reservation.date_reservation.isoformat(),
        "heure_debut": reservation.heure_debut.isoformat(),
        "heure_fin": reservation.heure_fin.isoformat(),
        "statut": reservation.statut,
    }


def format_email_time(value: time) -> str:
    return value.strftime("%H h %M")


def format_reservation_email(
    salle: Salle,
    date_reservation: date,
    heure_debut: time,
    heure_fin: time,
) -> str:
    return (
        f"Salle : {salle.nom}\n"
        f"Date : {date_reservation.strftime('%d/%m/%Y')}\n"
        f"Horaire : {format_email_time(heure_debut)} à "
        f"{format_email_time(heure_fin)}"
    )


def send_reservation_email(
    db: Session,
    user_id: int,
    subject: str,
    content: str,
):
    utilisateur = (
        db.query(Utilisateur)
        .filter(Utilisateur.id == user_id)
        .first()
    )

    if not utilisateur:
        return {
            "email_envoye": False,
            "email_mode": "smtp" if SMTP_ENABLED else "console",
        }

    email_sent = send_email(utilisateur.email, subject, content)

    return {
        "email_envoye": email_sent,
        "email_mode": "smtp" if SMTP_ENABLED else "console",
    }


def validate_reservation_rules(
    salle_id: int,
    date_reservation: date,
    heure_debut: time,
    heure_fin: time,
    db: Session,
) -> Salle:
    if date_reservation < date.today():
        raise HTTPException(
            status_code=400,
            detail="La date de réservation ne peut pas être passée"
        )

    if heure_debut >= heure_fin:
        raise HTTPException(
            status_code=400,
            detail="L'heure de début doit être antérieure à l'heure de fin"
        )

    salle = db.query(Salle).filter(Salle.id == salle_id).first()

    if not salle:
        raise HTTPException(
            status_code=404,
            detail="Salle introuvable"
        )

    if not salle.est_active:
        raise HTTPException(
            status_code=400,
            detail="Cette salle n'est pas disponible"
        )

    return salle


@router.get("/salles")
def list_salles(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return db.query(Salle).filter(Salle.est_active == True).all()


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
    salle = validate_reservation_rules(
        salle_id=salle_id,
        date_reservation=date_reservation,
        heure_debut=heure_debut,
        heure_fin=heure_fin,
        db=db,
    )

    conflit = (
        db.query(Reservation)
        .filter(
            Reservation.salle_id == salle_id,
            Reservation.date_reservation == date_reservation,
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
        date_reservation=date_reservation,
        heure_debut=heure_debut,
        heure_fin=heure_fin,
        statut=StatutReservation.CONFIRMEE.value,
    )

    db.add(reservation)

    notification = Notification(
        utilisateur_id=user["user_id"],
        sujet="Confirmation de réservation",
        message="Votre réservation de salle a été créée avec succès.",
        type=TypeNotification.CONFIRMATION_RESERVATION.value,
    )
    db.add(notification)

    db.commit()

    email_result = send_reservation_email(
        db=db,
        user_id=user["user_id"],
        subject="Confirmation de réservation",
        content=(
            "Votre réservation de salle a été créée avec succès.\n\n"
            f"{format_reservation_email(salle, date_reservation, heure_debut, heure_fin)}"
        ),
    )

    return {
        "message": "Réservation créée avec succès",
        **email_result,
    }


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

    salle = validate_reservation_rules(
        salle_id=salle_id,
        date_reservation=date_reservation,
        heure_debut=heure_debut,
        heure_fin=heure_fin,
        db=db,
    )

    conflit = (
        db.query(Reservation)
        .filter(
            Reservation.id != reservation_id,
            Reservation.salle_id == salle_id,
            Reservation.date_reservation == date_reservation,
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

    reservation.modifier_creneau(
        date=date_reservation,
        debut=heure_debut,
        fin=heure_fin,
    )
    reservation.salle_id = salle_id

    notification = Notification(
        utilisateur_id=user["user_id"],
        message="Votre réservation de salle a été modifiée avec succès."
    )
    db.add(notification)

    db.commit()

    email_result = send_reservation_email(
        db=db,
        user_id=user["user_id"],
        subject="Modification de réservation",
        content=(
            "Votre réservation de salle a été modifiée avec succès.\n\n"
            f"{format_reservation_email(salle, date_reservation, heure_debut, heure_fin)}"
        ),
    )

    return {
        "message": "Réservation modifiée avec succès",
        **email_result,
    }


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

    reservation_details = format_reservation_email(
        reservation.salle,
        reservation.date_reservation,
        reservation.heure_debut,
        reservation.heure_fin,
    )
    reservation.annuler()

    notification = Notification(
        utilisateur_id=user["user_id"],
        message="Votre réservation de salle a été annulée."
    )
    db.add(notification)

    db.commit()

    email_result = send_reservation_email(
        db=db,
        user_id=user["user_id"],
        subject="Annulation de réservation",
        content=(
            "Votre réservation de salle a été annulée.\n\n"
            f"{reservation_details}"
        ),
    )

    return {
        "message": "Réservation annulée avec succès",
        **email_result,
    }
