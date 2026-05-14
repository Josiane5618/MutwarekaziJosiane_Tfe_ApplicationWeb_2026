from datetime import date, datetime, time

import pytest
from fastapi import HTTPException

from app.models.demande_inscription import DemandeInscription
from app.models.donnee_faciale import DonneeFaciale
from app.models.log_acces import LogAcces
from app.models.notification import Notification
from app.models.reservation import Reservation
from app.models.salle import Salle
from app.models.statuts import (
    StatutCompte,
    StatutDemandeInscription,
    StatutReservation,
    StatutSalle,
)
from app.models.utilisateur import Utilisateur
from app.routers import admin as admin_router
from app.routers.admin import (
    SalleCreate,
    SalleUpdate,
    UserUpdate,
    create_salle,
    delete_salle,
    list_access_logs,
    list_pending_users,
    list_registration_requests,
    list_reservations,
    list_salles_admin,
    list_users,
    get_user_face_image,
    update_salle,
    update_user,
    validate_user,
)


def test_list_pending_users_returns_only_inactive_standard_users(db_session):
    pending_user = Utilisateur(
        prenom="Pending",
        nom="User",
        email="pending@example.com",
        mot_de_passe_hash="hash",
        role="utilisateur",
        actif=False
    )
    db_session.add_all([
        pending_user,
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
    db_session.flush()
    db_session.add(
        DemandeInscription(
            utilisateur_id=pending_user.id,
            statut=StatutDemandeInscription.EN_ATTENTE.value,
        )
    )
    db_session.commit()

    response = list_pending_users(db=db_session, admin={"role": "admin"})

    assert len(response) == 1
    assert response[0]["email"] == "pending@example.com"
    assert response[0]["actif"] is False
    assert response[0]["statut_compte"] == StatutCompte.EN_ATTENTE.value
    assert response[0]["demande_inscription"]["statut"] == (
        StatutDemandeInscription.EN_ATTENTE.value
    )
    assert response[0]["donnees_faciales_enregistrees"] is False


def test_validate_user_accepts_pending_user(db_session, monkeypatch):
    monkeypatch.setattr(admin_router, "SMTP_ENABLED", False)
    monkeypatch.setattr(admin_router, "send_email", lambda *args: False)

    user = Utilisateur(
        prenom="Josiane",
        nom="Mutwarekazi",
        email="josiane@example.com",
        mot_de_passe_hash="hash",
        role="utilisateur",
        actif=False
    )
    db_session.add(user)
    db_session.flush()
    db_session.add(
        DemandeInscription(
            utilisateur_id=user.id,
            statut=StatutDemandeInscription.EN_ATTENTE.value,
        )
    )
    db_session.commit()

    response = validate_user(
        user_id=user.id,
        accept=True,
        db=db_session,
        admin={"role": "admin"}
    )

    db_session.refresh(user)
    demande = (
        db_session.query(DemandeInscription)
        .filter(DemandeInscription.utilisateur_id == user.id)
        .first()
    )

    assert response["message"] == "Demande traitée avec succès"
    assert response["email_envoye"] is False
    assert response["email_mode"] == "console"
    assert user.actif is True
    assert demande.statut == StatutDemandeInscription.ACCEPTEE.value
    assert demande.date_traitement is not None


def test_validate_user_refuses_pending_user(db_session, monkeypatch):
    monkeypatch.setattr(admin_router, "SMTP_ENABLED", False)
    monkeypatch.setattr(admin_router, "send_email", lambda *args: False)

    user = Utilisateur(
        prenom="Josiane",
        nom="Mutwarekazi",
        email="refusee@example.com",
        mot_de_passe_hash="hash",
        role="utilisateur",
        actif=False
    )
    db_session.add(user)
    db_session.flush()
    db_session.add(
        DemandeInscription(
            utilisateur_id=user.id,
            statut=StatutDemandeInscription.EN_ATTENTE.value,
        )
    )
    db_session.commit()

    response = validate_user(
        user_id=user.id,
        accept=False,
        db=db_session,
        admin={"role": "admin"}
    )

    db_session.refresh(user)
    demande = (
        db_session.query(DemandeInscription)
        .filter(DemandeInscription.utilisateur_id == user.id)
        .first()
    )

    assert response["message"] == "Demande traitée avec succès"
    assert response["email_envoye"] is False
    assert response["email_mode"] == "console"
    assert user.actif is False
    assert user.statut_compte == StatutCompte.REFUSE.value
    assert demande.statut == StatutDemandeInscription.REFUSEE.value
    assert demande.date_traitement is not None


def test_list_registration_requests_returns_all_request_statuses(db_session):
    pending_user = Utilisateur(
        prenom="Pending",
        nom="User",
        email="pending-history@example.com",
        mot_de_passe_hash="hash",
        role="utilisateur",
        actif=False
    )
    accepted_user = Utilisateur(
        prenom="Accepted",
        nom="User",
        email="accepted-history@example.com",
        mot_de_passe_hash="hash",
        role="utilisateur",
        actif=True
    )
    refused_user = Utilisateur(
        prenom="Refused",
        nom="User",
        email="refused-history@example.com",
        mot_de_passe_hash="hash",
        role="utilisateur",
        actif=False
    )
    admin_user = Utilisateur(
        prenom="Admin",
        nom="User",
        email="admin-history@example.com",
        mot_de_passe_hash="hash",
        role="admin",
        actif=True
    )
    db_session.add_all([pending_user, accepted_user, refused_user, admin_user])
    db_session.flush()
    db_session.add_all([
        DemandeInscription(
            utilisateur_id=pending_user.id,
            statut=StatutDemandeInscription.EN_ATTENTE.value,
            date_soumission=datetime(2026, 5, 1, 10, 0),
        ),
        DemandeInscription(
            utilisateur_id=accepted_user.id,
            statut=StatutDemandeInscription.ACCEPTEE.value,
            date_soumission=datetime(2026, 5, 2, 10, 0),
            date_traitement=datetime(2026, 5, 2, 11, 0),
        ),
        DemandeInscription(
            utilisateur_id=refused_user.id,
            statut=StatutDemandeInscription.REFUSEE.value,
            date_soumission=datetime(2026, 5, 3, 10, 0),
            date_traitement=datetime(2026, 5, 3, 11, 0),
        ),
        DemandeInscription(
            utilisateur_id=admin_user.id,
            statut=StatutDemandeInscription.ACCEPTEE.value,
            date_soumission=datetime(2026, 5, 4, 10, 0),
        ),
    ])
    db_session.add(
        DonneeFaciale(
            utilisateur_id=accepted_user.id,
            image=b"fake-image",
            encodage=b"fake-encoding",
        )
    )
    db_session.commit()

    response = list_registration_requests(
        db=db_session,
        admin={"role": "admin"}
    )

    assert [request["utilisateur"]["email"] for request in response] == [
        "refused-history@example.com",
        "accepted-history@example.com",
        "pending-history@example.com",
    ]
    assert [request["statut"] for request in response] == [
        StatutDemandeInscription.REFUSEE.value,
        StatutDemandeInscription.ACCEPTEE.value,
        StatutDemandeInscription.EN_ATTENTE.value,
    ]
    assert response[1]["utilisateur"]["donnees_faciales_enregistrees"] is True


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


def test_admin_can_view_registered_face_image(db_session):
    user = Utilisateur(
        prenom="Face",
        nom="User",
        email="face@example.com",
        mot_de_passe_hash="hash",
        role="utilisateur",
        actif=False
    )
    db_session.add(user)
    db_session.flush()
    db_session.add(
        DonneeFaciale(
            utilisateur_id=user.id,
            image=b"fake-image",
            encodage=b"fake-encoding",
        )
    )
    db_session.commit()

    response = get_user_face_image(
        user_id=user.id,
        db=db_session,
        admin={"role": "admin"}
    )

    assert response.body == b"fake-image"
    assert response.media_type == "image/jpeg"


def test_admin_face_image_returns_404_when_missing(db_session):
    user = Utilisateur(
        prenom="No",
        nom="Face",
        email="noface@example.com",
        mot_de_passe_hash="hash",
        role="utilisateur",
        actif=False
    )
    db_session.add(user)
    db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        get_user_face_image(
            user_id=user.id,
            db=db_session,
            admin={"role": "admin"}
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Photo faciale introuvable"


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
        admin={"user_id": 9999, "role": "admin"}
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
            admin={"user_id": 9999, "role": "admin"}
        )

    assert getattr(exc_info.value, "status_code", None) == 400
    assert (
        getattr(exc_info.value, "detail", None)
        == "Impossible de désactiver le dernier administrateur actif"
    )


def test_admin_can_create_update_and_deactivate_salle(db_session):
    created = create_salle(
        payload=SalleCreate(
            nom="Salle A",
            description="Bloc administratif",
            localisation="Batiment A - local 105",
            equipements="Projecteur, ordinateur",
            capacite=20,
            active=True
        ),
        db=db_session,
        admin={"role": "admin"}
    )

    assert created["nom"] == "Salle A"
    assert created["description"] == "Bloc administratif"
    assert created["localisation"] == "Batiment A - local 105"
    assert created["equipements"] == "Projecteur, ordinateur"
    assert created["capacite"] == 20
    assert created["active"] is True
    assert created["statut_salle"] == StatutSalle.ACTIVE.value

    salle_id = created["id"]
    updated = update_salle(
        salle_id=salle_id,
        payload=SalleUpdate(
            description="Bloc principal",
            localisation="Batiment B - local 210",
            equipements="Audiovisuel, tableau blanc",
            capacite=24,
            active=False
        ),
        db=db_session,
        admin={"role": "admin"}
    )

    assert updated["description"] == "Bloc principal"
    assert updated["localisation"] == "Batiment B - local 210"
    assert updated["equipements"] == "Audiovisuel, tableau blanc"
    assert updated["capacite"] == 24
    assert updated["active"] is False
    assert updated["statut_salle"] == StatutSalle.INACTIVE.value

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
    assert response[0]["statut"] == StatutReservation.CONFIRMEE.value


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
