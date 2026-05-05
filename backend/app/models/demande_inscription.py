from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.statuts import StatutDemandeInscription


class DemandeInscription(Base):
    __tablename__ = "demandes_inscription"

    id = Column(Integer, primary_key=True, index=True)
    utilisateur_id = Column(
        Integer,
        ForeignKey("utilisateurs.id"),
        nullable=False,
        unique=True,
    )
    date_soumission = Column(DateTime, default=datetime.utcnow, nullable=False)
    date_traitement = Column(DateTime, nullable=True)
    commentaire_refus = Column(String, nullable=True)
    statut = Column(
        String(50),
        nullable=False,
        default=StatutDemandeInscription.EN_ATTENTE.value,
    )

    utilisateur = relationship(
        "Utilisateur",
        back_populates="demandes_inscription",
    )
