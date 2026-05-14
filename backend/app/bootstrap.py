from datetime import date, datetime

from app.config import (
    DEFAULT_ADMIN_EMAIL,
    DEFAULT_ADMIN_NOM,
    DEFAULT_ADMIN_PASSWORD,
    DEFAULT_ADMIN_PRENOM,
)
from app.database import Base, SessionLocal, engine
from app.models.administrateur import Administrateur
from app.models.demande_inscription import DemandeInscription
from app.models.donnee_faciale import DonneeFaciale
from app.models.reservation import Reservation
from app.models.salle import Salle
from app.models.statuts import StatutDemandeInscription, StatutReservation
from app.models.utilisateur import Utilisateur
from app.security.biometric_cipher import encrypt_encoding
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
    encrypt_existing_face_encodings()
    mark_terminated_reservations()


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

        with engine.begin() as connection:
            if "date_creation" not in utilisateur_columns:
                connection.execute(
                    text(
                        "ALTER TABLE utilisateurs "
                        "ADD COLUMN date_creation TIMESTAMP NOT NULL DEFAULT NOW()"
                    )
                )

            if "derniere_connexion" not in utilisateur_columns:
                connection.execute(
                    text(
                        "ALTER TABLE utilisateurs "
                        "ADD COLUMN derniere_connexion TIMESTAMP NULL"
                    )
                )

            if "niveau_acces" not in utilisateur_columns:
                connection.execute(
                    text(
                        "ALTER TABLE utilisateurs "
                        "ADD COLUMN niveau_acces INTEGER NULL"
                    )
                )

            if "derniere_action" not in utilisateur_columns:
                connection.execute(
                    text(
                        "ALTER TABLE utilisateurs "
                        "ADD COLUMN derniere_action VARCHAR NULL"
                    )
                )

    if "reservations" in table_names:
        reservation_columns_2 = {
            column["name"] for column in inspector.get_columns("reservations")
        }

        with engine.begin() as connection:
            if "date_creation" not in reservation_columns_2:
                connection.execute(
                    text(
                        "ALTER TABLE reservations "
                        "ADD COLUMN date_creation TIMESTAMP NOT NULL DEFAULT NOW()"
                    )
                )

            if "date_modification" not in reservation_columns_2:
                connection.execute(
                    text(
                        "ALTER TABLE reservations "
                        "ADD COLUMN date_modification TIMESTAMP NULL"
                    )
                )

    if "logs_acces" in table_names:
        log_columns = {
            column["name"] for column in inspector.get_columns("logs_acces")
        }

        if "details" not in log_columns:
            with engine.begin() as connection:
                connection.execute(
                    text("ALTER TABLE logs_acces ADD COLUMN details VARCHAR NULL")
                )

    if "notifications" in table_names:
        notification_columns = {
            column["name"] for column in inspector.get_columns("notifications")
        }

        with engine.begin() as connection:
            if "sujet" not in notification_columns:
                connection.execute(
                    text("ALTER TABLE notifications ADD COLUMN sujet VARCHAR NULL")
                )

            if "type" not in notification_columns:
                connection.execute(
                    text("ALTER TABLE notifications ADD COLUMN type VARCHAR(50) NULL")
                )

            if "est_envoyee" not in notification_columns:
                connection.execute(
                    text(
                        "ALTER TABLE notifications "
                        "ADD COLUMN est_envoyee BOOLEAN NOT NULL DEFAULT TRUE"
                    )
                )

    if "donnees_faciales" in table_names:
        donnee_columns = {
            column["name"] for column in inspector.get_columns("donnees_faciales")
        }

        if "est_chiffre" not in donnee_columns:
            with engine.begin() as connection:
                connection.execute(
                    text(
                        "ALTER TABLE donnees_faciales "
                        "ADD COLUMN est_chiffre BOOLEAN NOT NULL DEFAULT FALSE"
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
            admin = Administrateur(
                prenom=DEFAULT_ADMIN_PRENOM,
                nom=DEFAULT_ADMIN_NOM,
                email=DEFAULT_ADMIN_EMAIL,
                mot_de_passe_hash=hash_password(DEFAULT_ADMIN_PASSWORD),
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


def encrypt_existing_face_encodings() -> None:
    """Chiffre les encodages faciaux deja stockes en clair."""
    db = SessionLocal()

    try:
        donnees_a_chiffrer = (
            db.query(DonneeFaciale)
            .filter(DonneeFaciale.est_chiffre == False)
            .all()
        )

        for donnee in donnees_a_chiffrer:
            if donnee.encodage_facial is None:
                continue
            donnee.encodage_facial = encrypt_encoding(donnee.encodage_facial)
            donnee.est_chiffre = True

        db.commit()
    finally:
        db.close()


def mark_terminated_reservations() -> None:
    """Marque comme TERMINEE les reservations confirmees dont la date est passee."""
    db = SessionLocal()

    try:
        aujourd_hui = date.today()
        db.query(Reservation).filter(
            Reservation.statut == StatutReservation.CONFIRMEE.value,
            Reservation.date_reservation < aujourd_hui,
        ).update(
            {Reservation.statut: StatutReservation.TERMINEE.value},
            synchronize_session=False,
        )
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
