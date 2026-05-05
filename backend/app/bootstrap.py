from app.config import (
    DEFAULT_ADMIN_EMAIL,
    DEFAULT_ADMIN_NOM,
    DEFAULT_ADMIN_PASSWORD,
    DEFAULT_ADMIN_PRENOM,
)
from app.database import Base, SessionLocal, engine
from app.models.notification import Notification
from app.models.salle import Salle
from app.models.statuts import StatutReservation
from app.models.utilisateur import Utilisateur
from app.security.password import hash_password
from sqlalchemy import inspect, text

LEGACY_DEFAULT_ADMIN_EMAIL = "admin@local.test"
DEFAULT_SALLES = [
    {
        "nom": "Salle Horizon",
        "description": "Salle de reunion pour les validations administratives.",
        "capacite": 8,
    },
    {
        "nom": "Salle Atlas",
        "description": "Salle collaborative pour petits groupes.",
        "capacite": 12,
    },
    {
        "nom": "Salle Vision",
        "description": "Espace equipe avec ecran de projection.",
        "capacite": 20,
    },
]


def bootstrap_database() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_schema_columns()
    ensure_default_admin()
    ensure_default_salles()


def ensure_schema_columns() -> None:
    inspector = inspect(engine)

    if "reservations" not in inspector.get_table_names():
        return

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
        existing_names = {
            name for (name,) in db.query(Salle.nom).all()
        }

        salles_to_create = [
            Salle(**salle_data)
            for salle_data in DEFAULT_SALLES
            if salle_data["nom"] not in existing_names
        ]

        if salles_to_create:
            db.add_all(salles_to_create)
            db.commit()
    finally:
        db.close()
