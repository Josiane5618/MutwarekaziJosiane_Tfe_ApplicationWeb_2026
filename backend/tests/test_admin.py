from app.models.utilisateur import Utilisateur
from app.routers.admin import list_pending_users, validate_user


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
