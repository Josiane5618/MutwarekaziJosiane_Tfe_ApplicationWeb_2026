from datetime import date, time

import pytest
from fastapi import HTTPException

from app.models.notification import Notification
from app.models.reservation import Reservation
from app.models.salle import Salle
from app.models.utilisateur import Utilisateur
from app.routers.reservation import annuler_reservation


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


def create_reservation(db_session, user_id):
    salle = Salle(
        nom=f"Salle {user_id}",
        description="Salle de test",
        capacite=10,
        active=True
    )
    db_session.add(salle)
    db_session.commit()
    db_session.refresh(salle)

    reservation = Reservation(
        utilisateur_id=user_id,
        salle_id=salle.id,
        date=date(2026, 5, 4),
        heure_debut=time(9, 0),
        heure_fin=time(10, 0)
    )
    db_session.add(reservation)
    db_session.commit()
    db_session.refresh(reservation)
    return reservation


def test_user_can_cancel_own_reservation(db_session):
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
    assert remaining_reservation is None
    assert notification is not None
    assert "annulée" in notification.message


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
