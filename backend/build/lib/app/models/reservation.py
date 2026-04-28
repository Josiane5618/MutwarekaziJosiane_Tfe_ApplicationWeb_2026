from sqlalchemy import Column, Integer, Date, Time, ForeignKey, String
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.statuts import StatutReservation

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)

    utilisateur_id = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    salle_id = Column(Integer, ForeignKey("salles.id"), nullable=False)

    date = Column(Date, nullable=False)
    heure_debut = Column(Time, nullable=False)
    heure_fin = Column(Time, nullable=False)
    statut = Column(
        String(50),
        nullable=False,
        default=StatutReservation.CONFIRMEE.value
    )

    utilisateur = relationship("Utilisateur", backref="reservations")
    salle = relationship("Salle", back_populates="reservations")
