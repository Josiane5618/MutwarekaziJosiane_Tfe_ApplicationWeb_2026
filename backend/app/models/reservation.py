from datetime import datetime, date as date_type, time as time_type
from typing import List

from sqlalchemy import Column, Integer, Date, Time, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.statuts import StatutReservation


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)

    utilisateur_id = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    salle_id = Column(Integer, ForeignKey("salles.id"), nullable=False)

    date_reservation = Column("date", Date, nullable=False)
    heure_debut = Column(Time, nullable=False)
    heure_fin = Column(Time, nullable=False)
    statut = Column(
        String(50),
        nullable=False,
        default=StatutReservation.CONFIRMEE.value,
    )
    date_creation = Column(DateTime, nullable=False, default=datetime.utcnow)
    date_modification = Column(DateTime, nullable=True, onupdate=datetime.utcnow)

    utilisateur = relationship("Utilisateur", backref="reservations")
    salle = relationship("Salle", back_populates="reservations")

    # --- Methodes metier (conformes au diagramme de classes) ---

    def verifier_conflit(self, reservations_existantes: List) -> bool:
        for autre in reservations_existantes:
            if autre.id == self.id:
                continue
            if autre.salle_id != self.salle_id:
                continue
            if autre.date_reservation != self.date_reservation:
                continue
            if autre.statut != StatutReservation.CONFIRMEE.value:
                continue
            if (
                autre.heure_debut < self.heure_fin
                and autre.heure_fin > self.heure_debut
            ):
                return True
        return False

    def annuler(self) -> bool:
        if self.statut == StatutReservation.ANNULEE.value:
            return False
        self.statut = StatutReservation.ANNULEE.value
        return True

    def modifier_creneau(
        self,
        date: date_type,
        debut: time_type,
        fin: time_type,
    ) -> bool:
        self.date_reservation = date
        self.heure_debut = debut
        self.heure_fin = fin
        self.date_modification = datetime.utcnow()
        return True

    def duree_en_heures(self) -> float:
        debut_sec = (
            self.heure_debut.hour * 3600
            + self.heure_debut.minute * 60
            + self.heure_debut.second
        )
        fin_sec = (
            self.heure_fin.hour * 3600
            + self.heure_fin.minute * 60
            + self.heure_fin.second
        )
        return (fin_sec - debut_sec) / 3600.0
