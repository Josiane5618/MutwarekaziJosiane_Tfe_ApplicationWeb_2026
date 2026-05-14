from datetime import datetime

from app.config import (
    DEFAULT_ADMIN_EMAIL,
    DEFAULT_ADMIN_NOM,
    DEFAULT_ADMIN_PASSWORD,
    DEFAULT_ADMIN_PRENOM,
)
from app.database import Base, SessionLocal, engine
from app.models.demande_inscription import DemandeInscription
from app.models.salle import Salle
from app.models.statuts import StatutDemandeInscription, StatutReservation
from app.models.utilisateur import Utilisateur
from app.security.password import hash_password
from sqlalchemy import inspect, text

LEGACY_DEFAULT_ADMIN_EMAIL = "admin@local.test"
DEFAULT_SALLES = [
    {
        "nom": "Salle Horizon",
        "description": "Salle calme adaptee aux reunions administratives et aux entretiens.",
        "localisation": "Batiment A - local 101",
        "equipements": "Tableau blanc, ordinateur, connexion reseau",
        "capacite": 8,
    },
    {
        "nom": "Salle Atlas",
        "description": "Salle collaborative adaptee aux travaux de groupe.",
        "localisation": "Batiment A - local 203",
        "equipements": "Projecteur, tableau blanc, prises multiples",
        "capacite": 12,
    },
    {
        "nom": "Salle Vision",
        "description": "Grande salle adaptee aux presentations et formations.",
        "localisation": "Batiment B - local 305",
        "equipements": "Projecteur, ordinateur, ecran mural, audiovisuel",
        "capacite": 20,
    },
]


def bootstrap_database() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_schema_columns()
    ensure_missing_registration_requests()
    ensure_default_admin()
    ensure_default_salles()


def ensure_schema_columns() -> None:
    inspector = inspect(engine)

    table_names = inspector.get_table_names()

    if "reservations" in table_names:
        reservation_columns = {
            column["name"] for column in inspector.get_columns("reservations")
        }

        if "statut" not in reservation_columns:
            with engine.begin() as connection:
                connection.execute(
                    text(
                        "ALTER TABLE reservations "
                        "ADD COLUMN statut VARCHAR(50) NOT NULL "
                        f"DEFAULT '{StatutReservation.CONFIRMEE.value}'"
                    )
                )

    if "salles" in table_names:
        salle_columns = {
            column["name"] for column in inspector.get_columns("salles")
        }

        with engine.begin() as connection:
            if "localisation" not in salle_columns:
                connection.execute(
                    text("ALTER TABLE salles ADD COLUMN localisation VARCHAR")
                )

            if "equipements" not in salle_columns:
                connection.execute(
                    text("ALTER TABLE salles ADD COLUMN equipements VARCHAR")
                )

    if "utilisateurs" in table_names:
        utilisateur_columns = {
            column["name"] for column in inspector.get_columns("utilisateurs")
        }

        if "date_creation" not in utilisateur_columns:
            with engine.begin() as connection:
                connection.execute(
                    text(
                        "ALTER TABLE utilisateurs "
                        "ADD COLUMN date_creation TIMESTAMP NOT NULL DEFAULT NOW()"
                    )
                )


def ensure_missing_registration_requests() -> None:
    db = SessionLocal()

    try:
        standard_users = (
            db.query(Utilisateur)
            .filter(Utilisateur.role == "utilisateur")
            .all()
        )

        for user in standard_users:
            existing_request = (
                db.query(DemandeInscription)
                .filter(DemandeInscription.utilisateur_id == user.id)
                .first()
            )

            if existing_request is None:
                request_status = (
                    StatutDemandeInscription.ACCEPTEE.value
                    if user.actif
                    else StatutDemandeInscription.EN_ATTENTE.value
                )
                db.add(
                    DemandeInscription(
                        utilisateur_id=user.id,
                        statut=request_status,
                        date_traitement=(
                            datetime.utcnow()
                            if user.actif
                            else None
                        ),
                    )
                )

        db.commit()
    finally:
        db.close()


def ensure_default_admin() -> None:
    db = SessionLocal()

    try:
        admin = (
            db.query(Utilisateur)
            .filter(Utilisateur.email == DEFAULT_ADMIN_EMAIL)
            .first()
        )

        if admin is None:
            admin = (
                db.query(Utilisateur)
                .filter(Utilisateur.email == LEGACY_DEFAULT_ADMIN_EMAIL)
                .first()
            )

            if admin is not None:
                admin.email = DEFAULT_ADMIN_EMAIL
                admin.prenom = DEFAULT_ADMIN_PRENOM
                admin.nom = DEFAULT_ADMIN_NOM
                admin.role = "admin"
                admin.actif = True
                db.commit()
                return

        if admin is None:
            admin = Utilisateur(
                prenom=DEFAULT_ADMIN_PRENOM,
                nom=DEFAULT_ADMIN_NOM,
                email=DEFAULT_ADMIN_EMAIL,
                mot_de_passe_hash=hash_password(DEFAULT_ADMIN_PASSWORD),
                role="admin",
                actif=True,
            )
            db.add(admin)
            db.commit()
            return

        updated = False

        if admin.role != "admin":
            admin.role = "admin"
            updated = True

        if not admin.actif:
            admin.actif = True
            updated = True

        if updated:
            db.commit()
    finally:
        db.close()


def ensure_default_salles() -> None:
    db = SessionLocal()

    try:
        existing_salles = {
            salle.nom: salle for salle in db.query(Salle).all()
        }

        salles_to_create = []

        for salle_data in DEFAULT_SALLES:
            existing_salle = existing_salles.get(salle_data["nom"])

            if existing_salle is None:
                salles_to_create.append(Salle(**salle_data))
                continue

            for field, value in salle_data.items():
                if getattr(existing_salle, field) in (None, ""):
                    setattr(existing_salle, field, value)

        if salles_to_create:
            db.add_all(salles_to_create)

        db.commit()
    finally:
        db.close()
