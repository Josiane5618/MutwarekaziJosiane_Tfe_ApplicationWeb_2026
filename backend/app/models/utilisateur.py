from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import Session, relationship

from app.database import Base
from app.models.statuts import StatutCompte, StatutDemandeInscription


class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id = Column(Integer, primary_key=True, index=True)
    prenom = Column(String(100), nullable=False)
    nom = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    mot_de_passe_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="utilisateur")
    actif = Column(Boolean, default=True)
    date_creation = Column(DateTime, nullable=False, default=datetime.utcnow)
    derniere_connexion = Column(DateTime, nullable=True)

    demandes_inscription = relationship(
        "DemandeInscription",
        back_populates="utilisateur",
    )
    donnees_faciales = relationship(
        "DonneeFaciale",
        back_populates="utilisateur",
        uselist=False,
    )

    __mapper_args__ = {
        "polymorphic_identity": "utilisateur",
        "polymorphic_on": role,
    }

    @property
    def statut_compte(self) -> str:
        if self.actif:
            return StatutCompte.ACTIF.value

        latest_demande = max(
            self.demandes_inscription,
            key=lambda demande: demande.id or 0,
            default=None,
        )

        if latest_demande and latest_demande.statut == StatutDemandeInscription.REFUSEE.value:
            return StatutCompte.REFUSE.value

        return StatutCompte.EN_ATTENTE.value

    # --- Methodes metier (conformes au diagramme de classes) ---

    @classmethod
    def authentifier(
        cls,
        db: Session,
        email: str,
        mot_de_passe: str,
        nom: Optional[str] = None,
    ) -> bool:
        from app.security.password import verify_password

        utilisateur = db.query(cls).filter(cls.email == email).first()
        if utilisateur is None or not utilisateur.actif:
            return False
        return verify_password(mot_de_passe, utilisateur.mot_de_passe_hash)

    def consulter_salles(self, db: Session) -> List:
        from app.models.salle import Salle

        return db.query(Salle).filter(Salle.est_active.is_(True)).all()

    def consulter_mes_reservations(self, db: Session) -> List:
        from app.models.reservation import Reservation

        return (
            db.query(Reservation)
            .filter(Reservation.utilisateur_id == self.id)
            .all()
        )

    def modifier_profil(
        self,
        nom: Optional[str] = None,
        prenom: Optional[str] = None,
        email: Optional[str] = None,
    ) -> bool:
        if nom is not None:
            self.nom = nom
        if prenom is not None:
            self.prenom = prenom
        if email is not None:
            self.email = email
        return True

    def get_donnees_faciales(self):
        return self.donnees_faciales
