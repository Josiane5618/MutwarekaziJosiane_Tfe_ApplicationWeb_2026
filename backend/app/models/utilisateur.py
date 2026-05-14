from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship

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
    demandes_inscription = relationship(
        "DemandeInscription",
        back_populates="utilisateur",
    )
    donnees_faciales = relationship(
        "DonneeFaciale",
        back_populates="utilisateur",
        uselist=False,
    )

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
