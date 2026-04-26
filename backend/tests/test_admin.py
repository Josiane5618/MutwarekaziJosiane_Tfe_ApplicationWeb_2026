from app.models.utilisateur import Utilisateur
from app.routers import admin as admin_router


def test_admin_can_activate_user(db_session):
    user = Utilisateur(
        prenom="Josiane",
        nom="Mutwarekazi",
        email="validation@example.com",
        mot_de_passe_hash="hash-placeholder",
        role="utilisateur",
        actif=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    user_id = user.id

    response = admin_router.validate_user(
        user_id=user_id,
        accept=True,
        db=db_session,
        admin={"user_id": 999, "role": "admin"}
    )

    assert response["message"] == "Demande traitée avec succès"

    updated_user = db_session.query(Utilisateur).filter_by(id=user_id).first()
    assert updated_user.actif is True
