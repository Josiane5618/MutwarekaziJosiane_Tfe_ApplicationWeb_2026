from datetime import date, datetime, time

import pytest
from fastapi import HTTPException

from app.models.log_acces import LogAcces
from app.models.notification import Notification
from app.models.reservation import Reservation
from app.models.salle import Salle
from app.models.utilisateur import Utilisateur
from app.routers.admin import (
    SalleCreate,
    SalleUpdate,
    UserUpdate,
    create_salle,
    delete_salle,
    list_access_logs,
    list_pending_users,
    list_reservations,
    list_salles_admin,
    list_users,
    update_salle,
    update_user,
    validate_user,
)


def test_list_pending_users_returns_only_inactive_standard_users(db_session):
    db_session.add_all([
        Utilisateur(
            prenom="Pending",
            nom="User",
            email="pending@example.com",
            mot_de_passe_hash="hash",
            role="utilisateur",
            actif=False
        ),
        Utilisateur(
            prenom="Active",
            nom="User",
            email="active@example.com",
            mot_de_passe_hash="hash",
            role="utilisateur",
            actif=True
        ),
        Utilisateur(
            prenom="Admin",
            nom="Root",
            email="admin@example.com",
            mot_de_passe_hash="hash",
            role="admin",
            actif=True
        )
    ])
    db_session.commit()

    response = list_pending_users(db=db_session, admin={"role": "admin"})

    assert len(response) == 1
    assert response[0]["email"] == "pending@example.com"
    assert response[0]["actif"] is False


def test_validate_user_accepts_pending_user(db_session):
    user = Utilisateur(
        prenom="Josiane",
        nom="Mutwarekazi",
        email="josiane@example.com",
        mot_de_passe_hash="hash",
        role="utilisateur",
        actif=False
    )
    db_session.add(user)
    db_session.commit()

    response = validate_user(
        user_id=user.id,
        accept=True,
        db=db_session,
        admin={"role": "admin"}
    )

    db_session.refresh(user)

    assert response["message"] == "Demande traitée avec succès"
    assert user.actif is True


def test_list_users_returns_all_users_in_descending_id_order(db_session):
    db_session.add_all([
        Utilisateur(
            prenom="Alpha",
            nom="User",
            email="alpha@example.com",
            mot_de_passe_hash="hash",
            role="utilisateur",
            actif=True
        ),
        Utilisateur(
            prenom="Beta",
            nom="Admin",
            email="beta@example.com",
            mot_de_passe_hash="hash",
            role="admin",
            actif=True
        )
    ])
    db_session.commit()

    response = list_users(db=db_session, admin={"role": "admin"})

    assert [user["email"] for user in response] == [
        "beta@example.com",
        "alpha@example.com",
    ]


def test_admin_can_deactivate_standard_user(db_session):
    user = Utilisateur(
        prenom="Active",
        nom="User",
        email="active-user@example.com",
        mot_de_passe_hash="hash",
        role="utilisateur",
        actif=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    response = update_user(
        user_id=user.id,
        payload=UserUpdate(actif=False),
        db=db_session,
        admin={"role": "admin"}
    )

    db_session.refresh(user)
    notification = (
        db_session.query(Notification)
        .filter(Notification.utilisateur_id == user.id)
        .first()
    )

    assert response["actif"] is False
    assert user.actif is False
    assert notification is not None
    assert "désactivé" in notification.message


def test_admin_cannot_deactivate_admin_user(db_session):
    admin_user = Utilisateur(
        prenom="Admin",
        nom="Root",
        email="admin-root@example.com",
        mot_de_passe_hash="hash",
        role="admin",
        actif=True
    )
    db_session.add(admin_user)
    db_session.commit()
    db_session.refresh(admin_user)

    with pytest.raises(HTTPException) as exc_info:
        update_user(
            user_id=admin_user.id,
            payload=UserUpdate(actif=False),
            db=db_session,
            admin={"role": "admin"}
        )

    assert getattr(exc_info.value, "status_code", None) == 400
    assert getattr(exc_info.value, "detail", None) == "Impossible de désactiver un administrateur"


def test_admin_can_create_update_and_deactivate_salle(db_session):
    created = create_salle(
        payload=SalleCreate(
            nom="Salle A",
            description="Bloc administratif",
            capacite=20,
            active=True
        ),
        db=db_session,
        admin={"role": "admin"}
    )

    assert created["nom"] == "Salle A"
    assert created["capacite"] == 20
    assert created["active"] is True

    salle_id = created["id"]
    updated = update_salle(
        salle_id=salle_id,
        payload=SalleUpdate(
            description="Bloc principal",
            capacite=24,
            active=False
        ),
        db=db_session,
        admin={"role": "admin"}
    )

    assert updated["description"] == "Bloc principal"
    assert updated["capacite"] == 24
    assert updated["active"] is False

    deleted = delete_salle(
        salle_id=salle_id,
        db=db_session,
        admin={"role": "admin"}
    )

    assert deleted["message"] == "Salle desactivee avec succes"
    assert deleted["salle"]["active"] is False


def test_list_salles_admin_returns_active_and_inactive_rooms(db_session):
    db_session.add_all([
        Salle(nom="Salle inactive", active=False),
        Salle(nom="Salle active", active=True),
    ])
    db_session.commit()

    response = list_salles_admin(db=db_session, admin={"role": "admin"})

    assert [salle["nom"] for salle in response] == [
        "Salle active",
        "Salle inactive",
    ]


def test_list_reservations_returns_user_and_room_details(db_session):
    user = Utilisateur(
        prenom="Josiane",
        nom="Mutwarekazi",
        email="josiane@example.com",
        mot_de_passe_hash="hash",
        role="utilisateur",
        actif=True
    )
    salle = Salle(
        nom="Salle Reunion",
        description="Premier etage",
        capacite=12,
        active=True
    )
    db_session.add_all([user, salle])
    db_session.commit()

    reservation = Reservation(
        utilisateur_id=user.id,
        salle_id=salle.id,
        date=date(2026, 4, 29),
        heure_debut=time(9, 0),
        heure_fin=time(10, 0)
    )
    db_session.add(reservation)
    db_session.commit()

    response = list_reservations(db=db_session, admin={"role": "admin"})

    assert len(response) == 1
    assert response[0]["utilisateur"]["email"] == "josiane@example.com"
    assert response[0]["salle"]["nom"] == "Salle Reunion"
    assert response[0]["date"] == "2026-04-29"


def test_list_access_logs_returns_user_details(db_session):
    user = Utilisateur(
        prenom="Access",
        nom="User",
        email="access@example.com",
        mot_de_passe_hash="hash",
        role="utilisateur",
        actif=True
    )
    db_session.add(user)
    db_session.commit()

    log = LogAcces(
        utilisateur_id=user.id,
        date_acces=datetime(2026, 4, 29, 14, 30),
        resultat="ACCES_AUTORISE",
        distance=0.12
    )
    db_session.add(log)
    db_session.commit()

    response = list_access_logs(db=db_session, admin={"role": "admin"})

    assert len(response) == 1
    assert response[0]["utilisateur"]["email"] == "access@example.com"
    assert response[0]["resultat"] == "ACCES_AUTORISE"
    assert response[0]["distance"] == 0.12
