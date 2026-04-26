import asyncio

import numpy as np
import pytest

from app.models.donnee_faciale import DonneeFaciale
from app.models.utilisateur import Utilisateur
from app.routers import auth as auth_router
from fastapi import HTTPException


class FakeUploadFile:
    def __init__(self, content: bytes):
        self.content = content

    async def read(self):
        return self.content


def test_register_creates_inactive_user_with_face_data(db_session, monkeypatch):
    monkeypatch.setattr(
        auth_router,
        "extract_face_encoding",
        lambda image_bytes: np.ones(128, dtype=np.float32)
    )
    monkeypatch.setattr(
        auth_router,
        "hash_password",
        lambda password: "hashed-test-password"
    )

    upload = FakeUploadFile(b"fake-image-content")

    response = asyncio.run(
        auth_router.register_user(
            prenom="Josiane",
            nom="Mutwarekazi",
            email="josiane@example.com",
            password="motdepasse123",
            file=upload,
            db=db_session
        )
    )

    assert "user_id" in response

    user = db_session.query(Utilisateur).filter_by(email="josiane@example.com").first()
    face_data = (
        db_session.query(DonneeFaciale)
        .filter_by(utilisateur_id=user.id)
        .first()
    )

    assert user is not None
    assert user.actif is False
    assert user.role == "utilisateur"
    assert user.mot_de_passe_hash == "hashed-test-password"
    assert face_data is not None

def test_login_rejects_inactive_user(db_session, monkeypatch):
    monkeypatch.setattr(
        auth_router,
        "verify_password",
        lambda password, hashed_password: True
    )

    user = Utilisateur(
        prenom="Josiane",
        nom="Mutwarekazi",
        email="inactive@example.com",
        mot_de_passe_hash="hashed-password",
        role="utilisateur",
        actif=False
    )
    db_session.add(user)
    db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        auth_router.login_user(
            credentials=type(
                "Credentials",
                (),
                {"email": "inactive@example.com", "password": "motdepasse123"}
            )(),
            db=db_session
        )

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Compte non validé par un administrateur"


def test_login_returns_token_for_active_user(db_session, monkeypatch):
    monkeypatch.setattr(
        auth_router,
        "verify_password",
        lambda password, hashed_password: True
    )

    user = Utilisateur(
        prenom="Josiane",
        nom="Mutwarekazi",
        email="active@example.com",
        mot_de_passe_hash="hashed-password",
        role="utilisateur",
        actif=True
    )
    db_session.add(user)
    db_session.commit()

    response = auth_router.login_user(
        credentials=type(
            "Credentials",
            (),
            {"email": "active@example.com", "password": "motdepasse123"}
        )(),
        db=db_session
    )

    assert "access_token" in response
    assert response["token_type"] == "bearer"
