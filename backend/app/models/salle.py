from calendar import monthrange
from datetime import date as date_type, time as time_type
from typing import List

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import Session, relationship

from app.database import Base
from app.models.statuts import StatutSalle


class Salle(Base):
    __tablename__ = "salles"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    localisation = Column(String, nullable=True)
    equipements = Column(String, nullable=True)
    capacite = Column(Integer, nullable=True)
    est_active = Column("active", Boolean, default=True)

    reservations = relationship("Reservation", back_populates="salle")

    @property
    def statut_salle(self) -> str:
        return (
            StatutSalle.ACTIVE.value
            if self.est_active
            else StatutSalle.INACTIVE.value
        )

    # --- Methodes metier (conformes au diagramme de classes) ---

    def est_disponible(
        self,
        db: Session,
        date: date_type,
        heure_debut: time_type,
        heure_fin: time_type,
    ) -> bool:
        from app.models.reservation import Reservation
        from app.models.statuts import StatutReservation

        if not self.est_active:
            return False

        conflit = (
            db.query(Reservation)
            .filter(
                Reservation.salle_id == self.id,
                Reservation.date_reservation == date,
                Reservation.statut == StatutReservation.CONFIRMEE.value,
                Reservation.heure_debut < heure_fin,
                Reservation.heure_fin > heure_debut,
            )
            .first()
        )
        return conflit is None

    def get_reservations_par_date(
        self,
        db: Session,
        date: date_type,
    ) -> List:
        from app.models.reservation import Reservation

        return (
            db.query(Reservation)
            .filter(
                Reservation.salle_id == self.id,
                Reservation.date_reservation == date,
            )
            .all()
        )

    def get_taux_occupation(
        self,
        db: Session,
        mois: int,
        annee: int,
    ) -> float:
        from app.models.reservation import Reservation
        from app.models.statuts import StatutReservation

        nb_jours = monthrange(annee, mois)[1]
        heures_totales = nb_jours * 24.0

        reservations = (
            db.query(Reservation)
            .filter(
                Reservation.salle_id == self.id,
                Reservation.statut == StatutReservation.CONFIRMEE.value,
            )
            .all()
        )

        heures_reservees = 0.0
        for reservation in reservations:
            if (
                reservation.date_reservation.year != annee
                or reservation.date_reservation.month != mois
            ):
                continue
            heures_reservees += reservation.duree_en_heures()

        if heures_totales == 0:
            return 0.0

        return (heures_reservees / heures_totales) * 100.0
