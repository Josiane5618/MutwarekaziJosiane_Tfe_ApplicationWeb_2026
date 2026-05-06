from datetime import date, time, timedelta

import pytest
from fastapi import HTTPException

from app.models.notification import Notification
from app.models.reservation import Reservation
from app.models.salle import Salle
from app.models.statuts import StatutReservation
from app.models.utilisateur import Utilisateur
from app.routers import reservation as reservation_router
from app.routers.reservation import (
    annuler_reservation,
    creer_reservation,
    mes_reservations,
    modifier_reservation,
)


def future_date(days=30):
    return date.today() + timedelta(days=days)


def past_date():
    return date.today() - timedelta(days=1)


def create_user(db_session, email):
    user = Utilisateur(
        prenom="Test",
        nom="User",
        email=email,
        mot_de_passe_hash="hash",
        role="utilisateur",
        actif=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def create_salle(db_session, nom="Salle test"):
    salle = Salle(
        nom=nom,
        description="Salle de test",
        capacite=10,
        active=True
    )
    db_session.add(salle)
    db_session.commit()
    db_session.refresh(salle)
    return salle


def create_reservation(
    db_session,
    user_id,
    salle=None,
    start=time(9, 0),
    end=time(10, 0),
    reservation_date=None,
):
    if salle is None:
        salle = create_salle(db_session, nom=f"Salle {user_id}")

    reservation = Reservation(
        utilisateur_id=user_id,
        salle_id=salle.id,
        date=reservation_date or future_date(),
        heure_debut=start,
        heure_fin=end
    )
    db_session.add(reservation)
    db_session.commit()
    db_session.refresh(reservation)
    return reservation


def test_user_can_cancel_own_reservation(db_session, monkeypatch):
    monkeypatch.setattr(reservation_router, "SMTP_ENABLED", False)
    monkeypatch.setattr(reservation_router, "send_email", lambda *args: False)

    user = create_user(db_session, "owner@example.com")
    reservation = create_reservation(db_session, user.id)

    response = annuler_reservation(
        reservation_id=reservation.id,
        db=db_session,
        user={"user_id": user.id, "role": "utilisateur"}
    )

    remaining_reservation = (
        db_session.query(Reservation)
        .filter(Reservation.id == reservation.id)
        .first()
    )
    notification = (
        db_session.query(Notification)
        .filter(Notification.utilisateur_id == user.id)
        .first()
    )

    assert response["message"] == "Réservation annulée avec succès"
    assert response["email_envoye"] is False
    assert response["email_mode"] == "console"
    assert remaining_reservation is not None
    assert remaining_reservation.statut == StatutReservation.ANNULEE.value
    assert notification is not None
    assert "annulée" in notification.message


def test_user_reservations_include_confirmed_status(db_session):
    user = create_user(db_session, "owner@example.com")
    reservation = create_reservation(db_session, user.id)

    response = mes_reservations(
        db=db_session,
        user={"user_id": user.id, "role": "utilisateur"}
    )

    assert response == [
        {
            "id": reservation.id,
            "utilisateur_id": user.id,
            "salle_id": reservation.salle_id,
            "date": reservation.date.isoformat(),
            "heure_debut": "09:00:00",
            "heure_fin": "10:00:00",
            "statut": StatutReservation.CONFIRMEE.value,
        }
    ]


def test_create_reservation_ignores_cancelled_reservation_conflict(
    db_session,
    monkeypatch,
):
    monkeypatch.setattr(reservation_router, "SMTP_ENABLED", False)
    monkeypatch.setattr(reservation_router, "send_email", lambda *args: False)

    user = create_user(db_session, "owner@example.com")
    salle = create_salle(db_session)
    create_reservation(
        db_session,
        user.id,
        salle=salle,
        start=time(9, 0),
        end=time(10, 0),
    ).statut = StatutReservation.ANNULEE.value
    db_session.commit()

    response = creer_reservation(
        salle_id=salle.id,
        date_reservation=future_date(),
        heure_debut=time(9, 30),
        heure_fin=time(10, 30),
        db=db_session,
        user={"user_id": user.id, "role": "utilisateur"}
    )

    reservations = db_session.query(Reservation).all()

    assert response["message"] == "Réservation créée avec succès"
    assert response["email_envoye"] is False
    assert response["email_mode"] == "console"
    assert len(reservations) == 2
    assert reservations[-1].statut == StatutReservation.CONFIRMEE.value


def test_user_cannot_cancel_another_users_reservation(db_session):
    owner = create_user(db_session, "owner@example.com")
    other_user = create_user(db_session, "other@example.com")
    reservation = create_reservation(db_session, owner.id)

    with pytest.raises(HTTPException) as exc_info:
        annuler_reservation(
            reservation_id=reservation.id,
            db=db_session,
            user={"user_id": other_user.id, "role": "utilisateur"}
        )

    still_existing = (
        db_session.query(Reservation)
        .filter(Reservation.id == reservation.id)
        .first()
    )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Réservation introuvable"
    assert still_existing is not None
    assert still_existing.statut == StatutReservation.CONFIRMEE.value


def test_user_cannot_cancel_already_cancelled_reservation(db_session):
    user = create_user(db_session, "owner@example.com")
    reservation = create_reservation(db_session, user.id)
    reservation.statut = StatutReservation.ANNULEE.value
    db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        annuler_reservation(
            reservation_id=reservation.id,
            db=db_session,
            user={"user_id": user.id, "role": "utilisateur"}
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Cette réservation est déjà annulée"


def test_user_can_update_own_reservation(db_session, monkeypatch):
    monkeypatch.setattr(reservation_router, "SMTP_ENABLED", False)
    monkeypatch.setattr(reservation_router, "send_email", lambda *args: False)

    user = create_user(db_session, "owner@example.com")
    salle = create_salle(db_session, "Salle initiale")
    new_salle = create_salle(db_session, "Salle modifiée")
    reservation = create_reservation(db_session, user.id, salle=salle)

    response = modifier_reservation(
        reservation_id=reservation.id,
        salle_id=new_salle.id,
        date_reservation=future_date(days=31),
        heure_debut=time(11, 0),
        heure_fin=time(12, 0),
        db=db_session,
        user={"user_id": user.id, "role": "utilisateur"}
    )

    db_session.refresh(reservation)
    notification = (
        db_session.query(Notification)
        .filter(Notification.utilisateur_id == user.id)
        .first()
    )

    assert response["message"] == "Réservation modifiée avec succès"
    assert response["email_envoye"] is False
    assert response["email_mode"] == "console"
    assert reservation.salle_id == new_salle.id
    assert reservation.date == future_date(days=31)
    assert reservation.heure_debut == time(11, 0)
    assert reservation.heure_fin == time(12, 0)
    assert notification is not None
    assert "modifiée" in notification.message


def test_user_cannot_update_another_users_reservation(db_session):
    owner = create_user(db_session, "owner@example.com")
    other_user = create_user(db_session, "other@example.com")
    salle = create_salle(db_session)
    reservation = create_reservation(db_session, owner.id, salle=salle)

    with pytest.raises(HTTPException) as exc_info:
        modifier_reservation(
            reservation_id=reservation.id,
            salle_id=salle.id,
            date_reservation=future_date(days=31),
            heure_debut=time(11, 0),
            heure_fin=time(12, 0),
            db=db_session,
            user={"user_id": other_user.id, "role": "utilisateur"}
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Réservation introuvable"


def test_user_cannot_update_cancelled_reservation(db_session):
    user = create_user(db_session, "owner@example.com")
    salle = create_salle(db_session)
    reservation = create_reservation(db_session, user.id, salle=salle)
    reservation.statut = StatutReservation.ANNULEE.value
    db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        modifier_reservation(
            reservation_id=reservation.id,
            salle_id=salle.id,
            date_reservation=future_date(days=31),
            heure_debut=time(11, 0),
            heure_fin=time(12, 0),
            db=db_session,
            user={"user_id": user.id, "role": "utilisateur"}
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == (
        "Une réservation annulée ne peut pas être modifiée"
    )


def test_update_reservation_rejects_room_conflict(db_session):
    user = create_user(db_session, "owner@example.com")
    salle = create_salle(db_session)
    reservation = create_reservation(
        db_session,
        user.id,
        salle=salle,
        start=time(9, 0),
        end=time(10, 0)
    )
    create_reservation(
        db_session,
        user.id,
        salle=salle,
        start=time(11, 0),
        end=time(12, 0)
    )

    with pytest.raises(HTTPException) as exc_info:
        modifier_reservation(
            reservation_id=reservation.id,
            salle_id=salle.id,
            date_reservation=future_date(),
            heure_debut=time(11, 30),
            heure_fin=time(12, 30),
            db=db_session,
            user={"user_id": user.id, "role": "utilisateur"}
        )

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Créneau déjà réservé pour cette salle"


def test_create_reservation_rejects_past_date(db_session):
    user = create_user(db_session, "owner@example.com")
    salle = create_salle(db_session)

    with pytest.raises(HTTPException) as exc_info:
        creer_reservation(
            salle_id=salle.id,
            date_reservation=past_date(),
            heure_debut=time(9, 0),
            heure_fin=time(10, 0),
            db=db_session,
            user={"user_id": user.id, "role": "utilisateur"}
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == (
        "La date de réservation ne peut pas être passée"
    )


def test_create_reservation_rejects_inactive_room(db_session):
    user = create_user(db_session, "owner@example.com")
    salle = create_salle(db_session)
    salle.active = False
    db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        creer_reservation(
            salle_id=salle.id,
            date_reservation=future_date(),
            heure_debut=time(9, 0),
            heure_fin=time(10, 0),
            db=db_session,
            user={"user_id": user.id, "role": "utilisateur"}
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Cette salle n'est pas disponible"


def test_create_reservation_rejects_unknown_room(db_session):
    user = create_user(db_session, "owner@example.com")

    with pytest.raises(HTTPException) as exc_info:
        creer_reservation(
            salle_id=999,
            date_reservation=future_date(),
            heure_debut=time(9, 0),
            heure_fin=time(10, 0),
            db=db_session,
            user={"user_id": user.id, "role": "utilisateur"}
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Salle introuvable"
